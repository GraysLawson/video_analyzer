import os
import logging
from collections import defaultdict
from typing import Dict, List, Set, Optional, Callable, Tuple
from .video_metadata import VideoMetadata
from .content_info import ContentInfo

class VideoAnalyzer:
    def __init__(self, directory: str, output_dir: Optional[str] = None, dry_run: bool = False, min_similarity: float = 0.95):
        self.directory = directory
        self.output_dir = output_dir
        self.dry_run = dry_run
        self.min_similarity = min_similarity
        self.content_data = defaultdict(list)
        self.duplicates = {}
        self.selected_for_deletion = set()
        self._metadata_cache = {}
    
    def find_video_files(self) -> List[str]:
        """Find all video files in the directory and subdirectories."""
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        video_files = []
        
        logging.info(f"Scanning directory: {self.directory}")
        for dirpath, _, filenames in os.walk(self.directory):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in video_extensions:
                    file_path = os.path.join(dirpath, filename)
                    video_files.append(file_path)
                    logging.debug(f"Found video file: {file_path}")
        
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
        """Process the video files and extract metadata."""
        for file_path in video_files:
            try:
                metadata = self.process_single_file(file_path)
                if metadata:
                    self.add_file_metadata(file_path, metadata)
                
                if progress_callback:
                    progress_callback(file_path)
                
            except Exception as e:
                logging.error(f"Error processing {file_path}: {str(e)}")
    
    def _create_content_signature(self, metadata: Dict, file_path: str) -> str:
        """Create a content signature for grouping similar videos."""
        # Use duration as primary similarity metric
        duration = metadata.get('duration_value', 0)
        file_size = metadata.get('file_size_value', 0)
        
        # Create base name without extension and quality indicators
        base_name = os.path.splitext(os.path.basename(file_path))[0].lower()
        # Remove common quality indicators
        quality_indicators = {'1080p', '720p', '480p', '2160p', '4k', 'uhd', 'hd', 
                            'dvdrip', 'bdrip', 'webdl', 'bluray', 'web', 'hdtv'}
        
        # More efficient string cleaning
        words = base_name.split()
        cleaned_words = []
        for word in words:
            if word not in quality_indicators and not any(qi in word for qi in quality_indicators):
                cleaned_words.append(''.join(c for c in word if c.isalnum()))
        
        base_name = ' '.join(cleaned_words)
        
        # Create signature combining cleaned name and duration
        # Round duration to nearest second to account for small variations
        duration_key = round(duration)
        
        # If file size is very different, it might be a different encoding
        # Use size ranges to group similar files
        size_range = file_size // (100 * 1024)  # Group by 100MB ranges
        
        return f"{base_name}|{duration_key}|{size_range}"
    
    def find_duplicates(self) -> Dict:
        """Identify duplicates using content signatures and metadata."""
        self.duplicates = {}
        duplicate_groups = 0
        
        # Pre-calculate file sizes for better performance
        file_sizes = {
            file_info['path']: os.path.getsize(file_info['path'])
            for content_files in self.content_data.values()
            for file_info in content_files
        }
        
        for content_signature, files in self.content_data.items():
            if len(files) > 1:
                # Sort files by resolution (highest to lowest)
                files_sorted = sorted(
                    files,
                    key=lambda x: (
                        x.get('height', 0) * x.get('width', 0),
                        x.get('bitrate_value', 0)
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
                            size = file_sizes[file_info['path']]
                            logging.info(
                                f"  - {file_info['path']} "
                                f"({file_info['resolution']}, {size} bytes)"
                            )
        
        return self.duplicates
    
    def _group_similar_files(self, files: List[Dict]) -> List[List[Dict]]:
        """Group files that are likely duplicates based on multiple criteria."""
        groups = []
        used_files = set()
        
        for i, file1 in enumerate(files):
            if file1['path'] in used_files:
                continue
                
            current_group = [file1]
            used_files.add(file1['path'])
            
            for file2 in files[i + 1:]:
                if file2['path'] in used_files:
                    continue
                    
                if self._are_files_similar(file1, file2):
                    current_group.append(file2)
                    used_files.add(file2['path'])
            
            if current_group:
                groups.append(current_group)
        
        return groups
    
    def _are_files_similar(self, file1: Dict, file2: Dict) -> bool:
        """Compare two files to determine if they are likely duplicates."""
        # Duration should be very close
        duration_diff = abs(file1.get('duration_value', 0) - file2.get('duration_value', 0))
        if duration_diff > 2.0:  # Allow 2 second difference
            return False
        
        # Compare bitrates - higher quality files should have higher bitrates
        bitrate1 = file1.get('bitrate_value', 0)
        bitrate2 = file2.get('bitrate_value', 0)
        
        # If resolutions are different, bitrates should follow
        res1 = file1.get('width', 0) * file1.get('height', 0)
        res2 = file2.get('width', 0) * file2.get('height', 0)
        
        if res1 > res2 and bitrate1 < bitrate2:
            logging.debug(f"Suspicious bitrate relationship between {file1['path']} and {file2['path']}")
            return False
        
        # Calculate overall similarity score
        similarity_score = self._calculate_similarity_score(file1, file2)
        
        return similarity_score >= self.min_similarity
    
    def _calculate_similarity_score(self, file1: Dict, file2: Dict) -> float:
        """Calculate a similarity score between two files."""
        # Weighted scoring system
        scores = {
            'duration': 0.4,  # Duration is most important
            'resolution': 0.3,  # Resolution relationship
            'bitrate': 0.2,    # Bitrate relationship
            'format': 0.1      # Format/codec similarity
        }
        
        total_score = 0.0
        
        # Duration similarity
        duration_diff = abs(file1.get('duration_value', 0) - file2.get('duration_value', 0))
        duration_score = max(0, 1 - (duration_diff / 2.0))  # 2 second threshold
        total_score += duration_score * scores['duration']
        
        # Resolution relationship
        res1 = file1.get('width', 0) * file1.get('height', 0)
        res2 = file2.get('width', 0) * file2.get('height', 0)
        if res1 != res2:  # Different resolutions are expected for duplicates
            total_score += scores['resolution']
        
        # Bitrate relationship
        bitrate1 = file1.get('bitrate_value', 0)
        bitrate2 = file2.get('bitrate_value', 0)
        if (res1 > res2 and bitrate1 > bitrate2) or (res1 < res2 and bitrate1 < bitrate2):
            total_score += scores['bitrate']
        
        # Format/codec similarity
        if file1.get('codec', '') == file2.get('codec', ''):
            total_score += scores['format']
        
        return total_score
    
    def auto_select_files(self, files: List[Dict]) -> None:
        """Auto-select lower quality files for deletion."""
        if len(files) <= 1:
            return
        
        # Sort by quality score (resolution, bitrate, etc.)
        sorted_files = sorted(
            files,
            key=lambda x: (
                x.get('height', 0) * x.get('width', 0),  # Resolution
                x.get('bitrate_value', 0),               # Bitrate
                -os.path.getsize(x['path'])              # Negative size (prefer smaller files for same quality)
            ),
            reverse=True
        )
        
        # Keep the highest quality, select others for deletion
        for file in sorted_files[1:]:
            self.selected_for_deletion.add(file['path'])
            logging.info(f"Selected for deletion: {file['path']}")
    
    def delete_selected_files(self) -> Dict:
        """Delete all selected files and return deletion statistics."""
        if not self.selected_for_deletion:
            return {'deleted': 0, 'failed': 0, 'saved_space': 0}
        
        deleted = 0
        failed = 0
        saved_space = 0
        
        for file_path in sorted(self.selected_for_deletion):
            try:
                # Get file size before deletion
                file_size_bytes = os.path.getsize(file_path)
                
                if not self.dry_run:
                    os.remove(file_path)
                    logging.info(f"Deleted file: {file_path}")
                else:
                    logging.info(f"Would delete file (dry run): {file_path}")
                
                saved_space += file_size_bytes
                deleted += 1
                
            except Exception as e:
                logging.error(f"Failed to delete {file_path}: {str(e)}")
                failed += 1
        
        # Clear selected files
        self.selected_for_deletion.clear()
        
        result = {
            'deleted': deleted,
            'failed': failed,
            'saved_space': saved_space
        }
        
        logging.info(f"Deletion results: {result}")
        return result 