import os
import humanize
from typing import Dict, List, Set, Optional
from collections import defaultdict
import plotext as plt
from rich.table import Table
from rich import box
from rich.text import Text
from rich.panel import Panel
from rich.console import Group

# Constants for visualization
GRAPH_WIDTH = 60
GRAPH_HEIGHT = 15

class TableDisplayMixin:
    """Mixin class for table-related display functionality."""
    
    def create_duplicate_comparison_table(self, files: List[Dict], selected_files: Optional[Set[str]] = None) -> Table:
        """Create an enhanced table for displaying duplicate files with quality comparison."""
        if not selected_files:
            selected_files = set()
            
        table = Table(show_header=True, box=box.ROUNDED)
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("Select", width=6)
        table.add_column("Resolution", style="green")
        table.add_column("Bitrate", style="blue")
        table.add_column("Codec", style="magenta")
        table.add_column("Size", style="yellow")
        table.add_column("Quality", width=12)
        table.add_column("Filename")
        
        for i, file_info in enumerate(files, 1):
            is_selected = file_info['path'] in selected_files
            is_highest = file_info.get('is_highest_quality', False)
            
            # Get resolution details
            resolution = file_info.get('resolution', 'Unknown')
            quality_text = "⭐ BEST" if is_highest else ""
            
            # Get comparison if available
            comparison = file_info.get('compared_to_best', {})
            quality_percent = comparison.get('quality_percent', 100)
            
            # Build quality indicator
            if is_highest:
                quality_indicator = "[bold green]100%[/bold green]"
            elif quality_percent >= 90:
                quality_indicator = f"[green]{quality_percent}%[/green]"
            elif quality_percent >= 70:
                quality_indicator = f"[yellow]{quality_percent}%[/yellow]"
            else:
                quality_indicator = f"[red]{quality_percent}%[/red]"
            
            # Add row with enhanced formatting
            table.add_row(
                str(i),
                "✓" if is_selected else "",
                f"[{'bold green' if is_highest else 'default'}]{resolution}[/]",
                file_info.get('bitrate', 'Unknown'),
                file_info.get('codec', 'Unknown'),
                file_info.get('file_size', 'Unknown'),
                quality_indicator,
                os.path.basename(file_info['path'])
            )
            
            # Add comparison details in a separate row if not the highest quality
            if not is_highest and comparison:
                res_diff = comparison.get('resolution_diff', '')
                bitrate_diff = comparison.get('bitrate_diff', '')
                
                comparison_text = f"[dim]Compared to best: {res_diff} | {bitrate_diff}[/dim]"
                
                # Add a subrow with comparison details
                table.add_row(
                    "",
                    "",
                    comparison_text,
                    "",
                    "",
                    "",
                    "",
                    ""
                )
        
        return table
    
    def show_deletion_summary(self, files_to_delete: list):
        """Show an enhanced summary of files selected for deletion with visualizations."""
        if not files_to_delete:
            self.console.print("[yellow]No files selected for deletion.[/yellow]")
            return
        
        # Calculate statistics
        total_size = sum(file['size'] for file in files_to_delete)
        self.selected_size = total_size
        
        # Group by resolution
        resolution_groups = defaultdict(int)
        file_type_groups = defaultdict(int)
        
        for file in files_to_delete:
            filename = os.path.basename(file['path'])
            ext = os.path.splitext(filename)[1].lower() or "unknown"
            file_type_groups[ext] += 1
            
            # This would be more accurate if we had the metadata
            # For now we'll try to extract resolution from filename
            for res in ['480p', '720p', '1080p', '2160p', '4k']:
                if res in filename.lower():
                    resolution_groups[res] += 1
                    break
            else:
                resolution_groups['unknown'] += 1
        
        # Create a summary table
        table = Table(title="Deletion Summary", box=box.ROUNDED)
        table.add_column("Statistic", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Files to Delete", str(len(files_to_delete)))
        table.add_row("Total Space to Free", humanize.naturalsize(total_size))
        
        # Generate resolution distribution chart
        if resolution_groups:
            plt.clf()
            plt.plotsize(GRAPH_WIDTH, GRAPH_HEIGHT)
            plt.title("Resolutions Selected for Deletion")
            
            labels = list(resolution_groups.keys())
            values = list(resolution_groups.values())
            
            plt.bar(labels, values, color="red")
            plt.ylabel("Number of Files")
            
            self.console.print("\n[bold]Files by Resolution:[/bold]")
            self.console.print(plt.build())
        
        # Generate file type distribution chart
        if file_type_groups:
            plt.clf()
            plt.plotsize(GRAPH_WIDTH, GRAPH_HEIGHT)
            plt.title("File Types Selected for Deletion")
            
            labels = list(file_type_groups.keys())
            values = list(file_type_groups.values())
            
            plt.bar(labels, values, color="yellow")
            plt.ylabel("Number of Files")
            
            self.console.print("\n[bold]Files by Type:[/bold]")
            self.console.print(plt.build())
        
        # Show the deletion list
        self.console.print("\n[bold]Files Selected for Deletion:[/bold]")
        
        deletion_table = Table(show_header=True, box=box.SIMPLE)
        deletion_table.add_column("Filename", style="red")
        deletion_table.add_column("Size", style="yellow")
        deletion_table.add_column("Path")
        
        for file in files_to_delete:
            deletion_table.add_row(
                os.path.basename(file['path']),
                humanize.naturalsize(file['size']),
                os.path.dirname(file['path'])
            )
        
        self.console.print(deletion_table)
        
        # Show confirmation message
        self.console.print(f"\n[bold green]Total space that will be freed:[/bold green] {humanize.naturalsize(total_size)}")
        if 'moved_to' in files_to_delete[0]:
            self.console.print("[bold yellow]Files will be moved, not deleted.[/bold yellow]")
            self.console.print(f"Destination: {os.path.dirname(files_to_delete[0]['moved_to'])}")
        else:
            self.console.print("[bold red]Warning: Files will be permanently deleted![/bold red]")
        
        self.console.print("\nPlease review the list before confirming.") 