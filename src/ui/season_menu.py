from typing import Dict, List, Tuple
from tabulate import tabulate
from colorama import Fore, Style, Back
from ..utils.display import DisplayUtils
from ..core.analyzer import VideoAnalyzer

class SeasonMenu:
    def __init__(self, analyzer: VideoAnalyzer, content_key: str, season: int,
                 season_data: List[Tuple[str, List[Dict]]]):
        self.analyzer = analyzer
        self.content_key = content_key
        self.season = season
        self.season_data = season_data
        self.display = DisplayUtils()
    
    def show_menu(self) -> None:
        """Display the season menu and handle user input."""
        while True:
            self.display.clear_screen()
            
            # Show header
            print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} 📺 Managing {self.content_key[4:]} - "
                  f"Season {self.season} {Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}\n")
            
            # Show episodes with duplicates
            print(f"{Fore.YELLOW}{Style.BRIGHT}Episodes with duplicates:{Style.RESET_ALL}")
            
            episode_table = self._create_episode_table()
            print(tabulate(episode_table, headers=["#", "Episode", "Files", "Status"],
                         tablefmt="simple"))
            
            # Show options
            print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
            options_table = [
                [f"{Fore.CYAN}1-{len(self.season_data)}{Style.RESET_ALL}", "Manage specific episode"],
                [f"{Fore.CYAN}a{Style.RESET_ALL}", "Auto-select lower resolution files"],
                [f"{Fore.CYAN}c{Style.RESET_ALL}", "Clear selections for this season"],
                [f"{Fore.CYAN}b{Style.RESET_ALL}", "Back to show menu"]
            ]
            print(tabulate(options_table, tablefmt="plain"))
            
            # Get user choice
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            if not self._handle_choice(choice):
                break
    
    def _create_episode_table(self) -> List[List[str]]:
        """Create table data for episodes list."""
        episode_table = []
        for i, (_, files) in enumerate(sorted(
            self.season_data,
            key=lambda x: x[1][0]['episode']
        ), 1):
            episode_info = files[0]['episode_info']
            episode_num = files[0]['episode']
            num_files = len(files)
            
            # Count selected files in this episode
            selected = sum(1 for file in files if file['path'] in self.analyzer.selected_for_deletion)
            
            status = (f"{Fore.GREEN}[{selected}/{num_files} selected]{Style.RESET_ALL}"
                     if selected > 0 else f"{Fore.YELLOW}[0 selected]{Style.RESET_ALL}")
            
            episode_table.append([
                f"{Fore.CYAN}{i}{Style.RESET_ALL}",
                episode_info,
                f"{num_files} files",
                status
            ])
        return episode_table
    
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
        for _, files in self.season_data:
            self.analyzer.auto_select_files(files)
        
        self.display.print_status(f"Auto-selected lower resolution files for season {self.season}",
                                Fore.GREEN)
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_clear(self) -> None:
        """Handle clear selections option."""
        cleared = 0
        for _, files in self.season_data:
            for file in files:
                if file['path'] in self.analyzer.selected_for_deletion:
                    self.analyzer.selected_for_deletion.remove(file['path'])
                    cleared += 1
        
        self.display.print_status(f"Cleared {cleared} selections", Fore.YELLOW)
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_numeric_choice(self, choice: str) -> None:
        """Handle numeric choice for episode selection."""
        try:
            opt_num = int(choice)
            sorted_episodes = sorted(self.season_data, key=lambda x: x[1][0]['episode'])
            
            if 1 <= opt_num <= len(sorted_episodes):
                _, files = sorted_episodes[opt_num - 1]
                from .episode_menu import EpisodeMenu
                episode_menu = EpisodeMenu(self.analyzer, files)
                episode_menu.show_menu()
            else:
                self.display.print_status(f"Invalid episode option: {opt_num}", Fore.RED)
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            self.display.print_status(f"Invalid option: {choice}", Fore.RED)
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}") 