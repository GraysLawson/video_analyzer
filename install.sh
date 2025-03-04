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

# Function to get latest release information
get_latest_release() {
    if ! command_exists curl; then
        echo -e "${RED}Error: curl is required but not installed.${NC}"
        echo "Please install curl first:"
        echo "  Debian/Ubuntu: sudo apt-get install curl"
        echo "  RHEL/CentOS: sudo yum install curl"
        echo "  macOS: brew install curl"
        exit 1
    fi

    echo -e "${YELLOW}Fetching latest release information...${NC}"
    if ! release_info=$(curl -sL $API_URL); then
        echo -e "${RED}Error: Failed to fetch release information${NC}"
        exit 1
    fi

    if [[ $release_info == *"Not Found"* ]]; then
        echo -e "${RED}Error: No releases found${NC}"
        echo "Please check https://github.com/${REPO_OWNER}/${REPO_NAME}/releases"
        exit 1
    fi

    echo "$release_info"
}

# Function to download file with verification
download_file() {
    local url=$1
    local output=$2
    local description=$3

    echo -e "${YELLOW}Downloading ${description}...${NC}"
    if ! curl -L -o "$output" "$url"; then
        echo -e "${RED}Error: Failed to download ${description}${NC}"
        echo "URL: $url"
        return 1
    fi
    return 0
}

# Function to verify binary
verify_binary() {
    local binary=$1
    local checksum_file="${binary}.sha256"
    local signature_file="${binary}.sig"

    echo -e "${YELLOW}Verifying binary integrity...${NC}"
    
    if [[ ! -f "$binary" ]]; then
        echo -e "${RED}Error: Binary file not found${NC}"
        return 1
    fi

    if [[ ! -f "$checksum_file" ]]; then
        echo -e "${RED}Error: Checksum file not found${NC}"
        return 1
    }

    if command_exists sha256sum; then
        if ! sha256sum -c "${checksum_file}"; then
            echo -e "${RED}SHA256 verification failed!${NC}"
            return 1
        fi
    elif command_exists shasum; then
        if ! shasum -a 256 -c "${checksum_file}"; then
            echo -e "${RED}SHA256 verification failed!${NC}"
            return 1
        fi
    else
        echo -e "${RED}Error: No SHA256 verification tool found${NC}"
        return 1
    fi

    if [[ -f "${signature_file}" ]] && command_exists gpg; then
        echo -e "${YELLOW}Verifying GPG signature...${NC}"
        if ! gpg --verify "${signature_file}" "${binary}"; then
            echo -e "${RED}GPG signature verification failed!${NC}"
            return 1
        fi
    fi

    return 0
}

# Main installation function
main() {
    local arch=$(detect_arch)
    local os=$(detect_os)
    local install_dir="/usr/local/bin"
    local binary_name
    local release_info

    echo -e "${GREEN}Detected system: $os on $arch${NC}"

    # Check for required tools
    if ! command_exists curl; then
        echo -e "${RED}Error: curl is required but not installed${NC}"
        exit 1
    fi

    # Determine binary name based on OS and architecture
    case $os in
        linux)
            if [[ $arch == "unsupported" ]]; then
                echo -e "${RED}Unsupported architecture: $(uname -m)${NC}"
                exit 1
            fi
            binary_name="video-analyzer-${arch}"
            
            # Check GLIBC version for Linux
            local glibc_version=$(check_glibc_version)
            echo -e "${GREEN}Detected GLIBC version: $glibc_version${NC}"
            
            # Verify minimum GLIBC version (2.17 for Debian 10+)
            if [[ $(echo "$glibc_version" | cut -d. -f1,2 | sed 's/\.//') -lt 217 ]]; then
                echo -e "${RED}Error: GLIBC version too old. Minimum required version is 2.17${NC}"
                exit 1
            fi
            ;;
        macos)
            binary_name="video-analyzer-macos"
            ;;
        windows)
            binary_name="video-analyzer.exe"
            install_dir="$HOME/bin"
            ;;
        *)
            echo -e "${RED}Unsupported operating system${NC}"
            exit 1
            ;;
    esac

    # Get latest release information
    release_info=$(get_latest_release)
    if [[ $? -ne 0 ]]; then
        exit 1
    fi

    # Extract download URLs from release info
    local download_url=$(echo "$release_info" | grep -o "\"browser_download_url\": \"[^\"]*${binary_name}\"" | grep -o "https://[^\"]*")
    local checksum_url=$(echo "$release_info" | grep -o "\"browser_download_url\": \"[^\"]*${binary_name}.sha256\"" | grep -o "https://[^\"]*")
    local signature_url=$(echo "$release_info" | grep -o "\"browser_download_url\": \"[^\"]*${binary_name}.sig\"" | grep -o "https://[^\"]*")

    if [[ -z "$download_url" ]]; then
        echo -e "${RED}Error: Could not find download URL for ${binary_name}${NC}"
        echo "Please check https://github.com/${REPO_OWNER}/${REPO_NAME}/releases"
        exit 1
    fi

    # Create temporary directory
    local temp_dir=$(mktemp -d)
    cd "$temp_dir" || exit 1

    # Download files
    download_file "$download_url" "$binary_name" "binary" || exit 1
    download_file "$checksum_url" "${binary_name}.sha256" "checksum file" || exit 1
    if [[ $os == "linux" && ! -z "$signature_url" ]]; then
        download_file "$signature_url" "${binary_name}.sig" "signature file" || exit 1
    fi

    # Verify the binary
    if ! verify_binary "$binary_name"; then
        cd - >/dev/null
        rm -rf "$temp_dir"
        exit 1
    fi

    # Create installation directory if it doesn't exist
    if [[ ! -d "$install_dir" ]]; then
        sudo mkdir -p "$install_dir"
    fi

    # Install the binary
    echo -e "${YELLOW}Installing video analyzer...${NC}"
    sudo mv "$binary_name" "$install_dir/video-analyzer"
    sudo chmod +x "$install_dir/video-analyzer"

    # Cleanup
    cd - >/dev/null
    rm -rf "$temp_dir"

    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo -e "${YELLOW}You can now run 'video-analyzer' from anywhere.${NC}"
}

# Run main installation
main 