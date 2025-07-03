# Install Grype from GitHub
$toolsDir = "$env:LOCALAPPDATA\SecurityTools"
if (!(Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir -Force
}

$grypeDir = "$toolsDir\grype"
if (!(Test-Path $grypeDir)) {
    New-Item -ItemType Directory -Path $grypeDir -Force
}

$grypeUrl = "https://github.com/anchore/grype/releases/latest/download/grype_windows_amd64.zip"
$grypeZip = "$env:TEMP\grype.zip"

Write-Host "Downloading Grype..."
Invoke-WebRequest -Uri $grypeUrl -OutFile $grypeZip -UseBasicParsing

Write-Host "Extracting Grype..."
Expand-Archive -Path $grypeZip -DestinationPath $grypeDir -Force

Remove-Item $grypeZip -Force

Write-Host "Grype installed to: $grypeDir"
Write-Host "Please add $grypeDir to your PATH manually"