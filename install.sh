#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Repository information
REPO_OWNER="GraysLawson"
REPO_NAME="video_analyzer"

# Default installation paths
SYSTEM_INSTALL_DIR="/usr/local"
USER_INSTALL_DIR="$HOME/.local"
INSTALL_DIR=""
VENV_DIR=""
BIN_DIR=""
BIN_PATH=""
CONFIG_DIR=""
BACKUP_DIR=""

# Essential dependencies
REQUIRED_PACKAGES=(
    "ffmpeg"
    "python3"
    "python3-pip"
    "python3-venv"
    "python3-tk"
)

# Add logging configuration
LOG_FILE="/tmp/video-analyzer-install.log"
VERBOSE=false

# Function to log messages
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    if [ "$VERBOSE" = true ]; then
        case "$level" in
            "ERROR") echo -e "${RED}[$level] $message${NC}" ;;
            "WARNING") echo -e "${YELLOW}[$level] $message${NC}" ;;
            "INFO") echo -e "${GREEN}[$level] $message${NC}" ;;
            *) echo "[$level] $message" ;;
        esac
    fi
}

# Function to setup installation paths
setup_paths() {
    local install_type=$1
    if [ "$install_type" = "system" ]; then
        INSTALL_DIR="$SYSTEM_INSTALL_DIR"
        BIN_DIR="$SYSTEM_INSTALL_DIR/bin"
    else
        INSTALL_DIR="$USER_INSTALL_DIR"
        BIN_DIR="$USER_INSTALL_DIR/bin"
        mkdir -p "$BIN_DIR"
    fi
    
    VENV_DIR="${INSTALL_DIR}/video-analyzer-env"
    BIN_PATH="${BIN_DIR}/video-analyzer"
    CONFIG_DIR="${INSTALL_DIR}/video-analyzer/config"
    BACKUP_DIR="${INSTALL_DIR}/video-analyzer/backups"
}

# Function to detect if program is installed
check_installation() {
    if [ -d "$SYSTEM_INSTALL_DIR/video-analyzer-env" ]; then
        setup_paths "system"
        return 0
    elif [ -d "$USER_INSTALL_DIR/video-analyzer-env" ]; then
        setup_paths "user"
        return 0
    fi
    return 1
}

# Function to backup configuration
backup_config() {
    if [ -d "$CONFIG_DIR" ]; then
        echo -e "${YELLOW}Backing up configuration...${NC}"
        mkdir -p "$BACKUP_DIR"
        backup_name="config_backup_$(date +%Y%m%d_%H%M%S)"
        cp -r "$CONFIG_DIR" "$BACKUP_DIR/$backup_name"
        echo -e "${GREEN}Configuration backed up to: $BACKUP_DIR/$backup_name${NC}"
    fi
}

