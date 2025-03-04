import os
import platform
import subprocess
import sys
from PyInstaller.__main__ import run as pyinstaller_run

def run_command(command):
    """Run a command and return its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        return False

def build_executable():
    """Build the executable for the current platform."""
    system = platform.system().lower()
    
    # Install development dependencies
    print("Installing development dependencies...")
    if not run_command("pip install -e .[dev]"):
        return False

    print(f"\nBuilding executable for {system}...")
    
    # Define PyInstaller options
    options = [
        'video_analyzer/__main__.py',  # Script to build
        '--name=video-analyzer',       # Output name
        '--onefile',                   # Create single executable
        '--clean',                     # Clean cache
        '--noconsole',                # No console window (Windows only)
        '--add-data=README.md:.',     # Include README
        '--icon=NONE'                 # No icon for now
    ]
    
    if system == "windows":
        options.append('--console')  # Show console on Windows
        output_name = "video-analyzer.exe"
    elif system == "darwin":
        output_name = "video-analyzer-macos"
    else:
        output_name = "video-analyzer"
    
    try:
        pyinstaller_run(options)
        
        # Create dist directory if it doesn't exist
        os.makedirs("dist", exist_ok=True)
        
        print("\nBuild completed successfully!")
        print("\nExecutable location:")
        print(f"  dist/{output_name}")
        
        return True
    except Exception as e:
        print(f"\nError during build: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if build_executable():
        print("\nYou can now distribute the executable from the 'dist' directory.")
    else:
        print("\nBuild failed. Please check the error messages above.", file=sys.stderr)
        sys.exit(1) 