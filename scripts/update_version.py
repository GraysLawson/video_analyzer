#!/usr/bin/env python3
"""
Script to update version information for the Video Analyzer.

This script updates the build number in the version.py file.
It can be used as a pre-commit hook or in a GitHub Actions workflow
to automatically increment the version on each commit.
"""

import os
import sys
import datetime
import re
import argparse
import subprocess

# Path to the version file relative to the project root
VERSION_FILE_PATH = "video_analyzer/version.py"

def get_git_info():
    """Get information about the git repository."""
    try:
        # Get the current commit hash
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], universal_newlines=True
        ).strip()
        
        # Get the current branch name
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], universal_newlines=True
        ).strip()
        
        # Get commit date
        commit_date = subprocess.check_output(
            ["git", "show", "-s", "--format=%ci", "HEAD"], universal_newlines=True
        ).strip()
        
        # Get commit count
        commit_count = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"], universal_newlines=True
        ).strip()
        
        return {
            "commit_hash": commit_hash,
            "branch": branch,
            "commit_date": commit_date,
            "commit_count": commit_count
        }
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None

def update_version(version_file, increment_type=None, new_version=None):
    """Update the version information in the version file.
    
    Args:
        version_file: Path to the version.py file
        increment_type: Type of increment: 'major', 'minor', or 'patch'
        new_version: Explicitly set a new version string (overrides increment_type)
        
    Returns:
        dict: Updated version information
    """
    # Read the current version file
    with open(version_file, 'r') as f:
        content = f.read()
    
    # Extract current version information
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    build_match = re.search(r'__build__\s*=\s*["\']([^"\']+)["\']', content)
    
    if not version_match or not build_match:
        print("Error: Could not find version information in the file.")
        sys.exit(1)
    
    current_version = version_match.group(1)
    current_build = build_match.group(1)
    
    # Parse the current version
    version_parts = current_version.split('.')
    if len(version_parts) != 3:
        print(f"Error: Invalid version format: {current_version}")
        sys.exit(1)
    
    major, minor, patch = map(int, version_parts)
    
    # Get git information
    git_info = get_git_info()
    
    # Increment version if specified
    if new_version:
        # Use explicitly provided version
        updated_version = new_version
    elif increment_type:
        if increment_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif increment_type == 'minor':
            minor += 1
            patch = 0
        elif increment_type == 'patch':
            patch += 1
        else:
            print(f"Error: Invalid increment type: {increment_type}")
            sys.exit(1)
        
        updated_version = f"{major}.{minor}.{patch}"
    else:
        # Keep the current version
        updated_version = current_version
    
    # Generate a new build number based on date and commit count
    today = datetime.datetime.now()
    commit_number = git_info["commit_count"] if git_info else "0"
    
    # Format: YYYYMMDD + commit count (padded to 3 digits)
    updated_build = f"{today.strftime('%Y%m%d')}{int(commit_number):03d}"
    
    # Update the release date
    release_date = today.strftime('%Y-%m-%d')
    
    # Update the content with new version info
    updated_content = re.sub(
        r'__version__\s*=\s*["\']([^"\']+)["\']',
        f'__version__ = "{updated_version}"',
        content
    )
    updated_content = re.sub(
        r'__build__\s*=\s*["\']([^"\']+)["\']',
        f'__build__ = "{updated_build}"',
        updated_content
    )
    updated_content = re.sub(
        r'__release_date__\s*=\s*["\']([^"\']+)["\']',
        f'__release_date__ = "{release_date}"',
        updated_content
    )
    
    # Write the updated content back to the file
    with open(version_file, 'w') as f:
        f.write(updated_content)
    
    print(f"Updated version: {updated_version} (build {updated_build})")
    
    return {
        "version": updated_version,
        "build": updated_build,
        "release_date": release_date
    }

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update Video Analyzer version information")
    parser.add_argument(
        "--increment", 
        choices=["major", "minor", "patch"],
        help="Increment the version (major, minor, or patch)"
    )
    parser.add_argument(
        "--version",
        help="Set a specific version (format: X.Y.Z)"
    )
    
    args = parser.parse_args()
    
    # Find the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Path to the version file
    version_file = os.path.join(project_root, VERSION_FILE_PATH)
    
    if not os.path.isfile(version_file):
        print(f"Error: Version file not found at {version_file}")
        sys.exit(1)
    
    # Update the version
    update_version(version_file, args.increment, args.version)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 