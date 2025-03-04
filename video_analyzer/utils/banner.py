"""Banner display utilities for Video Analyzer."""

from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich import box
from .. import __version__, __author__, __email__, __social__

def show_banner():
    """Display a beautiful startup banner with author information."""
    console = Console()
    
    # Create the main title
    title = (
        "[bold cyan]Video Analyzer[/bold cyan]\n"
        "[dim]A powerful tool for managing duplicate videos[/dim]"
    )
    
    # Create the version and author info
    info = (
        f"[bold]Version:[/bold] [yellow]{__version__}[/yellow]\n"
        f"[bold]Author:[/bold]  [blue]{__author__}[/blue]\n"
        f"[bold]Email:[/bold]   [green]{__email__}[/green]\n"
        f"[bold]Social:[/bold]  [cyan]{__social__}[/cyan]"
    )
    
    # Create the panel
    panel = Panel(
        Align.center(f"{title}\n\n{info}"),
        box=box.ROUNDED,
        border_style="bright_blue",
        padding=(1, 2),
        title="[bold yellow]Welcome![/bold yellow]",
        subtitle="[dim]Press any key to continue...[/dim]"
    )
    
    # Clear screen and show banner
    console.clear()
    console.print("\n")
    console.print(panel)
    console.print("\n") 