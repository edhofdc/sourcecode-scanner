#!/bin/bash

# Source Code Scanner - Linux Installation Script
# This script installs all required tools for the security scanner

set -e

echo "🔧 Installing Security Scanner Tools for Linux..."
echo "==============================================="

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ Cannot detect Linux distribution"
    exit 1
fi

echo "📋 Detected OS: $OS"

# Update package manager
echo "📦 Updating package manager..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
elif command -v yum &> /dev/null; then
    sudo yum update -y
elif command -v dnf &> /dev/null; then
    sudo dnf update -y
elif command -v pacman &> /dev/null; then
    sudo pacman -Sy
else
    echo "⚠️  Unsupported package manager. Please install tools manually."
fi

# Install Python and pip
echo "🐍 Installing Python and pip..."
if command -v apt-get &> /dev/null; then
    sudo apt-get install -y python3 python3-pip curl wget
elif command -v yum &> /dev/null; then
    sudo yum install -y python3 python3-pip curl wget
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3 python3-pip curl wget
elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm python python-pip curl wget
fi

# Install Docker
echo "🐳 Installing Docker..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get install -y apt-transport-https ca-certificates gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum install -y yum-utils
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    sudo yum install -y docker-ce docker-ce-cli containerd.io
elif command -v dnf &> /dev/null; then
    # Fedora
    sudo dnf -y install dnf-plugins-core
    sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
    sudo dnf install -y docker-ce docker-ce-cli containerd.io
elif command -v pacman &> /dev/null; then
    # Arch Linux
    sudo pacman -S --noconfirm docker
fi

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Install Semgrep
echo "🔍 Installing Semgrep..."
pip3 install --user semgrep

# Install Grype
echo "📦 Installing Grype..."
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b ~/.local/bin

# Install TruffleHog
echo "🔑 Installing TruffleHog..."
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b ~/.local/bin

# Add local bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [ -f "../requirements.txt" ]; then
    pip3 install --user -r ../requirements.txt
else
    echo "⚠️  requirements.txt not found in parent directory"
fi

echo "✅ Installation completed successfully!"
echo ""
echo "⚠️  IMPORTANT: Please log out and log back in for Docker group changes to take effect."
echo "   Or run: newgrp docker"
echo ""
echo "🚀 You can now run the scanner with:"
echo "   python3 ../run.py --url https://example.com"
echo ""
echo "📋 Installed tools:"
echo "   • Semgrep: $(~/.local/bin/semgrep --version 2>/dev/null || semgrep --version 2>/dev/null || echo 'Not found')"
echo "   • Grype: $(~/.local/bin/grype version 2>/dev/null || grype version 2>/dev/null || echo 'Not found')"
echo "   • TruffleHog: $(~/.local/bin/trufflehog --version 2>/dev/null || trufflehog --version 2>/dev/null || echo 'Not found')"
echo "   • Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "   • Docker: $(docker --version 2>/dev/null || echo 'Not found')"