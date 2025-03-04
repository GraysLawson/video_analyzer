# Video Analyzer

A Python tool to find and manage duplicate video files with different resolutions.

## Features

- Scans directories for video files
- Detects duplicate videos with different resolutions
- Interactive menu system for managing duplicates
- Auto-select lower resolution files for deletion
- Support for both movies and TV shows
- Dry-run mode to preview changes

## Requirements

- Python 3.7 or higher
- ffprobe (part of ffmpeg) installed and available in PATH

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd video-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package:
```bash
pip install -e .
```

## Usage

Basic usage:
```bash
video-analyzer /path/to/videos
```

With dry-run mode (no actual deletion):
```bash
video-analyzer --dry-run /path/to/videos
```

Save results to a file:
```bash
video-analyzer --output results.json /path/to/videos
```

## Interactive Menu System

The tool provides an interactive menu system for managing duplicates:

1. Main Menu:
   - List of content (TV shows/movies) with duplicates
   - Options to auto-select files or manage specific content

2. Content Menu (TV Show):
   - List of seasons with duplicates
   - List of all episodes with duplicates
   - Options to manage specific episodes or entire seasons

3. Content Menu (Movie):
   - List of available versions with resolution and quality info
   - Options to select specific versions for deletion

4. Episode Menu:
   - List of available versions for the episode
   - Options to select specific versions for deletion

## License

This project is licensed under the MIT License - see the LICENSE file for details.