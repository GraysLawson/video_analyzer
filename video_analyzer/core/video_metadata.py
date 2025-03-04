import os
import subprocess
import json
from typing import Dict, Optional
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor

class VideoMetadata:
    # Cache for checking if ffprobe exists - avoid repeated checks
    _ffprobe_path = None
    
    @classmethod
    def _get_ffprobe_path(cls):
        """Get the path to ffprobe executable, with caching."""
        if cls._ffprobe_path is None:
            cls._ffprobe_path = shutil.which('ffprobe')
        return cls._ffprobe_path
    
    @staticmethod
    def get_video_metadata(file_path: str) -> Optional[Dict]:
        """Extract resolution, bitrate, and format info using ffprobe."""
        try:
            # Check if file exists
            if not os.path.isfile(file_path):
                logging.error(f"File does not exist: {file_path}")
                return None
                
            # Check if ffprobe is available
            ffprobe_path = VideoMetadata._get_ffprobe_path()
            if not ffprobe_path:
                logging.error("ffprobe not found. Please install ffmpeg.")
                return None
                
            cmd = [
                ffprobe_path, 
                '-v', 'quiet', 
                '-print_format', 'json', 
                '-show_format', 
                '-show_streams', 
                file_path
            ]
            
            # Add a timeout of 30 seconds
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                logging.error(f"ffprobe failed with return code {result.returncode}")
                if result.stderr:
                    logging.error(f"Error output: {result.stderr}")
                return None
                
            # Parse JSON output
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                logging.error(f"Failed to parse ffprobe output for {file_path}")
                return None
            
            # Find the video stream
            video_stream = next(
                (stream for stream in data.get('streams', [])
                 if stream.get('codec_type') == 'video'),
                None
            )
            
            if not video_stream:
                logging.warning(f"No video stream found in {file_path}")
                return None
            
            # Extract metadata
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            resolution = f"{width}x{height}"
            
            # Get format and bitrate info
            format_info = data.get('format', {})
            format_name = format_info.get('format_name', 'unknown')
            
            # Convert bitrate from string to float and then to Mbps
            bitrate_str = format_info.get('bit_rate', '0')
            try:
                bitrate_mbps = round(float(bitrate_str) / 1000000, 2)
                bitrate = f"{bitrate_mbps} Mbps"
                bitrate_value = bitrate_mbps
            except (ValueError, TypeError):
                bitrate = "unknown"
                bitrate_value = 0
            
            # Get file size in MB
            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
            
            # Get duration
            duration_str = format_info.get('duration', '0')
            try:
                duration_sec = float(duration_str)
                mins = int(duration_sec // 60)
                secs = int(duration_sec % 60)
                duration = f"{mins}m {secs}s"
                duration_value = duration_sec
            except (ValueError, TypeError):
                duration = "unknown"
                duration_value = 0
            
            # Get codec name
            codec_name = video_stream.get('codec_name', 'unknown')
            
            # Get frames per second if available
            fps = 0
            fps_str = video_stream.get('r_frame_rate', '0/0')
            if '/' in fps_str:
                try:
                    num, den = map(int, fps_str.split('/'))
                    if den != 0:
                        fps = round(num / den, 2)
                except (ValueError, ZeroDivisionError):
                    pass
            
            return {
                'resolution': resolution,
                'width': width,
                'height': height,
                'bitrate': bitrate,
                'bitrate_value': bitrate_value,
                'format': format_name,
                'codec': codec_name,
                'duration': duration,
                'duration_value': duration_value,
                'file_size': f"{file_size_mb} MB",
                'file_size_value': file_size_mb,
                'fps': fps
            }
        
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout while processing {file_path}")
            return None
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def batch_process_files(file_paths, max_workers=None):
        """Process multiple files in parallel using ThreadPoolExecutor."""
        results = {}
        
        # Determine optimal number of workers if not specified
        if max_workers is None:
            max_workers = min(32, os.cpu_count() + 4)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(VideoMetadata.get_video_metadata, file_path): file_path
                for file_path in file_paths
            }
            
            # Process results as they complete
            for future in future_to_file:
                file_path = future_to_file[future]
                try:
                    metadata = future.result()
                    if metadata:
                        results[file_path] = metadata
                except Exception as e:
                    logging.error(f"Exception while processing {file_path}: {str(e)}")
        
        return results 