import os
import platform
import subprocess
import sys

def run_command(command):
    """Run a command and return its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        return False

def build_executable():
    """Build the executable for the current platform."""
    system = platform.system().lower()
    
    # Install development dependencies
    print("Installing development dependencies...")
    if not run_command("pip install -e .[dev]"):
        return False

    # Create spec file with custom options
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['video_analyzer/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='video-analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("video_analyzer.spec", "w") as f:
        f.write(spec_content.strip())

    # Build the executable
    print(f"Building executable for {system}...")
    if not run_command("pyinstaller --clean video_analyzer.spec"):
        return False

    # Create dist directory if it doesn't exist
    os.makedirs("dist", exist_ok=True)

    print("\nBuild completed successfully!")
    print("\nExecutable location:")
    if system == "windows":
        print("  dist\\video-analyzer.exe")
    else:
        print("  dist/video-analyzer")
    
    return True

if __name__ == "__main__":
    if build_executable():
        print("\nYou can now distribute the executable from the 'dist' directory.")
    else:
        print("\nBuild failed. Please check the error messages above.", file=sys.stderr)
        sys.exit(1) 