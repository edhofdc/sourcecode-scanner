#!/usr/bin/env pwsh
# PowerShell script untuk menjalankan Source Code Scanner menggunakan Docker

param(
    [Parameter(Position=0)]
    [string]$Command = "",
    [Parameter(Position=1)]
    [string]$Url = ""
)

function Show-Usage {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Source Code Scanner" -ForegroundColor Cyan
    Write-Host "Docker Setup" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\run-docker.ps1 build          - Build Docker image" -ForegroundColor White
    Write-Host "  .\run-docker.ps1 run            - Run interactive container" -ForegroundColor White
    Write-Host "  .\run-docker.ps1 scan [url]     - Run vulnerability scan" -ForegroundColor White
    Write-Host "  .\run-docker.ps1 test           - Test tools installation" -ForegroundColor White
    Write-Host "  .\run-docker.ps1 shell          - Open shell in container" -ForegroundColor White
    Write-Host "  .\run-docker.ps1 stop           - Stop and remove containers" -ForegroundColor White
    Write-Host "  .\run-docker.ps1 logs           - Show container logs" -ForegroundColor White
    Write-Host "  .\run-docker.ps1 clean          - Clean up Docker resources" -ForegroundColor White
    Write-Host ""
}

function Test-DockerInstalled {
    try {
        $null = docker --version
        return $true
    }
    catch {
        Write-Host "Error: Docker is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Docker Desktop first" -ForegroundColor Red
        return $false
    }
}

function Test-DockerRunning {
    try {
        $null = docker ps
        return $true
    }
    catch {
        Write-Host "Error: Docker is not running" -ForegroundColor Red
        Write-Host "Please start Docker Desktop" -ForegroundColor Red
        return $false
    }
}

if ($Command -eq "") {
    Show-Usage
    exit 0
}

# Check Docker prerequisites
if (-not (Test-DockerInstalled)) {
    exit 1
}

if (-not (Test-DockerRunning)) {
    exit 1
}

switch ($Command.ToLower()) {
    "build" {
        Write-Host "Building Docker image..." -ForegroundColor Green
        docker-compose build
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "Build failed!" -ForegroundColor Red
        }
    }
    
    "run" {
        Write-Host "Starting interactive container..." -ForegroundColor Green
        docker-compose up -d sourcecode-scanner
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Container started. Opening shell..." -ForegroundColor Green
            docker-compose exec sourcecode-scanner /bin/bash
        }
    }
    
    "scan" {
        Write-Host "Running vulnerability scan..." -ForegroundColor Green
        if ($Url -ne "") {
            docker-compose run --rm scanner-cli python run.py -u $Url
        } else {
            docker-compose run --rm scanner-cli python run.py
        }
    }
    
    "test" {
        Write-Host "Testing tools installation..." -ForegroundColor Green
        docker-compose run --rm scanner-cli python test_tools.py
    }
    
    "shell" {
        Write-Host "Opening shell in running container..." -ForegroundColor Green
        docker-compose exec sourcecode-scanner /bin/bash
    }
    
    "stop" {
        Write-Host "Stopping and removing containers..." -ForegroundColor Green
        docker-compose down
        Write-Host "Containers stopped." -ForegroundColor Green
    }
    
    "logs" {
        Write-Host "Showing container logs..." -ForegroundColor Green
        docker-compose logs -f sourcecode-scanner
    }
    
    "clean" {
        Write-Host "Cleaning up Docker resources..." -ForegroundColor Yellow
        docker-compose down --rmi all --volumes --remove-orphans
        Write-Host "Cleanup completed." -ForegroundColor Green
    }
    
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use '.\run-docker.ps1' without arguments to see usage." -ForegroundColor Red
        exit 1
    }
}