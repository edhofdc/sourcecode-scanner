@echo off
REM Script untuk menjalankan Source Code Scanner menggunakan Docker

echo ========================================
echo Source Code Scanner
echo Docker Setup
echo ========================================
echo.

if "%1"=="" (
    echo Usage:
    echo   run-docker.bat build          - Build Docker image
    echo   run-docker.bat run            - Run interactive container
    echo   run-docker.bat scan           - Run vulnerability scan
    echo   run-docker.bat test           - Test tools installation
    echo   run-docker.bat shell          - Open shell in container
    echo   run-docker.bat stop           - Stop and remove containers
    echo   run-docker.bat logs           - Show container logs
    echo.
    goto :end
)

if "%1"=="build" (
    echo Building Docker image...
    docker-compose build
    goto :end
)

if "%1"=="run" (
    echo Starting interactive container...
    docker-compose up -d sourcecode-scanner
docker-compose exec sourcecode-scanner /bin/bash
    goto :end
)

if "%1"=="scan" (
    echo Running vulnerability scan...
    docker-compose run --rm scanner-cli python run.py
    goto :end
)

if "%1"=="test" (
    echo Testing tools installation...
    docker-compose run --rm scanner-cli python test_tools.py
    goto :end
)

if "%1"=="shell" (
    echo Opening shell in running container...
    docker-compose exec sourcecode-scanner /bin/bash
    goto :end
)

if "%1"=="stop" (
    echo Stopping and removing containers...
    docker-compose down
    goto :end
)

if "%1"=="logs" (
    echo Showing container logs...
    docker-compose logs -f sourcecode-scanner
    goto :end
)

echo Unknown command: %1
echo Use 'run-docker.bat' without arguments to see usage.

:end