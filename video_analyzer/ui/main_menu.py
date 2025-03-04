from msilib import Table
import os
import humanize
from rich.console import Console
from rich.menu import Menu
from ..utils.display import DisplayManager
from ..core.analyzer import VideoAnalyzer

class MainMenu:
    def __init__(self, analyzer: VideoAnalyzer):
        self.analyzer = analyzer
        self.display = DisplayManager()
        self.console = Console()
    
    def show_menu(self):
        """Display the main menu."""
        while True:
            self.console.clear()
            self.console.print("[bold cyan]Video Analyzer Menu[/bold cyan]")
            self.console.print()
            
            menu_items = [
                ("1", "View Duplicate Groups"),
                ("2", "Auto-Select Lower Quality Files"),
                ("3", "View Storage Analysis Chart"),
                ("4", "View Duplicates Distribution"),
                ("5", "Review Selected Files"),
                ("6", "Execute Deletion"),
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
            elif choice == 'q':
                break
    
    def _show_duplicate_groups(self):
        """Display duplicate groups with detailed information."""
        self.console.clear()
        
        if not self.analyzer.duplicates:
            self.console.print("[yellow]No duplicate groups found.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        for group_id, files in self.analyzer.duplicates.items():
            self.console.print(f"\n[bold cyan]Group {group_id}:[/bold cyan]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("File Name")
            table.add_column("Resolution")
            table.add_column("Size")
            table.add_column("Bitrate")
            
            for file in files:
                table.add_row(
                    os.path.basename(file['path']),
                    file.get('resolution', 'Unknown'),
                    file.get('file_size', 'Unknown'),
                    file.get('bitrate', 'Unknown')
                )
            
            self.console.print(table)
        
        input("\nPress Enter to continue...")
    
    def _auto_select_files(self):
        """Auto-select lower quality files and show summary."""
        total_size_before = sum(os.path.getsize(file['path']) 
                              for group in self.analyzer.duplicates.values() 
                              for file in group)
        
        for group in self.analyzer.duplicates.values():
            self.analyzer.auto_select_files(group)
        
        selected_size = sum(os.path.getsize(path) 
                          for path in self.analyzer.selected_for_deletion)
        
        self.display.show_deletion_summary([
            {'path': path} for path in self.analyzer.selected_for_deletion
        ])
        
        input("\nPress Enter to continue...")
    
    def _show_storage_analysis(self):
        """Display storage analysis chart."""
        total_size = sum(os.path.getsize(file['path']) 
                        for group in self.analyzer.duplicates.values() 
                        for file in group)
        duplicate_size = sum(os.path.getsize(file['path']) 
                           for group in self.analyzer.duplicates.values() 
                           for file in group[1:])
        selected_size = sum(os.path.getsize(path) 
                          for path in self.analyzer.selected_for_deletion)
        
        self.display.plot_storage_chart(total_size, duplicate_size, selected_size)
        input("\nPress Enter to continue...")
    
    def _show_duplicates_distribution(self):
        """Display duplicate files distribution chart."""
        self.display.plot_duplicate_distribution(self.analyzer.duplicates)
        input("\nPress Enter to continue...")
    
    def _review_selected_files(self):
        """Review files selected for deletion."""
        if not self.analyzer.selected_for_deletion:
            self.console.print("[yellow]No files selected for deletion.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        self.display.show_deletion_summary([
            {'path': path} for path in self.analyzer.selected_for_deletion
        ])
        input("\nPress Enter to continue...")
    
    def _execute_deletion(self):
        """Execute the deletion of selected files."""
        if not self.analyzer.selected_for_deletion:
            self.console.print("[yellow]No files selected for deletion.[/yellow]")
            input("\nPress Enter to continue...")
            return
        
        self.console.print("\n[bold red]Warning: This will permanently delete the selected files![/bold red]")
        confirm = input("Are you sure you want to proceed? (yes/no): ").lower()
        
        if confirm == 'yes':
            results = self.analyzer.delete_selected_files()
            self.console.print(f"\n[green]Deleted {results['deleted']} files[/green]")
            self.console.print(f"[green]Saved {humanize.naturalsize(results['saved_space'])}[/green]")
            if results['failed'] > 0:
                self.console.print(f"[red]Failed to delete {results['failed']} files[/red]")
        
        input("\nPress Enter to continue...") 