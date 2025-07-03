#!/bin/bash

# Source Code Scanner - macOS Docker Runner
# This script runs the security scanner using Docker

set -e

echo "🐳 Running Security Scanner with Docker on macOS..."
echo "================================================"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
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