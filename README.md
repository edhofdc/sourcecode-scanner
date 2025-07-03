# Source Code Scanner

A Python application for scanning security-relevant files from URLs to detect vulnerabilities and secrets using three leading security tools: Semgrep, Grype, and TruffleHog.

## 🚀 Fitur Utama

- **Static Code Analysis (Semgrep)**: Analisis statis untuk menemukan bug, celah keamanan, dan pola kode berbahaya dengan aturan yang dapat disesuaikan
- **Dependency Vulnerability Scanning (Grype)**: Memindai image dan paket aplikasi untuk menemukan CVE atau vulnerability berdasarkan database seperti NVD
- **Secret Detection (TruffleHog)**: Mencari secret atau credential (API key, token, password) yang tidak sengaja tercantum di kode atau repositori
- **Dual Interface**: Command-line interface dan Telegram bot
- **Comprehensive Reports**: Output berupa PDF (human-readable) dan JSON (structured data) dengan kategorisasi berdasarkan jenis temuan
- **Automatic JS Download**: Download otomatis semua file JavaScript (inline dan eksternal)

## 📋 Prerequisites

### Tools yang Diperlukan

⚠️ **PENTING**: Sebelum menjalankan scanner, Anda perlu menginstal tools security berikut:

1. **Semgrep** - Static code analysis
2. **Grype** - Dependency vulnerability scanning  
3. **TruffleHog** - Secret detection (sudah terinstal via pip)

### 🔧 Instalasi Tools

**Opsi 1: Docker Setup (Recommended) 🐳**
```bash
# Build Docker image
docker-compose build

# Test installation
docker-compose run --rm scanner-cli python test_tools.py

# Scan website
docker-compose run --rm scanner-cli python run.py -u https://example.com

# Interactive shell
docker-compose run --rm scanner-cli /bin/bash

# View help
docker-compose run --rm scanner-cli python run.py --help
```

**Opsi 2: Instalasi Otomatis (Windows)**
```powershell
# Jalankan sebagai Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install_tools.ps1
```

**Opsi 3: Instalasi Manual**

Lihat panduan lengkap di **[INSTALLATION.md](INSTALLATION.md)** untuk:
- Instalasi step-by-step untuk Windows/macOS/Linux
- Troubleshooting common issues
- Alternative installation methods

**Opsi 4: Docker Setup (Detailed)**

📖 **Dokumentasi Docker:**
- [DOCKER_SIMPLE.md](DOCKER_SIMPLE.md) - Panduan sederhana menggunakan docker-compose
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Dokumentasi lengkap dengan script PowerShell

### Verifikasi Instalasi

```bash
semgrep --version
grype version
trufflehog --version
```

**Atau gunakan script verifikasi:**
```bash
python test_tools.py
```

**Jika tools belum terinstal**, scanner akan menampilkan error seperti:
```json
{
  "semgrep_results": {
    "error": "Semgrep not installed or not accessible"
  },
  "grype_results": {
    "error": "Grype not installed or not accessible"
  }
}
```

**Sumber GitHub Resmi:**
- **Semgrep**: https://github.com/semgrep/semgrep
- **Grype**: https://github.com/anchore/grype
- **TruffleHog**: https://github.com/trufflesecurity/trufflehog

## 🛠️ Instalasi

1. **Clone atau download proyek ini**
   ```bash
   git clone <repository-url>
   cd "Vuln And Secret JS FIle"
   ```

2. **Install dependencies Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Security Tools dari GitHub**
   
   **Opsi A: Instalasi Otomatis (Windows)**
   ```powershell
   # PowerShell (Recommended)
   .\install_tools.ps1
   
   # Atau Batch
   .\install_tools.bat
   ```
   
   **Opsi B: Instalasi Manual**
   
   Lihat panduan lengkap di [`INSTALLATION.md`](INSTALLATION.md) untuk instalasi manual dari sumber GitHub resmi.

