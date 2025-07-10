#!/bin/bash
# NetPulse Build Script for Linux/macOS

echo "Building NetPulse..."
echo "==================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Install build dependencies
echo "Installing build dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller requests

# Run build script
echo "Running build script..."
python3 build.py

# Create installer executable (Linux/macOS)
echo "Creating installer package..."
python3 create_installer.py

echo ""
echo "Build completed!"
echo "Check the dist folder for packages."