#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Repository information
REPO_OWNER="GraysLawson"
REPO_NAME="video_analyzer"

# Installation paths
INSTALL_DIR="/usr/local"
VENV_DIR="${INSTALL_DIR}/video-analyzer-env"
BIN_PATH="${INSTALL_DIR}/bin/video-analyzer"

# Essential dependencies
REQUIRED_PACKAGES=(
    "ffmpeg"
    "python3"
    "python3-pip"
    "python3-venv"
    "python3-tk"
)

# Function to detect if program is installed
check_installation() {
    if [ -d "$VENV_DIR" ] && [ -f "$BIN_PATH" ]; then
        return 0  # installed
    else
        return 1  # not installed
    fi
}

# Function to uninstall
uninstall() {
    echo -e "${YELLOW}Uninstalling video-analyzer...${NC}"
    
    # Remove virtual environment
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
    fi
    
    # Remove binary
    if [ -f "$BIN_PATH" ]; then
        rm -f "$BIN_PATH"
    fi
    
    echo -e "${GREEN}Uninstallation complete!${NC}"
}

# Function to get current version
get_current_version() {
    if [ -f "$VENV_DIR/lib/python"*"/site-packages/video_analyzer/__init__.py" ]; then
        CURRENT_VERSION=$(grep "__version__" "$VENV_DIR"/lib/python*/site-packages/video_analyzer/__init__.py | cut -d'"' -f2)
        echo "$CURRENT_VERSION"
    else
        echo "unknown"
    fi
}

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

    # Get Python version and create package directory
    echo -e "${YELLOW}Creating package directory...${NC}"
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PACKAGE_DIR="/usr/local/video-analyzer-env/lib/python${PYTHON_VERSION}/site-packages/video_analyzer"
    mkdir -p "$PACKAGE_DIR"

    # Create the main script
    echo -e "${YELLOW}Creating main script...${NC}"
    cat > "$PACKAGE_DIR/__init__.py" << 'EOF'
"""Video Analyzer - A tool for finding and managing duplicate video files."""
__version__ = "1.0.0"
EOF

    cat > "$PACKAGE_DIR/__main__.py" << 'EOF'
import os
import sys
import json
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
        return json.loads(result.stdout)
    except Exception as e:
        print(f"{Fore.RED}Error processing {file_path}: {e}{Fore.RESET}")
        return None

def process_directory(directory):
    """Process all video files in the directory."""
    print(f"{Fore.BLUE}Scanning directory: {directory}{Fore.RESET}")

    video_files = []
    for ext in ('*.mp4', '*.mkv', '*.avi', '*.mov'):
        video_files.extend(Path(directory).rglob(ext))

    if not video_files:
        print(f"{Fore.RED}No video files found{Fore.RESET}")
        return

    print(f"{Fore.GREEN}Found {len(video_files)} video files{Fore.RESET}")

    # Prepare table data
    table_data = []
    for file in tqdm(video_files, desc="Processing"):
        info = get_video_info(file)
        if info:
            size = os.path.getsize(file)
            duration = float(info['format'].get('duration', 0))
            
            # Get video stream info
            video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
            resolution = 'N/A'
            codec = 'N/A'
            
            if video_stream:
                resolution = f"{video_stream.get('width', 'N/A')}x{video_stream.get('height', 'N/A')}"
                codec = video_stream.get('codec_name', 'N/A')

            table_data.append([
                str(file),
                humanize.naturalsize(size),
                f"{int(duration//60)}m {int(duration%60)}s",
                resolution,
                codec
            ])

    # Print results in a nice table
    if table_data:
        headers = ["File", "Size", "Duration", "Resolution", "Codec"]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\n{Fore.GREEN}Analysis complete!{Fore.RESET}")

