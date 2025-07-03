# Windows Installation Guide

## Source Code Scanner - Windows Setup

This folder contains Windows-specific installation and run scripts for the Source Code Scanner.

## 📋 Prerequisites

- Windows 10/11
- PowerShell 5.1 or later
- Administrator privileges (for some installations)

## 🚀 Quick Start

### Option 1: PowerShell Installation (Recommended)

1. **Run as Administrator**: Right-click PowerShell and select "Run as Administrator"
2. **Enable script execution**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. **Install all tools**:
   ```powershell
   .\install_tools.ps1
   ```

### Option 2: Batch File Installation

1. **Run as Administrator**: Right-click Command Prompt and select "Run as Administrator"
2. **Install all tools**:
   ```cmd
   install_tools.bat
   ```

### Option 3: Individual Tool Installation

Install tools separately:
```powershell
.\install_grype.ps1
.\install_trufflehog.ps1
.\install_github_tools.ps1
```

## 🐳 Docker Usage

### Run with Docker (Recommended for isolation)

1. **PowerShell**:
   ```powershell
   .\run-docker.ps1 https://example.com
   ```

2. **Batch file**:
   ```cmd
   run-docker.bat https://example.com
   ```

## 🔧 Manual Tool Execution

After installation, you can run individual tools:

```cmd
# Run Semgrep
semgrep.bat

# Run Grype
grype.bat

# Run TruffleHog
trufflehog.bat
```

## 📁 Files in this Directory

- `install_tools.ps1` - Main PowerShell installation script
- `install_tools.bat` - Main batch installation script
- `install_grype.ps1` - Grype-specific installation
- `install_trufflehog.ps1` - TruffleHog-specific installation
- `install_github_tools.ps1` - GitHub CLI and related tools
- `run-docker.ps1` - PowerShell Docker runner
- `run-docker.bat` - Batch Docker runner
- `grype.bat` - Grype execution wrapper
- `semgrep.bat` - Semgrep execution wrapper
- `trufflehog.bat` - TruffleHog execution wrapper

## 🛠️ Troubleshooting

### PowerShell Execution Policy
If you get execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### Windows Defender
Windows Defender might flag security tools. Add exclusions for:
- The scanner directory
- Downloaded tools (Grype, TruffleHog, etc.)

### Path Issues
If tools are not found after installation, restart your terminal or add tool directories to your PATH.

## 🔗 Related Documentation

- [Main README](../README.md)
- [Installation Guide](../INSTALLATION.md)
- [Troubleshooting](../TROUBLESHOOTING.md)
- [Docker Setup](../DOCKER_SETUP.md)