import os
import plotext as plt
import humanize
from collections import defaultdict
from typing import Dict

# Constants for graph styling
GRAPH_WIDTH = 60
GRAPH_HEIGHT = 15

class ChartDisplayMixin:
    """Mixin class that adds charting and visualization capabilities."""
    
    def plot_storage_chart(self, total_size: int, duplicate_size: int, selected_size: int):
        """Create an improved storage usage chart with percentages and grid."""
        # Update instance variables
        self.total_size = total_size
        self.potential_savings = selected_size
        
        # Set up the plot
        plt.clf()
        plt.title("Storage Analysis")
        plt.plotsize(GRAPH_WIDTH, GRAPH_HEIGHT)
        
        # Create labels and data
        labels = ["Unique Files", "Potential Savings"]
        unique_size = total_size - duplicate_size
        values = [unique_size, selected_size]
        
        # Calculate percentages
        unique_percent = (unique_size / max(1, total_size)) * 100
        savings_percent = (selected_size / max(1, total_size)) * 100
        
        # Enhanced labels with size and percentage
        labels_with_info = [
            f"Unique: {humanize.naturalsize(unique_size)} ({unique_percent:.1f}%)",
            f"Savings: {humanize.naturalsize(selected_size)} ({savings_percent:.1f}%)"
        ]
        
        # Create the bar chart with improved styling
        plt.bar(labels, values, orientation="horizontal")
        plt.xlabel("Storage Space (bytes)")
        plt.grid(True, axis="x") 
        
        # Add value labels to bars
        for i, value in enumerate(values):
            plt.text(
                value + (total_size * 0.01),  # Position text slightly to the right of the bar
                i,                           # Y position aligned with bar
                labels_with_info[i],         # Label with size info
                color="cyan"                 # Text color
            )
        
        # Display the plot to the terminal
        self.console.print("\n[bold blue]Storage Analysis[/bold blue]")
        self.console.print(plt.build())
        
        # Additional storage information
        self.console.print(f"\n[bold]Total Storage:[/bold] {humanize.naturalsize(total_size)}")
        self.console.print(f"[bold]Unique Content:[/bold] {humanize.naturalsize(unique_size)} ({unique_percent:.1f}%)")
        self.console.print(f"[bold]All Duplicates:[/bold] {humanize.naturalsize(duplicate_size)} ({(duplicate_size / max(1, total_size)) * 100:.1f}%)")
        self.console.print(f"[bold]Selected for Removal:[/bold] {humanize.naturalsize(selected_size)} ({savings_percent:.1f}%)")
        
        # If duplicates exist, show potential recovery percentage
        if duplicate_size > 0:
            recovery_percent = (selected_size / max(1, duplicate_size)) * 100
            self.console.print(f"[bold]Recovery Efficiency:[/bold] {recovery_percent:.1f}% of duplicate space can be recovered")
    
    def plot_duplicate_distribution(self, duplicate_groups: dict):
        """Create an enhanced distribution chart of duplicate files with resolution categories."""
        if not duplicate_groups:
            self.console.print("[yellow]No duplicate groups to analyze.[/yellow]")
            return
        
        # Store the duplicate groups count
        self.duplicate_groups = len(duplicate_groups)
        
        # Analyze duplicate groups
        group_sizes = defaultdict(int)
        resolution_counts = defaultdict(int)
        file_sizes = defaultdict(int)
        total_duplicates = 0
        
        for group_name, files in duplicate_groups.items():
            group_size = len(files)
            group_sizes[group_size] += 1
            total_duplicates += group_size - 1  # Count files beyond the first as duplicates
            
            # Track resolutions in duplicates
            for file_info in files:
                resolution = file_info.get('resolution_category', 'Unknown')
                resolution_counts[resolution] += 1
                
                # Track file sizes in categories
                size = file_info.get('file_size_value', 0)
                category = self._get_size_category(size * 1024 * 1024)  # Convert MB to bytes
                file_sizes[category] += 1
        
        # Plot 1: Group Size Distribution
        plt.clf()
        plt.plotsize(GRAPH_WIDTH, GRAPH_HEIGHT)
        plt.title("Duplicate Group Sizes")
        
        sizes = list(sorted(group_sizes.keys()))
        counts = [group_sizes[size] for size in sizes]
        
        plt.bar(
            [f"{size} files" for size in sizes],
            counts,
            color="cyan"
        )
        plt.ylabel("Number of Groups")
        plt.grid(True, axis="y")
        
        self.console.print("\n[bold blue]Duplicate Group Distribution[/bold blue]")
        self.console.print(plt.build())
        
        # Plot 2: Resolution Distribution
        plt.clf()
        plt.plotsize(GRAPH_WIDTH, GRAPH_HEIGHT)
        plt.title("Resolution Distribution of Duplicates")
        
        # Sort resolutions by quality (SD, HD, Full HD, 4K, 8K+)
        resolution_order = ["Unknown", "SD", "HD", "Full HD", "4K", "8K+"]
        sorted_resolutions = sorted(
            resolution_counts.items(),
            key=lambda x: resolution_order.index(x[0]) if x[0] in resolution_order else -1
        )
        
        plt.bar(
            [res for res, _ in sorted_resolutions],
            [count for _, count in sorted_resolutions],
            color="green"
        )
        plt.ylabel("Number of Files")
        plt.grid(True, axis="y")
        
        self.console.print("\n[bold blue]Resolution Distribution[/bold blue]")
        self.console.print(plt.build())
        
        # Plot 3: File Size Distribution
        plt.clf()
        plt.plotsize(GRAPH_WIDTH, GRAPH_HEIGHT)
        plt.title("File Size Distribution of Duplicates")
        
        # Get size categories in order
        size_order = ["Small (<100MB)", "Medium (<500MB)", "Large (<1GB)", "Very Large (1GB+)"]
        sorted_sizes = sorted(
            file_sizes.items(),
            key=lambda x: size_order.index(x[0]) if x[0] in size_order else -1
        )
        
        plt.bar(
            [size for size, _ in sorted_sizes],
            [count for _, count in sorted_sizes],
            color="yellow"
        )
        plt.ylabel("Number of Files")
        plt.grid(True, axis="y")
        
        self.console.print("\n[bold blue]File Size Distribution[/bold blue]")
        self.console.print(plt.build())
        
        # Summary statistics
        self.console.print(f"\n[bold]Total Duplicate Groups:[/bold] {len(duplicate_groups)}")
        self.console.print(f"[bold]Total Duplicate Files:[/bold] {total_duplicates}")
        if total_duplicates > 0:
            self.console.print(f"[bold]Average Duplicates per Group:[/bold] {total_duplicates / len(duplicate_groups):.1f}")
    
    def _get_size_category(self, size_bytes: int) -> str:
        """Categorize file size into readable categories."""
        if size_bytes < 100 * 1024 * 1024:  # Less than 100 MB
            return "Small (<100MB)"
        elif size_bytes < 500 * 1024 * 1024:  # Less than 500 MB
            return "Medium (<500MB)"
        elif size_bytes < 1024 * 1024 * 1024:  # Less than 1 GB
            return "Large (<1GB)"
        else:
            return "Very Large (1GB+)" 