def main():
    # Try to use GUI mode
    try:
        import tkinter as tk
        from tkinter import filedialog, ttk
        
        class VideoAnalyzer(tk.Tk):
            def __init__(self):
                super().__init__()

                self.title("Video Analyzer")
                self.geometry("800x600")

                # Create main frame
                self.main_frame = ttk.Frame(self)
                self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                # Create buttons frame
                self.button_frame = ttk.Frame(self.main_frame)
                self.button_frame.pack(fill=tk.X, pady=(0, 10))

                # Create Select Directory button
                self.select_btn = ttk.Button(
                    self.button_frame,
                    text="Select Directory",
                    command=self.select_directory
                )
                self.select_btn.pack(side=tk.LEFT, padx=5)

                # Create progress bar
                self.progress = ttk.Progressbar(
                    self.main_frame,
                    orient=tk.HORIZONTAL,
                    mode='determinate'
                )
                self.progress.pack(fill=tk.X, pady=(0, 10))

                # Create text widget for results
                self.text_widget = tk.Text(
                    self.main_frame,
                    wrap=tk.WORD,
                    height=20,
                    bg='white',
                    fg='black'
                )
                self.text_widget.pack(fill=tk.BOTH, expand=True)

                # Create scrollbar
                scrollbar = ttk.Scrollbar(
                    self.main_frame,
                    orient=tk.VERTICAL,
                    command=self.text_widget.yview
                )
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                self.text_widget.configure(yscrollcommand=scrollbar.set)

                # Show initial message
                self.log_message("Welcome to Video Analyzer!", "blue")
                self.log_message("Click 'Select Directory' to choose a folder with videos.", "black")

            def select_directory(self):
                directory = filedialog.askdirectory(
                    title="Select Directory with Videos"
                )
                if directory:
                    self.process_directory(directory)

            def log_message(self, message, color="black"):
                self.text_widget.insert(tk.END, message + "\n")
                last_line = self.text_widget.get("end-2c linestart", "end-1c")
                self.text_widget.tag_add(color, f"end-{len(last_line)+1}c linestart", "end-1c")
                self.text_widget.tag_config("red", foreground="red")
                self.text_widget.tag_config("blue", foreground="blue")
                self.text_widget.tag_config("green", foreground="green")
                self.text_widget.see(tk.END)
                self.update()

            def process_directory(self, directory):
                self.text_widget.delete(1.0, tk.END)
                self.log_message(f"Scanning directory: {directory}", "blue")

                video_files = []
                for ext in ('*.mp4', '*.mkv', '*.avi', '*.mov'):
                    video_files.extend(Path(directory).rglob(ext))

                if not video_files:
                    self.log_message("No video files found", "red")
                    return

                self.log_message(f"Found {len(video_files)} video files", "green")
                self.progress['maximum'] = len(video_files)
                self.progress['value'] = 0

                for file in video_files:
                    info = get_video_info(file)
                    if info:
                        size = os.path.getsize(file)
                        duration = float(info['format'].get('duration', 0))
                        self.log_message(f"\nFile: {file.name}", "blue")
                        self.log_message(f"Size: {humanize.naturalsize(size)}")
                        self.log_message(f"Duration: {int(duration//60)}m {int(duration%60)}s")
                        
                        video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
                        if video_stream:
                            resolution = f"{video_stream.get('width', 'N/A')}x{video_stream.get('height', 'N/A')}"
                            self.log_message(f"Resolution: {resolution}")
                            self.log_message(f"Codec: {video_stream.get('codec_name', 'N/A')}")

                    self.progress['value'] += 1
                    self.update()

                self.progress['value'] = 0
                self.log_message("\nAnalysis complete!", "green")

        app = VideoAnalyzer()
        app.mainloop()
        
    except (ImportError, _tkinter.TclError):
        # If GUI is not available, use command line interface
        print(f"{Fore.YELLOW}GUI mode not available, using command line interface{Fore.RESET}")
        
        # Ask for directory input
        while True:
            print("\nEnter the directory path to scan (or 'q' to quit):")
            directory = input("> ").strip()
            
            if directory.lower() == 'q':
                break
                
            if not os.path.isdir(directory):
                print(f"{Fore.RED}Error: Invalid directory path{Fore.RESET}")
                continue
                
            process_directory(directory)

if __name__ == '__main__':
    main()
EOF

    # Create wrapper script
    echo -e "${YELLOW}Creating wrapper script...${NC}"
    cat > /usr/local/bin/video-analyzer << 'EOF'
#!/bin/bash
source /usr/local/video-analyzer-env/bin/activate
python -m video_analyzer
EOF

    # Make wrapper script executable
    chmod +x /usr/local/bin/video-analyzer

    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo -e "${YELLOW}You can now run 'video-analyzer' to launch the program${NC}"
}

# Main installation function
main() {
    local arch=$(detect_arch)
    local os=$(detect_os)

    if check_installation; then
        current_version=$(get_current_version)
        echo -e "${YELLOW}Video Analyzer version ${current_version} is already installed.${NC}"
        echo -e "Choose an option:"
        echo -e "1) Update"
        echo -e "2) Uninstall"
        echo -e "3) Exit"
        read -p "Enter your choice (1-3): " choice
        
        case $choice in
            1)
                echo -e "${YELLOW}Updating video-analyzer...${NC}"
                uninstall
                install_system_dependencies
                install_minimal
                echo -e "${GREEN}Update complete!${NC}"
                echo -e "${YELLOW}Run 'video-analyzer' to start the program${NC}"
                ;;
            2)
                uninstall
                ;;
            3)
                echo -e "${YELLOW}Exiting...${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice. Exiting...${NC}"
                exit 1
                ;;
        esac
    else
        echo -e "${GREEN}Detected system: $os on $arch${NC}"
        echo -e "${YELLOW}Installing video-analyzer...${NC}"
        install_system_dependencies
        install_minimal
        echo -e "${GREEN}Installation complete!${NC}"
        echo -e "${YELLOW}Run 'video-analyzer' to start the program${NC}"
    fi
}

# Run main installation
main