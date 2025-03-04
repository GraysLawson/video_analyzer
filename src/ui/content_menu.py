from typing import Dict, List, Tuple
from tabulate import tabulate
from colorama import Fore, Style, Back
from ..utils.display import DisplayUtils
from ..core.analyzer import VideoAnalyzer
import os

class ContentMenu:
    def __init__(self, analyzer: VideoAnalyzer, content_key: str):
        self.analyzer = analyzer
        self.content_key = content_key
        self.display = DisplayUtils()
        self.content_dups = self.analyzer.duplicates[content_key]
        self.is_tv_show = content_key.startswith("TV:")
    
    def show_menu(self) -> None:
        """Display the content menu and handle user input."""
        while True:
            self.display.clear_screen()
            
            # Show header
            icon = "📺" if self.is_tv_show else "🎬"
            content_type = "TV Show" if self.is_tv_show else "Movie"
            print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} {icon} Managing {content_type}: "
                  f"{self.content_key[4:]} {Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}\n")
            
            if self.is_tv_show:
                self._show_tv_show_menu()
            else:
                self._show_movie_menu()
            
            # Get user choice
            choice = input(f"\n{Fore.GREEN}Enter your choice: {Style.RESET_ALL}")
            
            if not self._handle_choice(choice):
                break
    
    def _show_tv_show_menu(self) -> None:
        """Show menu for TV show content."""
        # Group by season
        by_season = self._group_by_season()
        seasons = sorted(by_season.keys())
        
        # Show seasons summary
        print(f"{Fore.YELLOW}{Style.BRIGHT}Seasons with duplicates:{Style.RESET_ALL}")
        season_table = self._create_season_table(by_season, seasons)
        print(tabulate(season_table, headers=["#", "Season", "Episodes", "Files", "Status"],
                      tablefmt="simple"))
        
        # Show all episodes
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}All episodes with duplicates:{Style.RESET_ALL}")
        episode_table = self._create_episode_table()
        print(tabulate(episode_table, headers=["#", "Episode", "Files", "Status"],
                      tablefmt="simple"))
        
        # Show options
        print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
        options_table = [
            [f"{Fore.CYAN}1-{len(self.content_dups)}{Style.RESET_ALL}", "Manage specific episode"],
            [f"{Fore.CYAN}s1-s{len(seasons)}{Style.RESET_ALL}", "Manage all episodes in a season"],
            [f"{Fore.CYAN}a{Style.RESET_ALL}", "Auto-select lower resolution files for all episodes"],
            [f"{Fore.CYAN}c{Style.RESET_ALL}", "Clear selections for this show"],
            [f"{Fore.CYAN}b{Style.RESET_ALL}", "Back to main menu"]
        ]
        print(tabulate(options_table, tablefmt="plain"))
    
    def _show_movie_menu(self) -> None:
        """Show menu for movie content."""
        print(f"{Fore.YELLOW}{Style.BRIGHT}Available versions:{Style.RESET_ALL}")
        
        # There's only one unique_id for a movie
        unique_id = list(self.content_dups.keys())[0]
        files = self.content_dups[unique_id]
        
        # Sort files by resolution (highest to lowest)
        sorted_files = sorted(files, key=lambda x: (x['height'], x['width']), reverse=True)
        
        # Create table
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
            [f"{Fore.CYAN}c{Style.RESET_ALL}", "Clear selections for this movie"],
            [f"{Fore.CYAN}b{Style.RESET_ALL}", "Back to main menu"]
        ]
        print(tabulate(options_table, tablefmt="plain"))
    
    def _group_by_season(self) -> Dict[int, List[Tuple[str, List[Dict]]]]:
        """Group episodes by season."""
        by_season = {}
        for unique_id, files in self.content_dups.items():
            season = files[0]['season']  # All files in this unique_id have the same season
            if season not in by_season:
                by_season[season] = []
            by_season[season].append((unique_id, files))
        return by_season
    
    def _create_season_table(self, by_season: Dict, seasons: List[int]) -> List[List[str]]:
        """Create table data for seasons summary."""
        season_table = []
        for i, season in enumerate(seasons, 1):
            episodes = len(by_season[season])
            total_files = sum(len(files) for _, files in by_season[season])
            
            # Count selected files in this season
            selected = sum(
                1 for _, files in by_season[season]
                for file in files
                if file['path'] in self.analyzer.selected_for_deletion
            )
            
            status = (f"{Fore.GREEN}[{selected}/{total_files} selected]{Style.RESET_ALL}"
                     if selected > 0 else f"{Fore.YELLOW}[0 selected]{Style.RESET_ALL}")
            
            season_table.append([
                f"{Fore.CYAN}s{i}{Style.RESET_ALL}",
                f"Season {season}",
                f"{episodes} episodes",
                f"{total_files} files",
                status
            ])
        return season_table
    
    def _create_episode_table(self) -> List[List[str]]:
        """Create table data for episodes list."""
        episode_table = []
        for i, (unique_id, files) in enumerate(sorted(
            self.content_dups.items(),
            key=lambda x: (x[1][0]['season'], x[1][0]['episode'])
        ), 1):
            episode_info = files[0]['episode_info']
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
        elif choice.lower().startswith('s') and self.is_tv_show:
            self._handle_season_choice(choice)
        else:
            self._handle_numeric_choice(choice)
        return True
    
    def _handle_auto_select(self) -> None:
        """Handle auto-select option."""
        for files in self.content_dups.values():
            self.analyzer.auto_select_files(files)
        
        self.display.print_status("Auto-selected lower resolution files", Fore.GREEN)
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_clear(self) -> None:
        """Handle clear selections option."""
        cleared = 0
        for files in self.content_dups.values():
            for file in files:
                if file['path'] in self.analyzer.selected_for_deletion:
                    self.analyzer.selected_for_deletion.remove(file['path'])
                    cleared += 1
        
        self.display.print_status(f"Cleared {cleared} selections", Fore.YELLOW)
        input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_season_choice(self, choice: str) -> None:
        """Handle season selection choice."""
        try:
            by_season = self._group_by_season()
            seasons = sorted(by_season.keys())
            season_idx = int(choice[1:]) - 1
            
            if 0 <= season_idx < len(seasons):
                season = seasons[season_idx]
                from .season_menu import SeasonMenu
                season_menu = SeasonMenu(self.analyzer, self.content_key, season, by_season[season])
                season_menu.show_menu()
            else:
                self.display.print_status(f"Invalid season option: {choice}", Fore.RED)
                input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        except ValueError:
            self.display.print_status(f"Invalid option: {choice}", Fore.RED)
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_numeric_choice(self, choice: str) -> None:
        """Handle numeric choice for episode/file selection."""
        try:
            opt_num = int(choice)
            if self.is_tv_show:
                self._handle_episode_selection(opt_num)
            else:
                self._handle_movie_file_selection(opt_num)
        except ValueError:
            self.display.print_status(f"Invalid option: {choice}", Fore.RED)
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_episode_selection(self, opt_num: int) -> None:
        """Handle episode selection for TV shows."""
        sorted_episodes = sorted(
            self.content_dups.items(),
            key=lambda x: (x[1][0]['season'], x[1][0]['episode'])
        )
        
        if 1 <= opt_num <= len(sorted_episodes):
            _, files = sorted_episodes[opt_num - 1]
            from .episode_menu import EpisodeMenu
            episode_menu = EpisodeMenu(self.analyzer, files)
            episode_menu.show_menu()
        else:
            self.display.print_status(f"Invalid episode option: {opt_num}", Fore.RED)
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _handle_movie_file_selection(self, opt_num: int) -> None:
        """Handle file selection for movies."""
        unique_id = list(self.content_dups.keys())[0]
        files = sorted(
            self.content_dups[unique_id],
            key=lambda x: (x['height'], x['width']),
            reverse=True
        )
        
        if 1 <= opt_num <= len(files):
            file = files[opt_num - 1]
            if file['path'] in self.analyzer.selected_for_deletion:
                self.analyzer.selected_for_deletion.remove(file['path'])
                self.display.print_status(f"Unselected: {os.path.basename(file['path'])}", Fore.YELLOW)
            else:
                self.analyzer.selected_for_deletion.add(file['path'])
                self.display.print_status(f"Selected for deletion: {os.path.basename(file['path'])}", Fore.GREEN)
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        else:
            self.display.print_status(f"Invalid file option: {opt_num}", Fore.RED)
            input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}") 