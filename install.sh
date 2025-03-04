#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
display_banner() {
    echo -e "${BLUE}"
    echo "##############################################"
    echo "#                                            #"
    echo "#            Video Analyzer                  #"
    echo "#        Installation Assistant              #"
    echo "#                                            #"
    echo "##############################################"
    echo -e "${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ -f /etc/debian_version ]]; then
        echo "debian"
    elif [[ -f /etc/redhat-release ]]; then
        echo "redhat"
    elif [[ -f /etc/arch-release ]]; then
        echo "arch"
    elif command_exists pacman; then
        echo "arch"
    elif command_exists apt-get; then
        echo "debian"
    elif command_exists dnf || command_exists yum; then
        echo "redhat"
    elif command_exists brew; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Detect architecture
detect_arch() {
    local arch=$(uname -m)
    case $arch in
        x86_64)
            echo "x64"
            ;;
        i386|i686)
            echo "x86"
            ;;
        arm*|aarch*)
            echo "arm"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Install system dependencies based on OS
install_system_dependencies() {
    echo -e "${YELLOW}Installing system dependencies...${NC}"
    
    local os=$1
    case $os in
        macos)
            if ! command_exists brew; then
                echo -e "${YELLOW}Installing Homebrew...${NC}"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew update
            if ! command_exists python3; then
                brew install python
            fi
            ;;
        debian)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        redhat)
            if command_exists dnf; then
                sudo dnf install -y python3 python3-pip python3-devel
            else
                sudo yum install -y python3 python3-pip python3-devel
            fi
            ;;
        arch)
            sudo pacman -Sy python python-pip
            ;;
        *)
            echo -e "${RED}Unsupported operating system. Please install Python 3.7+ manually.${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}System dependencies installed successfully!${NC}"
}

# Create virtual environment and install Python dependencies
setup_python_environment() {
    echo -e "${YELLOW}Setting up Python environment...${NC}"
    
    # Check if Python 3.7+ is installed
    if ! command_exists python3; then
        echo -e "${RED}Python 3 is not installed. Please install Python 3.7 or higher.${NC}"
        exit 1
    fi
    
    # Check Python version
    local python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    local major_version=$(echo $python_version | cut -d. -f1)
    local minor_version=$(echo $python_version | cut -d. -f2)
    
    if [[ $major_version -lt 3 || ($major_version -eq 3 && $minor_version -lt 7) ]]; then
        echo -e "${RED}Python 3.7 or higher is required. You have Python $python_version.${NC}"
        exit 1
    fi
    
    # Create virtual environment
    local venv_dir=$1
    echo -e "${YELLOW}Creating virtual environment in $venv_dir...${NC}"
    python3 -m venv "$venv_dir"
    
    # Activate virtual environment
    source "$venv_dir/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -e .
    
    echo -e "${GREEN}Python environment set up successfully!${NC}"
}

# Install the application
install_application() {
    local install_dir=$1
    local venv_dir=$2
    
    echo -e "${YELLOW}Installing Video Analyzer...${NC}"
    
    # Create launcher script
    local launcher="$install_dir/video-analyzer"
    
    echo "#!/bin/bash" > "$launcher"
    echo "source \"$venv_dir/bin/activate\"" >> "$launcher"
    echo "python -m video_analyzer \"\$@\"" >> "$launcher"
    echo "deactivate" >> "$launcher"
    
    chmod +x "$launcher"
    
    echo -e "${GREEN}Installation complete!${NC}"
    echo -e "${CYAN}You can now run Video Analyzer by typing:${NC}"
    echo -e "${CYAN}$launcher${NC}"
    
    # Ask if user wants to create a symbolic link
    read -p "Do you want to create a symbolic link in /usr/local/bin? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ -w /usr/local/bin ]]; then
            ln -sf "$launcher" /usr/local/bin/video-analyzer
            echo -e "${GREEN}Symbolic link created. You can now run 'video-analyzer' from anywhere.${NC}"
        else
            echo -e "${YELLOW}Creating symbolic link with sudo...${NC}"
            sudo ln -sf "$launcher" /usr/local/bin/video-analyzer
            echo -e "${GREEN}Symbolic link created. You can now run 'video-analyzer' from anywhere.${NC}"
        fi
    fi
}

# Build standalone executable
build_executable() {
    local install_dir=$1
    local venv_dir=$2
    
    echo -e "${YELLOW}Building standalone executable...${NC}"
    
    # Activate virtual environment
    source "$venv_dir/bin/activate"
    
    # Install development dependencies
    pip install -e ".[dev]"
    
    # Run build script
    python build.py
    
    # Copy executable to install directory
    os=$(detect_os)
    arch=$(detect_arch)
    
    local executable=""
    if [[ "$os" == "macos" ]]; then
        executable="dist/video-analyzer-macos"
    else
        executable="dist/video-analyzer"
    fi
    
    if [[ -f "$executable" ]]; then
        cp "$executable" "$install_dir/"
        chmod +x "$install_dir/video-analyzer"
        echo -e "${GREEN}Standalone executable built successfully!${NC}"
        echo -e "${CYAN}You can find it at:${NC} $install_dir/video-analyzer"
    else
        echo -e "${RED}Failed to build standalone executable.${NC}"
        echo -e "${YELLOW}Falling back to Python script version.${NC}"
    fi
    
    # Deactivate virtual environment
    deactivate
}

# Main installation function
main() {
    display_banner
    
    echo -e "${CYAN}Welcome to the Video Analyzer Installation Assistant!${NC}"
    echo -e "${CYAN}This script will help you install Video Analyzer on your system.${NC}"
    echo
    
    # Detect OS and architecture
    local os=$(detect_os)
    local arch=$(detect_arch)
    echo -e "${CYAN}Detected operating system:${NC} $os"
    echo -e "${CYAN}Detected architecture:${NC} $arch"
    echo
    
    # Ask for installation directory
    local default_install_dir="$HOME/.local/video-analyzer"
    read -p "Enter installation directory [$default_install_dir]: " install_dir
    install_dir=${install_dir:-$default_install_dir}
    
    # Create installation directory
    mkdir -p "$install_dir"
    echo -e "${GREEN}Installation directory created: $install_dir${NC}"
    
    # Virtual environment directory
    local venv_dir="$install_dir/venv"
    
    # Ask for installation type
    echo -e "${CYAN}Installation Options:${NC}"
    echo "1. Python package (recommended)"
    echo "2. Standalone executable (experimental)"
    read -p "Select an option [1-2]: " -n 1 -r
    echo
    
    # Install dependencies
    install_system_dependencies "$os"
    
    if [[ $REPLY =~ ^[2]$ ]]; then
        # Standalone executable
        setup_python_environment "$venv_dir"
        build_executable "$install_dir" "$venv_dir"
    else
        # Python package (default)
        setup_python_environment "$venv_dir"
        install_application "$install_dir" "$venv_dir"
    fi
    
    echo
    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo -e "${CYAN}Thank you for installing Video Analyzer!${NC}"
}

# Execute main function
main 