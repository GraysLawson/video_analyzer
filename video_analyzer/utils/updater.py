"""
Update utility for Video Analyzer.

This module provides functionality to check for updates on GitHub and
apply them to the current installation.
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
import requests
from rich.console import Console
from rich.progress import Progress
from ..version import __version__, __build__, is_newer_version

# GitHub repository information
GITHUB_REPO = "your-username/video-analyzer"  # Replace with actual repository
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}"

class UpdateChecker:
    """Class to check for and apply updates from GitHub."""
    
    def __init__(self, console=None):
        """Initialize the update checker.
        
        Args:
            console: Rich Console instance for output
        """
        self.console = console or Console()
        self.temp_dir = None
    
    def check_for_updates(self):
        """Check if updates are available on GitHub.
        
        Returns:
            dict: Update information or None if no updates available
        """
        self.console.print("[cyan]Checking for updates...[/cyan]")
        
        try:
            # Get latest release information
            response = requests.get(f"{GITHUB_API_URL}/releases/latest", timeout=10)
            response.raise_for_status()
            
            release_info = response.json()
            latest_version = release_info.get("tag_name", "").lstrip("v")
            latest_build = None
            
            # Try to extract build number from release body
            body = release_info.get("body", "")
            for line in body.splitlines():
                if line.startswith("Build:"):
                    latest_build = line.split(":", 1)[1].strip()
                    break
            
            # If no build number found, use release id as fallback
            if not latest_build:
                latest_build = str(release_info.get("id", "0"))
            
            # Check if this is a newer version
            if latest_version and latest_build and is_newer_version(latest_version, latest_build):
                self.console.print(f"[green]New version available: v{latest_version} (build {latest_build})[/green]")
                return {
                    "version": latest_version,
                    "build": latest_build,
                    "url": release_info.get("html_url"),
                    "assets": release_info.get("assets", []),
                    "published_at": release_info.get("published_at")
                }
            else:
                self.console.print("[green]You have the latest version.[/green]")
                return None
                
        except requests.RequestException as e:
            self.console.print(f"[red]Error checking for updates: {str(e)}[/red]")
            return None
    
    def download_update(self, update_info):
        """Download update assets.
        
        Args:
            update_info: Update information dictionary
            
        Returns:
            str: Path to the downloaded files or None if failed
        """
        if not update_info or not update_info.get("assets"):
            self.console.print("[yellow]No update assets found.[/yellow]")
            return None
        
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="video_analyzer_update_")
        
        try:
            with Progress() as progress:
                task = progress.add_task("[cyan]Downloading update...", total=len(update_info["assets"]))
                
                for asset in update_info["assets"]:
                    asset_url = asset.get("browser_download_url")
                    asset_name = asset.get("name")
                    
                    if asset_url and asset_name:
                        # Download the asset
                        response = requests.get(asset_url, stream=True, timeout=60)
                        response.raise_for_status()
                        
                        # Save to the temporary directory
                        asset_path = os.path.join(self.temp_dir, asset_name)
                        with open(asset_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                    progress.advance(task)
                
            self.console.print(f"[green]Downloaded update to {self.temp_dir}[/green]")
            return self.temp_dir
            
        except Exception as e:
            self.console.print(f"[red]Error downloading update: {str(e)}[/red]")
            self._cleanup()
            return None
    
    def download_version_info(self):
        """Download just the version.py file to check for updates.
        
        Returns:
            dict: Version information or None if failed
        """
        try:
            response = requests.get(f"{GITHUB_RAW_URL}/main/video_analyzer/version.py", timeout=10)
            response.raise_for_status()
            
            # Extract version info from the file content
            version_info = {}
            for line in response.text.splitlines():
                if line.startswith("__version__"):
                    version_info["version"] = line.split("=")[1].strip().strip('"\'')
                elif line.startswith("__build__"):
                    version_info["build"] = line.split("=")[1].strip().strip('"\'')
            
            if version_info.get("version") and version_info.get("build"):
                return version_info
                
        except requests.RequestException as e:
            self.console.print(f"[yellow]Error fetching version info: {str(e)}[/yellow]")
        
        return None
    
    def apply_update(self, update_dir, install_path):
        """Apply the downloaded update to the installation.
        
        Args:
            update_dir: Directory with the update files
            install_path: Path to the installation
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not update_dir or not os.path.isdir(update_dir):
            self.console.print("[red]Update directory not found.[/red]")
            return False
        
        try:
            # Find the update archive (zip, tar.gz, etc.)
            archives = [f for f in os.listdir(update_dir) 
                      if f.endswith(('.zip', '.tar.gz', '.tgz'))]
            
            if not archives:
                self.console.print("[yellow]No update archive found.[/yellow]")
                return False
            
            archive_path = os.path.join(update_dir, archives[0])
            
            # Extract the archive and apply the update
            self.console.print("[cyan]Extracting update...[/cyan]")
            
            # Create a temp extraction directory
            extract_dir = os.path.join(self.temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            # Extract the archive
            if archive_path.endswith('.zip'):
                shutil.unpack_archive(archive_path, extract_dir, 'zip')
            else:
                shutil.unpack_archive(archive_path, extract_dir, 'gztar')
            
            # Find the source directory in the extracted files
            # It's likely a directory inside the extract_dir
            source_dir = extract_dir
            subdirs = [d for d in os.listdir(extract_dir) 
                     if os.path.isdir(os.path.join(extract_dir, d))]
            
            if subdirs:
                source_dir = os.path.join(extract_dir, subdirs[0])
                
            # Now copy the files to the installation path
            self.console.print("[cyan]Installing update...[/cyan]")
            self._copy_tree(source_dir, install_path)
            
            self.console.print("[green]Update successfully applied![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error applying update: {str(e)}[/red]")
            return False
        finally:
            self._cleanup()
    
    def _copy_tree(self, src, dst):
        """Copy a directory tree, similar to shutil.copytree but merges directories.
        
        Args:
            src: Source directory
            dst: Destination directory
        """
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            
            if os.path.isdir(s):
                os.makedirs(d, exist_ok=True)
                self._copy_tree(s, d)
            else:
                shutil.copy2(s, d)
    
    def _cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            except Exception as e:
                self.console.print(f"[yellow]Warning: Failed to clean up temporary files: {str(e)}[/yellow]")


def update_from_github(install_path, force=False):
    """Check for and apply updates from GitHub.
    
    Args:
        install_path: Path to the installation
        force: Force update even if not newer
        
    Returns:
        bool: True if updated, False otherwise
    """
    console = Console()
    updater = UpdateChecker(console)
    
    # Check for updates
    version_info = updater.download_version_info()
    
    # If no version info could be retrieved, exit
    if not version_info:
        console.print("[yellow]Could not retrieve version information from GitHub.[/yellow]")
        return False
    
    # Check if this is a newer version
    if not force and not is_newer_version(version_info["version"], version_info["build"]):
        console.print("[green]You have the latest version.[/green]")
        return False
    
    # Get full update information
    update_info = updater.check_for_updates()
    
    if not update_info and not force:
        return False
    
    # If no update info but we're forcing, create a minimal info dict
    if not update_info and force:
        update_info = {
            "version": version_info["version"],
            "build": version_info["build"],
            "assets": []
        }
    
    # Ask for confirmation
    if not console.input(
        f"[yellow]Do you want to update to version {version_info['version']} (build {version_info['build']})? [y/N]: [/yellow]"
    ).lower().startswith('y'):
        console.print("[yellow]Update cancelled.[/yellow]")
        return False
    
    # Download the update
    update_dir = updater.download_update(update_info)
    
    if not update_dir:
        # If there are no assets, try cloning the repository
        console.print("[cyan]No release assets found. Cloning repository instead...[/cyan]")
        
        try:
            # Create a temp directory for the clone
            clone_dir = tempfile.mkdtemp(prefix="video_analyzer_clone_")
            
            # Clone the repository
            result = subprocess.run(
                ["git", "clone", f"https://github.com/{GITHUB_REPO}.git", clone_dir],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            # Apply the update from the cloned repository
            return updater.apply_update(clone_dir, install_path)
            
        except subprocess.SubprocessError as e:
            console.print(f"[red]Error cloning repository: {str(e)}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Error during update: {str(e)}[/red]")
            return False
    
    # Apply the update
    return updater.apply_update(update_dir, install_path) 