# Function to restore configuration
restore_config() {
    if [ -d "$BACKUP_DIR" ]; then
        latest_backup=$(ls -t "$BACKUP_DIR" | head -n1)
        if [ -n "$latest_backup" ]; then
            echo -e "${YELLOW}Restoring configuration from backup...${NC}"
            mkdir -p "$CONFIG_DIR"
            cp -r "$BACKUP_DIR/$latest_backup"/* "$CONFIG_DIR/"
            echo -e "${GREEN}Configuration restored from: $latest_backup${NC}"
        fi
    fi
}

# Function to uninstall
uninstall() {
    log "INFO" "Starting uninstallation process"
    echo -e "${YELLOW}Uninstalling video-analyzer...${NC}"
    
    local keep_deps="n"
    local keep_config="n"
    
    if [ "$INTERACTIVE" = true ]; then
        read -p "Keep system dependencies? (y/n): " keep_deps
        read -p "Keep configuration files? (y/n): " keep_config
    else
        log "INFO" "Non-interactive mode: removing everything"
    fi
    
    if [[ $keep_deps != "y" ]]; then
        log "INFO" "Removing system dependencies"
        echo -e "${YELLOW}Removing system dependencies...${NC}"
        if command_exists apt-get; then
            sudo apt-get remove -y "${REQUIRED_PACKAGES[@]}"
        elif command_exists yum; then
            sudo yum remove -y "${REQUIRED_PACKAGES[@]}"
        elif command_exists dnf; then
            sudo dnf remove -y "${REQUIRED_PACKAGES[@]}"
        fi
    else
        log "INFO" "Keeping system dependencies"
    fi
    
    if [[ $keep_config != "y" ]]; then
        log "INFO" "Removing configuration files"
        rm -rf "$CONFIG_DIR" "$BACKUP_DIR"
    else
        log "INFO" "Keeping configuration files"
    fi
    
    # Remove virtual environment and binary
    log "INFO" "Removing virtual environment and binary"
    rm -rf "$VENV_DIR"
    rm -f "$BIN_PATH"
    
    log "INFO" "Uninstallation complete"
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
    python3 -m venv "$VENV_DIR"

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Install minimal dependencies
    pip install --no-cache-dir \
        tabulate \
        tqdm \
        colorama \
        humanize

    # Get Python version and create package directory
    echo -e "${YELLOW}Creating package directory...${NC}"
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PACKAGE_DIR="$VENV_DIR/lib/python${PYTHON_VERSION}/site-packages/video_analyzer"
    mkdir -p "$PACKAGE_DIR"
    mkdir -p "$CONFIG_DIR"

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
    # Check if DISPLAY is available
    if os.environ.get('DISPLAY'):
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
            
        except ImportError:
            use_cli = True
    else:
        use_cli = True

    if use_cli:
        print(f"{Fore.YELLOW}Using command line interface{Fore.RESET}")
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
    cat > "$BIN_PATH" << 'EOF'
#!/bin/bash

# Function to check X11 forwarding and display availability
check_x11() {
    # Check if running in SSH session with X11 forwarding
    if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
        if [ -n "$DISPLAY" ]; then
            # Verify X11 forwarding works
            if command -v xdpyinfo >/dev/null 2>&1; then
                if xdpyinfo >/dev/null 2>&1; then
                    echo "ssh_x11"
                    return 0
                fi
            fi
        fi
        echo "ssh_no_x11"
        return 1
    fi

    # Check local X server
    if [ -n "$DISPLAY" ]; then
        if command -v xdpyinfo >/dev/null 2>&1; then
            if xdpyinfo >/dev/null 2>&1; then
                echo "local_x11"
                return 0
            fi
        fi
    fi

    # Check if Wayland is available
    if [ -n "$WAYLAND_DISPLAY" ]; then
        if command -v xwayland >/dev/null 2>&1; then
            echo "wayland"
            return 0
        fi
    fi

    echo "no_display"
    return 1
}

# Activate virtual environment
source "VENV_DIR_PLACEHOLDER/bin/activate"

# Check display availability
display_type=$(check_x11)

case "$display_type" in
    "ssh_x11")
        echo "Using X11 forwarding over SSH"
        python -m video_analyzer
        ;;
    "local_x11")
        echo "Using local X11 display"
        export DISPLAY="${DISPLAY:-:0}"
        python -m video_analyzer
        ;;
    "wayland")
        echo "Using Wayland display"
        export DISPLAY="${WAYLAND_DISPLAY}"
        python -m video_analyzer
        ;;
    *)
        echo "No display available, using CLI mode"
        unset DISPLAY
        python -m video_analyzer
        ;;
esac
EOF

    # Replace placeholder with actual VENV_DIR
    sed -i "s|VENV_DIR_PLACEHOLDER|$VENV_DIR|g" "$BIN_PATH"

    # Make wrapper script executable
    chmod +x "$BIN_PATH"

    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo -e "${YELLOW}Run 'video-analyzer' to launch the program${NC}"
    echo -e "${YELLOW}(GUI mode will be used if available, otherwise CLI mode)${NC}"
}

# Main installation function
main() {
    # Initialize log file
    echo "=== Video Analyzer Installation Log ===" > "$LOG_FILE"
    echo "Started at: $(date)" >> "$LOG_FILE"
    log "INFO" "Starting installation script"
    
    local arch=$(detect_arch)
    local os=$(detect_os)
    log "INFO" "Detected system: $os on $arch"

    # Check if script is running interactively
    if [ -t 0 ]; then
        INTERACTIVE=true
        log "INFO" "Running in interactive mode"
    else
        INTERACTIVE=false
        log "INFO" "Running in non-interactive mode"
        # If not interactive and no arguments, show instructions
        if [ -z "$1" ]; then
            log "INFO" "No arguments provided in non-interactive mode"
            echo -e "${YELLOW}Non-interactive shell detected. Please run one of the following commands:${NC}"
            echo "curl -sSLO https://raw.githubusercontent.com/GraysLawson/video_analyzer/main/install.sh"
            echo "chmod +x install.sh"
            echo "./install.sh install     # For fresh installation"
            echo "./install.sh update      # To update existing installation"
            echo "./install.sh uninstall   # To uninstall"
            log "INFO" "Exiting with instructions"
            exit 1
        fi
        log "INFO" "Argument provided: $1"
    fi

    if check_installation; then
        current_version=$(get_current_version)
        log "INFO" "Found existing installation version: $current_version"
        echo -e "${YELLOW}Video Analyzer version ${current_version} is already installed.${NC}"
        
        if [ "$INTERACTIVE" = true ]; then
            echo -e "Choose an option:"
            echo -e "1) Update"
            echo -e "2) Uninstall"
            echo -e "3) Exit"
            read -p "Enter your choice (1-3): " choice
            log "INFO" "User selected option: $choice"
            
            case $choice in
                1)
                    ACTION="update"
                    ;;
                2)
                    ACTION="uninstall"
                    ;;
                3)
                    log "INFO" "User chose to exit"
                    echo -e "${YELLOW}Exiting...${NC}"
                    exit 0
                    ;;
                *)
                    log "ERROR" "Invalid choice selected"
                    echo -e "${RED}Invalid choice. Exiting...${NC}"
                    exit 1
                    ;;
            esac
        else
            # Non-interactive mode, use command line argument
            case "$1" in
                update|uninstall)
                    ACTION="$1"
                    log "INFO" "Non-interactive mode: $ACTION selected"
                    ;;
                *)
                    log "ERROR" "Invalid argument in non-interactive mode: $1"
                    echo -e "${RED}Invalid argument. Use 'update' or 'uninstall'${NC}"
                    exit 1
                    ;;
            esac
        fi

        case "$ACTION" in
            update)
                log "INFO" "Starting update process"
                echo -e "${YELLOW}Updating video-analyzer...${NC}"
                backup_config
                uninstall
                install_system_dependencies
                install_minimal
                restore_config
                log "INFO" "Update completed successfully"
                echo -e "${GREEN}Update complete!${NC}"
                echo -e "${YELLOW}Run 'video-analyzer' to start the program${NC}"
                ;;
            uninstall)
                uninstall
                ;;
        esac
    else
        log "INFO" "No existing installation found"
        echo -e "${GREEN}Detected system: $os on $arch${NC}"
        
        if [ "$INTERACTIVE" = true ]; then
            echo -e "Choose installation type:"
            echo -e "1) System-wide (requires sudo)"
            echo -e "2) User-local"
            read -p "Enter your choice (1-2): " install_type
            log "INFO" "User selected installation type: $install_type"
            
            case $install_type in
                1)
                    INSTALL_TYPE="system"
                    ;;
                2)
                    INSTALL_TYPE="user"
                    ;;
                *)
                    log "ERROR" "Invalid installation type selected"
                    echo -e "${RED}Invalid choice. Exiting...${NC}"
                    exit 1
                    ;;
            esac
        else
            # Default to user-local installation in non-interactive mode
            INSTALL_TYPE="user"
            if [ "$1" = "install-system" ]; then
                INSTALL_TYPE="system"
            fi
            log "INFO" "Non-interactive mode: selected $INSTALL_TYPE installation"
        fi
        
        setup_paths "$INSTALL_TYPE"
        log "INFO" "Set up paths for $INSTALL_TYPE installation"
        
        if [ "$INSTALL_TYPE" = "user" ]; then
            # Add user's bin to PATH if not already there
            if [[ ":$PATH:" != *":$USER_INSTALL_DIR/bin:"* ]]; then
                log "INFO" "Adding user bin directory to PATH"
                echo "export PATH=\"\$PATH:$USER_INSTALL_DIR/bin\"" >> ~/.bashrc
                export PATH="$PATH:$USER_INSTALL_DIR/bin"
            fi
        fi
        
        log "INFO" "Starting installation process"
        echo -e "${YELLOW}Installing video-analyzer...${NC}"
        install_system_dependencies
        install_minimal
        log "INFO" "Installation completed successfully"
        echo -e "${GREEN}Installation complete!${NC}"
        echo -e "${YELLOW}Run 'video-analyzer' to start the program${NC}"
    fi
    
    log "INFO" "Installation script finished"
    echo -e "${YELLOW}Installation log available at: $LOG_FILE${NC}"
}

# Run main installation with all arguments
main "$@"