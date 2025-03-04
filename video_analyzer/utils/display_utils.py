import time
import os
from typing import Dict
from colorama import Fore, Style, Back

class DisplayUtils:
    @staticmethod
    def print_status(message: str, color: str = Fore.BLUE) -> None:
        """Print a status message with timestamp and color."""
        timestamp = time.strftime("%H:%M:%S")
        print(f"{Style.BRIGHT}{Fore.CYAN}[{timestamp}] {color}{message}{Style.RESET_ALL}")
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Convert file size in bytes to human-readable format."""
        for unit in ['bytes', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    
    @staticmethod
    def format_table_row(file_info: Dict, index: int, selected: bool = False) -> list:
        """Format a file info dictionary into a table row."""
        check = "✓" if selected else " "
        is_highest = file_info.get('is_highest_quality', False)
        resolution = file_info.get('resolution', 'Unknown')
        bitrate = file_info.get('bitrate', 'Unknown')
        codec = file_info.get('codec', 'Unknown')
        file_size = file_info.get('file_size', 'Unknown')
        
        # Format based on quality
        if is_highest:
            resolution = f"{Fore.GREEN}{resolution} ⭐{Style.RESET_ALL}"
            bitrate = f"{Fore.GREEN}{bitrate}{Style.RESET_ALL}"
        elif 'compared_to_best' in file_info:
            comparison = file_info['compared_to_best']
            res_percent = comparison.get('resolution_percent', 100)
            if res_percent < 50:
                resolution = f"{Fore.RED}{resolution} ({res_percent}%){Style.RESET_ALL}"
            elif res_percent < 75:
                resolution = f"{Fore.YELLOW}{resolution} ({res_percent}%){Style.RESET_ALL}"
            else:
                resolution = f"{Fore.BLUE}{resolution} ({res_percent}%){Style.RESET_ALL}"
        
        return [
            f"{Fore.CYAN}{index}{Style.RESET_ALL}",
            f"{check}",
            resolution,
            bitrate,
            f"{Fore.MAGENTA}{codec}{Style.RESET_ALL}",
            f"{Fore.YELLOW}{file_size}{Style.RESET_ALL}",
            f"{file_info['filename']}"
        ]
    
    @staticmethod
    def clear_screen() -> None:
        """Clear the terminal screen in a cross-platform way."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def format_quality_comparison(file_info: Dict) -> str:
        """Format quality comparison information for display."""
        if not file_info.get('is_highest_quality', False) and 'compared_to_best' in file_info:
            comparison = file_info['compared_to_best']
            res_diff = comparison.get('resolution_diff', 'Unknown')
            bitrate_diff = comparison.get('bitrate_diff', 'Unknown')
            size_diff = comparison.get('size_diff', 'Unknown')
            quality_percent = comparison.get('quality_percent', 100)
            
            return (
                f"Resolution: {res_diff} | "
                f"Bitrate: {bitrate_diff} | "
                f"Size: {size_diff} | "
                f"Quality: {quality_percent}% of best"
            )
        elif file_info.get('is_highest_quality', False):
            return "✅ HIGHEST QUALITY VERSION"
        else:
            return "" 