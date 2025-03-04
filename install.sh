#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Function to check GLIBC version
check_glibc_version() {
    local version=$(ldd --version 2>&1 | head -n1 | grep -oP 'GLIBC \K[\d.]+')
    echo "$version"
}

# Function to verify binary
verify_binary() {
    local binary=$1
    local checksum_file="${binary}.sha256"
    local signature_file="${binary}.sig"

    echo -e "${YELLOW}Verifying binary integrity...${NC}"
    
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum -c "${checksum_file}" || {
            echo -e "${RED}SHA256 verification failed!${NC}"
            exit 1
        }
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 -c "${checksum_file}" || {
            echo -e "${RED}SHA256 verification failed!${NC}"
            exit 1
        }
    fi

    if [[ -f "${signature_file}" ]] && command -v gpg >/dev/null 2>&1; then
        echo -e "${YELLOW}Verifying GPG signature...${NC}"
        gpg --verify "${signature_file}" "${binary}" || {
            echo -e "${RED}GPG signature verification failed!${NC}"
            exit 1
        }
    fi
}

# Main installation function
main() {
    local arch=$(detect_arch)
    local os=$(detect_os)
    local install_dir="/usr/local/bin"
    local binary_name

    echo -e "${GREEN}Detected system: $os on $arch${NC}"

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

    # Create installation directory if it doesn't exist
    if [[ ! -d "$install_dir" ]]; then
        sudo mkdir -p "$install_dir"
    fi

    # Download binary and verification files
    echo -e "${YELLOW}Downloading video analyzer binary...${NC}"
    curl -L -o "$binary_name" "https://github.com/GraysLawson/video_analyzer/releases/latest/download/$binary_name"
    curl -L -o "$binary_name.sha256" "https://github.com/GraysLawson/video_analyzer/releases/latest/download/$binary_name.sha256"
    
    if [[ $os == "linux" ]]; then
        curl -L -o "$binary_name.sig" "https://github.com/GraysLawson/video_analyzer/releases/latest/download/$binary_name.sig"
    fi

    # Verify the binary
    verify_binary "$binary_name"

    # Install the binary
    echo -e "${YELLOW}Installing video analyzer...${NC}"
    sudo mv "$binary_name" "$install_dir/video-analyzer"
    sudo chmod +x "$install_dir/video-analyzer"

    # Cleanup
    rm -f "$binary_name.sha256" "$binary_name.sig"

    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo -e "${YELLOW}You can now run 'video-analyzer' from anywhere.${NC}"
}

# Run main installation
main 