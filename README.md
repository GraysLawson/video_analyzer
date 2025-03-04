# Video Analyzer

<div align="center">

![Video Analyzer Logo](https://img.shields.io/badge/Video%20Analyzer-v1.0-blue?style=for-the-badge&logo=video&logoColor=white)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20|%20macOS%20|%20Windows-green.svg)](https://github.com/GraysLawson/video_analyzer)

</div>

> Find and manage duplicate video files with different resolutions. Automatically identify duplicate videos and keep only the highest quality versions.

## ✨ Features

- 🔍 **Smart Detection**: Scan directories for video files and extract detailed metadata
- 🎥 **Duplicate Identification**: Identify duplicate videos even with different resolutions
- 📊 **Quality Comparison**: Compare video quality based on resolution, bitrate, and file size
- 🗑️ **Intelligent Selection**: Automatically select lower quality duplicates for removal
- 🔄 **Safe Operations**: Move files to backup location instead of deleting them
- 📋 **Interactive UI**: Modern, user-friendly menu for managing duplicate files
- 📈 **Visual Analytics**: Rich progress tracking, statistics, and data visualization
- 🔄 **Parallel Processing**: Efficiently analyze large video collections with multi-threading

## 📋 Compatibility

| Platform | Status | Requirements |
|----------|--------|--------------|
| Linux (Debian/Ubuntu) | ✅ Fully Supported | Python 3.7+, FFmpeg |
| Linux (RedHat/Fedora) | ✅ Fully Supported | Python 3.7+, FFmpeg |
| Linux (Arch) | ✅ Fully Supported | Python 3.7+, FFmpeg |
| macOS (Intel) | ✅ Fully Supported | Python 3.7+, FFmpeg |
| macOS (Apple Silicon) | ✅ Fully Supported | Python 3.7+, FFmpeg |
| Windows | ⚠️ Partial Support | Python 3.7+, FFmpeg in PATH |

## 🚀 Installation

### Quick Install Script (Recommended)

The easiest way to install Video Analyzer is using our provided install script, which supports Linux, macOS, and ARM devices:

```bash
# Download the installation script
curl -sSL https://raw.githubusercontent.com/GraysLawson/video_analyzer/main/install.sh -o install.sh

# Make it executable
chmod +x install.sh

# Run the installation script
./install.sh
```

The install script will:
- Detect your operating system and architecture
- Install required dependencies (Python, FFmpeg, etc.)
- Check for existing installations with options to update or repair
- Set up the application with your preferred settings
- Create necessary launcher scripts and symlinks

#### Installation Options

During installation, you can choose between:

1. **User Installation**: Installs in your home directory (~/.local/video-analyzer)
2. **System-wide Installation**: Installs for all users (/usr/local/share/video-analyzer)
3. **Python Package**: Standard Python package installation (recommended)
4. **Standalone Executable**: Creates a standalone binary (experimental)

### Manual Installation

If you prefer to install manually:

#### Prerequisites

- Python 3.7 or higher
- FFmpeg (for video metadata extraction)
- pip (Python package manager)

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

## 🔧 Usage

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

```bash
# Scan a specific directory in interactive mode
video-analyzer -d /path/to/videos

# Perform a dry run (no actual deletions)
video-analyzer -d /path/to/videos --dry-run

# Move duplicate files to a backup location instead of deleting
video-analyzer -d /path/to/videos -m /path/to/backup

# Run with custom similarity threshold in non-interactive mode
video-analyzer -d /path/to/videos -s 0.85 -n
```

## ⚠️ Troubleshooting

### Common Issues

#### 1. Module `rich.menu` not found

If you encounter this error:
```
ModuleNotFoundError: No module named 'rich.menu'
```

**Solution:**
- Run the installation script with the repair option (option 3)
- Or manually install the compatible version: `pip install rich==12.6.0`

#### 2. Missing FFmpeg

If you see errors related to FFmpeg:
```
FileNotFoundError: ffprobe not found. Please install ffmpeg.
```

**Solution:**
- Install FFmpeg using your package manager:
  - Debian/Ubuntu: `sudo apt-get install ffmpeg`
  - RedHat/Fedora: `sudo dnf install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

#### 3. Permission Errors

If you get permission errors when running the application:

**Solution:**
- For user installations, ensure the directory is writable
- For system-wide installations, run with sudo: `sudo video-analyzer`

#### 4. Windows-specific Modules Missing

If you see errors like:
```
ModuleNotFoundError: No module named 'msilib'
```

**Solution:**
- This is typically an incompatibility with Linux. Please reinstall the application or run the repair option.

### Installation Logs

The installation script creates detailed logs at:
```
/tmp/video-analyzer-install-TIMESTAMP.log
```

Check these logs if you encounter installation issues.

## 🛠️ Recent Improvements

- ✅ Improved installation script with multi-platform support
- ✅ Added repair functionality for fixing common issues
- ✅ Enhanced error handling and logging
- ✅ Fixed dependency issues with rich package versions
- ✅ Added system-wide installation option
- ✅ Improved performance with caching and parallel processing
- ✅ Enhanced duplicate detection algorithms
- ✅ Added option to move files instead of deletion

## 📊 How It Works

Video Analyzer uses sophisticated algorithms to:

1. Scan specified directories for video files
2. Extract rich metadata (resolution, bitrate, duration, codec, etc.) using FFmpeg
3. Group similar videos based on filename patterns and duration
4. Calculate similarity scores between potential duplicates
5. Rank videos in each group by quality metrics
6. Present results with interactive management options

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FFmpeg](https://ffmpeg.org/) for video metadata extraction
- [Rich](https://github.com/Textualize/rich) for beautiful terminal interfaces
- [Plotext](https://github.com/piccolomo/plotext) for terminal-based plotting