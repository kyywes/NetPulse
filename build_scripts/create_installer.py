#!/usr/bin/env python3
"""
Create NetPulse Installer
Standalone script to create installer executable
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def create_installer_executable():
    """Create installer executable using PyInstaller"""
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(script_dir)
    installer_dir = os.path.join(app_dir, 'installer')
    setup_script = os.path.join(installer_dir, 'setup_wizard.py')
    
    if not os.path.exists(setup_script):
        print("Error: setup_wizard.py not found in installer directory")
        return False
    
    # Install PyInstaller if needed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Create temporary work directory
    with tempfile.TemporaryDirectory() as temp_dir:
        work_dir = os.path.join(temp_dir, 'installer_build')
        os.makedirs(work_dir)
        
        # Copy installer files
        for file in os.listdir(installer_dir):
            src = os.path.join(installer_dir, file)
            dst = os.path.join(work_dir, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
        
        # Copy application files to installer
        app_files_dir = os.path.join(work_dir, 'netpulse_app')
        shutil.copytree(app_dir, app_files_dir, 
                       ignore=shutil.ignore_patterns(
                           'build', 'dist', '.git', '__pycache__', '*.pyc', 
                           'installer', 'build_scripts', 'backup', 'temp'
                       ))
        
        # Create installer spec file
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{os.path.join(work_dir, "setup_wizard.py")}'],
    pathex=['{work_dir}'],
    binaries=[],
    datas=[
        ('{app_files_dir}', 'netpulse_app'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'requests',
        'json',
        'shutil',
        'subprocess',
        'threading',
        'zipfile',
        'tempfile',
        'pathlib',
        'datetime',
        'winreg',
        'win32com.client',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NetPulse-Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{os.path.join(app_dir, "icon.ico") if os.path.exists(os.path.join(app_dir, "icon.ico")) else None}',
)
'''
        
        spec_file = os.path.join(work_dir, 'installer.spec')
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # Build installer
        print("Creating installer executable...")
        cmd = [sys.executable, '-m', 'PyInstaller', spec_file, '--distpath', os.path.join(app_dir, 'dist')]
        
        result = subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Installer executable created successfully!")
            print(f"Location: {os.path.join(app_dir, 'dist', 'NetPulse-Setup.exe')}")
            return True
        else:
            print("Failed to create installer executable")
            print("Error:", result.stderr)
            return False

if __name__ == "__main__":
    create_installer_executable()