4. **Setup environment variables**
   
   Buat file `.env` dan isi dengan konfigurasi yang diperlukan:
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   
   # Logging Configuration
   LOG_LEVEL=INFO
   LOG_FILE=scanner.log
   
   # Scanner Configuration
   OUTPUT_DIR=output
   TEMP_DIR=temp
   MAX_FILE_SIZE_MB=50
   DOWNLOAD_TIMEOUT=30
   SCAN_TIMEOUT=300
   ```

5. **Buat direktori output**
   ```bash
   mkdir output
   mkdir temp
   ```

## 🚀 Quick Start

### 🐳 Docker Setup (Recommended)
```bash
# 1. Build Docker image (one-time setup)
.\run-docker.ps1 build

# 2. Test tools installation
.\run-docker.ps1 test

# 3. Run vulnerability scan
.\run-docker.ps1 scan

# 4. Interactive mode (optional)
.\run-docker.ps1 run
```

### 💻 Manual Setup (CLI Only)
```bash
# Install dependencies
pip install -r requirements.txt

# Install security tools (Windows)
.\install_tools.ps1

# Langsung scan URL
python run.py -u https://example.com
```

### 🤖 Dengan Telegram Bot
```bash
# Install dependencies
pip install -r requirements.txt

# Setup token di .env file
# TELEGRAM_BOT_TOKEN=your_actual_token_here

# Jalankan bot
python bot.py
```

## 📖 Penggunaan

### Command Line Interface (Utama)

```bash
# Scan URL
python run.py -u https://example.com

# Dengan opsi verbose
python run.py -u https://example.com -v

# Lihat help
python run.py --help
```

**Output:**
- `output/report_YYYYMMDD_HHMMSS.pdf` - Laporan PDF yang mudah dibaca
- `output/result_YYYYMMDD_HHMMSS.json` - Data terstruktur JSON

### Telegram Bot Interface (Opsional)

```bash
# Cek dan jalankan bot (opsional)
python bot.py

