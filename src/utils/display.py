import time
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
        return [
            f"{Fore.CYAN}{index}{Style.RESET_ALL}",
            f"{check}",
            f"{Fore.GREEN}{file_info['resolution']}{Style.RESET_ALL}",
            f"{Fore.BLUE}{file_info['bitrate']}{Style.RESET_ALL}",
            f"{Fore.MAGENTA}{file_info['codec']}{Style.RESET_ALL}",
            f"{Fore.YELLOW}{file_info['file_size']}{Style.RESET_ALL}",
            f"{file_info['filename']}"
        ]
    
    @staticmethod
    def clear_screen() -> None:
        """Clear the terminal screen in a cross-platform way."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear') 