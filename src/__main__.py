#!/usr/bin/env python3
import os
import argparse
import colorama
import logging
from datetime import datetime
from tqdm import tqdm
from .core.analyzer import VideoAnalyzer
from .ui.main_menu import MainMenu
from .utils.display import DisplayUtils

def setup_logging(output_dir=None):
    """Setup logging configuration"""
    if output_dir is None:
        output_dir = os.getcwd()
    
    log_dir = os.path.join(output_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'video_analyzer_{timestamp}.log')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    return log_file

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
        help='Output directory for logs and results (optional)',
        default=None
    )
    parser.add_argument(
        '--dry-run',
        help='Show what would be deleted without actually deleting',
        action='store_true'
    )
    parser.add_argument(
        '--min-similarity',
        type=float,
        default=0.95,
        help='Minimum similarity threshold for duplicate detection (0.0-1.0)'
    )
    args = parser.parse_args()
    
    # Setup logging
    log_file = setup_logging(args.output)
    logging.info(f"Starting video analysis of directory: {args.directory}")
    logging.info(f"Log file: {log_file}")
    
    # Create display utility
    display = DisplayUtils()
    
    try:
        # Create analyzer
        analyzer = VideoAnalyzer(args.directory, args.output, args.dry_run, args.min_similarity)
        
        # Find video files
        display.print_status(f"Scanning directory: {args.directory}")
        video_files = analyzer.find_video_files()
        logging.info(f"Found {len(video_files)} video files")
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
                logging.debug(f"Processed file: {filename}")
            
            analyzer.scan_video_files(video_files, progress_callback=update_progress)
        
        # Find duplicates
        duplicates = analyzer.find_duplicates()
        logging.info(f"Found {len(duplicates)} groups of duplicate videos")
        
        # Show menu
        menu = MainMenu(analyzer)
        menu.show_menu()
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        display.print_status(f"Error: {str(e)}", colorama.Fore.RED)
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 