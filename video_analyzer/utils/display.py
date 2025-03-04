import time
from typing import Dict
from colorama import Fore, Style, Back
import os
import humanize
import plotext as plt
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich import box
from collections import defaultdict

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
        os.system('cls' if os.name == 'nt' else 'clear')

class DisplayManager:
    def __init__(self):
        self.console = Console()
        self.total_files = 0
        self.current_file = ""
        self.duplicate_groups = 0
        self.total_size = 0
        self.potential_savings = 0
        self.selected_size = 0
        
    def create_progress_display(self, total_files: int) -> Progress:
        """Create a rich progress display."""
        self.total_files = total_files
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            console=self.console
        )
        return progress
    
    def create_status_layout(self) -> Layout:
        """Create the main status layout."""
        layout = Layout()
        layout.split_column(
            Layout(name="progress"),
            Layout(name="stats"),
            Layout(name="current_file")
        )
        return layout
    
    def update_stats_panel(self) -> Panel:
        """Create the statistics panel."""
        stats_table = Table(box=box.ROUNDED, show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Files", str(self.total_files))
        stats_table.add_row("Duplicate Groups", str(self.duplicate_groups))
        stats_table.add_row("Total Size", humanize.naturalsize(self.total_size))
        stats_table.add_row("Potential Space Savings", humanize.naturalsize(self.potential_savings))
        stats_table.add_row("Selected for Deletion", humanize.naturalsize(self.selected_size))
        
        return Panel(stats_table, title="Analysis Statistics", border_style="blue")
    
    def update_current_file_panel(self) -> Panel:
        """Create the current file panel."""
        return Panel(
            self.current_file,
            title="Currently Processing",
            border_style="yellow"
        )
    
    def plot_storage_chart(self, total_size: int, duplicate_size: int, selected_size: int):
        """Create a storage visualization chart."""
        self.console.clear()
        plt.clear_figure()
        
        # Create bar chart
        categories = ['Total Storage', 'Duplicate Files', 'Selected for Deletion']
        sizes = [total_size / (1024**3), duplicate_size / (1024**3), selected_size / (1024**3)]
        colors = ['cyan', 'yellow', 'red']
        
        plt.bar(categories, sizes, color=colors)
        plt.title("Storage Analysis (GB)")
        plt.show()
    
    def plot_duplicate_distribution(self, duplicate_groups: dict):
        """Create a chart showing duplicate file distribution."""
        self.console.clear()
        plt.clear_figure()
        
        # Group files by resolution
        resolutions = defaultdict(int)
        for group in duplicate_groups.values():
            for file in group:
                res = file.get('resolution', 'Unknown')
                resolutions[res] += 1
        
        # Create pie chart
        plt.pie(list(resolutions.values()), list(resolutions.keys()))
        plt.title("Duplicate Files by Resolution")
        plt.show()
    
    def show_deletion_summary(self, files_to_delete: list):
        """Show a summary of files selected for deletion."""
        table = Table(title="Files Selected for Deletion", box=box.ROUNDED)
        table.add_column("File Name", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Resolution", style="yellow")
        
        total_size = 0
        for file in files_to_delete:
            size = os.path.getsize(file['path'])
            total_size += size
            table.add_row(
                os.path.basename(file['path']),
                humanize.naturalsize(size),
                file.get('resolution', 'Unknown')
            )
        
        self.console.print(table)
        self.console.print(f"\nTotal space to be freed: {humanize.naturalsize(total_size)}") 