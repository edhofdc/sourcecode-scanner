# 🐳 Docker Simple Setup

Panduan sederhana untuk menjalankan Source Code Scanner menggunakan docker-compose langsung.

## Prerequisites
- Docker Desktop terinstall dan berjalan
- Git (untuk clone repository)

## Quick Start

### 1. Build Docker Image
```bash
docker-compose build
```

### 2. Test Installation
```bash
docker-compose run --rm scanner-cli python test_tools.py
```

### 3. Scan Website
```bash
# Scan dengan URL
docker-compose run --rm scanner-cli python run.py -u https://example.com

# Scan dengan opsi verbose
docker-compose run --rm scanner-cli python run.py -u https://example.com -v

# Scan dengan custom output directory
docker-compose run --rm scanner-cli python run.py -u https://example.com -o custom_output
```

### 4. Interactive Mode
```bash
# Buka shell di container
docker-compose run --rm scanner-cli /bin/bash

# Di dalam container, jalankan:
python run.py -u https://example.com
python test_tools.py
ls output/  # lihat hasil scan
```

### 5. View Help
```bash
docker-compose run --rm scanner-cli python run.py --help
```

## Available Commands

### Scanner Commands
```bash
# Basic scan
docker-compose run --rm scanner-cli python run.py -u <URL>

# Verbose scan
docker-compose run --rm scanner-cli python run.py -u <URL> -v

# Custom output directory
docker-compose run --rm scanner-cli python run.py -u <URL> -o <output_dir>

# Custom temp directory
docker-compose run --rm scanner-cli python run.py -u <URL> -t <temp_dir>
```

### Test Commands
```bash
# Test all tools
docker-compose run --rm scanner-cli python test_tools.py

# Test individual tools
docker-compose run --rm scanner-cli semgrep --version
docker-compose run --rm scanner-cli grype version
docker-compose run --rm scanner-cli python -m truffleHog --help
```

### Utility Commands
```bash
# List files in output directory
docker-compose run --rm scanner-cli ls -la output/

# View scan results
docker-compose run --rm scanner-cli cat output/result_*.json

# Clean temp files
docker-compose run --rm scanner-cli rm -rf temp/*
```

## File Structure

Setelah scan, file akan tersimpan di:
- `output/` - Laporan PDF dan JSON hasil scan
- `temp/` - File JavaScript yang didownload (temporary)

## Docker Services

- `scanner-cli` - Service untuk menjalankan scan sekali jalan
- `sourcecode-scanner` - Service untuk mode interactive/daemon

## Troubleshooting

### Container tidak bisa dijalankan
```bash
# Check Docker status
docker --version
docker-compose --version

# Rebuild image
docker-compose build --no-cache
```

### Permission issues
```bash
# Fix permission (Linux/Mac)
sudo chown -R $USER:$USER output/ temp/
```

### Clean up
```bash
# Stop all containers
docker-compose down

# Remove images
docker-compose down --rmi all

# Remove volumes
docker-compose down --volumes
```

## Examples

### Scan OWASP NodeGoat
```bash
docker-compose run --rm scanner-cli python run.py -u https://github.com/OWASP/NodeGoat -v
```

### Scan dengan output custom
```bash
docker-compose run --rm scanner-cli python run.py -u https://example.com -o my_reports
```

### Interactive debugging
```bash
# Masuk ke container
docker-compose run --rm scanner-cli /bin/bash

# Di dalam container:
cd /app
python run.py -u https://example.com
ls -la output/
cat scanner.log
```