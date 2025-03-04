from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.console import Group
from rich import box
from datetime import datetime
import os
from rich.table import Table

class InteractiveDisplayMixin:
    """Mixin class providing interactive display functionality for the DisplayManager."""
    
    def create_status_layout(self) -> Layout:
        """Create the main status layout with improved structure."""
        layout = Layout()
        
        # Create a more detailed layout with separate sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main")
        )
        
        # Create main layout with stats and processing info
        layout["main"].split_row(
            Layout(name="left_panel", ratio=2),
            Layout(name="right_panel", ratio=3)
        )
        
        # Split left panel for stats and charts
        layout["left_panel"].split_column(
            Layout(name="stats", ratio=1),
            Layout(name="charts", ratio=2)
        )
        
        # Split right panel for current file and log
        layout["right_panel"].split_column(
            Layout(name="progress", ratio=1),
            Layout(name="current_file", ratio=1),
            Layout(name="processing_log", ratio=2)
        )
        
        return layout
    
    def update_current_file_panel(self) -> Panel:
        """Create a panel showing the current file being processed with progress info."""
        # Display the current filename prominently
        if hasattr(self, 'current_file'):
            current_file_text = f"[bold]{self.current_file}[/bold]"
            
            # Create a progress representation
            progress_percent = (self.processed_files / max(1, self.total_files)) * 100
            progress_bar_width = 50
            filled_length = int(progress_bar_width * progress_percent / 100)
            progress_bar = f"[{'=' * filled_length}{'>' if filled_length < progress_bar_width else ''}{'.' * (progress_bar_width - filled_length - 1)}] {progress_percent:.1f}%"
            
            content = Group(
                Text(current_file_text, justify="center"),
                Text(f"File {self.processed_files} of {self.total_files}", justify="center"),
                Text(progress_bar, justify="center")
            )
        else:
            content = Text("No files processed yet", justify="center")
        
        return Panel(
            content,
            title="[bold green]Currently Processing[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
    
    def update_processing_log_panel(self) -> Panel:
        """Create a scrollable panel of recently processed files."""
        if not self.processing_log:
            content = Text("No files processed yet.", justify="center")
        else:
            # Create a table for the log
            log_table = Table(show_header=True, box=box.SIMPLE)
            log_table.add_column("Time", style="cyan", no_wrap=True)
            log_table.add_column("File", style="green")
            
            # Add the most recent files first
            for entry in reversed(self.processing_log):
                log_table.add_row(entry['timestamp'], entry['filename'])
            
            content = Group(
                Text("Most recently processed files:", style="bold"),
                log_table
            )
        
        return Panel(
            content,
            title="[bold yellow]Processing Log[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
    
    def create_header_panel(self) -> Panel:
        """Create a header panel with overall status information."""
        status_text = "❓ Analyzing" if self.processed_files < self.total_files else "✅ Analysis Complete"
        return Panel(
            Text(f"Video Analyzer - {status_text}", justify="center"),
            style="bold blue on black"
        )
    
    def update_layout(self, layout: Layout) -> None:
        """Update all panels in the layout with the latest information."""
        # Update the header
        layout["header"].update(self.create_header_panel())
        
        # Update the statistics panel
        layout["stats"].update(self.update_stats_panel())
        
        # Update the current file and processing log panels
        layout["current_file"].update(self.update_current_file_panel())
        layout["processing_log"].update(self.update_processing_log_panel()) 