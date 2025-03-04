from rich.table import Table
import os
import humanize
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import box
from ..utils.display import DisplayManager
from ..core.analyzer import VideoAnalyzer
from typing import Dict, List, Set

# Custom menu implementation to replace rich.menu
class Menu:
    def __init__(self, title, choices):
        self.title = title
        self.choices = choices
        self.console = Console()
    
    def show(self):
        self.console.print(f"\n[bold]{self.title}[/bold]\n")
        for i, choice in enumerate(self.choices, 1):
            self.console.print(f"  {i}. {choice}")
        self.console.print()
        
        while True:
            selection = Prompt.ask("Select an option", default="1")
            try:
                index = int(selection) - 1
                if 0 <= index < len(self.choices):
                    return index
                self.console.print("[red]Invalid selection. Please try again.[/red]")
            except ValueError:
                self.console.print("[red]Please enter a number.[/red]")

class MainMenu:
    def __init__(self, analyzer: VideoAnalyzer):
        self.analyzer = analyzer
        self.display = DisplayManager()
        self.console = Console()
    
    def show_menu(self):
        """Display the main menu with enhanced options."""
        while True:
            self.console.clear()
            self.console.print("[bold cyan]Video Analyzer Menu[/bold cyan]")
            self.console.print()
            
            # Show summary of analyzed content if available
            if self.analyzer.duplicates:
                tv_shows = sum(1 for name in self.analyzer.duplicates if ' - S' in name)
                movies = len(self.analyzer.duplicates) - tv_shows
                
                total_duplicate_files = sum(len(files) for files in self.analyzer.duplicates.values())
                total_files_for_deletion = len(self.analyzer.selected_for_deletion)
                
                self.console.print(f"[green]Found {len(self.analyzer.duplicates)} duplicate groups[/green]")
                self.console.print(f"  • [yellow]{tv_shows} TV Show episodes[/yellow]")
                self.console.print(f"  • [yellow]{movies} Movies[/yellow]")
                self.console.print(f"[green]Selected {total_files_for_deletion} files for removal[/green]")
                self.console.print()
            
            menu_items = [
                ("1", "View Duplicate Groups"),
                ("2", "Auto-Select Lower Quality Files"),
                ("3", "View Storage Analysis Chart"),
                ("4", "View Duplicates Distribution"),
                ("5", "Review Selected Files"),
                ("6", "Execute Deletion"),
                ("7", "Filter by Resolution"),
                ("q", "Quit")
            ]
            
            for key, desc in menu_items:
                self.console.print(f"[yellow]{key}[/yellow]: {desc}")
            
            choice = input("\nEnter your choice: ").lower()
            
            if choice == '1':
                self._show_duplicate_groups()
            elif choice == '2':
                self._auto_select_files()
            elif choice == '3':
                self._show_storage_analysis()
            elif choice == '4':
                self._show_duplicates_distribution()
            elif choice == '5':
                self._review_selected_files()
            elif choice == '6':
                self._execute_deletion()
            elif choice == '7':
                self._filter_by_resolution()
            elif choice == 'q':
                break
    
    def _show_duplicate_groups(self):
        """Display duplicate groups with enhanced resolution comparison."""
        self.console.clear()
        
        if not self.analyzer.duplicates:
            self.console.print("[yellow]No duplicate groups found.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Categorize groups
        tv_groups = {}
        movie_groups = {}
        
        for group_name, files in self.analyzer.duplicates.items():
            if ' - S' in group_name:  # TV Show pattern
                tv_groups[group_name] = files
            else:
                movie_groups[group_name] = files
        
        # Create menu options
        menu_options = []
        if tv_groups:
            menu_options.append("View TV Show Duplicates")
        if movie_groups:
            menu_options.append("View Movie Duplicates")
        menu_options.append("View All Duplicates")
        menu_options.append("Back to Main Menu")
        
        menu = Menu("Select Category to View", menu_options)
        choice = menu.show()
        
        if choice >= len(menu_options) - 1:  # Back to Main Menu
            return
        
        # Determine which groups to show
        if menu_options[choice] == "View TV Show Duplicates":
            self._display_group_list(tv_groups, "TV Show Episodes")
        elif menu_options[choice] == "View Movie Duplicates":
            self._display_group_list(movie_groups, "Movies")
        else:  # View All
            self._display_group_list(self.analyzer.duplicates, "All Duplicate Groups")
    
    def _display_group_list(self, groups, title):
        """Display a list of duplicate groups with details."""
        while True:
            self.console.clear()
            self.console.print(f"[bold cyan]{title}[/bold cyan] ({len(groups)} groups)\n")
            
            # Create a table for the groups
            table = Table(show_header=True, box=box.ROUNDED)
            table.add_column("#", style="cyan", width=4)
            table.add_column("Group Name", style="green")
            table.add_column("Files", style="yellow", justify="center")
            table.add_column("Resolutions", style="magenta")
            table.add_column("Total Size", style="blue", justify="right")
            
            # Add rows for each group
            for i, (group_name, files) in enumerate(groups.items(), 1):
                # Get unique resolutions in the group
                resolutions = set(file.get('resolution_category', 'Unknown') for file in files)
                resolutions_str = ", ".join(sorted(resolutions))
                
                # Calculate total size
                total_size = sum(self.analyzer._get_file_size(file['path']) for file in files)
                
                table.add_row(
                    str(i),
                    group_name,
                    str(len(files)),
                    resolutions_str,
                    humanize.naturalsize(total_size)
                )
            
            self.console.print(table)
            
            # Ask for selection
            selection = input("\nEnter group number to view details (or 'b' to go back): ")
            
            if selection.lower() == 'b':
                break
            
            try:
                group_idx = int(selection) - 1
                if 0 <= group_idx < len(groups):
                    group_name = list(groups.keys())[group_idx]
                    self._display_group_details(group_name, groups[group_name])
                else:
                    self.console.print("[red]Invalid group number. Please try again.[/red]")
                    input("\nPress Enter to continue...")
            except ValueError:
                self.console.print("[red]Please enter a number or 'b'.[/red]")
                input("\nPress Enter to continue...")
    
    def _display_group_details(self, group_name, files):
        """Display detailed information for a specific duplicate group with resolution comparison."""
        while True:
            self.console.clear()
            self.console.print(f"[bold green]Group: {group_name}[/bold green]\n")
            
            # Create a comparison table using the enhanced display functionality
            comparison_table = self.display.create_duplicate_comparison_table(
                files, 
                self.analyzer.selected_for_deletion
            )
            
            self.console.print(comparison_table)
            
            # Show additional information for the highest quality file
            highest_quality = files[0]  # First file should be highest quality from sort
            
            highest_info = Panel(
                f"[bold]Highest Quality Version:[/bold] {os.path.basename(highest_quality['path'])}\n"
                f"[bold]Resolution:[/bold] {highest_quality.get('resolution', 'Unknown')}\n"
                f"[bold]Bitrate:[/bold] {highest_quality.get('bitrate', 'Unknown')}\n"
                f"[bold]Codec:[/bold] {highest_quality.get('codec', 'Unknown')}\n"
                f"[bold]Size:[/bold] {highest_quality.get('file_size', 'Unknown')}\n",
                title="Reference File",
                border_style="green"
            )
            
            self.console.print(highest_info)
            
            # Show selection options
            self.console.print("\n[bold cyan]Options:[/bold cyan]")
            self.console.print("  1. Select files to keep")
            self.console.print("  2. Select files to delete")
            self.console.print("  3. Toggle all except highest quality")
            self.console.print("  4. Back to group list")
            
            choice = input("\nEnter choice: ")
            
            if choice == '1':
                self._select_files_to_keep(files)
            elif choice == '2':
                self._select_files_to_delete(files)
            elif choice == '3':
                self._toggle_all_except_highest(files)
            elif choice == '4':
                break
    
    def _select_files_to_keep(self, files):
        """Select files to keep, marking others for deletion."""
        self.console.clear()
        self.console.print("[bold]Select files to KEEP (all others will be marked for deletion):[/bold]\n")
        
        for i, file in enumerate(files, 1):
            is_highest = file.get('is_highest_quality', False)
            resolution = file.get('resolution', 'Unknown')
            quality_info = ""
            
            if is_highest:
                quality_info = " [green]⭐ HIGHEST QUALITY[/green]"
            elif 'compared_to_best' in file:
                comparison = file['compared_to_best']
                quality_percent = comparison.get('quality_percent', 100)
                quality_info = f" [yellow]({quality_percent}% of best quality)[/yellow]"
            
            self.console.print(f"{i}. {os.path.basename(file['path'])} - {resolution}{quality_info}")
        
        selection = input("\nEnter numbers of files to KEEP (comma-separated, or 'a' for all, 'h' for highest only): ")
        
        if selection.lower() == 'a':
            # Keep all files (remove all from selection)
            for file in files:
                if file['path'] in self.analyzer.selected_for_deletion:
                    self.analyzer.selected_for_deletion.remove(file['path'])
        elif selection.lower() == 'h':
            # Keep only highest quality
            self._toggle_all_except_highest(files)
        else:
            try:
                # Parse selection
                keep_indices = [int(idx.strip()) - 1 for idx in selection.split(',') if idx.strip()]
                
                # Verify indices
                valid_indices = [idx for idx in keep_indices if 0 <= idx < len(files)]
                
                # Update selection
                for i, file in enumerate(files):
                    if i in valid_indices:
                        # Remove from deletion selection if present
                        if file['path'] in self.analyzer.selected_for_deletion:
                            self.analyzer.selected_for_deletion.remove(file['path'])
                    else:
                        # Add to deletion selection
                        self.analyzer.selected_for_deletion.add(file['path'])
                        
            except ValueError:
                self.console.print("[red]Invalid input. Please enter comma-separated numbers.[/red]")
                input("\nPress Enter to continue...")
    
    def _select_files_to_delete(self, files):
        """Select files to delete directly."""
        self.console.clear()
        self.console.print("[bold]Select files to DELETE:[/bold]\n")
        
        for i, file in enumerate(files, 1):
            is_highest = file.get('is_highest_quality', False)
            resolution = file.get('resolution', 'Unknown')
            quality_info = ""
            
            if is_highest:
                quality_info = " [green]⭐ HIGHEST QUALITY[/green]"
            elif 'compared_to_best' in file:
                comparison = file['compared_to_best']
                quality_percent = comparison.get('quality_percent', 100)
                quality_info = f" [yellow]({quality_percent}% of best quality)[/yellow]"
            
            self.console.print(f"{i}. {os.path.basename(file['path'])} - {resolution}{quality_info}")
        
        selection = input("\nEnter numbers of files to DELETE (comma-separated, or 'a' for all except highest): ")
        
        if selection.lower() == 'a':
            # Delete all except highest quality
            self._toggle_all_except_highest(files)
        else:
            try:
                # Parse selection
                delete_indices = [int(idx.strip()) - 1 for idx in selection.split(',') if idx.strip()]
                
                # Verify indices
                valid_indices = [idx for idx in delete_indices if 0 <= idx < len(files)]
                
                # Update selection
                for i, file in enumerate(files):
                    if i in valid_indices:
                        # Add to deletion selection
                        self.analyzer.selected_for_deletion.add(file['path'])
                    else:
                        # Remove from deletion selection if present
                        if file['path'] in self.analyzer.selected_for_deletion:
                            self.analyzer.selected_for_deletion.remove(file['path'])
                        
            except ValueError:
                self.console.print("[red]Invalid input. Please enter comma-separated numbers.[/red]")
                input("\nPress Enter to continue...")
    
    def _toggle_all_except_highest(self, files):
        """Toggle selection to keep only the highest quality file."""
        if not files:
            return
            
        # The first file should be the highest quality due to sorting
        highest_quality = files[0]
        
        # Remove highest quality from deletion
        if highest_quality['path'] in self.analyzer.selected_for_deletion:
            self.analyzer.selected_for_deletion.remove(highest_quality['path'])
        
        # Add all others to deletion
        for file in files[1:]:
            self.analyzer.selected_for_deletion.add(file['path'])
    
    def _auto_select_files(self):
        """Auto-select files for deletion based on resolution and quality."""
        self.console.clear()
        
        if not self.analyzer.duplicates:
            self.console.print("[yellow]No duplicate groups found. Cannot auto-select files.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        self.console.print("[bold cyan]Auto-Selection Options[/bold cyan]\n")
        self.console.print("1. Keep highest resolution/quality version only")
        self.console.print("2. Keep smallest file size version only")
        self.console.print("3. Smart selection (balanced quality/size)")
        self.console.print("4. Cancel")
        
        choice = input("\nEnter choice: ")
        
        if choice == '1':
            self.analyzer.auto_select_files(keep_highest_resolution=True)
            self.console.print("\n[green]Selected lower resolution files for deletion.[/green]")
            self.console.print(f"[green]{len(self.analyzer.selected_for_deletion)} files marked for deletion.[/green]")
        elif choice == '2':
            self.analyzer.auto_select_files(keep_highest_resolution=False)
            self.console.print("\n[green]Selected larger file size versions for deletion.[/green]")
            self.console.print(f"[green]{len(self.analyzer.selected_for_deletion)} files marked for deletion.[/green]")
        elif choice == '3':
            self._smart_selection()
            self.console.print("\n[green]Performed smart selection based on quality and size.[/green]")
            self.console.print(f"[green]{len(self.analyzer.selected_for_deletion)} files marked for deletion.[/green]")
        elif choice == '4':
            return
        
        input("\nPress Enter to continue...")
    
    def _smart_selection(self):
        """Perform smart selection considering both quality and file size."""
        # Clear current selection
        self.analyzer.selected_for_deletion.clear()
        
        # Process each duplicate group
        for group_name, files in self.analyzer.duplicates.items():
            if len(files) <= 1:
                continue
            
            # Get highest quality file
            highest_quality = files[0]
            
            for file in files[1:]:
                # Skip files that are very close to highest quality but smaller
                if 'compared_to_best' in file:
                    comparison = file['compared_to_best']
                    quality_percent = comparison.get('quality_percent', 0)
                    size_diff_value = comparison.get('size_diff_value', 0)
                    
                    # If quality is >90% of best but file is >20% smaller, consider keeping it
                    if quality_percent > 90 and size_diff_value > 0 and \
                       (size_diff_value / self.analyzer._get_file_size(highest_quality['path'])) > 0.2:
                        # Keep this file, possibly mark highest for deletion if it's not much better
                        if quality_percent > 95:  # Very close in quality
                            self.analyzer.selected_for_deletion.add(highest_quality['path'])
                            break
                        continue
                
                # Mark lower quality for deletion
                self.analyzer.selected_for_deletion.add(file['path'])
    
    def _show_storage_analysis(self):
        """Show storage analysis with enhanced charts."""
        self.console.clear()
        
        if not self.analyzer.duplicates:
            self.console.print("[yellow]No duplicate groups found. Cannot show storage analysis.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Calculate storage metrics
        total_size = sum(
            sum(self.analyzer._get_file_size(file['path']) for file in files)
            for files in self.analyzer.duplicates.values()
        )
        
        duplicate_size = sum(
            sum(self.analyzer._get_file_size(file['path']) for file in files[1:])
            for files in self.analyzer.duplicates.values()
        )
        
        selected_size = sum(
            self.analyzer._get_file_size(path)
            for path in self.analyzer.selected_for_deletion
        )
        
        # Show the storage chart
        self.display.plot_storage_chart(total_size, duplicate_size, selected_size)
        
        input("\nPress Enter to continue...")
    
    def _show_duplicates_distribution(self):
        """Show distribution of duplicates with enhanced visualization."""
        self.console.clear()
        
        if not self.analyzer.duplicates:
            self.console.print("[yellow]No duplicate groups found.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Show distribution charts
        self.display.plot_duplicate_distribution(self.analyzer.duplicates)
        
        input("\nPress Enter to continue...")
    
    def _review_selected_files(self):
        """Review files selected for deletion with enhanced display."""
        self.console.clear()
        
        if not self.analyzer.selected_for_deletion:
            self.console.print("[yellow]No files selected for deletion.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Create a list of files with their sizes
        files_info = []
        for path in self.analyzer.selected_for_deletion:
            size = self.analyzer._get_file_size(path)
            files_info.append({
                'path': path,
                'size': size
            })
        
        # Sort by size (largest first)
        files_info.sort(key=lambda x: x['size'], reverse=True)
        
        # Show the enhanced deletion summary
        self.display.show_deletion_summary(files_info)
        
        # Confirm if user wants to keep this selection
        if Confirm.ask("\nKeep this selection?", default=True):
            self.console.print("[green]Selection confirmed.[/green]")
        else:
            self.analyzer.selected_for_deletion.clear()
            self.console.print("[yellow]Selection cleared.[/yellow]")
        
        input("\nPress Enter to continue...")
    
    def _execute_deletion(self):
        """Execute the deletion or moving of selected files."""
        self.console.clear()
        
        if not self.analyzer.selected_for_deletion:
            self.console.print("[yellow]No files selected for deletion.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Count total files and size
        total_files = len(self.analyzer.selected_for_deletion)
        total_size = sum(self.analyzer._get_file_size(path) for path in self.analyzer.selected_for_deletion)
        
        # Show summary
        self.console.print(f"[bold red]WARNING: About to {'move' if self.analyzer.output_dir else 'delete'} {total_files} files[/bold red]")
        self.console.print(f"[bold]Total space to be freed:[/bold] {humanize.naturalsize(total_size)}")
        
        if self.analyzer.output_dir:
            self.console.print(f"[bold]Files will be moved to:[/bold] {self.analyzer.output_dir}")
        else:
            self.console.print("[bold red]Files will be PERMANENTLY DELETED![/bold red]")
        
        # Confirm deletion
        if not Confirm.ask("\nProceed with operation?", default=False):
            self.console.print("[yellow]Operation cancelled.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Execute deletion
        results = self.analyzer.delete_selected_files()
        
        # Show results
        self.console.print("\n[bold green]Operation completed:[/bold green]")
        self.console.print(f"  • Files processed: {len(results['deleted']) + len(results['failed'])}")
        self.console.print(f"  • Successful: {len(results['deleted'])}")
        self.console.print(f"  • Failed: {len(results['failed'])}")
        self.console.print(f"  • Total space freed: {humanize.naturalsize(results['total_freed'])}")
        
        # Reset selection after deletion
        self.analyzer.selected_for_deletion.clear()
        
        # Update duplicates dictionary to remove deleted files
        self._update_duplicates_after_deletion(results['deleted'])
        
        input("\nPress Enter to continue...")
    
    def _update_duplicates_after_deletion(self, deleted_files):
        """Update the duplicates dictionary after deletion."""
        deleted_paths = {file['path'] for file in deleted_files}
        
        # Create a new duplicates dictionary without the deleted files
        updated_duplicates = {}
        
        for group_name, files in self.analyzer.duplicates.items():
            # Filter out deleted files
            updated_files = [file for file in files if file['path'] not in deleted_paths]
            
            # Only keep groups with at least one file
            if updated_files:
                updated_duplicates[group_name] = updated_files
        
        # Update the analyzer's duplicates
        self.analyzer.duplicates = updated_duplicates
    
    def _filter_by_resolution(self):
        """Filter duplicate groups by resolution category."""
        self.console.clear()
        
        if not self.analyzer.duplicates:
            self.console.print("[yellow]No duplicate groups found.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Collect all available resolutions
        all_resolutions = set()
        for files in self.analyzer.duplicates.values():
            for file in files:
                all_resolutions.add(file.get('resolution_category', 'Unknown'))
        
        # Sort resolutions by quality
        resolution_order = ["Unknown", "SD", "HD", "Full HD", "4K", "8K+"]
        sorted_resolutions = sorted(
            all_resolutions,
            key=lambda x: resolution_order.index(x) if x in resolution_order else -1
        )
        
        # Create menu options
        menu_options = [f"Show groups with {res}" for res in sorted_resolutions]
        menu_options.append("Show ALL resolution groups")
        menu_options.append("Back to Main Menu")
        
        menu = Menu("Filter by Resolution", menu_options)
        choice = menu.show()
        
        if choice >= len(menu_options) - 1:  # Back to Main Menu
            return
        
        # Filter groups by selected resolution
        if menu_options[choice] == "Show ALL resolution groups":
            self._display_group_list(self.analyzer.duplicates, "All Duplicate Groups")
            return
        
        selected_resolution = sorted_resolutions[choice]
        filtered_groups = {}
        
        for group_name, files in self.analyzer.duplicates.items():
            # Check if any file has the selected resolution
            has_resolution = any(file.get('resolution_category', 'Unknown') == selected_resolution for file in files)
            if has_resolution:
                filtered_groups[group_name] = files
        
        # Show filtered groups
        self._display_group_list(filtered_groups, f"Groups with {selected_resolution} Resolution") 