# macOS Installation Guide

## Source Code Scanner - macOS Setup

This folder contains macOS-specific installation and run scripts for the Source Code Scanner.

## 📋 Prerequisites

- macOS 10.15 (Catalina) or later
- Homebrew package manager
- Xcode Command Line Tools

## 🚀 Quick Start

### Step 1: Install Prerequisites

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```

### Step 2: Install Security Scanner Tools

1. **Make the script executable**:
   ```bash
   chmod +x install_tools.sh
   ```

2. **Run the installation script**:
   ```bash
   ./install_tools.sh
   ```

## 🐳 Docker Usage

### Run with Docker (Recommended for isolation)

1. **Make the script executable**:
   ```bash
   chmod +x run-docker.sh
   ```

2. **Run the scanner**:
   ```bash
   ./run-docker.sh https://example.com
   ```

## 🔧 Manual Usage

After installation, you can run the scanner directly:

```bash
# Navigate to parent directory
cd ..

# Run the scanner
python3 run.py --url https://example.com

# Or run individual tools
semgrep --config=auto .
grype .
trufflehog filesystem .
```

## 📁 Files in this Directory

- `install_tools.sh` - Main installation script for macOS
- `run-docker.sh` - Docker runner script
- `README.md` - This documentation file

## 🛠️ What Gets Installed

The installation script will install:

- **Python 3** (via Homebrew)
- **Docker Desktop** (via Homebrew Cask)
- **Semgrep** (via pip)
- **Grype** (via official installer)
- **TruffleHog** (via Homebrew)
- **Python dependencies** (from requirements.txt)

## 🔧 Troubleshooting

### Permission Issues
If you encounter permission errors:
```bash
sudo chown -R $(whoami) /usr/local/lib/python*/site-packages
```

### Homebrew Issues
If Homebrew commands fail:
```bash
brew doctor
brew update
```

### Docker Issues
- Make sure Docker Desktop is running
- Check Docker preferences for resource allocation
- Restart Docker Desktop if containers fail to start

### Python Path Issues
If Python packages are not found:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### M1/M2 Mac Compatibility
For Apple Silicon Macs, some tools might need Rosetta 2:
```bash
softwareupdate --install-rosetta
```

## 🔗 Related Documentation

- [Main README](../README.md)
- [Installation Guide](../INSTALLATION.md)
- [Troubleshooting](../TROUBLESHOOTING.md)
- [Docker Setup](../DOCKER_SETUP.md)

## 📝 Notes

- The installation script uses Homebrew for most packages
- Docker Desktop requires manual startup after installation
- Some tools may require additional configuration for enterprise environments
- All tools are installed with user permissions (no sudo required after Homebrew setup)