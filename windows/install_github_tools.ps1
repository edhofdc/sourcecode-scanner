# Script untuk menginstal Semgrep, Grype, dan TruffleHog langsung dari GitHub
# Jalankan sebagai Administrator

Write-Host "Installing Security Tools from GitHub Releases..." -ForegroundColor Green
Write-Host "Source: Official GitHub repositories" -ForegroundColor Cyan

# Create tools directory
$toolsDir = "$env:LOCALAPPDATA\SecurityTools"
if (!(Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir -Force
    Write-Host "Created tools directory: $toolsDir" -ForegroundColor Green
}

# Function to add to PATH
function Add-ToPath {
    param([string]$Directory)
    
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$Directory*") {
        $newPath = "$currentPath;$Directory"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "Added $Directory to PATH" -ForegroundColor Green
        return $true
    }
    return $false
}

# Install Semgrep from GitHub
Write-Host "`n1. Installing Semgrep from GitHub..." -ForegroundColor Yellow
try {
    # For Semgrep, we'll use the official PyPI package but from GitHub source
    Write-Host "Installing Semgrep from GitHub source..." -ForegroundColor Yellow
    
    # Check if git is available
    try {
        git --version | Out-Null
        # Install from GitHub source
        pip install git+https://github.com/semgrep/semgrep.git
        Write-Host "✅ Semgrep installed from GitHub source" -ForegroundColor Green
    } catch {
        Write-Host "Git not found, using PyPI package..." -ForegroundColor Yellow
        pip install semgrep
        Write-Host "✅ Semgrep installed from PyPI" -ForegroundColor Green
    }
    
    Write-Host "Source: https://github.com/semgrep/semgrep" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to install Semgrep: $($_.Exception.Message)" -ForegroundColor Red
}

# Install Grype from GitHub
Write-Host "`n2. Installing Grype from GitHub..." -ForegroundColor Yellow
try {
    $grypeDir = "$toolsDir\grype"
    if (!(Test-Path $grypeDir)) {
        New-Item -ItemType Directory -Path $grypeDir -Force
    }
    
    # Get latest release info
    Write-Host "Fetching latest Grype release..." -ForegroundColor Yellow
    $grypeUrl = "https://github.com/anchore/grype/releases/latest/download/grype_windows_amd64.zip"
    $grypeZip = "$env:TEMP\grype.zip"
    
    # Download
    Write-Host "Downloading Grype binary..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $grypeUrl -OutFile $grypeZip -UseBasicParsing
    
    # Extract
    Write-Host "Extracting Grype..." -ForegroundColor Yellow
    Expand-Archive -Path $grypeZip -DestinationPath $grypeDir -Force
    
    # Add to PATH
    Add-ToPath -Directory $grypeDir
    
    # Clean up
    Remove-Item $grypeZip -Force
    
    Write-Host "✅ Grype installed from GitHub releases" -ForegroundColor Green
    Write-Host "Source: https://github.com/anchore/grype" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to install Grype: $($_.Exception.Message)" -ForegroundColor Red
}

# Install TruffleHog from GitHub
Write-Host "`n3. Installing TruffleHog from GitHub..." -ForegroundColor Yellow
try {
    $truffleDir = "$toolsDir\trufflehog"
    if (!(Test-Path $truffleDir)) {
        New-Item -ItemType Directory -Path $truffleDir -Force
    }
    
    # Get latest release
    Write-Host "Fetching latest TruffleHog release..." -ForegroundColor Yellow
    $truffleUrl = "https://github.com/trufflesecurity/trufflehog/releases/latest/download/trufflehog_windows_amd64.tar.gz"
    $truffleTar = "$env:TEMP\trufflehog.tar.gz"
    
    # Download
    Write-Host "Downloading TruffleHog binary..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $truffleUrl -OutFile $truffleTar -UseBasicParsing
    
    # Extract using tar (Windows 10+)
    Write-Host "Extracting TruffleHog..." -ForegroundColor Yellow
    tar -xzf $truffleTar -C $truffleDir
    
    # Add to PATH
    Add-ToPath -Directory $truffleDir
    
    # Clean up
    Remove-Item $truffleTar -Force
    
    Write-Host "✅ TruffleHog installed from GitHub releases" -ForegroundColor Green
    Write-Host "Source: https://github.com/trufflesecurity/trufflehog" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to install TruffleHog: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Alternative: Use Docker - docker pull trufflesecurity/trufflehog:latest" -ForegroundColor Yellow
}

# Summary
Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "INSTALLATION SUMMARY" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host "`nTools installed to: $toolsDir" -ForegroundColor Cyan
Write-Host "`nGitHub Sources:" -ForegroundColor Green
Write-Host "  • Semgrep: https://github.com/semgrep/semgrep" -ForegroundColor Cyan
Write-Host "  • Grype: https://github.com/anchore/grype" -ForegroundColor Cyan
Write-Host "  • TruffleHog: https://github.com/trufflesecurity/trufflehog" -ForegroundColor Cyan

Write-Host "`n🔄 IMPORTANT: Please restart your terminal/PowerShell" -ForegroundColor Yellow
Write-Host "`n✅ Verify installations with:" -ForegroundColor Green
Write-Host "  semgrep --version" -ForegroundColor White
Write-Host "  grype version" -ForegroundColor White
Write-Host "  trufflehog --version" -ForegroundColor White

Write-Host "`n🧪 Run comprehensive test:" -ForegroundColor Green
Write-Host "  python test_tools.py" -ForegroundColor White

Write-Host "`n📚 If you encounter issues:" -ForegroundColor Yellow
Write-Host "  1. Make sure you are running as Administrator" -ForegroundColor White
Write-Host "  2. Restart your terminal after installation" -ForegroundColor White
Write-Host "  3. Check INSTALLATION.md for manual steps" -ForegroundColor White
Write-Host "  4. See TROUBLESHOOTING.md for common issues" -ForegroundColor White