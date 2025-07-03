# Panduan Instalasi Tools Security Scanner

Untuk menjalankan Source Code Scanner, Anda perlu menginstal beberapa tools security dari sumber GitHub resmi.

## Tools yang Diperlukan (Sumber GitHub Resmi)

1. **Semgrep** - Static code analysis
   - GitHub: https://github.com/semgrep/semgrep
2. **Grype** - Dependency vulnerability scanning
   - GitHub: https://github.com/anchore/grype
3. **TruffleHog** - Secret detection
   - GitHub: https://github.com/trufflesecurity/trufflehog

## Metode Instalasi

### Opsi 1: Instalasi Otomatis (Recommended)

**Opsi A: GitHub Tools Script (Recommended untuk GitHub)**
```powershell
# Jalankan sebagai Administrator - Install langsung dari GitHub releases
.\install_github_tools.ps1
```

**Opsi B: PowerShell Script (Standard)**
```powershell
# Buka PowerShell sebagai Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install_tools.ps1
```

**Opsi C: Batch Script**
```cmd
# Jalankan sebagai Administrator
.\install_tools.bat
```

### Opsi 2: Instalasi Manual

#### 1. Install Semgrep dari GitHub

**Sumber:** https://github.com/semgrep/semgrep

**Via pip (Metode Resmi):**
```bash
pip install semgrep
```

**Via Docker (Alternative):**
```bash
docker pull semgrep/semgrep
```

**Verifikasi instalasi:**
```bash
semgrep --version
```

#### 2. Install Grype dari GitHub

**Sumber:** https://github.com/anchore/grype

**Windows (Metode Resmi):**

1. Download binary dari [GitHub Releases](https://github.com/anchore/grype/releases/latest)
2. Download file `grype_windows_amd64.zip`
3. Extract ke folder (contoh: `C:\tools\grype`)
4. Tambahkan folder tersebut ke PATH environment variable

**Via Installation Script (Linux/macOS):**
```bash
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
```

**Via Package Manager:**
```powershell
# Chocolatey
choco install grype

# Scoop
scoop install grype
```

**Verifikasi instalasi:**
```bash
grype version
```

#### 3. Install TruffleHog dari GitHub

**Sumber:** https://github.com/trufflesecurity/trufflehog

**Windows (Binary Release):**

1. Download dari [GitHub Releases](https://github.com/trufflesecurity/trufflehog/releases/latest)
2. Download file `trufflehog_windows_amd64.tar.gz`
3. Extract menggunakan tar atau 7-zip
4. Tambahkan ke PATH environment variable

**Via Installation Script (Linux/macOS):**
```bash
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
```

**Via Docker (Semua Platform):**
```bash
docker pull trufflesecurity/trufflehog:latest
```

**Verifikasi instalasi:**
```bash
trufflehog --version
```

## Troubleshooting

### Semgrep Issues

**Error: "semgrep command not found"**
- Pastikan Python dan pip terinstal
- Restart terminal setelah instalasi
- Cek PATH environment variable

**Error: "Permission denied"**
- Jalankan terminal sebagai Administrator
- Atau gunakan `pip install --user semgrep`

### Grype Issues

**Error: "grype command not found"**
- Pastikan binary sudah di-extract dengan benar
- Tambahkan folder grype ke PATH
- Restart terminal

**Error: "Access denied"**
- Jalankan PowerShell sebagai Administrator
- Pastikan antivirus tidak memblokir file

### PATH Environment Variable

**Windows:**
1. Buka System Properties → Advanced → Environment Variables
2. Edit PATH variable untuk User atau System
3. Tambahkan path ke folder tools
4. Restart terminal

**PowerShell:**
```powershell
# Tambah ke PATH sementara (session ini saja)
$env:PATH += ";C:\path\to\your\tools"

# Tambah ke PATH permanent
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\path\to\your\tools", "User")
```

## Verifikasi Instalasi

Setelah instalasi dari sumber GitHub, jalankan perintah berikut untuk memverifikasi:

```bash
# Check Semgrep
semgrep --version

# Check Grype  
grype version

# Check TruffleHog
trufflehog --version
```

**Atau gunakan script verifikasi:**
```bash
python test_tools.py
```

## Alternative: Docker Installation (Dari GitHub)

Jika mengalami kesulitan instalasi, Anda bisa menggunakan Docker dengan image resmi dari GitHub:

```dockerfile
# Dockerfile menggunakan image resmi dari GitHub
FROM python:3.9-slim

# Install Semgrep dari GitHub
RUN pip install semgrep

# Install Grype dari GitHub
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Install TruffleHog dari GitHub
RUN curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

WORKDIR /app
COPY . .

CMD ["python", "run.py"]
```

**Atau gunakan image resmi yang sudah ada:**
```bash
# Semgrep
docker run --rm -v "${PWD}:/src" semgrep/semgrep

# Grype
docker run --rm -v "${PWD}:/pwd" anchore/grype

# TruffleHog
docker run --rm -v "${PWD}:/pwd" trufflesecurity/trufflehog:latest
```

## Sumber Resmi dan Dokumentasi

- **Semgrep GitHub**: https://github.com/semgrep/semgrep
- **Semgrep Documentation**: https://semgrep.dev/docs/
- **Grype GitHub**: https://github.com/anchore/grype
- **Grype Documentation**: https://github.com/anchore/grype#readme
- **TruffleHog GitHub**: https://github.com/trufflesecurity/trufflehog
- **TruffleHog Documentation**: https://github.com/trufflesecurity/trufflehog#readme

## Bantuan Lebih Lanjut

Jika masih mengalami masalah:
1. Periksa dokumentasi resmi di GitHub masing-masing tool
2. Lihat file `TROUBLESHOOTING.md` untuk masalah umum
3. Jalankan `python test_tools.py` untuk diagnosis
4. Buat issue di repository ini dengan detail error yang dialami