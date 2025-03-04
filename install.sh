#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Repository information
REPO_OWNER="GraysLawson"
REPO_NAME="video_analyzer"

# Essential dependencies
REQUIRED_PACKAGES=(
    "ffmpeg"
    "python3"
    "python3-pip"
    "python3-venv"
)

# Function to detect system architecture
detect_arch() {
    local arch=$(uname -m)
    case $arch in
        x86_64)
            echo "x86_64"
            ;;
        aarch64|arm64)
            echo "aarch64"
            ;;
        armv7l|armv7)
            echo "armv7l"
            ;;
        *)
            echo "unsupported"
            ;;
    esac
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unsupported"
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system dependencies
install_system_dependencies() {
    echo -e "${YELLOW}Installing system dependencies...${NC}"
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y "${REQUIRED_PACKAGES[@]}"
    elif command_exists yum; then
        sudo yum install -y "${REQUIRED_PACKAGES[@]}"
    elif command_exists dnf; then
        sudo dnf install -y "${REQUIRED_PACKAGES[@]}"
    else
        echo -e "${RED}Could not install dependencies. Please install them manually:${NC}"
        printf '%s\n' "${REQUIRED_PACKAGES[@]}"
        exit 1
    fi
}

# Function to install minimal dependencies
install_minimal() {
    echo -e "${YELLOW}Installing minimal dependencies...${NC}"
    
    # Create virtual environment
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv /usr/local/video-analyzer-env

    # Activate virtual environment
    source /usr/local/video-analyzer-env/bin/activate

    # Install minimal dependencies
    pip install --no-cache-dir \
        tabulate \
        tqdm \
        colorama \
        humanize

    # Create the main script
    echo -e "${YELLOW}Creating main script...${NC}"
    mkdir -p /usr/local/video-analyzer-env/lib/video_analyzer
    cat > /usr/local/video-analyzer-env/lib/video_analyzer/__init__.py << 'EOF'
"""Video Analyzer - A tool for finding and managing duplicate video files."""
__version__ = "1.0.0"
EOF

    cat > /usr/local/video-analyzer-env/lib/video_analyzer/__main__.py << 'EOF'
import os
import sys
import subprocess
from pathlib import Path
from tabulate import tabulate
from tqdm import tqdm
from colorama import init, Fore
import humanize

init()

def get_video_info(file_path):
    """Get video metadata using ffprobe."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"{Fore.RED}Error processing {file_path}: {e}{Fore.RESET}")
        return None

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    if not target_dir.is_dir():
        print(f"{Fore.RED}Error: {target_dir} is not a directory{Fore.RESET}")
        sys.exit(1)

    print(f"{Fore.GREEN}Scanning directory: {target_dir}{Fore.RESET}")
    video_files = []
    for ext in ('*.mp4', '*.mkv', '*.avi', '*.mov'):
        video_files.extend(target_dir.rglob(ext))

    if not video_files:
        print(f"{Fore.YELLOW}No video files found{Fore.RESET}")
        return

    print(f"\nFound {len(video_files)} video files")
    for file in tqdm(video_files, desc="Processing"):
        info = get_video_info(file)
        if info:
            size = os.path.getsize(file)
            print(f"\n{Fore.CYAN}{file.name}{Fore.RESET}")
            print(f"Size: {humanize.naturalsize(size)}")

if __name__ == '__main__':
    main()
EOF

    # Create wrapper script
    echo -e "${YELLOW}Creating wrapper script...${NC}"
    cat > /usr/local/bin/video-analyzer << 'EOF'
#!/bin/bash
source /usr/local/video-analyzer-env/bin/activate
python -m video_analyzer "$@"
EOF

    # Make wrapper script executable
    chmod +x /usr/local/bin/video-analyzer

    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo -e "${YELLOW}You can now run 'video-analyzer <directory>' from anywhere.${NC}"
}

# Main installation function
main() {
    local arch=$(detect_arch)
    local os=$(detect_os)
    local install_dir="/usr/local/bin"

    echo -e "${GREEN}Detected system: $os on $arch${NC}"

    # Install system dependencies
    install_system_dependencies

    # Install minimal version
    install_minimal

    echo -e "${GREEN}Installation complete!${NC}"
    echo -e "${YELLOW}Run 'video-analyzer <directory>' to analyze videos${NC}"
}

# Run main installation
main 