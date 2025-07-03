# Script untuk menginstal Semgrep, Grype, dan TruffleHog di Windows
# Jalankan sebagai Administrator

Write-Host "Installing Semgrep, Grype, and TruffleHog security tools..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python first from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if pip is available
try {
    pip --version | Out-Null
    Write-Host "pip is available" -ForegroundColor Green
} catch {
    Write-Host "pip not found. Please install pip first" -ForegroundColor Red
    exit 1
}

# Install Semgrep
Write-Host "Installing Semgrep from GitHub..." -ForegroundColor Yellow
try {
    # Install Semgrep directly from GitHub using pip
    Write-Host "Installing Semgrep from GitHub repository..." -ForegroundColor Yellow
    pip install git+https://github.com/semgrep/semgrep.git
    
    Write-Host "Semgrep installed successfully from GitHub" -ForegroundColor Green
    Write-Host "Source: https://github.com/semgrep/semgrep" -ForegroundColor Cyan
    
    # Verify installation
    try {
        $semgrepVersion = semgrep --version
        Write-Host "Semgrep version: $semgrepVersion" -ForegroundColor Green
    } catch {
        Write-Host "Semgrep installed but verification failed. Try restarting terminal." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Failed to install Semgrep from GitHub: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Fallback: trying pip install semgrep..." -ForegroundColor Yellow
    try {
        pip install semgrep
        Write-Host "Semgrep installed via pip" -ForegroundColor Green
    } catch {
        Write-Host "Both GitHub and pip installation failed" -ForegroundColor Red
        Write-Host "Please visit: https://github.com/semgrep/semgrep" -ForegroundColor Yellow
    }
}

# Install Grype
Write-Host "Installing Grype from GitHub..." -ForegroundColor Yellow

# Check if we're on Windows
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    # Use official installation script from GitHub
    try {
        # Download and run the official install script
        Write-Host "Using official Grype installation script..." -ForegroundColor Yellow
        $installScript = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/anchore/grype/main/install.sh" -UseBasicParsing
        
        # For Windows, we'll download the binary directly
        $grypeUrl = "https://github.com/anchore/grype/releases/latest/download/grype_windows_amd64.zip"
        $tempDir = $env:TEMP
        $grypeZip = "$tempDir\grype.zip"
        $grypeDir = "$env:LOCALAPPDATA\grype"
        
        # Create grype directory
        if (!(Test-Path $grypeDir)) {
            New-Item -ItemType Directory -Path $grypeDir -Force
        }
        
        # Download Grype
        Write-Host "Downloading Grype from GitHub releases..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $grypeUrl -OutFile $grypeZip
        
        # Extract Grype
        Write-Host "Extracting Grype..." -ForegroundColor Yellow
        Expand-Archive -Path $grypeZip -DestinationPath $grypeDir -Force
        
        # Add to PATH if not already there
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*$grypeDir*") {
            $newPath = "$currentPath;$grypeDir"
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            Write-Host "Added Grype to PATH. Please restart your terminal." -ForegroundColor Green
        }
        
        # Clean up
        Remove-Item $grypeZip -Force
        
        Write-Host "Grype installed successfully from GitHub" -ForegroundColor Green
        Write-Host "Source: https://github.com/anchore/grype" -ForegroundColor Cyan
        
    } catch {
        Write-Host "Failed to install Grype: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please visit: https://github.com/anchore/grype" -ForegroundColor Yellow
    }
} else {
    Write-Host "This script is designed for Windows. For other OS, please visit: https://github.com/anchore/grype#installation" -ForegroundColor Yellow
}

# Install TruffleHog
Write-Host "Installing TruffleHog from GitHub..." -ForegroundColor Yellow

# Check if we're on Windows
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    try {
        # Download TruffleHog binary for Windows
        $truffleUrl = "https://github.com/trufflesecurity/trufflehog/releases/latest/download/trufflehog_windows_amd64.tar.gz"
        $tempDir = $env:TEMP
        $truffleTar = "$tempDir\trufflehog.tar.gz"
        $truffleDir = "$env:LOCALAPPDATA\trufflehog"
        
        # Create trufflehog directory
        if (!(Test-Path $truffleDir)) {
            New-Item -ItemType Directory -Path $truffleDir -Force
        }
        
        Write-Host "Downloading TruffleHog from GitHub releases..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $truffleUrl -OutFile $truffleTar
        
        # Extract using tar (available in Windows 10+)
        Write-Host "Extracting TruffleHog..." -ForegroundColor Yellow
        tar -xzf $truffleTar -C $truffleDir
        
        # Add to PATH if not already there
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*$truffleDir*") {
            $newPath = "$currentPath;$truffleDir"
            [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
            Write-Host "Added TruffleHog to PATH. Please restart your terminal." -ForegroundColor Green
        }
        
        # Clean up
        Remove-Item $truffleTar -Force
        
        Write-Host "TruffleHog installed successfully from GitHub" -ForegroundColor Green
        Write-Host "Source: https://github.com/trufflesecurity/trufflehog" -ForegroundColor Cyan
        
    } catch {
        Write-Host "Failed to install TruffleHog: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please visit: https://github.com/trufflesecurity/trufflehog" -ForegroundColor Yellow
        Write-Host "Alternative: Use Docker - docker pull trufflesecurity/trufflehog:latest" -ForegroundColor Yellow
    }
} else {
    Write-Host "This script is designed for Windows. For other OS, please visit: https://github.com/trufflesecurity/trufflehog#installation" -ForegroundColor Yellow
}

Write-Host "\nInstallation completed!" -ForegroundColor Green
Write-Host "Please restart your terminal and verify installations:" -ForegroundColor Yellow
Write-Host "  semgrep --version" -ForegroundColor Cyan
Write-Host "  grype version" -ForegroundColor Cyan
Write-Host "  trufflehog --version" -ForegroundColor Cyan

Write-Host "\nGitHub Sources:" -ForegroundColor Green
Write-Host "  Semgrep: https://github.com/semgrep/semgrep" -ForegroundColor Cyan
Write-Host "  Grype: https://github.com/anchore/grype" -ForegroundColor Cyan
Write-Host "  TruffleHog: https://github.com/trufflesecurity/trufflehog" -ForegroundColor Cyan

Write-Host "\nIf you encounter any issues:" -ForegroundColor Yellow
Write-Host "1. Make sure you're running as Administrator" -ForegroundColor White
Write-Host "2. Restart your terminal after installation" -ForegroundColor White
Write-Host "3. Check that Python and pip are properly installed" -ForegroundColor White
Write-Host "4. You may need to add tools manually to your PATH" -ForegroundColor White
Write-Host "5. Run 'python test_tools.py' to verify all installations" -ForegroundColor White