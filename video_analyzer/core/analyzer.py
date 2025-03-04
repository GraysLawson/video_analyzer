import os
import logging
import concurrent.futures
from collections import defaultdict
from typing import Dict, List, Set, Optional, Callable, Tuple, Any
import hashlib
from functools import lru_cache
from .video_metadata import VideoMetadata
from .content_info import ContentInfo

class VideoAnalyzer:
    def __init__(self, directory: str, output_dir: Optional[str] = None, dry_run: bool = False, min_similarity: float = 0.95):
        self.directory = os.path.abspath(directory)
        self.output_dir = output_dir
        self.dry_run = dry_run
        self.min_similarity = min_similarity
        self.content_data = defaultdict(list)
        self.duplicates = {}
        self.selected_for_deletion = set()
        self._metadata_cache = {}
        # Cache of file sizes for better performance
        self._file_size_cache = {}
    
    def find_video_files(self) -> List[str]:
        """Find all video files in the directory and subdirectories."""
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        video_files = []
        
        logging.info(f"Scanning directory: {self.directory}")
        # Use os.walk with topdown=True for better memory usage
        for dirpath, _, filenames in os.walk(self.directory, topdown=True):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in video_extensions:
                    file_path = os.path.join(dirpath, filename)
                    video_files.append(file_path)
                    # Cache file size while we're at it
                    try:
                        self._file_size_cache[file_path] = os.path.getsize(file_path)
                    except OSError:
                        logging.warning(f"Could not get size of {file_path}")
        
        logging.info(f"Found {len(video_files)} video files")
        return video_files
    
    def process_single_file(self, file_path: str) -> Optional[Dict]:
        """Process a single video file and return its metadata."""
        try:
            # Check cache first
            if file_path in self._metadata_cache:
                return self._metadata_cache[file_path]
            
            # Get metadata
            metadata = VideoMetadata.get_video_metadata(file_path)
            if metadata:
                self._metadata_cache[file_path] = metadata
                # Cache file size if not already cached
                if file_path not in self._file_size_cache:
                    try:
                        self._file_size_cache[file_path] = os.path.getsize(file_path)
                    except OSError:
                        pass
            return metadata
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            return None
    
    def add_file_metadata(self, file_path: str, metadata: Dict) -> None:
        """Add processed file metadata to the content data."""
        # Create content signature
        content_signature = self._create_content_signature(metadata, file_path)
        
        # Add file info to content data
        self.content_data[content_signature].append({
            'path': file_path,
            'filename': os.path.basename(file_path),
            **metadata
        })
    
    def scan_video_files(self, video_files: List[str], progress_callback: Optional[Callable] = None) -> None:
        """Process the video files and extract metadata using parallel processing."""
        # Use batch processing for better performance
        batch_size = min(100, max(10, len(video_files) // (os.cpu_count() or 1)))
        
        # Process files in batches
        for i in range(0, len(video_files), batch_size):
            batch = video_files[i:i + batch_size]
            # Use VideoMetadata's batch processing capabilities
            results = VideoMetadata.batch_process_files(batch)
            
            # Add results to our data structures
            for file_path, metadata in results.items():
                self.add_file_metadata(file_path, metadata)
                if progress_callback:
                    progress_callback(file_path)
    
    @lru_cache(maxsize=1024)
    def _clean_filename(self, filename: str) -> str:
        """Clean filename by removing quality indicators and non-alphanumeric chars."""
        quality_indicators = {'1080p', '720p', '480p', '2160p', '4k', 'uhd', 'hd', 
                            'dvdrip', 'bdrip', 'webdl', 'bluray', 'web', 'hdtv'}
        
        # Get base name without extension
        base_name = os.path.splitext(filename)[0].lower()
        
        # More efficient string cleaning
        words = base_name.split()
        cleaned_words = []
        for word in words:
            if word not in quality_indicators and not any(qi in word for qi in quality_indicators):
                cleaned_words.append(''.join(c for c in word if c.isalnum()))
        
        return ' '.join(cleaned_words)
    
    def _create_content_signature(self, metadata: Dict, file_path: str) -> str:
        """Create a content signature for grouping similar videos."""
        # Use duration as primary similarity metric
        duration = metadata.get('duration_value', 0)
        file_size = metadata.get('file_size_value', 0)
        
        # Clean the filename
        base_name = self._clean_filename(os.path.basename(file_path))
        
        # Create signature combining cleaned name and duration
        # Round duration to nearest second to account for small variations
        duration_key = round(duration)
        
        # If file size is very different, it might be a different encoding
        # Use size ranges to group similar files
        size_range = file_size // (100 * 1024)  # Group by 100MB ranges
        
        # Include a hash of the first part of the base name for better differentiation
        # This helps avoid false positives when duration is similar but content is different
        name_hash = hashlib.md5(base_name[:20].encode()).hexdigest()[:8]
        
        return f"{name_hash}|{duration_key}|{size_range}"
    
    def find_duplicates(self) -> Dict:
        """Identify duplicates using content signatures and metadata."""
        self.duplicates = {}
        duplicate_groups = 0
        
        for content_signature, files in self.content_data.items():
            if len(files) > 1:
                # Sort files by resolution (highest to lowest)
                files_sorted = sorted(
                    files,
                    key=lambda x: (
                        x.get('height', 0) * x.get('width', 0),
                        x.get('bitrate_value', 0),
                        x.get('fps', 0)
                    ),
                    reverse=True
                )
                
                # Compare file metadata for similarity
                similar_files = self._group_similar_files(files_sorted)
                
                # Add groups with multiple files to duplicates
                for group in similar_files:
                    if len(group) > 1:
                        self.duplicates[f"group_{duplicate_groups}"] = group
                        duplicate_groups += 1
                        
                        # Log duplicate group details
                        logging.info(f"Found duplicate group {duplicate_groups}:")
                        for file_info in group:
                            size = self._get_file_size(file_info['path'])
                            logging.info(
                                f"  - {file_info['path']} "
                                f"({file_info['resolution']}, {size} bytes)"
                            )
        
        return self.duplicates
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size with caching."""
        if file_path not in self._file_size_cache:
            try:
                self._file_size_cache[file_path] = os.path.getsize(file_path)
            except OSError:
                logging.warning(f"Could not get size of {file_path}")
                return 0
        return self._file_size_cache[file_path]
    
    def _group_similar_files(self, files: List[Dict]) -> List[List[Dict]]:
        """Group files that are similar based on metadata."""
        # Use more efficient algorithm for grouping similar files
        result_groups = []
        remaining = set(range(len(files)))
        
        while remaining:
            # Get the next file index
            i = min(remaining)
            remaining.remove(i)
            
            # Create a new group with this file
            current_group = [files[i]]
            
            # Find all files similar to this one
            for j in list(remaining):
                if self._are_files_similar(files[i], files[j]):
                    current_group.append(files[j])
                    remaining.remove(j)
            
            # Add the group to results
            result_groups.append(current_group)
        
        return result_groups
    
    def _are_files_similar(self, file1: Dict, file2: Dict) -> bool:
        """Determine if two files are similar based on their metadata."""
        # If paths are the same, they're the same file
        if file1['path'] == file2['path']:
            return True
        
        # Calculate similarity score
        similarity_score = self._calculate_similarity_score(file1, file2)
        
        # Check if similarity exceeds threshold
        return similarity_score >= self.min_similarity
    
    def _calculate_similarity_score(self, file1: Dict, file2: Dict) -> float:
        """Calculate similarity score between two files based on metadata."""
        # Start with a base score
        score = 0.0
        total_weight = 0.0
        
        # Check filename similarity (excluding resolution markers and extensions)
        base_name1 = self._clean_filename(os.path.basename(file1['path']))
        base_name2 = self._clean_filename(os.path.basename(file2['path']))
        
        # Calculate weighted scores
        weights = {
            'filename': 0.3,
            'duration': 0.5,
            'resolution': 0.1,
            'format': 0.05,
            'codec': 0.05
        }
        
        # Filename similarity (Jaccard similarity of words)
        if base_name1 and base_name2:
            words1 = set(base_name1.split())
            words2 = set(base_name2.split())
            
            if words1 and words2:
                overlap = len(words1.intersection(words2))
                jaccard = overlap / len(words1.union(words2))
                score += jaccard * weights['filename']
            else:
                # Skip filename comparison if no words
                score += weights['filename']
        else:
            # Skip filename comparison if no valid names
            score += weights['filename']
        
        total_weight += weights['filename']
        
        # Duration similarity (weighted heavily)
        duration1 = file1.get('duration_value', 0)
        duration2 = file2.get('duration_value', 0)
        
        if duration1 > 0 and duration2 > 0:
            # Calculate duration similarity
            dur_ratio = min(duration1, duration2) / max(duration1, duration2)
            score += dur_ratio * weights['duration']
            total_weight += weights['duration']
        
        # Format and codec similarity (small weights)
        if file1.get('format') == file2.get('format'):
            score += weights['format']
        total_weight += weights['format']
        
        if file1.get('codec') == file2.get('codec'):
            score += weights['codec']
        total_weight += weights['codec']
        
        # Normalize the score
        if total_weight > 0:
            return score / total_weight
        return 0.0
    
    def auto_select_files(self, keep_highest_resolution: bool = True) -> None:
        """Automatically select files for deletion based on criteria."""
        self.selected_for_deletion.clear()
        
        # Process each duplicate group
        for group_id, files in self.duplicates.items():
            if len(files) <= 1:
                continue
                
            if keep_highest_resolution:
                # Sort by resolution (highest first)
                sorted_files = sorted(
                    files, 
                    key=lambda x: (
                        x.get('height', 0) * x.get('width', 0),
                        x.get('bitrate_value', 0),
                        -self._get_file_size(x['path'])  # Prefer smaller file size if resolution is the same
                    ), 
                    reverse=True
                )
                
                # Keep the highest resolution, mark others for deletion
                for file_info in sorted_files[1:]:
                    self.selected_for_deletion.add(file_info['path'])
            else:
                # Sort by file size (smallest first)
                sorted_files = sorted(
                    files,
                    key=lambda x: self._get_file_size(x['path'])
                )
                
                # Keep the smallest file, mark others for deletion
                for file_info in sorted_files[1:]:
                    self.selected_for_deletion.add(file_info['path'])
    
    def delete_selected_files(self) -> Dict[str, Any]:
        """Delete the files that have been selected for deletion."""
        results = {
            'deleted': [],
            'failed': [],
            'skipped': [],
            'total_freed': 0
        }
        
        if self.dry_run:
            logging.info("Dry run mode: No files will be deleted")
            for file_path in self.selected_for_deletion:
                logging.info(f"Would delete: {file_path}")
                size = self._get_file_size(file_path)
                results['skipped'].append({
                    'path': file_path,
                    'size': size
                })
                results['total_freed'] += size
            return results
            
        for file_path in self.selected_for_deletion:
            try:
                size = self._get_file_size(file_path)
                
                # Create output directory if specified
                if self.output_dir:
                    os.makedirs(self.output_dir, exist_ok=True)
                    
                    # Move to output directory instead of deleting
                    target_path = os.path.join(self.output_dir, os.path.basename(file_path))
                    os.rename(file_path, target_path)
                    logging.info(f"Moved: {file_path} -> {target_path}")
                    results['deleted'].append({
                        'path': file_path,
                        'size': size,
                        'moved_to': target_path
                    })
                else:
                    # Delete the file
                    os.remove(file_path)
                    logging.info(f"Deleted: {file_path}")
                    results['deleted'].append({
                        'path': file_path,
                        'size': size
                    })
                    
                results['total_freed'] += size
                
            except Exception as e:
                logging.error(f"Failed to delete {file_path}: {str(e)}")
                results['failed'].append({
                    'path': file_path,
                    'error': str(e)
                })
                
        return results 