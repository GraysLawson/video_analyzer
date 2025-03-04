from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from typing import Dict, List, Optional
from datetime import datetime
import humanize
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.table import Table
from rich import box
from collections import defaultdict

class ProgressDisplayMixin:
    """Mixin class providing progress tracking and display functionality for the DisplayManager."""
    
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
    
    def log_processing(self, filename: str) -> None:
        """Add a file to the processing log with timestamp and keep a scrollable history."""
        self.processed_files += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add to the processing log
        self.processing_log.append({
            'timestamp': timestamp,
            'filename': self._get_basename(filename),
            'path': filename
        })
        
        # Limit log size for scrolling display
        if len(self.processing_log) > self.MAX_LOG_LINES:
            self.processing_log = self.processing_log[-self.MAX_LOG_LINES:]
            
        # Update the current file
        self.current_file = self._get_basename(filename)
        
        # Update file type statistics if available
        extension = self._get_extension(filename).lower()
        if extension:
            self.file_types[extension] += 1
    
    def update_stats_panel(self) -> Panel:
        """Create an enhanced statistics panel with more metrics."""
        # Create a Table for general stats
        stats_table = Table(box=box.ROUNDED, show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        # Calculate elapsed time
        elapsed = datetime.now() - self.start_time
        elapsed_str = f"{elapsed.seconds // 3600:02}:{(elapsed.seconds % 3600) // 60:02}:{elapsed.seconds % 60:02}"
        
        # Calculate processing rate
        rate = self.processed_files / max(1, elapsed.seconds) if elapsed.seconds > 0 else 0
        
        # Calculate estimated time remaining
        if rate > 0 and self.processed_files < self.total_files:
            remaining_files = self.total_files - self.processed_files
            seconds_remaining = int(remaining_files / rate)
            remaining_str = f"{seconds_remaining // 3600:02}:{(seconds_remaining % 3600) // 60:02}:{seconds_remaining % 60:02}"
        else:
            remaining_str = "00:00:00"
        
        # Calculate completion percentage
        completion = (self.processed_files / max(1, self.total_files)) * 100
        
        # Add rows to the table with improved formatting
        stats_table.add_row("Total Files", f"[bold]{self.total_files}[/bold]")
        stats_table.add_row("Processed Files", f"[bold]{self.processed_files}[/bold] ([cyan]{completion:.1f}%[/cyan])")
        stats_table.add_row("Elapsed Time", f"[bold]{elapsed_str}[/bold]")
        stats_table.add_row("Processing Rate", f"[bold]{rate:.2f}[/bold] files/sec")
        stats_table.add_row("Est. Time Remaining", f"[bold]{remaining_str}[/bold]")
        stats_table.add_row("Duplicate Groups", f"[bold]{self.duplicate_groups}[/bold]")
        stats_table.add_row("Total Size", f"[bold]{humanize.naturalsize(self.total_size)}[/bold]")
        stats_table.add_row("Potential Space Savings", f"[bold cyan]{humanize.naturalsize(self.potential_savings)}[/bold cyan]")
        
        # Create a mini bar chart for file types
        if self.file_types:
            # Sort file types by count
            sorted_types = sorted(
                self.file_types.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 types
            
            file_type_chart = "\n[bold]File Types:[/bold]\n"
            max_count = max(count for _, count in sorted_types)
            max_label_len = max(len(ext) for ext, _ in sorted_types)
            
            for ext, count in sorted_types:
                bar_len = int((count / max_count) * 20)
                percent = (count / max(1, self.processed_files)) * 100
                file_type_chart += f"{ext.ljust(max_label_len)} | {'█' * bar_len} {count} ({percent:.1f}%)\n"
        else:
            file_type_chart = "\n[bold]File Types:[/bold]\n(No files processed yet)"
        
        # Combine all stats components
        stats_content = Group(
            stats_table,
            Text(file_type_chart, justify="left")
        )
        
        return Panel(
            stats_content,
            title="[bold blue]Analysis Statistics[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
    
    def _get_basename(self, path: str) -> str:
        """Extract the filename from a path."""
        import os
        return os.path.basename(path)
    
    def _get_extension(self, path: str) -> str:
        """Extract the file extension from a path."""
        import os
        return os.path.splitext(path)[1] 