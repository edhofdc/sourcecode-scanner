# Docker Setup untuk Source Code Scanner

Setup ini memungkinkan Anda menjalankan semua security tools (Semgrep, Grype, TruffleHog) dalam Docker container tanpa perlu instalasi manual di sistem host.

## Prerequisites

- Docker Desktop terinstal dan berjalan
- Docker Compose tersedia

## Quick Start

### 1. Build Docker Image
```bash
# Build image dengan semua tools
run-docker.bat build
```

### 2. Jalankan Scanner
```bash
# Jalankan vulnerability scan
run-docker.bat scan

# Atau jalankan interactive mode
run-docker.bat run
```

### 3. Test Tools
```bash
# Test apakah semua tools terinstal dengan benar
run-docker.bat test
```

## Available Commands

| Command | Description |
|---------|-------------|
| `run-docker.bat build` | Build Docker image dengan semua tools |
| `run-docker.bat run` | Jalankan container interaktif |
| `run-docker.bat scan` | Jalankan vulnerability scan |
| `run-docker.bat test` | Test instalasi tools |
| `run-docker.bat shell` | Buka shell di container yang sedang berjalan |
| `run-docker.bat stop` | Stop dan hapus containers |
| `run-docker.bat logs` | Tampilkan logs container |

## Tools yang Tersedia

### Semgrep
- **Purpose**: Static analysis untuk mencari vulnerabilities dan bugs
- **Usage dalam container**: `semgrep --config=auto /app`

### Grype
- **Purpose**: Vulnerability scanner untuk container images dan filesystems
- **Usage dalam container**: `grype /app`

### TruffleHog v3
- **Purpose**: Secret scanner untuk mencari credentials dan API keys
- **Usage dalam container**: `trufflehog filesystem /app`

## File Structure

```
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── run-docker.bat         # Helper script untuk Windows
├── DOCKER_SETUP.md        # Dokumentasi ini
└── ...
```

## Volume Mounts

Container akan mount direktori berikut:
- `./output` → `/app/output` (hasil scan)
- `./temp` → `/app/temp` (file temporary)
- `./bot_output` → `/app/bot_output` (output bot)
- `./bot_temp` → `/app/bot_temp` (temp bot)

## Environment Variables

Container akan membaca file `.env` untuk konfigurasi environment variables.

## Troubleshooting

### Docker Build Gagal
```bash
# Clean build tanpa cache
docker-compose build --no-cache
```

### Container Tidak Bisa Akses Docker Socket
Pastikan Docker Desktop berjalan dan Docker socket tersedia di `/var/run/docker.sock`.

### Permission Issues
```bash
# Jalankan dengan user privileges
docker-compose run --user root scanner-cli /bin/bash
```

### Tools Tidak Ditemukan
```bash
# Check instalasi tools
run-docker.bat test

# Manual check dalam container
run-docker.bat shell
which semgrep grype trufflehog
```

## Manual Docker Commands

Jika tidak ingin menggunakan script helper:

```bash
# Build
docker-compose build

# Run interactive
docker-compose up -d sourcecode-scanner
docker-compose exec sourcecode-scanner /bin/bash

# Run scan
docker-compose run --rm scanner-cli python run.py

# Stop
docker-compose down
```

## Performance Notes

- First build akan memakan waktu karena download dan compile tools
- Subsequent builds akan lebih cepat karena Docker layer caching
- Container sharing Docker socket untuk Grype functionality

## Security Considerations

- Container mount Docker socket untuk Grype functionality
- Semua tools berjalan dalam isolated container environment
- Output files disimpan di host melalui volume mounts