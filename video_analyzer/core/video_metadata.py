import os
import subprocess
import json
from typing import Dict, Optional
import logging

class VideoMetadata:
    @staticmethod
    def get_video_metadata(file_path: str) -> Optional[Dict]:
        """Extract resolution, bitrate, and format info using ffprobe."""
        try:
            print(f"Processing file: {file_path}")  # Debug output
            cmd = [
                'ffprobe', 
                '-v', 'quiet', 
                '-print_format', 'json', 
                '-show_format', 
                '-show_streams', 
                file_path
            ]
            
            # Add a timeout of 30 seconds
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"ffprobe failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error output: {result.stderr}")
                return None
                
            data = json.loads(result.stdout)
            
            # Find the video stream
            video_stream = next(
                (stream for stream in data.get('streams', [])
                 if stream.get('codec_type') == 'video'),
                None
            )
            
            if not video_stream:
                return None
            
            # Extract metadata
            width = video_stream.get('width', 0)
            height = video_stream.get('height', 0)
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
                'file_size_value': file_size_mb
            }
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None 