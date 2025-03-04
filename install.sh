#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Repository information
REPO_OWNER="GraysLawson"
REPO_NAME="video_analyzer"
API_URL="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest"

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

# Function to check GLIBC version
check_glibc_version() {
    local version=$(ldd --version 2>&1 | head -n1 | grep -oP 'GLIBC \K[\d.]+')
    echo "$version"
}

# Function to install using pip
install_using_pip() {
    echo -e "${YELLOW}Attempting installation using pip...${NC}"
    
    # Check if pip is installed
    if ! command_exists pip; then
        echo -e "${YELLOW}Installing pip...${NC}"
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3-pip
        elif command_exists yum; then
            sudo yum install -y python3-pip
        elif command_exists dnf; then
            sudo dnf install -y python3-pip
        else
            echo -e "${RED}Could not install pip. Please install python3-pip manually.${NC}"
            exit 1
        fi
    fi

    # Create virtual environment
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv /usr/local/video-analyzer-env

    # Activate virtual environment
    source /usr/local/video-analyzer-env/bin/activate

    # Install the package
    echo -e "${YELLOW}Installing video-analyzer...${NC}"
    pip install video-analyzer

    # Create wrapper script
    echo -e "${YELLOW}Creating wrapper script...${NC}"
    cat > /usr/local/bin/video-analyzer << 'EOF'
#!/bin/bash
source /usr/local/video-analyzer-env/bin/activate
python -m video_analyzer "$@"
EOF

    # Make wrapper script executable
    chmod +x /usr/local/bin/video-analyzer

    echo -e "${GREEN}Installation completed successfully using pip!${NC}"
    echo -e "${YELLOW}You can now run 'video-analyzer' from anywhere.${NC}"
}

# Function to install from source
install_from_source() {
    echo -e "${YELLOW}Attempting installation from source...${NC}"
    
    # Check if git is installed
    if ! command_exists git; then
        echo -e "${YELLOW}Installing git...${NC}"
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y git
        elif command_exists yum; then
            sudo yum install -y git
        elif command_exists dnf; then
            sudo dnf install -y git
        else
            echo -e "${RED}Could not install git. Please install git manually.${NC}"
            exit 1
        fi
    fi

    # Create temporary directory
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"

    # Clone repository
    echo -e "${YELLOW}Cloning repository...${NC}"
    git clone https://github.com/${REPO_OWNER}/${REPO_NAME}.git
    cd ${REPO_NAME}

    # Create virtual environment
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv /usr/local/video-analyzer-env

    # Activate virtual environment
    source /usr/local/video-analyzer-env/bin/activate

    # Install the package
    echo -e "${YELLOW}Installing dependencies and package...${NC}"
    pip install -e .

    # Create wrapper script
    echo -e "${YELLOW}Creating wrapper script...${NC}"
    cat > /usr/local/bin/video-analyzer << 'EOF'
#!/bin/bash
source /usr/local/video-analyzer-env/bin/activate
python -m video_analyzer "$@"
EOF

    # Make wrapper script executable
    chmod +x /usr/local/bin/video-analyzer

    # Cleanup
    cd - >/dev/null
    rm -rf "$temp_dir"

    echo -e "${GREEN}Installation completed successfully from source!${NC}"
    echo -e "${YELLOW}You can now run 'video-analyzer' from anywhere.${NC}"
}

# Main installation function
main() {
    local arch=$(detect_arch)
    local os=$(detect_os)
    local install_dir="/usr/local/bin"

    echo -e "${GREEN}Detected system: $os on $arch${NC}"

    # Check for Python
    if ! command_exists python3; then
        echo -e "${YELLOW}Installing Python 3...${NC}"
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-venv
        elif command_exists yum; then
            sudo yum install -y python3 python3-venv
        elif command_exists dnf; then
            sudo dnf install -y python3 python3-venv
        else
            echo -e "${RED}Could not install Python 3. Please install python3 and python3-venv manually.${NC}"
            exit 1
        fi
    fi

    # Try pip installation first
    if install_using_pip; then
        exit 0
    fi

    echo -e "${YELLOW}Pip installation failed, trying source installation...${NC}"
    
    # Try source installation
    if install_from_source; then
        exit 0
    fi

    echo -e "${RED}All installation methods failed.${NC}"
    echo -e "${RED}Please report this issue at: https://github.com/${REPO_OWNER}/${REPO_NAME}/issues${NC}"
    exit 1
}

# Run main installation
main 