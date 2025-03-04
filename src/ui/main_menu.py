from typing import Dict, List
from tabulate import tabulate
from colorama import Fore, Style, Back
from ..utils.display import DisplayUtils
from ..core.analyzer import VideoAnalyzer

class MainMenu:
    def __init__(self, analyzer: VideoAnalyzer):
        self.analyzer = analyzer
        self.display = DisplayUtils()
    
    def show_menu(self) -> None:
        """Display the main menu and handle user input."""
        while True:
            self.display.clear_screen()
            
            # Show header
            print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} 📹 Duplicate Video Manager 📹 {Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}\n")
            
            if not self.analyzer.duplicates:
                print(f"{Fore.GREEN}No duplicates found. Nothing to manage.{Style.RESET_ALL}")
                return
            
            # Show summary of duplicates
            print(f"{Fore.YELLOW}{Style.BRIGHT}Found duplicates in:{Style.RESET_ALL}")
            
            # Create a menu of content with duplicates
            content_options = self._get_content_options()
            table_data = self._create_table_data(content_options)
            
            # Display the table
            headers = ["#", "Content", "Duplicate Items", "Total Files", "Status"]
            print(tabulate(table_data, headers=headers, tablefmt="simple"))
            
            # Show options
            print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
            options_table = [
                [f"{Fore.CYAN}1-{len(content_options)}{Style.RESET_ALL}", "Manage specific content"],
                [f"{Fore.CYAN}a{Style.RESET_ALL}", "Auto-select lower resolution files"],
                [f"{Fore.CYAN}d{Style.RESET_ALL}", "Delete all selected files"],
                [f"{Fore.CYAN}c{Style.RESET_ALL}", "Clear all selections"],
                [f"{Fore.CYAN}q{Style.RESET_ALL}", "Quit"]
            ]
            print(tabulate(options_table, tablefmt="plain"))
            
            # Get user choice
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            if not self._handle_choice(choice, content_options):
                break
    
    def _get_content_options(self) -> List[tuple]:
        """Get list of content options with their details."""
        content_options = []
        i = 1
        for content_key in sorted(self.analyzer.duplicates.keys()):
            num_dups = len(self.analyzer.duplicates[content_key])
            total_files = sum(len(files) for files in self.analyzer.duplicates[content_key].values())
            
            # Count selected files
            selected = sum(
                1 for files in self.analyzer.duplicates[content_key].values()
                for file in files
                if file['path'] in self.analyzer.selected_for_deletion
            )
            
            content_options.append((i, content_key, num_dups, total_files, selected))
            i += 1
        
        return content_options
    
    def _create_table_data(self, content_options: List[tuple]) -> List[List[str]]:
        """Create table data from content options."""
        table_data = []
        for opt_num, content_key, num_dups, total_files, selected in content_options:
            status = (f"{Fore.GREEN}[{selected}/{total_files} selected]{Style.RESET_ALL}"
                     if selected > 0 else f"{Fore.YELLOW}[0 selected]{Style.RESET_ALL}")
            
            table_data.append([
                f"{Fore.CYAN}{opt_num}{Style.RESET_ALL}",
                content_key,
                f"{num_dups} items",
                f"{total_files} files",
                status
            ])
        return table_data
    
    def _handle_choice(self, choice: str, content_options: List[tuple]) -> bool:
        """Handle user menu choice. Returns False if should exit menu."""
        if choice.lower() == 'q':
            return False
        elif choice.lower() == 'a':
            self._handle_auto_select()
        elif choice.lower() == 'd':
            self._handle_delete()
        elif choice.lower() == 'c':
            self._handle_clear()
        else:
            try:
                opt_num = int(choice)
                if 1 <= opt_num <= len(content_options):
                    content_key = content_options[opt_num - 1][1]
                    from .content_menu import ContentMenu
                    content_menu = ContentMenu(self.analyzer, content_key)
                    content_menu.show_menu()
                else:
                    self.display.print_status(f"Invalid option: {choice}", Fore.RED)
                    input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            except ValueError:
                self.display.print_status(f"Invalid option: {choice}", Fore.RED)
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        return True
    
    def _handle_auto_select(self) -> None:
        """Handle auto-select option."""
        total_selected = 0
        for content_dups in self.analyzer.duplicates.values():
            for files in content_dups.values():
                before = len(self.analyzer.selected_for_deletion.intersection(
                    file['path'] for file in files
                ))
                self.analyzer.auto_select_files(files)
                after = len(self.analyzer.selected_for_deletion.intersection(
                    file['path'] for file in files
                ))
                total_selected += (after - before)
        
        self.display.print_status(f"Auto-selected {total_selected} files for deletion", Fore.GREEN)
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_delete(self) -> None:
        """Handle delete option."""
        if not self.analyzer.selected_for_deletion:
            self.display.print_status("No files selected for deletion", Fore.YELLOW)
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Show confirmation
        print(f"\n{Fore.RED}{Style.BRIGHT}WARNING: You are about to delete "
              f"{len(self.analyzer.selected_for_deletion)} files.{Style.RESET_ALL}")
        print(f"{Fore.RED}This action cannot be undone.{Style.RESET_ALL}")
        
        if self.analyzer.dry_run:
            print(f"\n{Fore.YELLOW}DRY RUN MODE: No files will actually be deleted.{Style.RESET_ALL}")
        
        # Ask for confirmation
        confirm = input(f"\n{Fore.RED}Type 'DELETE' to confirm: {Style.RESET_ALL}")
        
        if confirm.upper() != "DELETE":
            self.display.print_status("Deletion cancelled", Fore.YELLOW)
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        # Delete files
        result = self.analyzer.delete_selected_files()
        
        # Show summary
        saved_space_str = self.display.format_file_size(result['saved_space'])
        if self.analyzer.dry_run:
            self.display.print_status(
                f"DRY RUN: Would have deleted {result['deleted']} files "
                f"(saved {saved_space_str}), {result['failed']} failed",
                Fore.GREEN
            )
        else:
            self.display.print_status(
                f"Deleted {result['deleted']} files "
                f"(saved {saved_space_str}), {result['failed']} failed",
                Fore.GREEN
            )
        
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_clear(self) -> None:
        """Handle clear selections option."""
        self.analyzer.selected_for_deletion.clear()
        self.display.print_status("All selections cleared", Fore.YELLOW)
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}") 