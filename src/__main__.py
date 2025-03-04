#!/usr/bin/env python3
import os
import argparse
import colorama
from tqdm import tqdm
from .core.analyzer import VideoAnalyzer
from .ui.main_menu import MainMenu
from .utils.display import DisplayUtils

def main():
    # Initialize colorama for cross-platform colored terminal output
    colorama.init(autoreset=True)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Find and manage duplicate video files with different resolutions.'
    )
    parser.add_argument(
        'directory',
        help='Directory to scan for video files'
    )
    parser.add_argument(
        '--output',
        help='Output file to save results (optional)',
        default=None
    )
    parser.add_argument(
        '--dry-run',
        help='Show what would be deleted without actually deleting',
        action='store_true'
    )
    args = parser.parse_args()
    
    # Create display utility
    display = DisplayUtils()
    
    # Create analyzer
    analyzer = VideoAnalyzer(args.directory, args.output, args.dry_run)
    
    # Find video files
    display.print_status(f"Scanning directory: {args.directory}")
    video_files = analyzer.find_video_files()
    display.print_status(f"Found {len(video_files)} video files", colorama.Fore.GREEN)
    
    # Process files with progress bar
    display.print_status("Analyzing videos...")
    with tqdm(
        total=len(video_files),
        desc=f"{colorama.Fore.YELLOW}Analyzing videos{colorama.Style.RESET_ALL}",
        bar_format="{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    ) as progress_bar:
        def update_progress(filename):
            progress_bar.set_description(
                f"{colorama.Fore.YELLOW}Analyzing{colorama.Style.RESET_ALL} "
                f"{colorama.Fore.CYAN}{os.path.basename(filename)[:40]}{colorama.Style.RESET_ALL}"
            )
            progress_bar.update(1)
        
        analyzer.scan_video_files(video_files)
    
    # Find duplicates
    analyzer.find_duplicates()
    
    # Show menu
    menu = MainMenu(analyzer)
    menu.show_menu()

if __name__ == '__main__':
    main() 