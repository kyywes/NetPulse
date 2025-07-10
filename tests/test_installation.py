#!/usr/bin/env python3
"""
NetPulse Installation & Update Test Script
Tests the installation and auto-update functionality
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def test_installation_system():
    """Test the installation system"""
    print("Testing NetPulse Installation & Update System")
    print("=" * 50)
    
    # Test 1: Check installer wizard
    print("1. Testing Installer Wizard...")
    installer_path = os.path.join(os.path.dirname(__file__), 'installer', 'setup_wizard.py')
    if os.path.exists(installer_path):
        print("   ✓ Installer wizard found")
    else:
        print("   ✗ Installer wizard not found")
    
    # Test 2: Check auto-updater
    print("2. Testing Auto-Updater...")
    updater_path = os.path.join(os.path.dirname(__file__), 'updater_enhanced.py')
    if os.path.exists(updater_path):
        print("   ✓ Enhanced updater found")
        
        # Test updater import
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from updater_enhanced import UpdateManager
            print("   ✓ UpdateManager import successful")
            
            # Test updater initialization
            updater = UpdateManager()
            print("   ✓ UpdateManager initialization successful")
            
            # Test configuration loading
            config = updater.load_config()
            print("   ✓ Configuration loading successful")
            
        except Exception as e:
            print(f"   ✗ Updater test failed: {e}")
    else:
        print("   ✗ Enhanced updater not found")
    
    # Test 3: Check build system
    print("3. Testing Build System...")
    build_script = os.path.join(os.path.dirname(__file__), 'build_scripts', 'build.py')
    if os.path.exists(build_script):
        print("   ✓ Build script found")
    else:
        print("   ✗ Build script not found")
    
    # Test 4: Check modern GUI
    print("4. Testing Modern GUI...")
    modern_gui_path = os.path.join(os.path.dirname(__file__), 'netpulsegui_modern.py')
    if os.path.exists(modern_gui_path):
        print("   ✓ Modern GUI found")
        
        # Test GUI import
        try:
            from netpulsegui_modern import ModernNetPulseGUI
            print("   ✓ Modern GUI import successful")
        except Exception as e:
            print(f"   ✗ Modern GUI import failed: {e}")
    else:
        print("   ✗ Modern GUI not found")
    
    # Test 5: Check configuration system
    print("5. Testing Configuration System...")
    config_manager_path = os.path.join(os.path.dirname(__file__), 'config_manager.py')
    if os.path.exists(config_manager_path):
        print("   ✓ Configuration manager found")
        
        try:
            from config_manager import ConfigManager
            config_mgr = ConfigManager()
            print("   ✓ Configuration manager working")
        except Exception as e:
            print(f"   ✗ Configuration manager failed: {e}")
    else:
        print("   ✗ Configuration manager not found")
    
    # Test 6: Check network tools
    print("6. Testing Network Tools...")
    network_tools_path = os.path.join(os.path.dirname(__file__), 'network_tools.py')
    if os.path.exists(network_tools_path):
        print("   ✓ Network tools found")
        
        try:
            from network_tools import NetworkTools
            tools = NetworkTools()
            print("   ✓ Network tools working")
        except Exception as e:
            print(f"   ✗ Network tools failed: {e}")
    else:
        print("   ✗ Network tools not found")
    
    # Test 7: Check version consistency
    print("7. Testing Version Consistency...")
    version_file = os.path.join(os.path.dirname(__file__), 'version.txt')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            version = f.read().strip()
        print(f"   ✓ Version: {version}")
        
        # Check main.py version
        main_py = os.path.join(os.path.dirname(__file__), 'main.py')
        if os.path.exists(main_py):
            with open(main_py, 'r') as f:
                content = f.read()
                if version in content:
                    print("   ✓ Version consistency check passed")
                else:
                    print("   ⚠ Version mismatch in main.py")
    else:
        print("   ✗ Version file not found")
    
    print("\n" + "=" * 50)
    print("Installation & Update System Test Complete")
    print("=" * 50)

def test_build_process():
    """Test the build process"""
    print("\nTesting Build Process...")
    print("-" * 30)
    
    # Create temporary directory for test build
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Copy source to temp directory
        source_dir = os.path.dirname(__file__)
        test_source = os.path.join(temp_dir, 'netpulse_test')
        
        try:
            shutil.copytree(source_dir, test_source, 
                          ignore=shutil.ignore_patterns('build', 'dist', '.git', '__pycache__'))
            print("✓ Source files copied for testing")
            
            # Test build script import
            sys.path.insert(0, os.path.join(test_source, 'build_scripts'))
            from build import NetPulseBuilder
            
            # Initialize builder
            builder = NetPulseBuilder(test_source)
            print("✓ Build system initialized")
            
            # Test configuration
            print(f"✓ Build configuration: {builder.config['name']} v{builder.config['version']}")
            
            # Test clean build
            builder.clean_build()
            print("✓ Clean build test passed")
            
        except Exception as e:
            print(f"✗ Build test failed: {e}")

if __name__ == "__main__":
    test_installation_system()
    test_build_process()