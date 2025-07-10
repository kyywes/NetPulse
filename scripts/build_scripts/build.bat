@echo off
REM NetPulse Build Script for Windows

echo Building NetPulse...
echo ==================

REM Set Python path
set PYTHON=python

REM Check if Python is available
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Install build dependencies
echo Installing build dependencies...
%PYTHON% -m pip install --upgrade pip
%PYTHON% -m pip install pyinstaller requests

REM Run build script
echo Running build script...
%PYTHON% build.py

REM Create installer executable
echo Creating installer executable...
%PYTHON% create_installer.py

echo.
echo Build completed!
echo Check the dist folder for packages.
pause