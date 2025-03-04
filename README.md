# Video Analyzer

A powerful tool for finding and managing duplicate video files with different resolutions. This tool helps you identify duplicate videos, compare their quality, and manage storage space efficiently.

<div align="center">

[![Author](https://img.shields.io/badge/Author-GraysLawson-blue)](mailto:grays@possumden.net)
[![Bluesky](https://img.shields.io/badge/Bluesky-@grays.bsky.possumden.net-1DA1F2)](https://bsky.app/profile/grays.bsky.possumden.net)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange)](https://github.com/GraysLawson/video_analyzer/releases)

</div>

## 🔧 Supported Platforms

### Linux
- **Architectures**: 
  - x86_64 (64-bit Intel/AMD)
  - aarch64 (64-bit ARM)
  - armv7l (32-bit ARM)
- **Distributions**:
  - Debian 10 (Buster)
  - Debian 11 (Bullseye)
  - Debian 12 (Bookworm)
  - Ubuntu 18.04 LTS and newer
  - Other Linux distributions with GLIBC 2.17 or newer

### Windows
- Windows 10 and 11 (64-bit)

### macOS
- macOS 10.15 (Catalina) and newer (Intel)

## 📥 Installation

### Automatic Installation (Recommended)

#### Linux and macOS
```bash
curl -sSL https://raw.githubusercontent.com/GraysLawson/video_analyzer/main/install.sh | bash
```

#### Windows
Download the latest `video-analyzer.exe` from the [releases page](https://github.com/GraysLawson/video_analyzer/releases).

### Manual Installation

1. **Determine your architecture**:
```bash
uname -m
```

2. **Download the appropriate binary**:

#### Linux x86_64
```bash
curl -LO https://github.com/GraysLawson/video_analyzer/releases/latest/download/video-analyzer-x86_64
chmod +x video-analyzer-x86_64
sudo mv video-analyzer-x86_64 /usr/local/bin/video-analyzer
```

#### Linux ARM64
```bash
curl -LO https://github.com/GraysLawson/video_analyzer/releases/latest/download/video-analyzer-aarch64
chmod +x video-analyzer-aarch64
sudo mv video-analyzer-aarch64 /usr/local/bin/video-analyzer
```

#### Linux ARM32
```bash
curl -LO https://github.com/GraysLawson/video_analyzer/releases/latest/download/video-analyzer-armv7l
chmod +x video-analyzer-armv7l
sudo mv video-analyzer-armv7l /usr/local/bin/video-analyzer
```

#### macOS
```bash
curl -LO https://github.com/GraysLawson/video_analyzer/releases/latest/download/video-analyzer-macos
chmod +x video-analyzer-macos
sudo mv video-analyzer-macos /usr/local/bin/video-analyzer
```

### Verifying Your Installation

Each binary comes with a SHA256 checksum and GPG signature (Linux only). To verify:

```bash
# Verify SHA256
sha256sum -c video-analyzer*.sha256

# Verify GPG signature (Linux only)
gpg --verify video-analyzer*.sig video-analyzer*
```

## 🔍 System Requirements

### Linux
- GLIBC 2.17 or newer
- x86_64, ARM64, or ARM32 processor
- FFmpeg installed (for video analysis)

### Windows
- Windows 10 or newer (64-bit)
- FFmpeg installed (for video analysis)

### macOS
- macOS 10.15 or newer
- Intel processor
- FFmpeg installed (for video analysis)

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

## Security & Binary Verification

### Binary Security Measures
Our binaries are built with several security measures:
- SHA256 checksums for all releases
- GPG signatures for Linux binaries
- Embedded build information and metadata
- Windows manifest with explicit permissions
- Transparent build process via GitHub Actions
- No elevated privileges required
- Full source code availability

### Linux Compatibility
The Linux binary is built on Ubuntu 18.04 for maximum compatibility. Tested and confirmed working on:

- Debian-based distributions:
  - Debian 10 (Buster) and newer
  - Ubuntu 18.04 LTS and newer
  - Linux Mint 19 and newer
  - Pop!_OS 18.04 and newer

- RPM-based distributions:
  - CentOS 7 and newer
  - Fedora 30 and newer
  - RHEL 7 and newer

- Other distributions:
  - OpenSUSE Leap 15 and newer
  - Arch Linux (rolling release)
  - Manjaro (rolling release)

### Verifying Binary Authenticity

#### Windows
1. Download both `video-analyzer.exe` and `video-analyzer.exe.sha256`
2. Run the verification script:
   ```powershell
   # Download the verification script
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/GraysLawson/video_analyzer/main/verify_binary.ps1" -OutFile "verify_binary.ps1"
   
   # Run the script
   .\verify_binary.ps1
   ```

3. Manual verification:
   ```powershell
   # Calculate SHA256 hash
   $fileHash = Get-FileHash -Algorithm SHA256 video-analyzer.exe
   
   # Compare with provided hash
   $expectedHash = Get-Content video-analyzer.exe.sha256
   if ($fileHash.Hash -eq $expectedHash) { 
       Write-Host "Verification successful" -ForegroundColor Green 
   }
   ```

#### Linux/macOS
1. Download the binary and checksum file:
   ```bash
   # Linux
   wget https://github.com/GraysLawson/video_analyzer/releases/download/v1.0.0/video-analyzer
   wget https://github.com/GraysLawson/video_analyzer/releases/download/v1.0.0/video-analyzer.sha256
   
   # Verify checksum
   sha256sum -c video-analyzer.sha256
   ```

   For Linux, you can also verify the GPG signature:
   ```bash
   # Download the signature
   wget https://github.com/GraysLawson/video_analyzer/releases/download/v1.0.0/video-analyzer.sig
   
   # Import the public key (first time only)
   curl -s https://raw.githubusercontent.com/GraysLawson/video_analyzer/main/public_key.asc | gpg --import
   
   # Verify signature
   gpg --verify video-analyzer.sig video-analyzer
   ```

### Understanding Windows SmartScreen Warnings
When running the Windows executable for the first time, you may see a SmartScreen warning. This is normal for new applications without an established reputation. Our binaries are built with several measures to ensure security:

1. **Why the warning appears:**
   - New applications need time to build reputation
   - We don't use paid code signing certificates
   - The application is distributed outside the Microsoft Store

2. **How to verify it's safe:**
   - Check the SHA256 checksum (instructions above)
   - Verify the embedded metadata using the verification script
   - Review the source code on GitHub
   - Check the build logs in GitHub Actions

3. **To run after verification:**
   - Click "More info" in the SmartScreen popup
   - Click "Run anyway"
   - The warning only appears on first run

### Alternative Installation Methods
If you prefer not to use the pre-built binaries, you have several alternatives:

1. **Install from PyPI:**
   ```bash
   pip install video-analyzer
   ```

2. **Install from source:**
   ```bash
   git clone https://github.com/GraysLawson/video_analyzer.git
   cd video_analyzer
   pip install -e .
   ```

3. **Build your own binary:**
   ```bash
   git clone https://github.com/GraysLawson/video_analyzer.git
   cd video_analyzer
   pip install -r requirements.txt
   python -m PyInstaller build_scripts/build.spec
   ```

### Build Information
Each binary includes embedded build information that can be extracted to verify its origin:
- Build date and time
- Source code commit hash
- Repository URL
- License information
- Full metadata

To view this information:
- Windows: Use the `verify_binary.ps1` script
- Linux/macOS: Use `strings` command:
  ```bash
  strings video-analyzer | grep -A 5 "Build Date"
  ```