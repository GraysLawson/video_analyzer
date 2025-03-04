#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Setup logging
LOG_FILE="/tmp/video-analyzer-install-$(date +%Y%m%d-%H%M%S).log"
VERBOSE=false

# Log message function
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Log to file
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    # If verbose, also print to stdout
    if [[ "$VERBOSE" == true || "$level" == "ERROR" ]]; then
        case "$level" in
            "ERROR") echo -e "${RED}[$level] $message${NC}" ;;
            "WARNING") echo -e "${YELLOW}[$level] $message${NC}" ;;
            "INFO") echo -e "${GREEN}[$level] $message${NC}" ;;
            *) echo "[$level] $message" ;;
        esac
    fi
}

# Initialize log file
init_logging() {
    echo "=== Video Analyzer Installation Log ===" > "$LOG_FILE"
    echo "Started at: $(date)" >> "$LOG_FILE"
    log "INFO" "Logging initialized to $LOG_FILE"
    log "INFO" "Working directory: $(pwd)"
}

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
    log "INFO" "Installing system dependencies for $1"
    
    local os=$1
    case $os in
        macos)
            if ! command_exists brew; then
                echo -e "${YELLOW}Installing Homebrew...${NC}"
                log "INFO" "Installing Homebrew"
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew update
            if ! command_exists python3; then
                log "INFO" "Installing Python via Homebrew"
                brew install python
            fi
            ;;
        debian)
            log "INFO" "Updating apt repositories"
            sudo apt-get update
            log "INFO" "Installing Python and development packages"
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        redhat)
            if command_exists dnf; then
                log "INFO" "Installing Python packages via dnf"
                sudo dnf install -y python3 python3-pip python3-devel
            else
                log "INFO" "Installing Python packages via yum"
                sudo yum install -y python3 python3-pip python3-devel
            fi
            ;;
        arch)
            log "INFO" "Installing Python packages via pacman"
            sudo pacman -Sy python python-pip
            ;;
        *)
            log "ERROR" "Unsupported operating system. Please install Python 3.7+ manually."
            echo -e "${RED}Unsupported operating system. Please install Python 3.7+ manually.${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}System dependencies installed successfully!${NC}"
    log "INFO" "System dependencies installed successfully"
}

# Download the project from GitHub
download_project() {
    local project_dir="$1"
    log "INFO" "Downloading project to $project_dir"
    
    # Create project directory if it doesn't exist
    if [[ ! -d "$project_dir" ]]; then
        log "INFO" "Creating project directory $project_dir"
        mkdir -p "$project_dir"
    fi
    
    # Clone or update the repository
    if [[ -d "$project_dir/.git" ]]; then
        log "INFO" "Git repository already exists, pulling latest changes"
        echo -e "${YELLOW}Updating existing repository...${NC}"
        (cd "$project_dir" && git pull) || {
            log "ERROR" "Failed to update repository"
            echo -e "${RED}Failed to update repository.${NC}"
            return 1
        }
    else
        log "INFO" "Cloning repository from GitHub"
        echo -e "${YELLOW}Downloading from GitHub...${NC}"
        git clone https://github.com/GraysLawson/video_analyzer.git "$project_dir" || {
            log "ERROR" "Failed to clone repository"
            echo -e "${RED}Failed to clone repository.${NC}"
            return 1
        }
    fi
    
    # Check if the project files exist
    if [[ ! -f "$project_dir/setup.py" ]]; then
        log "ERROR" "Project files not found in $project_dir"
        echo -e "${RED}Project files not found. Installation failed.${NC}"
        return 1
    fi
    
    log "INFO" "Project download/update completed successfully"
    return 0
}

# Create virtual environment and install Python dependencies
setup_python_environment() {
    echo -e "${YELLOW}Setting up Python environment...${NC}"
    log "INFO" "Setting up Python environment"
    
    local venv_dir="$1"
    local project_dir="$2"
    
    # Check if Python 3.7+ is installed
    if ! command_exists python3; then
        log "ERROR" "Python 3 is not installed"
        echo -e "${RED}Python 3 is not installed. Please install Python 3.7 or higher.${NC}"
        exit 1
    fi
    
    # Check Python version
    local python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    local major_version=$(echo $python_version | cut -d. -f1)
    local minor_version=$(echo $python_version | cut -d. -f2)
    
    log "INFO" "Detected Python version: $python_version"
    
    if [[ $major_version -lt 3 || ($major_version -eq 3 && $minor_version -lt 7) ]]; then
        log "ERROR" "Python 3.7 or higher is required. Found version $python_version"
        echo -e "${RED}Python 3.7 or higher is required. You have Python $python_version.${NC}"
        exit 1
    fi
    
    # Create virtual environment
    log "INFO" "Creating virtual environment in $venv_dir"
    echo -e "${YELLOW}Creating virtual environment in $venv_dir...${NC}"
    python3 -m venv "$venv_dir" || {
        log "ERROR" "Failed to create virtual environment"
        echo -e "${RED}Failed to create virtual environment.${NC}"
        exit 1
    }
    
    # Activate virtual environment
    log "INFO" "Activating virtual environment"
    source "$venv_dir/bin/activate" || {
        log "ERROR" "Failed to activate virtual environment"
        echo -e "${RED}Failed to activate virtual environment.${NC}"
        exit 1
    }
    
    # Upgrade pip
    log "INFO" "Upgrading pip"
    pip install --upgrade pip || {
        log "WARNING" "Failed to upgrade pip, continuing with existing version"
    }
    
    # Install dependencies
    log "INFO" "Installing Python dependencies from $project_dir"
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    
    # Change to the project directory and install
    (cd "$project_dir" && pip install -e .) || {
        log "ERROR" "Failed to install Python dependencies"
        echo -e "${RED}Failed to install Python dependencies.${NC}"
        exit 1
    }
    
    log "INFO" "Python environment set up successfully"
    echo -e "${GREEN}Python environment set up successfully!${NC}"
}

# Install the application
install_application() {
    local install_dir="$1"
    local venv_dir="$2"
    local project_dir="$3"
    
    log "INFO" "Installing Video Analyzer to $install_dir"
    echo -e "${YELLOW}Installing Video Analyzer...${NC}"
    
    # Create launcher script
    local launcher="$install_dir/video-analyzer"
    
    log "INFO" "Creating launcher script at $launcher"
    echo "#!/bin/bash" > "$launcher"
    echo "source \"$venv_dir/bin/activate\"" >> "$launcher"
    echo "python -m video_analyzer \"\$@\"" >> "$launcher"
    echo "deactivate" >> "$launcher"
    
    chmod +x "$launcher"
    
    log "INFO" "Installation completed successfully"
    echo -e "${GREEN}Installation complete!${NC}"
    echo -e "${CYAN}You can now run Video Analyzer by typing:${NC}"
    echo -e "${CYAN}$launcher${NC}"
    
    # Ask if user wants to create a symbolic link
    read -p "Do you want to create a symbolic link in /usr/local/bin? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ -w /usr/local/bin ]]; then
            log "INFO" "Creating symbolic link in /usr/local/bin"
            ln -sf "$launcher" /usr/local/bin/video-analyzer
            echo -e "${GREEN}Symbolic link created. You can now run 'video-analyzer' from anywhere.${NC}"
        else
            log "INFO" "Creating symbolic link with sudo"
            echo -e "${YELLOW}Creating symbolic link with sudo...${NC}"
            sudo ln -sf "$launcher" /usr/local/bin/video-analyzer
            echo -e "${GREEN}Symbolic link created. You can now run 'video-analyzer' from anywhere.${NC}"
        fi
    fi
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