# Atau langsung jalankan bot jika token sudah ada
python telegrambot.py
```

### Telegram Bot (Opsional)

Telegram bot adalah fitur opsional. Jika tidak ada token bot, aplikasi tetap dapat dijalankan menggunakan command line.

#### Opsi 1: Bot Opsional (Recommended)
```bash
# Akan mengecek token dan memberikan instruksi jika tidak ada
python bot.py
```

#### Opsi 2: Jalankan Bot Langsung
```bash
# Langsung menjalankan bot (memerlukan token)
python telegrambot.py
```

#### Setup Bot (Jika Ingin Menggunakan)
1. **Buat Telegram Bot**
   - Chat dengan [@BotFather](https://t.me/botfather)
   - Gunakan command `/newbot`
   - Ikuti instruksi untuk membuat bot
   - Salin token yang diberikan ke file `.env`

2. **Gunakan Bot**
   - Start chat dengan bot Anda
   - Kirim command `/start`
   - Kirim URL yang ingin di-scan
   - Tunggu hasil scanning

**Bot Commands:**
- `/start` - Tampilkan pesan selamat datang
- `/help` - Tampilkan bantuan detail
- `/status` - Cek status scanning yang sedang berjalan

## 📁 Struktur Proyek

```
Vuln And Secret JS FIle/
├── run.py                 # Command-line interface
├── bot.py                 # Optional bot launcher (checks token)
├── telegrambot.py         # Telegram bot implementation
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── README.md             # Dokumentasi
├── scanner/              # Scanner modules
│   ├── __init__.py
│   ├── downloader.py     # JavaScript file downloader
│   ├── semgrep_scan.py   # Semgrep scanner
│   ├── grype_scan.py     # Grype scanner
│   ├── trufflehog_scan.py # TruffleHog scanner
│   └── report_generator.py # Report generator
├── output/               # Scan results
└── temp/                 # Temporary files
```

## 🔧 Konfigurasi

### Environment Variables

| Variable | Deskripsi | Default |
|----------|-----------|----------|
| `TELEGRAM_BOT_TOKEN` | Token bot Telegram | - |
| `LOG_LEVEL` | Level logging (DEBUG, INFO, WARNING, ERROR) | INFO |
| `LOG_FILE` | File log | scanner.log |
| `OUTPUT_DIR` | Direktori output | output |
| `TEMP_DIR` | Direktori temporary | temp |
| `MAX_FILE_SIZE_MB` | Ukuran maksimal file (MB) | 50 |
| `DOWNLOAD_TIMEOUT` | Timeout download (detik) | 30 |
| `SCAN_TIMEOUT` | Timeout scanning (detik) | 300 |

### Scanner Configuration

Setiap scanner memiliki fokus dan konfigurasi yang berbeda:

- **Semgrep**: 
  - Menggunakan ruleset `p/javascript` dan `p/security-audit`
  - Mendeteksi: XSS, SQL injection, insecure crypto, code injection, dll
  - Target: File JavaScript (.js) yang telah didownload

- **Grype**: 
  - Scan file dependency: `package.json`, `yarn.lock`, `package-lock.json`
  - Mendeteksi: CVE pada npm packages berdasarkan database NVD
  - Target: Dependency manifests dan lock files

- **TruffleHog**: 
  - Kombinasi tool TruffleHog dan custom regex patterns
  - Mendeteksi: API keys, tokens, passwords, certificates, database URLs
  - Target: Semua file JavaScript dan dependency files

## 📊 Output Reports

### PDF Report

Laporan PDF berisi kategorisasi temuan berdasarkan jenis scanner:
- **Executive Summary** - Ringkasan keseluruhan dengan breakdown per tool
- **Semgrep Findings** - Bug, celah keamanan, dan pola kode berbahaya
- **Grype Findings** - CVE dan vulnerability pada dependencies
- **TruffleHog Findings** - Secrets dan credentials yang terekspos
- **Risk Assessment** - Penilaian risiko keseluruhan
- **Recommendations** - Rekomendasi spesifik per jenis temuan

### JSON Report

Data JSON terstruktur berisi:
```json
{
  "target_url": "https://example.com",
  "scan_timestamp": "2024-01-01T12:00:00",
  "downloaded_files": [...],
  "semgrep_results": {
    "results": ["bug dan security issues"],
    "summary": {"total_findings": 0, "by_severity": {}}
  },
  "grype_results": {
    "results": ["CVE dan vulnerabilities"],
    "summary": {"total_vulnerabilities": 0, "by_severity": {}}
  },
  "trufflehog_results": {
    "results": ["secrets dan credentials"],
    "summary": {"total_secrets": 0, "by_confidence": {}}
  },
  "overall_summary": {
    "total_files": 0,
    "total_issues": 0,
    "total_vulnerabilities": 0,
    "total_secrets": 0
  }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Tool tidak ditemukan**
   ```
   Error: semgrep/grype/trufflehog command not found
   ```
   **Solusi**: Pastikan tools sudah terinstal dan ada di PATH

2. **Permission denied**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **Solusi**: Jalankan dengan permission yang sesuai atau ubah direktori output

3. **Telegram bot tidak merespon**
   ```
   telegram.error.InvalidToken
   ```
   **Solusi**: Periksa `TELEGRAM_BOT_TOKEN` di file `.env`

4. **Download gagal**
   ```
   Failed to download JavaScript files
   ```
   **Solusi**: Periksa koneksi internet dan URL yang valid

### Debug Mode

Untuk debugging, set `LOG_LEVEL=DEBUG` di file `.env`:

```env
LOG_LEVEL=DEBUG
```

## 🔒 Security Considerations

- **Temporary Files**: Semua file temporary dibersihkan otomatis setelah scanning
- **Secrets Masking**: Secrets di-mask dalam output untuk keamanan
- **Rate Limiting**: Bot Telegram memiliki built-in rate limiting
- **Input Validation**: URL dan input lainnya divalidasi sebelum diproses

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Buat Pull Request

## 📝 License

Project ini menggunakan MIT License. Lihat file `LICENSE` untuk detail.

## 🙏 Acknowledgments

- [Semgrep](https://semgrep.dev/) - Static analysis tool
- [Grype](https://github.com/anchore/grype) - Vulnerability scanner
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Secret scanner
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram bot framework

## 📞 Support

Jika Anda mengalami masalah atau memiliki pertanyaan:

1. Periksa [Troubleshooting](#-troubleshooting) section
2. Buat issue di repository
3. Periksa log file untuk detail error

---

**⚠️ Disclaimer**: Tool ini hanya untuk tujuan educational dan security testing yang sah. Pastikan Anda memiliki izin untuk melakukan scanning terhadap website target.