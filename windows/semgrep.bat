@echo off
REM Wrapper script untuk menjalankan Semgrep melalui Python
REM Usage: semgrep.bat [arguments]

REM Jalankan Semgrep menggunakan Python module
python -m semgrep %*