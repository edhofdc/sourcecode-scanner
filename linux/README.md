# Linux Installation Guide

## Source Code Scanner - Linux Setup

This folder contains Linux-specific installation and run scripts for the Source Code Scanner.

## 📋 Prerequisites

- Linux distribution (Ubuntu, Debian, CentOS, RHEL, Fedora, Arch Linux)
- sudo privileges
- curl and wget (usually pre-installed)

## 🚀 Quick Start

### Step 1: Install Security Scanner Tools

1. **Make the script executable**:
   ```bash
   chmod +x install_tools.sh
   ```

2. **Run the installation script**:
   ```bash
   ./install_tools.sh
   ```

3. **Log out and log back in** (for Docker group changes to take effect)
   ```bash
   # Or run this to apply Docker group changes immediately:
   newgrp docker
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
~/.local/bin/semgrep --config=auto .
~/.local/bin/grype .
~/.local/bin/trufflehog filesystem .
```

## 📁 Files in this Directory

- `install_tools.sh` - Main installation script for Linux
- `run-docker.sh` - Docker runner script
- `README.md` - This documentation file

## 🛠️ What Gets Installed

The installation script will install:

- **Python 3 and pip** (via package manager)
- **Docker CE** (via official repositories)
- **Semgrep** (via pip, installed to ~/.local/bin)
- **Grype** (via official installer to ~/.local/bin)
- **TruffleHog** (via official installer to ~/.local/bin)
- **Python dependencies** (from requirements.txt)

## 🐧 Supported Distributions

### Debian/Ubuntu
- Uses `apt-get` package manager
- Installs Docker from official Docker repository
- Tested on Ubuntu 20.04+ and Debian 11+

### CentOS/RHEL
- Uses `yum` package manager
- Installs Docker from official Docker repository
- Tested on CentOS 7+ and RHEL 8+

### Fedora
- Uses `dnf` package manager
- Installs Docker from official Docker repository
- Tested on Fedora 35+

### Arch Linux
- Uses `pacman` package manager
- Installs Docker from official repositories
- Tested on Arch Linux (rolling release)

## 🔧 Troubleshooting

### Permission Issues
If you encounter permission errors with pip:
```bash
pip3 install --user <package_name>
```

### Docker Permission Issues
If Docker commands require sudo:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes immediately
newgrp docker

# Or log out and log back in
```

### PATH Issues
If installed tools are not found:
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Docker Service Issues
If Docker is not running:
```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Check Docker status
sudo systemctl status docker
```

### Firewall Issues
If Docker containers can't access the internet:
```bash
# For UFW (Ubuntu)
sudo ufw allow out 53
sudo ufw allow out 80
sudo ufw allow out 443

# For firewalld (CentOS/RHEL/Fedora)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### SELinux Issues (CentOS/RHEL/Fedora)
If SELinux blocks Docker:
```bash
# Check SELinux status
getenforce

# Temporarily disable (not recommended for production)
sudo setenforce 0

# Or configure SELinux for Docker
sudo setsebool -P container_manage_cgroup on
```

## 🔗 Related Documentation

- [Main README](../README.md)
- [Installation Guide](../INSTALLATION.md)
- [Troubleshooting](../TROUBLESHOOTING.md)
- [Docker Setup](../DOCKER_SETUP.md)

## 📝 Notes

- Tools are installed to `~/.local/bin` to avoid requiring sudo for pip installs
- Docker is installed system-wide but user is added to docker group
- The script automatically detects your Linux distribution
- Some enterprise environments may require additional proxy or certificate configuration
- For air-gapped environments, manual installation may be required