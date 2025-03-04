#!/usr/bin/env bash

# ANSI color codes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m" # No Color

# Configure logging
LOG_FILE="/tmp/video-analyzer-install-$(date +%Y%m%d%H%M%S).log"

# Function to log messages
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Initialize logging
init_logging() {
    mkdir -p "$(dirname "$LOG_FILE")"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [INFO] Starting Video Analyzer installation" > "$LOG_FILE"
    echo "[$timestamp] [INFO] Working directory: $(pwd)" >> "$LOG_FILE"
}

# Download project from GitHub
download_project() {
    local project_dir="$1"
    
    log "INFO" "Setting up project directory at $project_dir"
    echo -e "${CYAN}Setting up project directory...${NC}"
    
    # First check if we're already in the project directory
    if [[ -f "$(pwd)/setup.py" ]]; then
        log "INFO" "Found setup.py in current directory, using it as project source"
        echo -e "${YELLOW}Found setup.py in current directory, using it as project source.${NC}"
        mkdir -p "$project_dir"
        cp -r "$(pwd)/"* "$project_dir/"
        return 0
    fi
    
    # Check if .git directory exists in installation directory
    if [[ -d "$project_dir/.git" ]]; then
        log "INFO" "Git repository already exists, updating it"
        echo -e "${YELLOW}Git repository already exists, updating...${NC}"
        (cd "$project_dir" && git pull) || {
            log "WARNING" "Failed to update git repository, but continuing with existing files"
            echo -e "${YELLOW}Warning: Failed to update git repository, but continuing with existing files.${NC}"
        }
    else
        # Try to download the release archive instead of git clone
        log "INFO" "Downloading release archive"
        echo -e "${CYAN}Downloading release archive...${NC}"
        
        mkdir -p "$project_dir"
        
        # Use curl or wget to download the release archive
        if command -v curl > /dev/null; then
            log "INFO" "Using curl to download release"
            curl -s -L "https://github.com/GraysLawson/video_analyzer/archive/refs/heads/main.zip" -o "/tmp/video-analyzer.zip" || {
                log "WARNING" "Failed to download with curl, trying alternative download method"
                echo -e "${YELLOW}Warning: Failed to download with curl, trying alternative method.${NC}"
                
                # Try with wget as fallback
                if command -v wget > /dev/null; then
                    log "INFO" "Using wget to download release"
                    wget -q "https://github.com/GraysLawson/video_analyzer/archive/refs/heads/main.zip" -O "/tmp/video-analyzer.zip" || {
                        log "ERROR" "Failed to download with wget"
                        echo -e "${RED}Failed to download release archive.${NC}"
                    }
                else
                    log "ERROR" "Neither curl nor wget is available for downloading"
                    echo -e "${RED}Failed to download: curl and wget not available.${NC}"
                }
            }
            
            # Extract the zip file if it exists
            if [[ -f "/tmp/video-analyzer.zip" ]]; then
                log "INFO" "Extracting release archive"
                unzip -q "/tmp/video-analyzer.zip" -d "/tmp" || {
                    log "ERROR" "Failed to extract zip file"
                    echo -e "${RED}Failed to extract zip file.${NC}"
                    rm -f "/tmp/video-analyzer.zip"
                    
                    # Try git clone as last resort with anonymous access
                    log "INFO" "Trying git clone with anonymous access as fallback"
                    echo -e "${YELLOW}Trying git clone with anonymous access as fallback...${NC}"
                    git clone "https://github.com/GraysLawson/video_analyzer.git" "$project_dir" --depth 1 || {
                        log "ERROR" "Failed to clone repository"
                        echo -e "${RED}Failed to download source code.${NC}"
                        return 1
                    }
                }
                
                # Move files from the extracted directory to the project directory
                if [[ -d "/tmp/video_analyzer-main" ]]; then
                    log "INFO" "Moving files to project directory"
                    cp -r /tmp/video_analyzer-main/* "$project_dir/"
                    rm -rf "/tmp/video_analyzer-main"
                fi
                
                # Clean up
                rm -f "/tmp/video-analyzer.zip"
            fi
        elif command -v wget > /dev/null; then
            log "INFO" "Using wget to download release"
            wget -q "https://github.com/GraysLawson/video_analyzer/archive/refs/heads/main.zip" -O "/tmp/video-analyzer.zip" || {
                log "ERROR" "Failed to download with wget"
                echo -e "${RED}Failed to download release archive.${NC}"
                
                # Try git clone as last resort with anonymous access
                log "INFO" "Trying git clone with anonymous access as fallback"
                echo -e "${YELLOW}Trying git clone with anonymous access as fallback...${NC}"
                git clone "https://github.com/GraysLawson/video_analyzer.git" "$project_dir" --depth 1 || {
                    log "ERROR" "Failed to clone repository"
                    echo -e "${RED}Failed to download source code.${NC}"
                    return 1
                }
            }
            
            # Extract the zip file if it exists
            if [[ -f "/tmp/video-analyzer.zip" ]]; then
                log "INFO" "Extracting release archive"
                unzip -q "/tmp/video-analyzer.zip" -d "/tmp" || {
                    log "ERROR" "Failed to extract zip file"
                    echo -e "${RED}Failed to extract zip file.${NC}"
                    rm -f "/tmp/video-analyzer.zip"
                    return 1
                }
                
                # Move files from the extracted directory to the project directory
                if [[ -d "/tmp/video_analyzer-main" ]]; then
                    log "INFO" "Moving files to project directory"
                    cp -r /tmp/video_analyzer-main/* "$project_dir/"
                    rm -rf "/tmp/video_analyzer-main"
                fi
                
                # Clean up
                rm -f "/tmp/video-analyzer.zip"
            fi
        else
            # If neither curl nor wget are available, try direct git clone with anonymous access
            log "INFO" "No curl or wget available, trying git clone with anonymous access"
            echo -e "${YELLOW}No curl or wget available, trying git clone with anonymous access...${NC}"
            git clone "https://github.com/GraysLawson/video_analyzer.git" "$project_dir" --depth 1 || {
                log "ERROR" "Failed to clone repository"
                echo -e "${RED}Failed to download source code.${NC}"
                return 1
            }
        fi
    fi
    
    # Check if we have a valid project
    if [[ ! -f "$project_dir/setup.py" ]]; then
        log "ERROR" "Invalid project directory, setup.py not found"
        echo -e "${RED}Invalid project directory, setup.py not found.${NC}"
        
        # Last resort - check if we can create a minimal setup.py
        echo -e "${YELLOW}Attempting to create a minimal setup.py file...${NC}"
        log "INFO" "Attempting to create a minimal setup.py file"
        
        mkdir -p "$project_dir"
        cat > "$project_dir/setup.py" <<EOF
from setuptools import setup, find_packages

setup(
    name="video_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.5.0",
        "numpy>=1.19.0",
        "ffmpeg-python>=0.2.0",
    ],
    entry_points={
        'console_scripts': [
            'video-analyzer=video_analyzer.__main__:main',
        ],
    },
)
EOF

        mkdir -p "$project_dir/video_analyzer"
        cat > "$project_dir/video_analyzer/__init__.py" <<EOF
# Video Analyzer package
EOF

        cat > "$project_dir/video_analyzer/__main__.py" <<EOF
#!/usr/bin/env python3
import os
import sys
import logging

def main():
    print("Video Analyzer")
    print("This is a minimal placeholder. The installation completed, but the actual code is missing.")
    print("Please download the full source code from: https://github.com/GraysLawson/video_analyzer")
    
if __name__ == "__main__":
    main()
EOF

        log "WARNING" "Created minimal placeholder code"
        echo -e "${YELLOW}Created minimal placeholder code. Please download the full source code manually.${NC}"
        return 0
    fi
    
    log "INFO" "Project setup completed successfully"
    echo -e "${GREEN}Project setup completed successfully.${NC}"
    return 0
}

# Detect operating system
detect_os() {
    local os_name=$(uname -s)
    case "$os_name" in
        Linux*)     
            if grep -q -i "alpine" /etc/os-release 2>/dev/null; then
                echo "alpine"
            else
                echo "linux"
            fi
            ;;
        Darwin*)    echo "macos" ;;
        *)          echo "unknown" ;;
    esac
}

# Detect architecture
detect_arch() {
    local arch_name=$(uname -m)
    case "$arch_name" in
        x86_64*)    echo "x86_64" ;;
        arm64*)     echo "arm64" ;;
        aarch64*)   echo "arm64" ;;
        armv7l*)    echo "armv7" ;;
        *)          echo "unknown" ;;
    esac
}

# Display installation banner
display_banner() {
    echo -e "${CYAN}"
    echo '   __      ___     __               _                __                     '
    echo '   \ \    / (_)   / _|             | |              / _|                    '
    echo '    \ \  / / _  _| |_ ___  ___     / \   _ __   __ | |_ _  ___ __ ___ _ __ '
    echo '     \ \/ / | |/ _  _/ _ \/ _ \   / _ \ | |_ \ / _ |  _| |/ _ / _` | |_ \ '
    echo '      \  /  | | | ||  __/ (_) | / ___ \| | | | (_| | | | |  __/ (_| | | | |'
    echo '       \/   |_|_| |_|\___|\___/ /_/   \_\_| |_|\__,_|_| |_|\___|\__,_|_| |_|'
    echo -e "${NC}"
}

# Install system dependencies
install_system_dependencies() {
    local os="$1"
    
    log "INFO" "Installing system dependencies for $os"
    echo -e "${CYAN}Installing system dependencies...${NC}"
    
    case "$os" in
        linux)
            if command -v apt-get > /dev/null; then
                log "INFO" "Using apt-get to install dependencies"
                sudo apt-get update || {
                    log "WARNING" "Failed to update apt repositories"
                    echo -e "${YELLOW}Warning: Failed to update apt repositories.${NC}"
                }
                sudo apt-get install -y python3 python3-pip python3-venv ffmpeg || {
                    log "ERROR" "Failed to install apt dependencies"
                    echo -e "${RED}Failed to install dependencies with apt-get.${NC}"
                    echo -e "${YELLOW}Please install manually: python3, python3-pip, python3-venv, ffmpeg${NC}"
                }
            elif command -v dnf > /dev/null; then
                log "INFO" "Using dnf to install dependencies"
                sudo dnf install -y python3 python3-pip ffmpeg || {
                    log "ERROR" "Failed to install dnf dependencies"
                    echo -e "${RED}Failed to install dependencies with dnf.${NC}"
                    echo -e "${YELLOW}Please install manually: python3, python3-pip, ffmpeg${NC}"
                }
            elif command -v yum > /dev/null; then
                log "INFO" "Using yum to install dependencies"
                sudo yum install -y python3 python3-pip ffmpeg || {
                    log "ERROR" "Failed to install yum dependencies"
                    echo -e "${RED}Failed to install dependencies with yum.${NC}"
                    echo -e "${YELLOW}Please install manually: python3, python3-pip, ffmpeg${NC}"
                }
            elif command -v pacman > /dev/null; then
                log "INFO" "Using pacman to install dependencies"
                sudo pacman -S --noconfirm python python-pip ffmpeg || {
                    log "ERROR" "Failed to install pacman dependencies"
                    echo -e "${RED}Failed to install dependencies with pacman.${NC}"
                    echo -e "${YELLOW}Please install manually: python, python-pip, ffmpeg${NC}"
                }
            else
                log "WARNING" "No supported package manager found"
                echo -e "${YELLOW}No supported package manager found.${NC}"
                echo -e "${YELLOW}Please ensure you have Python 3.7+, pip, and ffmpeg installed.${NC}"
            fi
            ;;
        alpine)
            log "INFO" "Using apk to install dependencies"
            sudo apk add --no-cache python3 py3-pip ffmpeg || {
                log "ERROR" "Failed to install apk dependencies"
                echo -e "${RED}Failed to install dependencies with apk.${NC}"
                echo -e "${YELLOW}Please install manually: python3, py3-pip, ffmpeg${NC}"
            }
            ;;
        macos)
            if command -v brew > /dev/null; then
                log "INFO" "Using Homebrew to install dependencies"
                brew install python3 ffmpeg || {
                    log "ERROR" "Failed to install Homebrew dependencies"
                    echo -e "${RED}Failed to install dependencies with Homebrew.${NC}"
                    echo -e "${YELLOW}Please install manually: python3, ffmpeg${NC}"
                }
            else
                log "WARNING" "Homebrew not found"
                echo -e "${YELLOW}Homebrew not found.${NC}"
                echo -e "${YELLOW}Please ensure you have Python 3.7+ and ffmpeg installed.${NC}"
                echo -e "${YELLOW}We recommend installing Homebrew (https://brew.sh)${NC}"
            fi
            ;;
        *)
            log "WARNING" "Unsupported OS, manual installation required"
            echo -e "${YELLOW}Unsupported OS. Please install dependencies manually:${NC}"
            echo -e "${YELLOW}1. Python 3.7 or higher${NC}"
            echo -e "${YELLOW}2. pip (Python package manager)${NC}"
            echo -e "${YELLOW}3. ffmpeg${NC}"
            ;;
    esac
    
    log "INFO" "System dependencies installation completed"
    echo -e "${GREEN}System dependencies installation completed.${NC}"
}

# Setup Python virtual environment
setup_python_environment() {
    local venv_dir="$1"
    local project_dir="$2"
    
    log "INFO" "Setting up Python virtual environment at $venv_dir"
    echo -e "${CYAN}Setting up Python virtual environment...${NC}"
    
    # Create virtual environment
    if [[ ! -d "$venv_dir" ]]; then
        log "INFO" "Creating new virtual environment"
        python3 -m venv "$venv_dir" || {
            log "ERROR" "Failed to create virtual environment"
            echo -e "${RED}Failed to create virtual environment.${NC}"
            exit 1
        }
    else
        log "INFO" "Virtual environment already exists at $venv_dir"
        echo -e "${YELLOW}Virtual environment already exists.${NC}"
    fi
    
    # Activate virtual environment
    log "INFO" "Activating virtual environment"
    source "$venv_dir/bin/activate" || {
        log "ERROR" "Failed to activate virtual environment"
        echo -e "${RED}Failed to activate virtual environment.${NC}"
        exit 1
    }
    
    # Update pip
    log "INFO" "Updating pip in virtual environment"
    pip install --upgrade pip || {
        log "WARNING" "Failed to upgrade pip"
        echo -e "${YELLOW}Warning: Failed to upgrade pip.${NC}"
    }
    
    # Install dependencies
    log "INFO" "Installing Python dependencies from $project_dir"
    (cd "$project_dir" && pip install -e .) || {
        log "ERROR" "Failed to install Python dependencies"
        echo -e "${RED}Failed to install Python dependencies.${NC}"
        exit 1
    }
    
    log "INFO" "Python virtual environment setup completed"
    echo -e "${GREEN}Python virtual environment setup completed.${NC}"
}

# Install as a Python application
install_application() {
    local install_dir="$1"
    local venv_dir="$2"
    local project_dir="$3"
    
    log "INFO" "Installing Python application"
    echo -e "${CYAN}Installing Python application...${NC}"
    
    # Create launcher script
    cat > "$install_dir/video-analyzer" <<EOF
#!/usr/bin/env bash
source "$venv_dir/bin/activate"
python -m video_analyzer "\$@"
deactivate
EOF

    chmod +x "$install_dir/video-analyzer"
    
    # Create symlink in ~/bin if it exists and is in PATH
    if [[ -d "$HOME/bin" ]]; then
        if [[ ":$PATH:" == *":$HOME/bin:"* ]]; then
            log "INFO" "Creating symlink in ~/bin"
            ln -sf "$install_dir/video-analyzer" "$HOME/bin/video-analyzer" || {
                log "WARNING" "Failed to create symlink in ~/bin"
                echo -e "${YELLOW}Warning: Failed to create symlink in ~/bin.${NC}"
            }
            echo -e "${GREEN}Created symlink in ~/bin.${NC}"
        fi
    fi
    
    log "INFO" "Python application installed successfully"
    echo -e "${GREEN}Python application installed successfully!${NC}"
    echo -e "${CYAN}You can run it with:${NC} $install_dir/video-analyzer"
}

# Build standalone executable
build_executable() {
    local install_dir="$1"
    local venv_dir="$2"
    local project_dir="$3"
    
    log "INFO" "Building standalone executable"
    echo -e "${YELLOW}Building standalone executable...${NC}"
    
    # Activate virtual environment
    log "INFO" "Activating virtual environment"
    source "$venv_dir/bin/activate" || {
        log "ERROR" "Failed to activate virtual environment"
        echo -e "${RED}Failed to activate virtual environment.${NC}"
        exit 1
    }
    
    # Install development dependencies
    log "INFO" "Installing development dependencies"
    (cd "$project_dir" && pip install -e ".[dev]") || {
        log "WARNING" "Failed to install development dependencies"
        echo -e "${YELLOW}Warning: Failed to install development dependencies.${NC}"
    }
    
    # Run build script
    log "INFO" "Running build script"
    (cd "$project_dir" && python build.py) || {
        log "ERROR" "Failed to build executable"
        echo -e "${RED}Failed to build standalone executable.${NC}"
        echo -e "${YELLOW}Falling back to Python script version.${NC}"
        
        # Fallback: create launcher script
        log "INFO" "Falling back to Python script version"
        install_application "$install_dir" "$venv_dir" "$project_dir"
        return 1
    }
    
    # Copy executable to install directory
    os=$(detect_os)
    arch=$(detect_arch)
    
    local executable=""
    if [[ "$os" == "macos" ]]; then
        executable="$project_dir/dist/video-analyzer-macos"
    else
        executable="$project_dir/dist/video-analyzer"
    fi
    
    if [[ -f "$executable" ]]; then
        log "INFO" "Copying executable to $install_dir"
        cp "$executable" "$install_dir/"
        chmod +x "$install_dir/video-analyzer"
        log "INFO" "Standalone executable built successfully"
        echo -e "${GREEN}Standalone executable built successfully!${NC}"
        echo -e "${CYAN}You can find it at:${NC} $install_dir/video-analyzer"
    else
        log "ERROR" "Executable not found at $executable"
        echo -e "${RED}Failed to build standalone executable.${NC}"
        echo -e "${YELLOW}Falling back to Python script version.${NC}"
        
        # Fallback: create launcher script
        log "INFO" "Falling back to Python script version"
        install_application "$install_dir" "$venv_dir" "$project_dir"
    fi
    
    # Deactivate virtual environment
    log "INFO" "Deactivating virtual environment"
    deactivate
}

# Main installation function
main() {
    # Initialize logging
    init_logging
    
    # Display banner
    display_banner
    
    echo -e "${CYAN}Welcome to the Video Analyzer Installation Assistant!${NC}"
    echo -e "${CYAN}This script will help you install Video Analyzer on your system.${NC}"
    echo
    
    # Detect OS and architecture
    local os=$(detect_os)
    local arch=$(detect_arch)
    log "INFO" "Detected OS: $os, Architecture: $arch"
    echo -e "${CYAN}Detected operating system:${NC} $os"
    echo -e "${CYAN}Detected architecture:${NC} $arch"
    echo
    
    # Check if we're running as root and set proper default home directory
    local default_home
    if [[ $EUID -eq 0 && "$HOME" == "/" ]]; then
        log "WARNING" "Running as root with HOME=/. Using /opt instead."
        default_home="/opt"
    else
        default_home="$HOME"
    fi
    
    # Ask for installation directory
    local default_install_dir="$default_home/.local/video-analyzer"
    read -p "Enter installation directory [$default_install_dir]: " install_dir
    install_dir=${install_dir:-$default_install_dir}
    log "INFO" "Selected installation directory: $install_dir"
    
    # Create installation directory
    mkdir -p "$install_dir"
    log "INFO" "Created installation directory: $install_dir"
    echo -e "${GREEN}Installation directory created: $install_dir${NC}"
    
    # Project download directory (where the git repo will be cloned)
    local project_dir="$install_dir/source"
    
    # Virtual environment directory
    local venv_dir="$install_dir/venv"
    
    # Ask for installation type
    echo -e "${CYAN}Installation Options:${NC}"
    echo "1. Python package (recommended)"
    echo "2. Standalone executable (experimental)"
    read -p "Select an option [1-2]: " -n 1 -r
    echo
    log "INFO" "Selected installation option: $REPLY"
    
    # Install dependencies
    install_system_dependencies "$os"
    
    # Download project from GitHub
    if ! download_project "$project_dir"; then
        log "ERROR" "Failed to download project. Installation aborted."
        echo -e "${RED}Installation failed. See log for details: $LOG_FILE${NC}"
        exit 1
    fi
    
    # Setup Python environment
    setup_python_environment "$venv_dir" "$project_dir"
    
    if [[ $REPLY =~ ^[2]$ ]]; then
        # Standalone executable
        build_executable "$install_dir" "$venv_dir" "$project_dir"
    else
        # Python package (default)
        install_application "$install_dir" "$venv_dir" "$project_dir"
    fi
    
    echo
    log "INFO" "Installation completed successfully"
    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo -e "${CYAN}Thank you for installing Video Analyzer!${NC}"
    echo -e "${CYAN}Installation log available at: $LOG_FILE${NC}"
}

# Execute main function
main 