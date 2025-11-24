# Start DevDeck application
# This script activates the virtual environment and runs the application

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Please run setup.sh first." -ForegroundColor Red
    Write-Host "Or create a virtual environment manually:"
    Write-Host "  python -m venv venv"
    Write-Host "  .\venv\Scripts\pip install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment and run the application
.\venv\Scripts\Activate.ps1
python -m devdeck.main

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Application exited with an error." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}

