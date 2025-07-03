@echo off
REM Wrapper script untuk menjalankan Grype melalui Docker
REM Usage: grype.bat [arguments]

REM Jalankan Grype menggunakan Docker
docker run --rm -v "%cd%":/workspace anchore/grype:latest %*