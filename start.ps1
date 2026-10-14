# Stage Time launcher for Windows.
#
# The first run creates a private Python workspace OUTSIDE OneDrive, under
# %LOCALAPPDATA%\stage-time\venv, and installs what the app needs (5 to 15
# minutes). Every later run starts in a few seconds.
#
# Double-click start.bat, or in PowerShell:   .\start.ps1
# Optional port:                              .\start.ps1 8001

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$venv = Join-Path $env:LOCALAPPDATA "stage-time\venv"
$py = Join-Path $venv "Scripts\python.exe"
$port = if ($args.Count -gt 0) { $args[0] } else { 8000 }

function New-Workspace {
    Write-Host "First run: creating the app's private workspace at $venv"
    $made = $false
    foreach ($v in @("-3.12", "-3.13", "-3.11", "-3.10")) {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            & py $v -m venv $venv 2>$null
            if (Test-Path $py) { $made = $true; break }
        }
    }
    if (-not $made) {
        & python -m venv $venv
    }
    if (-not (Test-Path $py)) {
        throw "Could not create the workspace. Install Python 3.12 from python.org (tick 'Add python.exe to PATH') and run this again."
    }
    Write-Host "Installing the app's parts. Expect a wall of scrolling text for 5 to 15 minutes."
    & $py -m pip install --disable-pip-version-check -r (Join-Path $here "requirements.txt")
}

if (-not (Test-Path $py)) { New-Workspace }

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "ffmpeg is not installed, so recordings cannot be converted. Run:  winget install ffmpeg"
    Write-Host "then close this window, open a new one, and start again."
    Write-Host ""
}
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama is not installed. Coaching, roleplay follow-ups and lookups will be off until it is."
    Write-Host "Get it from https://ollama.com/download, then run:  ollama pull qwen2.5:3b"
    Write-Host ""
}

Set-Location $here
Write-Host "Stage Time is starting on http://127.0.0.1:$port"
Write-Host "Leave this window open. Press Ctrl+C to stop the app."
if (-not $env:STAGE_TIME_NO_BROWSER) {
    Start-Job -ScriptBlock {
        param($u) Start-Sleep -Seconds 4; Start-Process $u
    } -ArgumentList "http://127.0.0.1:$port" | Out-Null
}
& $py -m uvicorn main:app --host 127.0.0.1 --port $port
