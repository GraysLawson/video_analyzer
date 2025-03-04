# Video Analyzer Binary Verification Script
Write-Host "Video Analyzer Binary Verification Tool" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Check if video-analyzer.exe exists
if (-not (Test-Path "video-analyzer.exe")) {
    Write-Host "Error: video-analyzer.exe not found in current directory" -ForegroundColor Red
    exit 1
}

# Verify SHA256
if (Test-Path "video-analyzer.exe.sha256") {
    Write-Host "`nVerifying SHA256 checksum..." -ForegroundColor Yellow
    $fileHash = Get-FileHash -Algorithm SHA256 video-analyzer.exe
    $expectedHash = Get-Content video-analyzer.exe.sha256
    if ($fileHash.Hash -eq $expectedHash) {
        Write-Host "✓ SHA256 checksum verified successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ SHA256 checksum verification failed" -ForegroundColor Red
    }
} else {
    Write-Host "`n⚠️ SHA256 file not found, skipping checksum verification" -ForegroundColor Yellow
}

# Extract and display embedded information
Write-Host "`nExtracting file information..." -ForegroundColor Yellow
$fileInfo = Get-Item "video-analyzer.exe"
$versionInfo = $fileInfo.VersionInfo

Write-Host "`nFile Details:" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan
Write-Host "Product Name: $($versionInfo.ProductName)"
Write-Host "Description: $($versionInfo.FileDescription)"
Write-Host "Version: $($versionInfo.FileVersion)"
Write-Host "Copyright: $($versionInfo.LegalCopyright)"
Write-Host "Original Filename: $($versionInfo.OriginalFilename)"
Write-Host "Company: $($versionInfo.CompanyName)"

Write-Host "`nSecurity Information:" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host "This is an open-source tool available at:"
Write-Host "https://github.com/yourusername/video_analyzer" -ForegroundColor Blue

Write-Host "`nIf Windows SmartScreen shows a warning:" -ForegroundColor Yellow
Write-Host "1. This is normal for new, unsigned applications"
Write-Host "2. Click 'More info' in the SmartScreen popup"
Write-Host "3. Click 'Run anyway'"
Write-Host "4. The source code is available for inspection at the GitHub repository"

Write-Host "`nAlternative Installation:" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host "If you prefer not to run the binary, you can install from source:"
Write-Host "1. Clone: git clone https://github.com/yourusername/video_analyzer"
Write-Host "2. Install: pip install -e ."
Write-Host "3. Run: python -m video_analyzer" 