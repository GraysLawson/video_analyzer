import os
import logging
import concurrent.futures
from collections import defaultdict
from typing import Dict, List, Set, Optional, Callable, Tuple, Any
import hashlib
from functools import lru_cache
import re
from multiprocessing import cpu_count
from .video_metadata import VideoMetadata
from .content_info import ContentInfo
import humanize

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
        # Resolution groups for better organization
        self.resolution_groups = {
            'HD': [720, 1080],
            'UHD': [2160, 4320]  # 4K and 8K
        }
        # Track resolution groups for reporting
        self.resolution_stats = defaultdict(int)
        # Track TV shows versus movies
        self.content_types = {'tv_show': 0, 'movie': 0}
        # Number of threads to use for parallel processing
        self.num_threads = max(4, cpu_count() * 2)  # Use 2x CPU cores for I/O bound tasks
    
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
                # Extract content info from filename
                content_info = ContentInfo.extract_title_info(os.path.basename(file_path))
                metadata.update(content_info)
                
                # Classify resolution
                height = metadata.get('height', 0)
                metadata['resolution_category'] = self._classify_resolution(height)
                
                # Update statistics
                self.content_types[metadata.get('type', 'unknown')] += 1
                self.resolution_stats[metadata['resolution_category']] += 1
                
                # Cache the enhanced metadata
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
    
    def _classify_resolution(self, height: int) -> str:
        """Classify video resolution into categories."""
        if height <= 0:
            return "Unknown"
        elif height <= 480:
            return "SD"
        elif height <= 720:
            return "HD"
        elif height <= 1080:
            return "Full HD"
        elif height <= 2160:
            return "4K"
        else:
            return "8K+"
    
    def add_file_metadata(self, file_path: str, metadata: Dict) -> None:
        """Add processed file metadata to the content data."""
        # Create content signature with improved algorithm
        content_signature = self._create_content_signature(metadata, file_path)
        
        # Add file info to content data
        self.content_data[content_signature].append({
            'path': file_path,
            'filename': os.path.basename(file_path),
            **metadata
        })
    
    def scan_video_files(self, video_files: List[str], progress_callback: Optional[Callable] = None) -> None:
        """Process the video files and extract metadata using optimized parallel processing."""
        if not video_files:
            logging.warning("No video files found to scan.")
            return
            
        logging.info(f"Processing {len(video_files)} video files with {self.num_threads} threads")
        
        # Calculate optimal batch size based on number of files and threads
        # Small files can use smaller batches for better progress updates
        # Large collections need larger batches for efficiency
        batch_size = min(100, max(10, len(video_files) // self.num_threads))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Process files in batches for better performance and memory usage
            futures = []
            
            for i in range(0, len(video_files), batch_size):
                batch = video_files[i:i + batch_size]
                futures.append(executor.submit(self._process_batch, batch, progress_callback))
            
            # Wait for all batches to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error processing batch: {str(e)}")
    
    def _process_batch(self, batch: List[str], progress_callback: Optional[Callable] = None) -> None:
        """Process a batch of files and update metadata."""
        # Use VideoMetadata's batch processing capabilities
        results = VideoMetadata.batch_process_files(batch, max_workers=min(len(batch), 8))
        
        # Add results to our data structures
        for file_path, metadata in results.items():
            if metadata:
                # Extract content info and enhance metadata
                content_info = ContentInfo.extract_title_info(os.path.basename(file_path))
                metadata.update(content_info)
                metadata['resolution_category'] = self._classify_resolution(metadata.get('height', 0))
                
                # Update content statistics 
                self.content_types[metadata.get('type', 'unknown')] += 1
                self.resolution_stats[metadata['resolution_category']] += 1
                
                # Add to content data
                self.add_file_metadata(file_path, metadata)
                
                # Update progress
                if progress_callback:
                    progress_callback(file_path)
    
    @lru_cache(maxsize=1024)
    def _clean_filename(self, filename: str) -> str:
        """Clean filename by removing quality indicators and non-alphanumeric chars."""
        # Enhanced list of quality and release indicators
        quality_indicators = {
            '1080p', '720p', '480p', '2160p', '4k', 'uhd', 'hd', '8k',
            'dvdrip', 'bdrip', 'webdl', 'web-dl', 'webrip', 'bluray', 'web', 'hdtv',
            'x264', 'x265', 'h264', 'h265', 'hevc', 'xvid', 'divx',
            'remux', 'hdr', 'dolby', 'atmos', 'truehd', 'dts'
        }
        
        # Extract show/movie name and remove quality indicators
        # Get base name without extension
        base_name = os.path.splitext(filename)[0].lower()
        
        # Remove year patterns like (2020) or [2020]
        base_name = re.sub(r'[\(\[\.]?\d{4}[\)\]\.]?', ' ', base_name)
        
        # More efficient string cleaning
        words = base_name.split()
        cleaned_words = []
        for word in words:
            if word not in quality_indicators and not any(qi in word for qi in quality_indicators):
                cleaned_words.append(''.join(c for c in word if c.isalnum()))
        
        return ' '.join(cleaned_words)
    
    def _create_content_signature(self, metadata: Dict, file_path: str) -> str:
        """Create a content signature for grouping similar videos with improved accuracy."""
        # Get type (tv_show or movie)
        content_type = metadata.get('type', 'unknown')
        
        # For TV shows, include show name, season, and episode
        if content_type == 'tv_show':
            show_name = metadata.get('title', '').lower()
            season = metadata.get('season', 0)
            episode = metadata.get('episode', 0)
            # Create signature for TV shows including show name, season and episode
            name_hash = hashlib.md5(show_name.encode()).hexdigest()[:8]
            return f"tv:{name_hash}|s{season:02d}e{episode:02d}"
        
        # For movies, use duration, file name, and size range
        else:
            # Use duration as primary similarity metric
            duration = metadata.get('duration_value', 0)
            
            # Clean the filename
            base_name = self._clean_filename(os.path.basename(file_path))
            
            # Create signature combining cleaned name and duration
            # Round duration to nearest second to account for small variations
            duration_key = round(duration)
            
            # Use a hash of the base name for better differentiation
            name_hash = hashlib.md5(base_name.encode()).hexdigest()[:8]
            
            return f"movie:{name_hash}|{duration_key}"
    
    def find_duplicates(self) -> Dict:
        """Identify duplicates using content signatures and metadata with improved resolution handling."""
        self.duplicates = {}
        duplicate_groups = 0
        
        for content_signature, files in self.content_data.items():
            if len(files) > 1:
                # Sort files by resolution and quality (highest to lowest)
                files_sorted = sorted(
                    files,
                    key=lambda x: (
                        x.get('height', 0) * x.get('width', 0),  # Total pixels (resolution)
                        x.get('bitrate_value', 0),               # Bitrate
                        -self._calculate_quality_score(x),       # Overall quality score
                        -self._get_file_size(x['path'])          # Prefer smaller files if quality is the same
                    ),
                    reverse=True
                )
                
                # Group them by content type (TV show or movie)
                content_type = files_sorted[0].get('type', 'unknown')
                
                # Store the highest quality resolution for comparison
                highest_resolution = files_sorted[0].get('resolution', 'Unknown')
                highest_bitrate = files_sorted[0].get('bitrate', 'Unknown')
                
                # Add quality comparison data to each file for UI display
                for file_info in files_sorted:
                    file_resolution = file_info.get('resolution', 'Unknown')
                    file_info['is_highest_quality'] = (file_info == files_sorted[0])
                    file_info['compared_to_best'] = self._compare_to_highest_quality(
                        file_info, files_sorted[0]
                    )
                
                # Create a useful group name
                if content_type == 'tv_show':
                    title = files_sorted[0].get('title', 'Unknown')
                    season = files_sorted[0].get('season', 0)
                    episode = files_sorted[0].get('episode', 0)
                    group_name = f"{title} - S{season:02d}E{episode:02d}"
                else:
                    title = files_sorted[0].get('title', 'Unknown')
                    group_name = title
                
                self.duplicates[group_name] = files_sorted
                duplicate_groups += 1
                
                # Log duplicate group details
                logging.info(f"Found duplicate group: {group_name}")
                for file_info in files_sorted:
                    size = self._get_file_size(file_info['path'])
                    resolution = file_info.get('resolution', 'Unknown')
                    bitrate = file_info.get('bitrate', 'Unknown')
                    logging.info(
                        f"  - {file_info['path']} "
                        f"({resolution}, {bitrate}, {humanize.naturalsize(size)})"
                    )
        
        logging.info(f"Found {duplicate_groups} duplicate groups")
        return self.duplicates
    
    def _calculate_quality_score(self, file_info: Dict) -> float:
        """Calculate a quality score based on multiple factors."""
        # Base score starts at 0
        score = 0.0
        
        # Add points for resolution (0-40 points)
        height = file_info.get('height', 0)
        if height > 2160:  # 8K
            score += 40
        elif height > 1080:  # 4K
            score += 30
        elif height > 720:  # Full HD
            score += 20
        elif height > 480:  # HD
            score += 10
        else:  # SD
            score += 5
        
        # Add points for bitrate (0-30 points)
        bitrate = file_info.get('bitrate_value', 0)
        score += min(30, bitrate * 3)  # Up to 30 points based on bitrate
        
        # Add points for modern codecs (0-20 points)
        codec = file_info.get('codec', '').lower()
        if 'hevc' in codec or 'h265' in codec or 'av1' in codec:
            score += 20  # Modern codec with high efficiency
        elif 'h264' in codec or 'avc' in codec:
            score += 15  # Good standard codec
        else:
            score += 5   # Older codec
        
        # Add points for FPS (0-10 points)
        fps = file_info.get('fps', 0)
        if fps >= 60:
            score += 10  # High frame rate
        elif fps >= 30:
            score += 7   # Standard frame rate
        elif fps >= 24:
            score += 5   # Film frame rate
        else:
            score += 2   # Low frame rate
        
        return score
    
    def _compare_to_highest_quality(self, file_info: Dict, best_file: Dict) -> Dict:
        """Generate comparison metrics between this file and the highest quality version."""
        comparison = {}
        
        # Resolution comparison
        file_height = file_info.get('height', 0)
        best_height = best_file.get('height', 0)
        if file_height > 0 and best_height > 0:
            resolution_ratio = file_height / best_height
            comparison['resolution_percent'] = int(resolution_ratio * 100)
            comparison['resolution_diff'] = f"{file_height}p vs {best_height}p"
        else:
            comparison['resolution_percent'] = 100
            comparison['resolution_diff'] = "Unknown"
        
        # Bitrate comparison
        file_bitrate = file_info.get('bitrate_value', 0)
        best_bitrate = best_file.get('bitrate_value', 0)
        if file_bitrate > 0 and best_bitrate > 0:
            bitrate_ratio = file_bitrate / best_bitrate
            comparison['bitrate_percent'] = int(bitrate_ratio * 100)
            comparison['bitrate_diff'] = f"{file_bitrate:.2f} Mbps vs {best_bitrate:.2f} Mbps"
        else:
            comparison['bitrate_percent'] = 100
            comparison['bitrate_diff'] = "Unknown"
        
        # File size comparison
        file_size = self._get_file_size(file_info['path'])
        best_size = self._get_file_size(best_file['path'])
        if file_size > 0 and best_size > 0:
            size_ratio = file_size / best_size
            comparison['size_percent'] = int(size_ratio * 100)
            comparison['size_diff'] = f"{humanize.naturalsize(file_size)} vs {humanize.naturalsize(best_size)}"
            comparison['size_diff_value'] = best_size - file_size
        else:
            comparison['size_percent'] = 100
            comparison['size_diff'] = "Unknown"
            comparison['size_diff_value'] = 0
        
        # Overall quality score comparison
        file_score = self._calculate_quality_score(file_info)
        best_score = self._calculate_quality_score(best_file)
        if file_score > 0 and best_score > 0:
            quality_ratio = file_score / best_score
            comparison['quality_percent'] = int(quality_ratio * 100)
        else:
            comparison['quality_percent'] = 100
        
        return comparison
    
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
        
        # For TV shows, match on title, season, and episode
        if file1.get('type') == 'tv_show' and file2.get('type') == 'tv_show':
            if (file1.get('title') == file2.get('title') and
                file1.get('season') == file2.get('season') and
                file1.get('episode') == file2.get('episode')):
                return True
        
        # For everything else, calculate similarity score
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
                # The files are already sorted with highest quality first from find_duplicates()
                # Keep the highest resolution, mark others for deletion
                for file_info in files[1:]:
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