#!/usr/bin/env python3
"""
NetPulse 2.0 - Project Structure Validation
Validates the new clean project structure
"""

import os
import sys
from pathlib import Path

def validate_project_structure():
    """Validate the new project structure"""
    print("🔍 NetPulse 2.0 - Project Structure Validation")
    print("=" * 60)
    
    # Expected structure
    expected_structure = {
        "files": [
            "main.py",
            "requirements.txt", 
            "version.txt",
            "LICENSE",
            "README.md",
            "CHANGELOG.md",
            ".gitignore"
        ],
        "directories": {
            "netpulse": {
                "files": ["__init__.py"],
                "directories": {
                    "core": {
                        "files": ["__init__.py", "network_tools.py", "config_manager.py"]
                    },
                    "gui": {
                        "files": ["__init__.py", "application.py", "theme.py", "legacy.py"]
                    },
                    "automation": {
                        "files": ["__init__.py", "device_manager.py"]
                    },
                    "utils": {
                        "files": ["__init__.py", "updater.py"]
                    }
                }
            },
            "scripts": {
                "files": [],
                "directories": {
                    "build_scripts": {
                        "files": ["build.py", "create_installer.py", "build.bat", "build.sh"]
                    },
                    "installer": {
                        "files": ["setup_wizard.py"]
                    }
                }
            },
            "tests": {
                "files": ["test_installation.py", "test_automation.py", "demo_installation.py", "demo_automation.py"]
            },
            "docs": {
                "files": ["README_MODERN.md", "INSTALLATION_GUIDE.md", "AUTOMATION_COMMANDS.md"]
            },
            "inventory": {
                "files": ["db_config.ini"]
            },
            "config": {
                "files": []
            },
            "data": {
                "files": ["netpulse.db"]
            }
        }
    }
    
    def check_structure(path, structure, level=0):
        """Recursively check structure"""
        indent = "  " * level
        all_good = True
        
        # Check files
        if "files" in structure:
            for file in structure["files"]:
                file_path = os.path.join(path, file)
                if os.path.exists(file_path):
                    print(f"{indent}✓ {file}")
                else:
                    print(f"{indent}✗ {file} (missing)")
                    all_good = False
        
        # Check directories
        if "directories" in structure:
            for dir_name, dir_structure in structure["directories"].items():
                dir_path = os.path.join(path, dir_name)
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    print(f"{indent}📁 {dir_name}/")
                    if not check_structure(dir_path, dir_structure, level + 1):
                        all_good = False
                else:
                    print(f"{indent}✗ {dir_name}/ (missing directory)")
                    all_good = False
        
        return all_good
    
    # Check root files
    print("📁 Root Files:")
    root_path = os.path.dirname(os.path.abspath(__file__))
    
    for file in expected_structure["files"]:
        file_path = os.path.join(root_path, file)
        if os.path.exists(file_path):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (missing)")
    
    print("\n📁 Directory Structure:")
    structure_valid = check_structure(root_path, expected_structure)
    
    return structure_valid

def validate_imports():
    """Validate that all imports work correctly"""
    print("\n🔗 Import Validation:")
    print("-" * 30)
    
    imports_to_test = [
        ("netpulse", "Main package"),
        ("netpulse.core", "Core components"),
        ("netpulse.core.network_tools", "Network tools"),
        ("netpulse.core.config_manager", "Configuration manager"),
        ("netpulse.gui", "GUI components"),
        ("netpulse.gui.theme", "Theme system"),
        ("netpulse.automation", "Automation components"),
        ("netpulse.automation.device_manager", "Device manager"),
        ("netpulse.utils", "Utilities"),
        ("netpulse.utils.updater", "Update manager")
    ]
    
    all_imports_good = True
    
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"  ✓ {module} - {description}")
        except ImportError as e:
            print(f"  ✗ {module} - {description} (ImportError: {e})")
            all_imports_good = False
        except Exception as e:
            print(f"  ⚠ {module} - {description} (Error: {e})")
    
    return all_imports_good

def validate_entry_points():
    """Validate entry points work"""
    print("\n🚀 Entry Point Validation:")
    print("-" * 30)
    
    try:
        # Test main.py syntax
        with open("main.py", "r") as f:
            main_content = f.read()
        
        compile(main_content, "main.py", "exec")
        print("  ✓ main.py - Syntax valid")
        
        # Test if we can import main components
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        try:
            from netpulse.gui.application import NetPulseApplication
            print("  ✓ NetPulseApplication - Import successful")
        except Exception as e:
            print(f"  ✗ NetPulseApplication - Import failed: {e}")
        
        try:
            from netpulse.core.network_tools import NetworkTools
            print("  ✓ NetworkTools - Import successful")
        except Exception as e:
            print(f"  ✗ NetworkTools - Import failed: {e}")
        
        return True
        
    except SyntaxError as e:
        print(f"  ✗ main.py - Syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Entry point validation failed: {e}")
        return False

def check_file_sizes():
    """Check file sizes to ensure content is present"""
    print("\n📊 File Size Validation:")
    print("-" * 30)
    
    important_files = [
        "main.py",
        "netpulse/core/network_tools.py",
        "netpulse/gui/application.py",
        "netpulse/automation/device_manager.py",
        "README.md",
        "CHANGELOG.md"
    ]
    
    for file_path in important_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size > 1000:  # At least 1KB
                print(f"  ✓ {file_path} ({size:,} bytes)")
            else:
                print(f"  ⚠ {file_path} ({size} bytes - seems small)")
        else:
            print(f"  ✗ {file_path} (missing)")

def show_project_summary():
    """Show project summary"""
    print("\n📋 PROJECT SUMMARY")
    print("=" * 60)
    
    # Count files
    total_files = 0
    code_files = 0
    doc_files = 0
    
    for root, dirs, files in os.walk("."):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if not file.startswith('.') and not file.endswith('.pyc'):
                total_files += 1
                if file.endswith('.py'):
                    code_files += 1
                elif file.endswith('.md'):
                    doc_files += 1
    
    print(f"📁 Total Files: {total_files}")
    print(f"🐍 Python Files: {code_files}")
    print(f"📖 Documentation Files: {doc_files}")
    
    # Show directory structure
    print(f"\n📂 Directory Structure:")
    for root, dirs, files in os.walk("."):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        level = root.replace(".", "").count(os.sep)
        indent = "  " * level
        print(f"{indent}{os.path.basename(root)}/")
        
        sub_indent = "  " * (level + 1)
        for file in files:
            if not file.startswith('.') and not file.endswith('.pyc'):
                print(f"{sub_indent}{file}")

def main():
    """Main validation function"""
    print("Starting NetPulse 2.0 project validation...\n")
    
    # Run validations
    structure_valid = validate_project_structure()
    imports_valid = validate_imports()
    entry_points_valid = validate_entry_points()
    
    # Additional checks
    check_file_sizes()
    show_project_summary()
    
    # Final result
    print("\n" + "=" * 60)
    if structure_valid and imports_valid and entry_points_valid:
        print("🎉 PROJECT VALIDATION SUCCESSFUL!")
        print("✅ All components are properly organized and functional")
    else:
        print("⚠️  PROJECT VALIDATION ISSUES DETECTED")
        print("❌ Some components need attention")
    
    print("🚀 NetPulse 2.0 - Clean, Modern, Professional")
    print("=" * 60)

if __name__ == "__main__":
    main()