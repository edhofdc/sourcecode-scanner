#!/bin/bash

# Source Code Scanner - Linux Docker Runner
# This script runs the security scanner using Docker

set -e

echo "🐳 Running Security Scanner with Docker on Linux..."
echo "==============================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first:"
    echo "   sudo systemctl start docker"
    exit 1
fi

# Check if user is in docker group
if ! groups $USER | grep -q docker; then
    echo "⚠️  User $USER is not in the docker group."
    echo "   You may need to run with sudo or add user to docker group:"
    echo "   sudo usermod -aG docker $USER"
    echo "   Then log out and log back in."
fi

# Check if URL is provided
if [ -z "$1" ]; then
    echo "❌ Please provide a URL to scan"
    echo "Usage: $0 <URL>"
    echo "Example: $0 https://example.com"
    exit 1
fi

URL="$1"
echo "🔍 Scanning URL: $URL"

# Navigate to parent directory (where docker-compose.yml is located)
cd "$(dirname "$0")/.."

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in parent directory"
    exit 1
fi

# Run the scanner with Docker Compose
echo "🚀 Starting Docker containers..."
docker-compose run --rm scanner python run.py --url "$URL"

echo "✅ Scan completed! Check the output directory for results."