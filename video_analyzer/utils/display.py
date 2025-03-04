import time
from typing import Dict, List, Optional
from colorama import Fore, Style, Back
import os
import humanize
import plotext as plt
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich import box
from collections import defaultdict
from rich.logging import RichHandler
from rich.console import Group
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from datetime import datetime, timedelta

# Number of lines to keep in the scrolling log
MAX_LOG_LINES = 15
# Graph styling constants
GRAPH_WIDTH = 60
GRAPH_HEIGHT = 15

# Import all components
from .display_utils import DisplayUtils
from .basic_display import DisplayManager as BaseDisplayManager
from .chart_display import ChartDisplayMixin
from .table_display import TableDisplayMixin
from .interactive_display import InteractiveDisplayMixin
from .progress_display import ProgressDisplayMixin

# Define a new DisplayManager with proper inheritance instead of modifying __bases__
class DisplayManager(ChartDisplayMixin, TableDisplayMixin, InteractiveDisplayMixin, ProgressDisplayMixin, BaseDisplayManager):
    """DisplayManager combining all display functionality through proper inheritance."""
    pass

# Re-export the classes
__all__ = ['DisplayUtils', 'DisplayManager'] 