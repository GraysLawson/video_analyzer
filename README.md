# Video Analyzer

A powerful tool for finding and managing duplicate video files with different resolutions. This tool helps you identify duplicate videos, compare their quality, and manage storage space efficiently.

## Features

- 🔍 Smart duplicate detection using multiple criteria:
  - Video duration matching
  - Resolution comparison
  - Bitrate analysis
  - File size consideration
- 📊 Beautiful terminal UI with real-time statistics
- 📈 Storage analysis visualization
- 🚀 Parallel processing for faster scanning
- 📝 Comprehensive logging system
- ⚡ Efficient caching mechanism
- 🎯 Configurable similarity threshold
- 🔒 Safe deletion with dry-run option

## Project Structure

```
video_analyzer/
├── video_analyzer/        # Main package directory
│   ├── __init__.py       # Package initialization
│   ├── __main__.py       # Entry point
│   ├── core/             # Core functionality
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   └── video_metadata.py
│   ├── ui/               # User interface components
│   │   ├── __init__.py
│   │   └── main_menu.py
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── display.py
├── setup.py              # Package configuration
├── requirements.txt      # Dependencies
└── README.md            # Documentation
```

## Installation

### Option 1: Standalone Executable (Recommended)

1. Download the latest release for your platform:
   - [Windows (video-analyzer.exe)](https://github.com/yourusername/video_analyzer/releases/latest/download/video-analyzer.exe)
   - [Linux (video-analyzer)](https://github.com/yourusername/video_analyzer/releases/latest/download/video-analyzer)
   - [macOS (video-analyzer)](https://github.com/yourusername/video_analyzer/releases/latest/download/video-analyzer-macos)

2. Install FFmpeg:
   - **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
   - **Linux**: Run `sudo apt-get install ffmpeg`
   - **MacOS**: Run `brew install ffmpeg`

3. Run the program:
   - **Windows**: Double-click `video-analyzer.exe` or run from command prompt
   - **Linux/MacOS**: 
     ```bash
     chmod +x video-analyzer  # Make executable
     ./video-analyzer        # Run the program
     ```

### Option 2: Python Package Installation

If you prefer to install from source or need to modify the code:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/video_analyzer.git
cd video_analyzer
```

2. Install the package:
```bash
pip install .
```

3. Run the program:
```bash
video-analyzer
```

### Building from Source

To create your own standalone executable:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/video_analyzer.git
cd video_analyzer
```

2. Run the build script:
```bash
python build.py
```

The executable will be created in the `dist` directory.

## Dependencies

- Python 3.7 or higher
- FFmpeg (required for video analysis)
- Required Python packages:
  ```
  colorama>=0.4.6
  tabulate>=0.9.0
  tqdm>=4.65.0
  rich>=13.7.0
  plotext>=5.2.8
  humanize>=4.9.0
  ```

### Installing FFmpeg

- **Windows**:
  1. Download FFmpeg from https://ffmpeg.org/download.html
  2. Add FFmpeg to your system PATH

- **Linux**:
  ```bash
  sudo apt-get update
  sudo apt-get install ffmpeg
  ```

- **MacOS**:
  ```bash
  brew install ffmpeg
  ```

## Usage

1. Start the analyzer:
```bash
python -m video_analyzer
```

2. Interactive Setup:
```
┌─ Video Analyzer Setup ───────────────────────────────────────┐
│                                                             │
│ Welcome to Video Analyzer!                                  │
│                                                             │
│ This tool helps you find and manage duplicate video files   │
│ with different resolutions.                                 │
│ Please configure the following settings to begin:           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Enter the path to your video directory: /path/to/videos
Would you like to specify a custom log file location? (y/n): n
Enter minimum similarity threshold (0.0-1.0) [0.95]: 0.95
Enable dry run mode? (no actual deletions will be performed) (y/n): y

Configuration Summary:
Video Directory: /path/to/videos
Log File: /path/to/video_analyzer.log
Similarity Threshold: 0.95
Dry Run Mode: Yes

Proceed with these settings? (y/n): y
```

3. Analysis Progress:
```
┌─ Analysis Progress ──────────────────────────────────────────┐
│ ⠋ Analyzing videos... ███████████████░░░░░  63%  [1:45<0:58] │
└─────────────────────────────────────────────────────────────┘
┌─ Analysis Statistics ────────────────────────────────────────┐
│ Total Files:              1,234                             │
│ Duplicate Groups:         45                                │
│ Total Size:              1.2 TB                            │
│ Potential Space Savings:  234.5 GB                         │
│ Selected for Deletion:    0 B                              │
└─────────────────────────────────────────────────────────────┘
┌─ Currently Processing ────────────────────────────────────────┐
│ Movie.2023.2160p.BluRay.x265.mkv                            │
└─────────────────────────────────────────────────────────────┘
```

4. Main Menu:
```
┌─ Video Analyzer Menu ─────────────────────────────────────────┐
│                                                              │
│ 1: View Duplicate Groups                                     │
│ 2: Auto-Select Lower Quality Files                          │
│ 3: View Storage Analysis Chart                              │
│ 4: View Duplicates Distribution                             │
│ 5: Review Selected Files                                    │
│ 6: Execute Deletion                                         │
│ q: Quit                                                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

5. Storage Analysis Chart:
```
Storage Analysis (GB)
┌────────────────────────────────────────────────────┐
│                                                    │
│    1200 ┤ █████████                               │
│    1000 ┤ █████████                               │
│     800 ┤ █████████        ██████                 │
│     600 ┤ █████████        ██████     ████        │
│     400 ┤ █████████        ██████     ████        │
│     200 ┤ █████████        ██████     ████        │
│       0 ┤                                         │
└────────────────────────────────────────────────────┘
      Total      Duplicates    Selected
```

## Advanced Features

### Similarity Threshold

The similarity threshold (0.0-1.0) determines how strict the duplicate detection should be:
- Higher values (e.g., 0.95) are more strict
- Lower values (e.g., 0.80) are more lenient

### Parallel Processing

The tool automatically utilizes all available CPU cores for faster processing:
- Batch processing of video files
- Metadata caching
- Efficient string operations
- Optimized disk I/O

### Logging System

Comprehensive logging with different levels:
- INFO: General progress and statistics
- DEBUG: Detailed processing information
- WARNING: Potential issues
- ERROR: Processing failures

Log file example:
```
2024-03-04 15:30:45 [INFO] Starting video analysis of directory: /videos
2024-03-04 15:30:45 [INFO] Found 1234 video files
2024-03-04 15:30:46 [INFO] Found duplicate group 1:
2024-03-04 15:30:46 [INFO]   - video1_2160p.mkv (3840x2160, 15.2 GB)
2024-03-04 15:30:46 [INFO]   - video1_1080p.mkv (1920x1080, 4.3 GB)
```

## Performance Tips

1. **SSD Storage**: Place videos on SSD for faster scanning
2. **Memory Usage**: Ensure adequate RAM for large video collections
3. **CPU Cores**: The tool automatically uses all available cores
4. **Network Storage**: Local storage is recommended for best performance

## Troubleshooting

1. **Hanging on Analysis**:
   - Check FFmpeg installation
   - Verify file permissions
   - Check available disk space

2. **Missing Duplicates**:
   - Adjust similarity threshold
   - Verify video file integrity
   - Check file permissions

3. **Slow Performance**:
   - Check disk speed
   - Verify CPU usage
   - Monitor memory usage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.