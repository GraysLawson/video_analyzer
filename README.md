# Video Analyzer

Find and manage duplicate video files with different resolutions. Automatically identify duplicate videos and keep only the highest quality versions.

## Features

- 🔍 Scan directories for video files and extract metadata
- 🎥 Identify duplicate videos with different resolutions
- 📊 Compare video quality based on resolution, bitrate, and file size
- 🗑️ Automatically select lower quality duplicates for removal
- 🔄 Move files to backup location instead of deleting them
- 📋 Interactive menu for managing duplicate files
- 📈 Visual progress tracking and statistics

## Installation

### Quick Install Script (Linux, macOS, ARM)

The easiest way to install Video Analyzer is using our provided install script:

```bash
# Download the installation script
curl -sSL https://raw.githubusercontent.com/GraysLawson/video_analyzer/main/install.sh -o install.sh

# Make it executable
chmod +x install.sh

# Run the installation script
./install.sh
```

The install script will guide you through the installation process interactively and set up Video Analyzer based on your preferences.

### Manual Installation

If you prefer to install manually, you can follow these steps:

#### Prerequisites

- Python 3.7 or higher
- FFmpeg (for video metadata extraction)

#### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/GraysLawson/video_analyzer.git
   cd video_analyzer
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   
   # On Linux/macOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

4. Run Video Analyzer:
   ```bash
   python -m video_analyzer
   ```

### Building a Standalone Executable

You can build a standalone executable that doesn't require Python to be installed:

```bash
python build.py
```

The executable will be created in the `dist` directory.

## Usage

### Interactive Mode

Run Video Analyzer without any arguments to start in interactive mode:

```bash
video-analyzer
```

You'll be guided through the setup process and presented with an interactive menu for managing duplicate videos.

### Command Line Options

```
usage: video-analyzer [-h] [-d DIRECTORY] [-l LOG] [-s SIMILARITY] [--dry-run] [-m MOVE_TO] [-n]

Video Analyzer - Find and manage duplicate video files

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Directory to scan for video files
  -l LOG, --log LOG     Log file path
  -s SIMILARITY, --similarity SIMILARITY
                        Similarity threshold (0.0-1.0)
  --dry-run             Perform a dry run (no deletions)
  -m MOVE_TO, --move-to MOVE_TO
                        Move files instead of deleting them
  -n, --non-interactive
                        Run in non-interactive mode
```

### Examples

Scan a specific directory and run in non-interactive mode:
```bash
video-analyzer -d /path/to/videos -n
```

Perform a dry run (no actual deletions):
```bash
video-analyzer -d /path/to/videos --dry-run
```

Move duplicate files to a backup location instead of deleting:
```bash
video-analyzer -d /path/to/videos -m /path/to/backup
```

## How It Works

Video Analyzer works by:

1. Scanning the specified directory for video files
2. Extracting metadata (resolution, bitrate, duration, etc.) using FFmpeg
3. Grouping similar videos based on filename and duration
4. Calculating similarity scores between potential duplicates
5. Identifying the highest quality version of each video
6. Allowing you to manage duplicate files

The application uses several criteria to determine if videos are duplicates:
- Similar durations (within a few seconds)
- Similar filenames (after removing quality indicators like "1080p", "720p", etc.)
- Compatible resolutions and bitrates (higher resolution should have higher bitrate)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FFmpeg](https://ffmpeg.org/) for video metadata extraction
- [Rich](https://github.com/Textualize/rich) for beautiful terminal interfaces