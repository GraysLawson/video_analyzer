import os
from collections import defaultdict
from typing import Dict, List, Set, Optional
from .video_metadata import VideoMetadata
from .content_info import ContentInfo

class VideoAnalyzer:
    def __init__(self, directory: str, output_file: Optional[str] = None, dry_run: bool = False):
        self.directory = directory
        self.output_file = output_file
        self.dry_run = dry_run
        self.content_data = defaultdict(list)
        self.duplicates = {}
        self.selected_for_deletion = set()
    
    def find_video_files(self) -> List[str]:
        """Find all video files in the directory and subdirectories."""
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
        video_files = []
        
        for dirpath, _, filenames in os.walk(self.directory):
            for filename in filenames:
                _, ext = os.path.splitext(filename)
                if ext.lower() in video_extensions:
                    file_path = os.path.join(dirpath, filename)
                    video_files.append(file_path)
        
        return video_files
    
    def scan_video_files(self, video_files: List[str]) -> None:
        """Process the video files and extract metadata."""
        for file_path in video_files:
            filename = os.path.basename(file_path)
            
            # Get metadata
            metadata = VideoMetadata.get_video_metadata(file_path)
            if not metadata:
                continue
            
            # Extract title information
            title_info = ContentInfo.extract_title_info(filename)
            
            # Create a content key based on type and title
            if title_info['type'] == 'tv_show':
                content_key = f"TV: {title_info['title']}"
                episode_info = f"S{title_info['season']:02d}E{title_info['episode']:02d}"
                unique_id = f"{content_key}|{episode_info}"
            else:
                content_key = f"Movie: {title_info['title']}"
                episode_info = ""
                unique_id = content_key
            
            # Add file info to content data
            file_info = {
                'filename': filename,
                'path': file_path,
                'episode_info': episode_info,
                **metadata,  # Include all metadata
                'content_key': content_key,
                'unique_id': unique_id,
                'type': title_info['type']
            }
            
            # Add TV-specific info if applicable
            if title_info['type'] == 'tv_show':
                file_info['season'] = title_info['season']
                file_info['episode'] = title_info['episode']
            
            self.content_data[content_key].append(file_info)
    
    def find_duplicates(self) -> None:
        """Identify duplicates (same content with different resolutions)."""
        self.duplicates = {}
        
        # For each content (TV show or movie)
        for content_key, files in self.content_data.items():
            # Group by unique ID (episode or movie)
            by_unique_id = defaultdict(list)
            for file_info in files:
                by_unique_id[file_info['unique_id']].append(file_info)
            
            # Find duplicates (unique IDs with multiple files)
            for unique_id, files_list in by_unique_id.items():
                if len(files_list) > 1:
                    # If this is the first duplicate for this content
                    if content_key not in self.duplicates:
                        self.duplicates[content_key] = {}
                    
                    self.duplicates[content_key][unique_id] = files_list
    
    def auto_select_files(self, files: List[Dict]) -> None:
        """Auto-select lower resolution files for deletion."""
        if len(files) <= 1:
            return
        
        # Sort by resolution (highest to lowest)
        sorted_files = sorted(files, key=lambda x: (x['height'], x['width']), reverse=True)
        
        # Keep the highest resolution, select others for deletion
        for file in sorted_files[1:]:
            self.selected_for_deletion.add(file['path'])
    
    def delete_selected_files(self) -> Dict:
        """Delete all selected files and return deletion statistics."""
        if not self.selected_for_deletion:
            return {'deleted': 0, 'failed': 0, 'saved_space': 0}
        
        deleted = 0
        failed = 0
        saved_space = 0
        
        for file_path in sorted(self.selected_for_deletion):
            try:
                # Get file size before deletion (for reporting)
                file_size_bytes = os.path.getsize(file_path)
                saved_space += file_size_bytes
                
                if not self.dry_run:
                    os.remove(file_path)
                
                deleted += 1
            except Exception:
                failed += 1
        
        # Clear selected files
        self.selected_for_deletion.clear()
        
        return {
            'deleted': deleted,
            'failed': failed,
            'saved_space': saved_space
        } 