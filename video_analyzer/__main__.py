#!/usr/bin/env python3
import os
import argparse
import colorama
import logging
import concurrent.futures
from datetime import datetime
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from .core.analyzer import VideoAnalyzer
from .ui.main_menu import MainMenu
from .utils.display import DisplayManager

def setup_logging(log_path=None):
    """Setup logging configuration"""
    if log_path is None:
        log_path = os.path.join(os.getcwd(), 'video_analyzer.log')
    else:
        # Ensure directory exists
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # Also log to console
        ]
    )
    return log_path

def get_initial_settings():
    """Get initial settings from user through interactive prompt."""
    console = Console()
    console.clear()
    
    # Create welcome panel
    welcome = Panel(
        "[cyan]Welcome to Video Analyzer![/cyan]\n\n"
        "This tool helps you find and manage duplicate video files with different resolutions.\n"
        "Please configure the following settings to begin:",
        title="Video Analyzer Setup",
        border_style="blue"
    )
    console.print(welcome)
    
    # Get video directory
    while True:
        video_dir = Prompt.ask(
            "\n[yellow]Enter the path to your video directory[/yellow]",
            default=os.getcwd()
        )
        if os.path.exists(video_dir):
            break
        console.print("[red]Directory does not exist. Please enter a valid path.[/red]")
    
    # Get log file settings
    use_custom_log = Confirm.ask(
        "\n[yellow]Would you like to specify a custom log file location?[/yellow]",
        default=False
    )
    
    if use_custom_log:
        log_path = Prompt.ask(
            "[yellow]Enter the path for the log file[/yellow]",
            default=os.path.join(os.getcwd(), 'video_analyzer.log')
        )
    else:
        log_path = os.path.join(os.getcwd(), 'video_analyzer.log')
    
    # Get similarity threshold
    similarity = float(Prompt.ask(
        "\n[yellow]Enter minimum similarity threshold for duplicate detection (0.0-1.0)[/yellow]",
        default="0.95"
    ))
    
    # Get dry run preference
    dry_run = Confirm.ask(
        "\n[yellow]Enable dry run mode? (no actual deletions will be performed)[/yellow]",
        default=False
    )
    
    # Show summary
    console.print("\n[cyan]Configuration Summary:[/cyan]")
    summary = Table.grid()
    summary.add_column(style="bold")
    summary.add_column()
    summary.add_row("Video Directory:", video_dir)
    summary.add_row("Log File:", log_path)
    summary.add_row("Similarity Threshold:", str(similarity))
    summary.add_row("Dry Run Mode:", "Yes" if dry_run else "No")
    console.print(summary)
    
    if not Confirm.ask("\n[yellow]Proceed with these settings?[/yellow]", default=True):
        return get_initial_settings()
    
    return {
        'directory': video_dir,
        'log_path': log_path,
        'min_similarity': similarity,
        'dry_run': dry_run
    }

def process_video_batch(args):
    """Process a batch of video files in parallel."""
    files, analyzer, callback = args
    results = []
    for file in files:
        try:
            metadata = analyzer.process_single_file(file)
            if metadata and callback:
                callback(file)
            if metadata:
                results.append((file, metadata))
        except Exception as e:
            logging.error(f"Error processing {file}: {str(e)}")
    return results

def main():
    # Initialize colorama for cross-platform colored terminal output
    colorama.init(autoreset=True)
    
    # Get settings from user
    settings = get_initial_settings()
    
    # Setup logging
    log_file = setup_logging(settings['log_path'])
    logging.info(f"Starting video analysis of directory: {settings['directory']}")
    logging.info(f"Log file: {log_file}")
    
    # Create display manager
    display = DisplayManager()
    
    try:
        # Create analyzer
        analyzer = VideoAnalyzer(
            settings['directory'],
            None,  # output_dir not needed anymore
            settings['dry_run'],
            settings['min_similarity']
        )
        
        # Find video files
        logging.info(f"Scanning directory: {settings['directory']}")
        video_files = analyzer.find_video_files()
        total_files = len(video_files)
        logging.info(f"Found {total_files} video files")
        
        if total_files == 0:
            display.console.print("[yellow]No video files found in the specified directory.[/yellow]")
            return 0
        
        # Create progress display
        progress = display.create_progress_display(total_files)
        layout = display.create_status_layout()
        
        # Process files with live display
        with Live(layout, refresh_per_second=4) as live:
            # Add progress task
            task = progress.add_task("Analyzing videos...", total=total_files)
            layout["progress"].update(progress)
            
            def update_progress(filename):
                # Update progress
                progress.advance(task)
                
                # Update current file display
                display.current_file = os.path.basename(filename)
                layout["current_file"].update(display.update_current_file_panel())
                
                # Update statistics
                display.duplicate_groups = len(analyzer.duplicates)
                display.total_size = sum(os.path.getsize(f['path']) 
                                       for g in analyzer.duplicates.values() 
                                       for f in g)
                display.potential_savings = sum(os.path.getsize(f['path']) 
                                             for g in analyzer.duplicates.values() 
                                             for f in g[1:])
                layout["stats"].update(display.update_stats_panel())
            
            # Process files in parallel
            batch_size = 10  # Adjust based on system capabilities
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                # Split files into batches
                batches = [video_files[i:i + batch_size] 
                          for i in range(0, len(video_files), batch_size)]
                
                # Create tasks for each batch
                futures = []
                for batch in batches:
                    future = executor.submit(
                        process_video_batch,
                        (batch, analyzer, update_progress)
                    )
                    futures.append(future)
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(futures):
                    results = future.result()
                    for file_path, metadata in results:
                        analyzer.add_file_metadata(file_path, metadata)
        
        # Find duplicates
        duplicates = analyzer.find_duplicates()
        logging.info(f"Found {len(duplicates)} groups of duplicate videos")
        
        # Show menu
        menu = MainMenu(analyzer)
        menu.show_menu()
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        display.console.print(f"[red]Error: {str(e)}[/red]")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 