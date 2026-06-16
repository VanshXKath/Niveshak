# One-time project setup: virtual environment + dependencies
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "Creating virtual environment..."
py -3 -m venv .venv

Write-Host "Activating virtual environment..."
& ".\.venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "Next steps:"
Write-Host "  1. Activate: .\.venv\Scripts\Activate.ps1"
Write-Host "  2. Backend:  python -m uvicorn backend.app.main:app --reload"
Write-Host "  3. Frontend: python -m streamlit run frontend/streamlit_app.py"
