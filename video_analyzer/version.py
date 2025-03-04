"""
Video Analyzer version information.

This module contains version information and metadata for the Video Analyzer application.
It is used by both the application itself and the installation script to track versions
and determine if updates are available.
"""

import datetime

__version__ = "1.0.0"  # Major.Minor.Patch
__build__ = "20230915001"  # YYYYMMDDNNN format where NNN is build number that day
__release_date__ = "2023-09-15"  # YYYY-MM-DD

# Additional metadata
__author__ = "Video Analyzer Team"
__license__ = "MIT"
__status__ = "stable"

def get_version_info():
    """Return dictionary with all version information."""
    return {
        "version": __version__,
        "build": __build__,
        "release_date": __release_date__,
        "author": __author__,
        "license": __license__,
        "status": __status__
    }

def get_version_string():
    """Return a formatted version string."""
    return f"v{__version__} (build {__build__})"

def is_newer_version(other_version, other_build):
    """Compare versions to determine if the other version is newer.
    
    Args:
        other_version (str): Version string to compare (x.y.z format)
        other_build (str): Build number to compare
        
    Returns:
        bool: True if other_version is newer than current version
    """
    # First compare semantic version
    current_parts = [int(x) for x in __version__.split('.')]
    other_parts = [int(x) for x in other_version.split('.')]
    
    # Compare major, minor, patch
    for current, other in zip(current_parts, other_parts):
        if other > current:
            return True
        elif other < current:
            return False
    
    # If semantic versions are equal, compare build number
    return other_build > __build__ 