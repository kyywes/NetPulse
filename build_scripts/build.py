#!/usr/bin/env python3
"""
NetPulse Build Script
Creates distributable packages for NetPulse
"""

import os
import sys
import shutil
import zipfile
import subprocess
import json
import argparse
from datetime import datetime
from pathlib import Path

class NetPulseBuilder:
    """NetPulse build system"""
    
    def __init__(self, source_dir=None):
        self.source_dir = source_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.build_dir = os.path.join(self.source_dir, 'build')
        self.dist_dir = os.path.join(self.source_dir, 'dist')
        self.version = self.get_version()
        
        # Build configuration
        self.config = {
            'name': 'NetPulse',
            'version': self.version,
            'description': 'Modern Network Toolkit',
            'author': 'NetPulse Development Team',
            'license': 'MIT',
            'python_requires': '>=3.7',
            'platforms': ['Windows', 'Linux', 'macOS'],
            'build_date': datetime.now().isoformat()
        }
        
    def get_version(self):
        """Get version from version.txt"""
        version_file = os.path.join(self.source_dir, 'version.txt')
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        return '2.0.0'
    
    def clean_build(self):
        """Clean build directories"""
        print("Cleaning build directories...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        
        # Remove Python cache files
        for root, dirs, files in os.walk(self.source_dir):
            for d in dirs[:]:
                if d == '__pycache__':
                    shutil.rmtree(os.path.join(root, d))
                    dirs.remove(d)
            for f in files:
                if f.endswith(('.pyc', '.pyo')):
                    os.remove(os.path.join(root, f))
        
        print("Build directories cleaned")
    
    def prepare_build(self):
        """Prepare build environment"""
        print("Preparing build environment...")
        
        # Create build directories
        os.makedirs(self.build_dir, exist_ok=True)
        os.makedirs(self.dist_dir, exist_ok=True)
        
        # Copy source files
        app_build_dir = os.path.join(self.build_dir, 'NetPulse')
        self.copy_source_files(app_build_dir)
        
        # Create build info
        self.create_build_info(app_build_dir)
        
        print("Build environment prepared")
        return app_build_dir
    
    def copy_source_files(self, dest_dir):
        """Copy source files to build directory"""
        print("Copying source files...")
        
        # Files and directories to exclude
        exclude_patterns = {
            'build/', 'dist/', '.git/', '__pycache__/', '*.pyc', '*.pyo',
            '.pytest_cache/', '.vscode/', '.idea/', '*.log', 'temp/',
            'backup/', '.DS_Store', 'Thumbs.db'
        }
        
        def should_exclude(path):
            rel_path = os.path.relpath(path, self.source_dir)
            return any(
                rel_path.startswith(pattern.rstrip('/')) or
                rel_path.endswith(pattern.lstrip('*'))
                for pattern in exclude_patterns
            )
        
        # Copy files
        for root, dirs, files in os.walk(self.source_dir):
            if should_exclude(root):
                dirs.clear()
                continue
            
            # Filter directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            # Calculate destination path
            rel_path = os.path.relpath(root, self.source_dir)
            if rel_path == '.':
                dest_root = dest_dir
            else:
                dest_root = os.path.join(dest_dir, rel_path)
            
            # Create destination directory
            os.makedirs(dest_root, exist_ok=True)
            
            # Copy files
            for file in files:
                if not should_exclude(os.path.join(root, file)):
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_root, file)
                    shutil.copy2(src_file, dest_file)
        
        print("Source files copied")
    
    def create_build_info(self, app_dir):
        """Create build information file"""
        build_info = {
            'build_info': self.config,
            'files': self.get_file_list(app_dir),
            'checksums': self.calculate_checksums(app_dir)
        }
        
        build_info_file = os.path.join(app_dir, 'build_info.json')
        with open(build_info_file, 'w') as f:
            json.dump(build_info, f, indent=2)
        
        print("Build info created")
    
    def get_file_list(self, app_dir):
        """Get list of files in the build"""
        files = []
        for root, dirs, filenames in os.walk(app_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, app_dir)
                files.append({
                    'path': rel_path,
                    'size': os.path.getsize(file_path)
                })
        return files
    
    def calculate_checksums(self, app_dir):
        """Calculate file checksums"""
        import hashlib
        
        checksums = {}
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, app_dir)
                
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        checksums[rel_path] = file_hash
                except (IOError, OSError):
                    pass
        
        return checksums
    
    def create_portable_zip(self, app_dir):
        """Create portable ZIP package"""
        print("Creating portable ZIP package...")
        
        zip_filename = f"NetPulse-{self.version}-portable.zip"
        zip_path = os.path.join(self.dist_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(app_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, app_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Portable ZIP created: {zip_filename}")
        return zip_path
    
    def create_installer_package(self, app_dir):
        """Create installer package"""
        print("Creating installer package...")
        
        # Copy installer files
        installer_source = os.path.join(self.source_dir, 'installer')
        installer_dest = os.path.join(app_dir, 'installer')
        
        if os.path.exists(installer_source):
            shutil.copytree(installer_source, installer_dest)
        
        # Create installer ZIP
        installer_filename = f"NetPulse-{self.version}-installer.zip"
        installer_path = os.path.join(self.dist_dir, installer_filename)
        
        with zipfile.ZipFile(installer_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(app_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, app_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Installer package created: {installer_filename}")
        return installer_path
    
    def create_executable(self, app_dir):
        """Create executable using PyInstaller"""
        print("Creating executable...")
        
        try:
            # Install PyInstaller if not available
            try:
                import PyInstaller
            except ImportError:
                print("Installing PyInstaller...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            
            # PyInstaller command
            main_script = os.path.join(app_dir, 'main.py')
            
            pyinstaller_cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',
                '--windowed',
                '--name', f'NetPulse-{self.version}',
                '--distpath', self.dist_dir,
                '--workpath', os.path.join(self.build_dir, 'pyinstaller'),
                '--specpath', os.path.join(self.build_dir, 'pyinstaller'),
                main_script
            ]
            
            # Add icon if available
            icon_path = os.path.join(app_dir, 'icon.ico')
            if os.path.exists(icon_path):
                pyinstaller_cmd.extend(['--icon', icon_path])
            
            # Run PyInstaller
            subprocess.check_call(pyinstaller_cmd, cwd=app_dir)
            
            print("Executable created successfully")
            return True
            
        except Exception as e:
            print(f"Failed to create executable: {e}")
            return False
    
    def create_release_notes(self):
        """Create release notes"""
        print("Creating release notes...")
        
        release_notes = f"""# NetPulse {self.version} Release Notes

## Release Information
- **Version**: {self.version}
- **Build Date**: {self.config['build_date']}
- **Python Requirements**: {self.config['python_requires']}

## New Features in Version 2.0
- Modern tabbed interface with professional design
- Advanced network tools (Port Scanner, Network Discovery, Bandwidth Testing)
- Enhanced automation and device management
- Command history and favorites system
- Automatic updates with backup and restore
- Professional installer with uninstall support
- Improved performance with multi-threading
- Better error handling and user feedback

## Installation Options
1. **Installer Package**: `NetPulse-{self.version}-installer.zip`
   - Extract and run `setup_wizard.py` for guided installation
   - Includes auto-update capability and system integration

2. **Portable Package**: `NetPulse-{self.version}-portable.zip`
   - Extract and run `main.py` directly
   - No installation required, fully portable

3. **Executable**: `NetPulse-{self.version}.exe` (Windows)
   - Standalone executable, no Python required
   - Double-click to run

## System Requirements
- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: 3.7+ (for source/portable versions)
- **Memory**: 100MB RAM minimum
- **Storage**: 100MB free space
- **Network**: Internet connection for updates and remote operations

## Upgrade Instructions
1. **From v1.x**: Use installer for clean installation
2. **From v2.x**: Auto-update will handle the upgrade
3. **Portable Users**: Extract new version to replace old files

## Support
- GitHub Issues: https://github.com/kyywes/NetPulse/issues
- Documentation: README.md
- License: MIT License

---
*Thank you for using NetPulse!*
"""
        
        notes_file = os.path.join(self.dist_dir, f'NetPulse-{self.version}-ReleaseNotes.txt')
        with open(notes_file, 'w') as f:
            f.write(release_notes)
        
        print("Release notes created")
    
    def create_checksums_file(self):
        """Create checksums file for all packages"""
        print("Creating checksums file...")
        
        import hashlib
        
        checksums = {}
        
        for file in os.listdir(self.dist_dir):
            if file.endswith(('.zip', '.exe')):
                file_path = os.path.join(self.dist_dir, file)
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    checksums[file] = file_hash
        
        # Write checksums file
        checksums_file = os.path.join(self.dist_dir, 'checksums.txt')
        with open(checksums_file, 'w') as f:
            f.write(f"NetPulse {self.version} - Package Checksums\n")
            f.write("=" * 50 + "\n\n")
            for filename, checksum in checksums.items():
                f.write(f"{checksum}  {filename}\n")
        
        print("Checksums file created")
    
    def build_all(self, include_exe=True):
        """Build all packages"""
        print(f"Building NetPulse {self.version}...")
        print("=" * 50)
        
        # Clean previous builds
        self.clean_build()
        
        # Prepare build
        app_dir = self.prepare_build()
        
        # Create packages
        packages = []
        
        # Portable ZIP
        zip_path = self.create_portable_zip(app_dir)
        packages.append(zip_path)
        
        # Installer package
        installer_path = self.create_installer_package(app_dir)
        packages.append(installer_path)
        
        # Executable (optional)
        if include_exe:
            if self.create_executable(app_dir):
                packages.append("Executable created")
        
        # Release notes
        self.create_release_notes()
        
        # Checksums
        self.create_checksums_file()
        
        # Build summary
        print("\n" + "=" * 50)
        print("BUILD COMPLETE")
        print("=" * 50)
        print(f"Version: {self.version}")
        print(f"Build Date: {self.config['build_date']}")
        print(f"Output Directory: {self.dist_dir}")
        print("\nPackages Created:")
        for package in packages:
            print(f"  - {os.path.basename(package) if os.path.exists(package) else package}")
        
        return packages

def main():
    """Main build function"""
    parser = argparse.ArgumentParser(description='Build NetPulse packages')
    parser.add_argument('--no-exe', action='store_true', help='Skip executable creation')
    parser.add_argument('--clean-only', action='store_true', help='Only clean build directories')
    parser.add_argument('--source-dir', help='Source directory path')
    
    args = parser.parse_args()
    
    # Initialize builder
    builder = NetPulseBuilder(args.source_dir)
    
    if args.clean_only:
        builder.clean_build()
        print("Build directories cleaned")
        return
    
    # Build all packages
    try:
        packages = builder.build_all(include_exe=not args.no_exe)
        print(f"\nBuild completed successfully!")
        print(f"Created {len(packages)} packages")
        
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()