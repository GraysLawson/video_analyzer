#!/usr/bin/env python3
import os
import argparse
import colorama
import logging
import concurrent.futures
import sys
import signal
from datetime import datetime
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from .core.analyzer import VideoAnalyzer
from .ui.main_menu import MainMenu
from .utils.display import DisplayManager
from .utils.banner import show_banner
from .version import __version__, __build__, get_version_string

# Global flag for graceful shutdown
SHUTDOWN_REQUESTED = False

def signal_handler(sig, frame):
    """Handle interruption signals gracefully"""
    global SHUTDOWN_REQUESTED
    if not SHUTDOWN_REQUESTED:
        print("\nInterruption signal received. Finishing current tasks and shutting down...")
        SHUTDOWN_REQUESTED = True
    else:
        print("\nForced exit requested. Exiting immediately.")
        sys.exit(1)

def setup_logging(log_path=None):
    """Setup logging configuration"""
    if log_path is None:
        log_dir = os.path.join(os.path.expanduser("~"), ".video_analyzer", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_filename = f"video_analyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(log_dir, log_filename)
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
        video_dir = os.path.expanduser(video_dir)  # Expand ~/ if present
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
        log_path = os.path.expanduser(log_path)  # Expand ~/ if present
    else:
        log_path = None  # Will use default location
    
    # Get similarity threshold
    similarity = float(Prompt.ask(
        "\n[yellow]Enter minimum similarity threshold for duplicate detection (0.0-1.0)[/yellow]",
        default="0.95"
    ))
    
    # Get dry run preference
    dry_run = Confirm.ask(
        "\n[yellow]Enable dry run mode? (no actual deletions will be performed)[/yellow]",
        default=True
    )
    
    # Get output directory for moved files
    move_files = Confirm.ask(
        "\n[yellow]Move files instead of deleting them?[/yellow]",
        default=True
    )
    
    output_dir = None
    if move_files:
        output_dir = Prompt.ask(
            "[yellow]Enter directory to move files to[/yellow]",
            default=os.path.join(os.path.expanduser("~"), ".video_analyzer", "moved_files")
        )
        output_dir = os.path.expanduser(output_dir)  # Expand ~/ if present
    
    # Show summary
    console.print("\n[cyan]Configuration Summary:[/cyan]")
    summary = Table.grid()
    summary.add_column(style="bold")
    summary.add_column()
    summary.add_row("Video Directory:", video_dir)
    summary.add_row("Log File:", log_path if log_path else "Default location")
    summary.add_row("Similarity Threshold:", str(similarity))
    summary.add_row("Dry Run Mode:", "Yes" if dry_run else "No")
    summary.add_row("Move Files:", "Yes" if move_files else "No")
    if move_files:
        summary.add_row("Output Directory:", output_dir)
    console.print(summary)
    
    if not Confirm.ask("\n[yellow]Proceed with these settings?[/yellow]", default=True):
        return get_initial_settings()
    
    return {
        'directory': video_dir,
        'log_path': log_path,
        'min_similarity': similarity,
        'dry_run': dry_run,
        'output_dir': output_dir
    }

def check_dependencies():
    """Check if required dependencies are installed"""
    console = Console()
    
    # Check for ffmpeg/ffprobe
    try:
        from .core.video_metadata import VideoMetadata
        ffprobe_path = VideoMetadata._get_ffprobe_path()
        if not ffprobe_path:
            console.print("[red]Error: ffprobe not found.[/red]")
            console.print("[yellow]Please install ffmpeg and make sure it's in your PATH.[/yellow]")
            return False
    except Exception as e:
        console.print(f"[red]Error checking dependencies: {str(e)}[/red]")
        return False
    
    return True

def process_video_batch(args):
    """Process a batch of video files in parallel."""
    files, analyzer, callback = args
    results = []
    for file in files:
        if SHUTDOWN_REQUESTED:
            break
        try:
            metadata = analyzer.process_single_file(file)
            if metadata and callback:
                callback(file)
            if metadata:
                results.append((file, metadata))
        except Exception as e:
            logging.error(f"Error processing {file}: {str(e)}")
    return results

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Video Analyzer - Find and manage duplicate video files")
    parser.add_argument("-d", "--directory", help="Directory to scan for video files")
    parser.add_argument("-l", "--log", help="Log file path")
    parser.add_argument("-s", "--similarity", type=float, default=0.95, help="Similarity threshold (0.0-1.0)")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run (no deletions)")
    parser.add_argument("-m", "--move-to", help="Move files instead of deleting them")
    parser.add_argument("-n", "--non-interactive", action="store_true", help="Run in non-interactive mode")
    parser.add_argument("--no-update-check", action="store_true", help="Disable update check")
    
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize colorama for cross-platform colored terminal output
    colorama.init(autoreset=True)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Show the welcome banner unless in non-interactive mode
    if not args.non_interactive:
        show_banner()
        console = Console()
        console.print(f"[cyan]Video Analyzer {get_version_string()}[/cyan]")
        console.print()
    
    # Check for updates (unless in non-interactive mode or explicitly disabled)
    if not args.non_interactive and not args.no_update_check:
        from .utils.updater import UpdateChecker
        update_checker = UpdateChecker(console=Console())
        update_info = update_checker.check_for_updates()
        if update_info:
            console.print("[yellow]An update is available. You can update from the main menu.[/yellow]")
            console.print()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Get settings from user or command line
    if args.non_interactive:
        if not args.directory:
            print("Error: In non-interactive mode, --directory is required.")
            return 1
        
        settings = {
            'directory': args.directory,
            'log_path': args.log,
            'min_similarity': args.similarity,
            'dry_run': args.dry_run,
            'output_dir': args.move_to
        }
    else:
        # Interactive mode - either use command-line args as defaults or prompt user
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
            settings['output_dir'],
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
        
        # Add the progress panel to the layout - create a new slot for it
        # First make sure the layout has room for progress
        layout["right_panel"].split_column(
            layout(name="progress", ratio=1),
            layout(name="current_file", ratio=1),
            layout(name="processing_log", ratio=2)
        )
        
        # Process files with live display
        with Live(layout, refresh_per_second=4) as live:
            # Add progress task
            task = progress.add_task("Analyzing videos...", total=total_files)
            layout["progress"].update(progress)
            
            def update_progress(filename):
                # Log processing to update the display tracker
                display.log_processing(filename)
                
                # Update progress
                progress.advance(task)
                
                # Update the entire layout with latest info
                display.update_layout(layout)
                
                # Update additional statistics
                display.duplicate_groups = len(analyzer.duplicates)
                display.total_size = sum(sum(analyzer._get_file_size(f['path']) 
                                          for f in group) 
                                      for group in analyzer.duplicates.values())
                display.potential_savings = sum(sum(analyzer._get_file_size(f['path']) 
                                             for f in group[1:]) 
                                          for group in analyzer.duplicates.values())
            
            # Process files in parallel
            max_workers = min(os.cpu_count() or 4, 8)  # Limit to 8 workers max
            batch_size = max(10, total_files // (max_workers * 2))  # Ensure enough batches
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Split files into batches
                batches = [video_files[i:i + batch_size] 
                          for i in range(0, len(video_files), batch_size)]
                
                # Create tasks for each batch
                futures = []
                for batch in batches:
                    if SHUTDOWN_REQUESTED:
                        break
                    future = executor.submit(
                        process_video_batch,
                        (batch, analyzer, update_progress)
                    )
                    futures.append(future)
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(futures):
                    if SHUTDOWN_REQUESTED:
                        break
                    results = future.result()
                    for file_path, metadata in results:
                        analyzer.add_file_metadata(file_path, metadata)
                        
                    # Update the progress display
                    live.refresh()
        
        # If shutdown was requested, exit gracefully
        if SHUTDOWN_REQUESTED:
            logging.info("Operation interrupted by user. Exiting gracefully.")
            display.console.print("[yellow]Operation interrupted by user. Exiting gracefully.[/yellow]")
            return 0
            
        # Find duplicates
        display.console.print("\n[cyan]Finding duplicate videos...[/cyan]")
        duplicates = analyzer.find_duplicates()
        logging.info(f"Found {len(duplicates)} groups of duplicate videos")
        
        # Show results 
        if len(duplicates) == 0:
            display.console.print("[green]No duplicate videos found.[/green]")
            return 0
            
        display.console.print(f"[green]Found {len(duplicates)} groups of duplicate videos.[/green]")
        
        # Show menu in interactive mode only
        if not args.non_interactive:
            menu = MainMenu(analyzer)
            menu.show_menu()
        else:
            # In non-interactive mode, just print duplicate groups
            display.console.print("\n[cyan]Duplicate Groups:[/cyan]")
            for group_id, files in duplicates.items():
                display.console.print(f"\n[bold]Group {group_id}:[/bold]")
                for file in files:
                    display.console.print(f"  {file['path']} ({file['resolution']}, {file['bitrate']})")
        
    except KeyboardInterrupt:
        logging.info("Operation interrupted by user.")
        display.console.print("[yellow]Operation interrupted by user.[/yellow]")
        return 0
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        display.console.print(f"[red]Error: {str(e)}[/red]")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 