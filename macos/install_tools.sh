#!/bin/bash

# Source Code Scanner - macOS Installation Script
# This script installs all required tools for the security scanner

set -e

echo "🔧 Installing Security Scanner Tools for macOS..."
echo "================================================"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# Update Homebrew
echo "📦 Updating Homebrew..."
brew update

# Install Python if not available
if ! command -v python3 &> /dev/null; then
    echo "🐍 Installing Python..."
    brew install python
fi

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo "📦 Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Install Docker if not available
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    brew install --cask docker
    echo "⚠️  Please start Docker Desktop manually after installation"
fi

# Install Semgrep
echo "🔍 Installing Semgrep..."
pip3 install semgrep

# Install Grype
echo "📦 Installing Grype..."
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Install TruffleHog
echo "🔑 Installing TruffleHog..."
brew install trufflesecurity/trufflehog/trufflehog

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [ -f "../requirements.txt" ]; then
    pip3 install -r ../requirements.txt
else
    echo "⚠️  requirements.txt not found in parent directory"
fi

echo "✅ Installation completed successfully!"
echo ""
echo "🚀 You can now run the scanner with:"
echo "   python3 ../run.py --url https://example.com"
echo ""
echo "📋 Installed tools:"
echo "   • Semgrep: $(semgrep --version 2>/dev/null || echo 'Not found')"
echo "   • Grype: $(grype version 2>/dev/null || echo 'Not found')"
echo "   • TruffleHog: $(trufflehog --version 2>/dev/null || echo 'Not found')"
echo "   • Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "   • Docker: $(docker --version 2>/dev/null || echo 'Not found')"