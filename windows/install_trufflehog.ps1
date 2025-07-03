# Install TruffleHog from GitHub
$toolsDir = "$env:LOCALAPPDATA\SecurityTools"
if (!(Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir -Force
}

$truffleDir = "$toolsDir\trufflehog"
if (!(Test-Path $truffleDir)) {
    New-Item -ItemType Directory -Path $truffleDir -Force
}

$truffleUrl = "https://github.com/trufflesecurity/trufflehog/releases/latest/download/trufflehog_windows_amd64.tar.gz"
$truffleTar = "$env:TEMP\trufflehog.tar.gz"

Write-Host "Downloading TruffleHog..."
Invoke-WebRequest -Uri $truffleUrl -OutFile $truffleTar -UseBasicParsing

Write-Host "Extracting TruffleHog..."
tar -xzf $truffleTar -C $truffleDir

Remove-Item $truffleTar -Force

Write-Host "TruffleHog installed to: $truffleDir"
Write-Host "Please add $truffleDir to your PATH manually"