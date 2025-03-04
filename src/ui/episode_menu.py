from typing import Dict, List
from tabulate import tabulate
from colorama import Fore, Style, Back
from ..utils.display import DisplayUtils
from ..core.analyzer import VideoAnalyzer
import os

class EpisodeMenu:
    def __init__(self, analyzer: VideoAnalyzer, files: List[Dict]):
        self.analyzer = analyzer
        self.files = files
        self.display = DisplayUtils()
    
    def show_menu(self) -> None:
        """Display the episode menu and handle user input."""
        while True:
            self.display.clear_screen()
            
            # Get episode info
            episode_info = self.files[0]['episode_info']
            content_key = self.files[0]['content_key']
            
            # Show header
            print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} 📺 Managing {content_key[4:]} - "
                  f"{episode_info} {Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}\n")
            
            # Show available versions
            print(f"{Fore.YELLOW}{Style.BRIGHT}Available versions:{Style.RESET_ALL}")
            
            # Sort files by resolution (highest to lowest)
            sorted_files = sorted(self.files, key=lambda x: (x['height'], x['width']), reverse=True)
            
            file_table = []
            for i, file in enumerate(sorted_files, 1):
                selected = "✓" if file['path'] in self.analyzer.selected_for_deletion else " "
                file_table.append(self.display.format_table_row(file, i, selected))
            
            print(tabulate(file_table,
                         headers=["#", "Sel", "Resolution", "Bitrate", "Codec", "Size", "Filename"],
                         tablefmt="simple"))
            
            # Show options
            print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
            options_table = [
                [f"{Fore.CYAN}1-{len(sorted_files)}{Style.RESET_ALL}", "Toggle selection for a file"],
                [f"{Fore.CYAN}a{Style.RESET_ALL}", "Auto-select lower resolution files"],
                [f"{Fore.CYAN}c{Style.RESET_ALL}", "Clear selections for this episode"],
                [f"{Fore.CYAN}b{Style.RESET_ALL}", "Back to previous menu"]
            ]
            print(tabulate(options_table, tablefmt="plain"))
            
            # Get user choice
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            if not self._handle_choice(choice):
                break
    
    def _handle_choice(self, choice: str) -> bool:
        """Handle user menu choice. Returns False if should exit menu."""
        if choice.lower() == 'b':
            return False
        elif choice.lower() == 'a':
            self._handle_auto_select()
        elif choice.lower() == 'c':
            self._handle_clear()
        else:
            self._handle_numeric_choice(choice)
        return True
    
    def _handle_auto_select(self) -> None:
        """Handle auto-select option."""
        self.analyzer.auto_select_files(self.files)
        self.display.print_status("Auto-selected lower resolution files", Fore.GREEN)
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_clear(self) -> None:
        """Handle clear selections option."""
        cleared = 0
        for file in self.files:
            if file['path'] in self.analyzer.selected_for_deletion:
                self.analyzer.selected_for_deletion.remove(file['path'])
                cleared += 1
        
        self.display.print_status(f"Cleared {cleared} selections", Fore.YELLOW)
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_numeric_choice(self, choice: str) -> None:
        """Handle numeric choice for file selection."""
        try:
            opt_num = int(choice)
            sorted_files = sorted(self.files, key=lambda x: (x['height'], x['width']), reverse=True)
            
            if 1 <= opt_num <= len(sorted_files):
                file = sorted_files[opt_num - 1]
                if file['path'] in self.analyzer.selected_for_deletion:
                    self.analyzer.selected_for_deletion.remove(file['path'])
                    self.display.print_status(f"Unselected: {os.path.basename(file['path'])}",
                                           Fore.YELLOW)
                else:
                    self.analyzer.selected_for_deletion.add(file['path'])
                    self.display.print_status(f"Selected for deletion: {os.path.basename(file['path'])}",
                                           Fore.GREEN)
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            else:
                self.display.print_status(f"Invalid file option: {opt_num}", Fore.RED)
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            self.display.print_status(f"Invalid option: {choice}", Fore.RED)
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}") 