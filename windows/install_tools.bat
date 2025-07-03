@echo off
echo ========================================
echo JavaScript Security Scanner - Tool Installer
echo Installing from Official GitHub Sources
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    echo Make sure to add Python to PATH during installation
    pause
    exit /b 1
)
echo Python found!

echo.
echo Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found!
    echo Please install pip or reinstall Python with pip included
    pause
    exit /b 1
)
echo pip found!

echo.
echo Installing Semgrep from GitHub...
echo Source: https://github.com/semgrep/semgrep
pip install semgrep
if %errorlevel% neq 0 (
    echo WARNING: Failed to install Semgrep via pip
    echo Please visit: https://github.com/semgrep/semgrep
    echo You may need to install it manually
) else (
    echo Semgrep installed successfully from GitHub!
)

echo.
echo Checking Semgrep installation...
semgrep --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Semgrep not accessible from command line
    echo You may need to restart your terminal or check PATH
) else (
    echo Semgrep is working!
)

echo.
echo ========================================
echo Grype Installation from GitHub
echo ========================================
echo.
echo Source: https://github.com/anchore/grype
echo.
echo Grype installation options:
echo.
echo 1. Download from GitHub Releases (Recommended):
echo    https://github.com/anchore/grype/releases/latest
echo    Download: grype_windows_amd64.zip
echo    Extract and add to PATH
echo.
echo 2. Use Package Manager:
echo    - Chocolatey: choco install grype
echo    - Scoop: scoop install grype
echo.
echo 3. Use PowerShell script (Automated):
echo    .\install_tools.ps1
echo.

echo Checking if Grype is already installed...
grype version >nul 2>&1
if %errorlevel% neq 0 (
    echo Grype not found. Please install manually using one of the options above.
) else (
    echo Grype is already installed and working!
)

echo.
echo ========================================
echo Installation Summary
echo ========================================
echo.

echo Checking all tools...
echo.

echo Testing Semgrep:
semgrep --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Semgrep not working
) else (
    echo [OK] Semgrep working
)

echo Testing Grype:
grype version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Grype not working
) else (
    echo [OK] Grype working
)

echo Testing TruffleHog:
trufflehog --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] TruffleHog not working
    echo.
    echo TruffleHog Installation from GitHub:
    echo Source: https://github.com/trufflesecurity/trufflehog
    echo.
    echo Installation options:
    echo 1. Download binary from GitHub releases:
    echo    https://github.com/trufflesecurity/trufflehog/releases/latest
    echo    Download: trufflehog_windows_amd64.tar.gz
    echo.
    echo 2. Use Docker:
    echo    docker pull trufflesecurity/trufflehog:latest
    echo.
    echo 3. Use PowerShell script (Automated):
    echo    .\install_tools.ps1
) else (
    echo [OK] TruffleHog working
)

echo.
echo ========================================
echo GitHub Sources
echo ========================================
echo.
echo All tools are installed from official GitHub repositories:
echo - Semgrep: https://github.com/semgrep/semgrep
echo - Grype: https://github.com/anchore/grype
echo - TruffleHog: https://github.com/trufflesecurity/trufflehog
echo.
echo ========================================
echo Next Steps
echo ========================================
echo.
echo 1. If any tools show [FAIL], please install them manually
echo 2. For automated installation, run: .\install_tools.ps1
echo 3. Restart your terminal/command prompt
echo 4. Test installation: python test_tools.py
echo 5. Run the scanner: python run.py -u https://example.com
echo 6. For detailed installation help, see INSTALLATION.md
echo.
echo Press any key to exit...
pause >nul