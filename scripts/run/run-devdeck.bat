@echo off
REM Start DevDeck application
REM This script activates the virtual environment and runs the application

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.sh first.
    echo Or create a virtual environment manually:
    echo   python -m venv venv
    echo   venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment and run the application
REM Note: This uses CMD activation. For PowerShell, use run-devdeck.ps1 instead
call venv\Scripts\activate.bat
python -m devdeck.main

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)

