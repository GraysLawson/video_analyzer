import time
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
import os
import humanize

from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich import box

class DisplayManager:
    """Base class for display management in the Video Analyzer application.
    
    This class is extended by various mixins to provide specialized display functionality
    such as charts, tables, progress tracking, and interactive displays.
    """
    
    # Constants used by the mixins
    MAX_LOG_LINES = 15
    GRAPH_WIDTH = 60
    GRAPH_HEIGHT = 15
    
    def __init__(self):
        """Initialize the display manager with default values."""
        self.console = Console()
        self.total_files = 0
        self.processed_files = 0
        self.processing_log = []
        self.duplicate_groups = 0
        self.total_size = 0
        self.potential_savings = 0
        self.selected_size = 0
        self.start_time = datetime.now()
        self.file_types = defaultdict(int)
        self.resolutions = defaultdict(int)
        self.codec_counts = defaultdict(int)
        self.duplicate_resolutions = defaultdict(int)
        self.current_file = None 