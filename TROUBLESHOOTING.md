# Troubleshooting Guide

Panduan untuk mengatasi masalah umum saat menggunakan Source Code Scanner.

## 🚨 Error: Tools Not Installed

### Masalah
Scanner menampilkan error:
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

### Solusi

#### 1. Cek Instalasi Tools
```bash
# Test semgrep
semgrep --version

# Test grype
grype version

# Test trufflehog
python -c "import truffleHog; print('OK')"
```

#### 2. Install Tools yang Missing

**Semgrep:**
```bash
pip install semgrep
```

**Grype (Windows):**
- Download dari [GitHub Releases](https://github.com/anchore/grype/releases/latest)
- Extract `grype_windows_amd64.zip`
- Tambahkan ke PATH

**TruffleHog:**
```bash
pip install truffleHog
```

#### 3. Restart Terminal
Setelah instalasi, restart terminal/command prompt.

## 🔧 PATH Environment Issues

### Masalah
Tools sudah terinstal tapi tidak bisa dipanggil dari command line.

### Solusi Windows

#### Temporary Fix (Session ini saja)
```powershell
# Tambah Semgrep ke PATH
$env:PATH += ";C:\Users\YourUsername\AppData\Local\Programs\Python\Python39\Scripts"

# Tambah Grype ke PATH
$env:PATH += ";C:\path\to\grype"
```

#### Permanent Fix
1. Buka System Properties → Advanced → Environment Variables
2. Edit PATH variable
3. Tambahkan path ke tools:
   - Semgrep: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python39\Scripts`
   - Grype: `C:\path\to\grype\folder`
4. Restart terminal

## 🐍 Python Issues

### Masalah: Python Not Found
```
'python' is not recognized as an internal or external command
```

### Solusi
1. Install Python dari [python.org](https://python.org)
2. Pastikan centang "Add Python to PATH" saat instalasi
3. Atau tambahkan manual ke PATH:
   - `C:\Users\YourUsername\AppData\Local\Programs\Python\Python39`
   - `C:\Users\YourUsername\AppData\Local\Programs\Python\Python39\Scripts`

### Masalah: pip Not Found
```
'pip' is not recognized as an internal or external command
```

### Solusi
```bash
# Install pip
python -m ensurepip --upgrade

# Atau download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

## 📦 Package Installation Issues

### Masalah: Permission Denied
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

### Solusi
```bash
# Install untuk user saja
pip install --user semgrep

# Atau jalankan sebagai Administrator
# Buka Command Prompt sebagai Administrator
pip install semgrep
```

### Masalah: SSL Certificate Error
```
SSL: CERTIFICATE_VERIFY_FAILED
```

### Solusi
```bash
# Upgrade pip dan certificates
python -m pip install --upgrade pip
pip install --upgrade certifi

# Atau bypass SSL (tidak recommended)
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org semgrep
```

## 🔒 Antivirus Issues

### Masalah
Antivirus memblokir tools security atau file executable.

### Solusi
1. Tambahkan folder project ke whitelist antivirus
2. Tambahkan tools ke exception:
   - `semgrep.exe`
   - `grype.exe`
   - Python scripts
3. Temporary disable real-time protection saat instalasi

## 🌐 Network Issues

### Masalah: Download Timeout
```
Timeout occurred while downloading JavaScript files
```

### Solusi
1. Cek koneksi internet
2. Increase timeout di `.env`:
   ```
   DOWNLOAD_TIMEOUT=60
   ```
3. Coba URL yang berbeda
4. Gunakan VPN jika ada blocking

### Masalah: Proxy Issues
```
ProxyError: Cannot connect to proxy
```

### Solusi
```bash
# Set proxy untuk pip
pip install --proxy http://user:password@proxy.server:port semgrep

# Set proxy environment variables
set HTTP_PROXY=http://proxy.server:port
set HTTPS_PROXY=http://proxy.server:port
```

## 💾 Memory Issues

### Masalah: Out of Memory
```
MemoryError: Unable to allocate array
```

### Solusi
1. Scan file yang lebih kecil
2. Increase virtual memory
3. Close aplikasi lain
4. Gunakan 64-bit Python

## 📁 File Permission Issues

### Masalah: Access Denied
```
PermissionError: [Errno 13] Permission denied
```

### Solusi
1. Jalankan sebagai Administrator
2. Cek permission folder:
   ```bash
   # Windows
   icacls "C:\path\to\folder" /grant Users:F
   ```
3. Pindah project ke folder yang accessible

## 🔍 Debugging Steps

### 1. Enable Verbose Logging
```bash
python run.py -u https://example.com -v
```

### 2. Check Log Files
```bash
# Lihat scanner.log
type scanner.log

# Lihat telegram_bot.log (jika menggunakan bot)
type telegram_bot.log
```

### 3. Test Individual Components
```python
# Test downloader
python -c "from scanner.downloader import JSDownloader; print('Downloader OK')"

# Test scanners
python -c "from scanner.semgrep_scan import SemgrepScanner; print('Semgrep OK')"
python -c "from scanner.grype_scan import GrypeScanner; print('Grype OK')"
python -c "from scanner.trufflehog_scan import TruffleHogScanner; print('TruffleHog OK')"
```

## 🆘 Getting Help

Jika masalah masih berlanjut:

1. **Cek log files** untuk error detail
2. **Run dengan verbose mode**: `python run.py -u URL -v`
3. **Cek system requirements**:
   - Python 3.7+
   - Windows 10+ / macOS 10.14+ / Ubuntu 18.04+
   - 4GB RAM minimum
   - Internet connection

4. **Buat issue** di repository dengan informasi:
   - Operating system dan versi
   - Python version: `python --version`
   - Error message lengkap
   - Steps yang sudah dicoba
   - Log files (jika ada)

## 📚 Useful Commands

```bash
# System info
python --version
pip --version
echo $PATH  # Linux/macOS
echo %PATH% # Windows

# Check installed packages
pip list | grep -E "semgrep|truffleHog"

# Reinstall everything
pip uninstall semgrep truffleHog -y
pip install -r requirements.txt

# Clear pip cache
pip cache purge

# Update all packages
pip install --upgrade pip setuptools wheel
pip install --upgrade -r requirements.txt
```