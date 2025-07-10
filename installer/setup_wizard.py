#!/usr/bin/env python3
"""
NetPulse Setup Wizard
Professional installer for NetPulse Network Toolkit
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import json
import subprocess
import threading
import requests
from pathlib import Path
import winreg
import tempfile
import zipfile
from datetime import datetime

class NetPulseInstaller:
    """Professional NetPulse installer with wizard interface"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.current_step = 0
        self.total_steps = 6
        self.install_path = self._get_default_install_path()
        self.create_shortcuts = tk.BooleanVar(value=True)
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_menu = tk.BooleanVar(value=True)
        self.add_to_path = tk.BooleanVar(value=True)
        self.install_dependencies = tk.BooleanVar(value=True)
        self.enable_auto_update = tk.BooleanVar(value=True)
        
        self.setup_ui()
        
    def _get_default_install_path(self):
        """Get default installation path based on OS"""
        if sys.platform == "win32":
            return os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'NetPulse')
        else:
            return os.path.expanduser('~/Applications/NetPulse')
    
    def setup_ui(self):
        """Setup installer UI"""
        self.root.title("NetPulse 2.0 Setup Wizard")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Modern color scheme
        colors = {
            'bg': '#0D1117',
            'fg': '#F9FAFB',
            'accent': '#3B82F6',
            'secondary': '#161B22',
            'success': '#10B981',
            'border': '#374151'
        }
        
        self.root.configure(bg=colors['bg'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', 
                       background=colors['bg'], 
                       foreground=colors['fg'],
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=colors['bg'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Setup.TLabel',
                       background=colors['bg'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 10))
        
        style.configure('Setup.TButton',
                       background=colors['accent'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 10))
        
        style.configure('Setup.TFrame',
                       background=colors['bg'])
        
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Setup.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(self.main_frame, style='Setup.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="NetPulse 2.0 Setup", 
                 style='Title.TLabel').pack(side='left')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(header_frame, 
                                          variable=self.progress_var,
                                          maximum=self.total_steps)
        self.progress_bar.pack(side='right', fill='x', expand=True, padx=(20, 0))
        
        # Content frame
        self.content_frame = ttk.Frame(self.main_frame, style='Setup.TFrame')
        self.content_frame.pack(fill='both', expand=True)
        
        # Navigation frame
        nav_frame = ttk.Frame(self.main_frame, style='Setup.TFrame')
        nav_frame.pack(fill='x', pady=(20, 0))
        
        self.back_button = ttk.Button(nav_frame, text="Back", 
                                     command=self.go_back,
                                     style='Setup.TButton')
        self.back_button.pack(side='left')
        
        self.next_button = ttk.Button(nav_frame, text="Next", 
                                     command=self.go_next,
                                     style='Setup.TButton')
        self.next_button.pack(side='right')
        
        self.cancel_button = ttk.Button(nav_frame, text="Cancel", 
                                       command=self.cancel_install,
                                       style='Setup.TButton')
        self.cancel_button.pack(side='right', padx=(0, 10))
        
        # Show first step
        self.show_step()
        
    def show_step(self):
        """Show current installation step"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Update progress
        self.progress_var.set(self.current_step + 1)
        
        # Show appropriate step
        if self.current_step == 0:
            self.show_welcome()
        elif self.current_step == 1:
            self.show_license()
        elif self.current_step == 2:
            self.show_install_location()
        elif self.current_step == 3:
            self.show_components()
        elif self.current_step == 4:
            self.show_shortcuts()
        elif self.current_step == 5:
            self.show_install_progress()
        elif self.current_step == 6:
            self.show_complete()
            
        # Update navigation buttons
        self.back_button.config(state='normal' if self.current_step > 0 else 'disabled')
        
        if self.current_step == self.total_steps - 1:
            self.next_button.config(text="Install", command=self.start_installation)
        elif self.current_step == self.total_steps:
            self.next_button.config(text="Finish", command=self.finish_install)
        else:
            self.next_button.config(text="Next", command=self.go_next)
    
    def show_welcome(self):
        """Show welcome screen"""
        welcome_frame = ttk.Frame(self.content_frame, style='Setup.TFrame')
        welcome_frame.pack(fill='both', expand=True)
        
        ttk.Label(welcome_frame, text="Welcome to NetPulse 2.0 Setup", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        welcome_text = """This wizard will guide you through the installation of NetPulse 2.0 - Modern Network Toolkit.

NetPulse is a comprehensive network diagnostic and automation tool featuring:

• Modern tabbed interface with professional design
• Advanced network tools (Port Scanner, Network Discovery, Bandwidth Testing)
• Device automation and configuration management
• Command history and favorites system
• Automatic updates and professional export capabilities

Before you begin, please ensure you have:
• Administrative privileges (for system-wide installation)
• Internet connection (for downloading dependencies)
• At least 100MB of free disk space

Click 'Next' to continue with the installation."""
        
        text_widget = tk.Text(welcome_frame, wrap='word', height=15, width=60,
                             bg='#161B22', fg='#F9FAFB', font=('Segoe UI', 10),
                             relief='flat', padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', welcome_text)
        text_widget.config(state='disabled')
    
    def show_license(self):
        """Show license agreement"""
        license_frame = ttk.Frame(self.content_frame, style='Setup.TFrame')
        license_frame.pack(fill='both', expand=True)
        
        ttk.Label(license_frame, text="License Agreement", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        license_text = """MIT License

Copyright (c) 2024 NetPulse Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

By clicking 'Next', you agree to the terms of this license agreement."""
        
        text_widget = tk.Text(license_frame, wrap='word', height=15, width=60,
                             bg='#161B22', fg='#F9FAFB', font=('Consolas', 9),
                             relief='flat', padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', license_text)
        text_widget.config(state='disabled')
    
    def show_install_location(self):
        """Show installation location selection"""
        location_frame = ttk.Frame(self.content_frame, style='Setup.TFrame')
        location_frame.pack(fill='both', expand=True)
        
        ttk.Label(location_frame, text="Choose Installation Location", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        ttk.Label(location_frame, text="Setup will install NetPulse to the following folder:", 
                 style='Setup.TLabel').pack(anchor='w', pady=(0, 10))
        
        path_frame = ttk.Frame(location_frame, style='Setup.TFrame')
        path_frame.pack(fill='x', pady=(0, 20))
        
        self.install_path_var = tk.StringVar(value=self.install_path)
        path_entry = ttk.Entry(path_frame, textvariable=self.install_path_var, 
                              width=50, font=('Consolas', 10))
        path_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(path_frame, text="Browse", 
                  command=self.browse_install_path,
                  style='Setup.TButton').pack(side='right', padx=(10, 0))
        
        # Space requirements
        info_frame = ttk.Frame(location_frame, style='Setup.TFrame')
        info_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(info_frame, text="Space required: ~100 MB", 
                 style='Setup.TLabel').pack(anchor='w')
        
        try:
            free_space = shutil.disk_usage(os.path.dirname(self.install_path)).free
            free_space_mb = free_space / (1024 * 1024)
            ttk.Label(info_frame, text=f"Space available: {free_space_mb:.0f} MB", 
                     style='Setup.TLabel').pack(anchor='w')
        except:
            pass
    
    def show_components(self):
        """Show component selection"""
        components_frame = ttk.Frame(self.content_frame, style='Setup.TFrame')
        components_frame.pack(fill='both', expand=True)
        
        ttk.Label(components_frame, text="Select Components", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        ttk.Label(components_frame, text="Choose which components to install:", 
                 style='Setup.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Main application (required)
        main_frame = ttk.Frame(components_frame, style='Setup.TFrame')
        main_frame.pack(fill='x', pady=5)
        
        ttk.Checkbutton(main_frame, text="NetPulse Application (Required)", 
                       state='disabled', variable=tk.BooleanVar(value=True),
                       style='Setup.TCheckbutton').pack(anchor='w')
        
        # Dependencies
        deps_frame = ttk.Frame(components_frame, style='Setup.TFrame')
        deps_frame.pack(fill='x', pady=5)
        
        ttk.Checkbutton(deps_frame, text="Install Python Dependencies", 
                       variable=self.install_dependencies,
                       style='Setup.TCheckbutton').pack(anchor='w')
        
        # Auto-update
        update_frame = ttk.Frame(components_frame, style='Setup.TFrame')
        update_frame.pack(fill='x', pady=5)
        
        ttk.Checkbutton(update_frame, text="Enable Automatic Updates", 
                       variable=self.enable_auto_update,
                       style='Setup.TCheckbutton').pack(anchor='w')
        
        # File associations
        ttk.Label(components_frame, text="Additional Options:", 
                 style='Setup.TLabel').pack(anchor='w', pady=(20, 5))
        
        ttk.Checkbutton(components_frame, text="Add NetPulse to System PATH", 
                       variable=self.add_to_path,
                       style='Setup.TCheckbutton').pack(anchor='w', pady=2)
    
    def show_shortcuts(self):
        """Show shortcut options"""
        shortcuts_frame = ttk.Frame(self.content_frame, style='Setup.TFrame')
        shortcuts_frame.pack(fill='both', expand=True)
        
        ttk.Label(shortcuts_frame, text="Create Shortcuts", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        ttk.Label(shortcuts_frame, text="Choose where to create shortcuts:", 
                 style='Setup.TLabel').pack(anchor='w', pady=(0, 10))
        
        ttk.Checkbutton(shortcuts_frame, text="Create Desktop Shortcut", 
                       variable=self.create_desktop_shortcut,
                       style='Setup.TCheckbutton').pack(anchor='w', pady=5)
        
        ttk.Checkbutton(shortcuts_frame, text="Create Start Menu Entry", 
                       variable=self.create_start_menu,
                       style='Setup.TCheckbutton').pack(anchor='w', pady=5)
        
        # Installation summary
        summary_frame = ttk.Frame(shortcuts_frame, style='Setup.TFrame')
        summary_frame.pack(fill='x', pady=(30, 0))
        
        ttk.Label(summary_frame, text="Installation Summary:", 
                 style='Heading.TLabel').pack(anchor='w', pady=(0, 10))
        
        summary_text = f"""Installation Path: {self.install_path_var.get()}
Install Dependencies: {'Yes' if self.install_dependencies.get() else 'No'}
Auto-Updates: {'Enabled' if self.enable_auto_update.get() else 'Disabled'}
Desktop Shortcut: {'Yes' if self.create_desktop_shortcut.get() else 'No'}
Start Menu: {'Yes' if self.create_start_menu.get() else 'No'}
Add to PATH: {'Yes' if self.add_to_path.get() else 'No'}"""
        
        text_widget = tk.Text(summary_frame, wrap='word', height=8, width=60,
                             bg='#161B22', fg='#F9FAFB', font=('Consolas', 9),
                             relief='flat', padx=10, pady=10)
        text_widget.pack(fill='x')
        text_widget.insert('1.0', summary_text)
        text_widget.config(state='disabled')
    
    def show_install_progress(self):
        """Show installation progress"""
        progress_frame = ttk.Frame(self.content_frame, style='Setup.TFrame')
        progress_frame.pack(fill='both', expand=True)
        
        ttk.Label(progress_frame, text="Installing NetPulse 2.0", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        self.install_progress_var = tk.DoubleVar()
        self.install_progress_bar = ttk.Progressbar(progress_frame, 
                                                   variable=self.install_progress_var,
                                                   maximum=100)
        self.install_progress_bar.pack(fill='x', pady=(0, 20))
        
        self.install_status_var = tk.StringVar(value="Preparing installation...")
        ttk.Label(progress_frame, textvariable=self.install_status_var, 
                 style='Setup.TLabel').pack(anchor='w')
        
        # Installation log
        log_frame = ttk.Frame(progress_frame, style='Setup.TFrame')
        log_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        ttk.Label(log_frame, text="Installation Log:", 
                 style='Setup.TLabel').pack(anchor='w', pady=(0, 5))
        
        self.install_log = tk.Text(log_frame, wrap='word', height=10, width=60,
                                  bg='#161B22', fg='#F9FAFB', font=('Consolas', 8),
                                  relief='flat', padx=10, pady=10)
        self.install_log.pack(fill='both', expand=True)
        
        # Disable navigation during installation
        self.back_button.config(state='disabled')
        self.next_button.config(state='disabled')
        self.cancel_button.config(state='disabled')
    
    def show_complete(self):
        """Show installation complete"""
        complete_frame = ttk.Frame(self.content_frame, style='Setup.TFrame')
        complete_frame.pack(fill='both', expand=True)
        
        ttk.Label(complete_frame, text="Installation Complete!", 
                 style='Heading.TLabel').pack(pady=(0, 20))
        
        success_text = """NetPulse 2.0 has been successfully installed!

The following components have been installed:
• NetPulse Application
• Python Dependencies
• Configuration Files
• Documentation

You can now start using NetPulse by:
• Double-clicking the desktop shortcut (if created)
• Using the Start Menu entry (if created)
• Running 'netpulse' from command line (if added to PATH)

Thank you for choosing NetPulse!"""
        
        text_widget = tk.Text(complete_frame, wrap='word', height=15, width=60,
                             bg='#161B22', fg='#F9FAFB', font=('Segoe UI', 10),
                             relief='flat', padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', success_text)
        text_widget.config(state='disabled')
        
        # Launch option
        launch_frame = ttk.Frame(complete_frame, style='Setup.TFrame')
        launch_frame.pack(fill='x', pady=(20, 0))
        
        self.launch_app = tk.BooleanVar(value=True)
        ttk.Checkbutton(launch_frame, text="Launch NetPulse now", 
                       variable=self.launch_app,
                       style='Setup.TCheckbutton').pack(anchor='w')
    
    def browse_install_path(self):
        """Browse for installation path"""
        path = filedialog.askdirectory(initialdir=os.path.dirname(self.install_path))
        if path:
            self.install_path = os.path.join(path, 'NetPulse')
            self.install_path_var.set(self.install_path)
    
    def go_next(self):
        """Go to next step"""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.show_step()
    
    def go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()
    
    def start_installation(self):
        """Start the installation process"""
        self.current_step += 1
        self.show_step()
        
        # Start installation in separate thread
        install_thread = threading.Thread(target=self.perform_installation, daemon=True)
        install_thread.start()
    
    def perform_installation(self):
        """Perform the actual installation"""
        try:
            self.log_message("Starting NetPulse installation...")
            self.update_progress(0, "Creating installation directory...")
            
            # Create installation directory
            os.makedirs(self.install_path, exist_ok=True)
            self.log_message(f"Created directory: {self.install_path}")
            self.update_progress(10, "Copying application files...")
            
            # Copy application files
            source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.copy_files(source_dir, self.install_path)
            self.log_message("Application files copied successfully")
            self.update_progress(30, "Installing dependencies...")
            
            # Install dependencies
            if self.install_dependencies.get():
                self.install_python_dependencies()
            self.update_progress(50, "Creating configuration...")
            
            # Create configuration
            self.create_configuration()
            self.update_progress(60, "Creating shortcuts...")
            
            # Create shortcuts
            if self.create_desktop_shortcut.get():
                self.create_desktop_shortcut_file()
            if self.create_start_menu.get():
                self.create_start_menu_entry()
            self.update_progress(70, "Setting up auto-update...")
            
            # Setup auto-update
            if self.enable_auto_update.get():
                self.setup_auto_update()
            self.update_progress(80, "Adding to PATH...")
            
            # Add to PATH
            if self.add_to_path.get():
                self.add_to_system_path()
            self.update_progress(90, "Finalizing installation...")
            
            # Create uninstaller
            self.create_uninstaller()
            self.update_progress(100, "Installation complete!")
            
            self.log_message("NetPulse installation completed successfully!")
            
            # Move to completion screen
            self.root.after(1000, self.installation_complete)
            
        except Exception as e:
            self.log_message(f"Installation failed: {str(e)}")
            self.root.after(0, self.installation_failed, str(e))
    
    def copy_files(self, source_dir, dest_dir):
        """Copy application files"""
        exclude_patterns = {'.git', '__pycache__', '.pytest_cache', 'installer', 'build', 'dist'}
        
        for root, dirs, files in os.walk(source_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            
            # Calculate relative path
            rel_path = os.path.relpath(root, source_dir)
            if rel_path == '.':
                dest_root = dest_dir
            else:
                dest_root = os.path.join(dest_dir, rel_path)
            
            # Create destination directory
            os.makedirs(dest_root, exist_ok=True)
            
            # Copy files
            for file in files:
                if not file.endswith(('.pyc', '.pyo')):
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_root, file)
                    shutil.copy2(src_file, dest_file)
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        self.log_message("Installing Python dependencies...")
        
        requirements_file = os.path.join(self.install_path, 'requirements.txt')
        if os.path.exists(requirements_file):
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', requirements_file
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self.log_message("Dependencies installed successfully")
                else:
                    self.log_message(f"Warning: Some dependencies failed to install: {result.stderr}")
            except subprocess.TimeoutExpired:
                self.log_message("Warning: Dependency installation timed out")
            except Exception as e:
                self.log_message(f"Warning: Could not install dependencies: {str(e)}")
    
    def create_configuration(self):
        """Create initial configuration"""
        config_dir = os.path.join(self.install_path, 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        config = {
            'installation': {
                'path': self.install_path,
                'version': '2.0.0',
                'installed_date': datetime.now().isoformat(),
                'auto_update': self.enable_auto_update.get()
            },
            'settings': {
                'first_run': True,
                'check_updates_on_startup': True,
                'theme': 'dark'
            }
        }
        
        config_file = os.path.join(config_dir, 'installation.json')
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_message("Configuration created")
    
    def create_desktop_shortcut_file(self):
        """Create desktop shortcut"""
        try:
            if sys.platform == "win32":
                import win32com.client
                
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                shortcut_path = os.path.join(desktop, 'NetPulse.lnk')
                
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = os.path.join(self.install_path, 'main.py')
                shortcut.WorkingDirectory = self.install_path
                shortcut.IconLocation = os.path.join(self.install_path, 'icon.ico')
                shortcut.Description = "NetPulse 2.0 - Modern Network Toolkit"
                shortcut.save()
                
                self.log_message("Desktop shortcut created")
            else:
                # Linux/Mac desktop file
                desktop_file = f"""[Desktop Entry]
Name=NetPulse
Comment=Modern Network Toolkit
Exec=python3 "{os.path.join(self.install_path, 'main.py')}"
Icon={os.path.join(self.install_path, 'icon.png')}
Terminal=false
Type=Application
Categories=Network;System;
"""
                
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'NetPulse.desktop')
                with open(desktop_path, 'w') as f:
                    f.write(desktop_file)
                
                os.chmod(desktop_path, 0o755)
                self.log_message("Desktop shortcut created")
                
        except Exception as e:
            self.log_message(f"Could not create desktop shortcut: {str(e)}")
    
    def create_start_menu_entry(self):
        """Create Start Menu entry"""
        try:
            if sys.platform == "win32":
                import win32com.client
                
                start_menu = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
                shortcut_path = os.path.join(start_menu, 'NetPulse.lnk')
                
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = os.path.join(self.install_path, 'main.py')
                shortcut.WorkingDirectory = self.install_path
                shortcut.IconLocation = os.path.join(self.install_path, 'icon.ico')
                shortcut.Description = "NetPulse 2.0 - Modern Network Toolkit"
                shortcut.save()
                
                self.log_message("Start Menu entry created")
            else:
                # Linux applications directory
                app_dir = os.path.expanduser('~/.local/share/applications')
                os.makedirs(app_dir, exist_ok=True)
                
                desktop_file = f"""[Desktop Entry]
Name=NetPulse
Comment=Modern Network Toolkit
Exec=python3 "{os.path.join(self.install_path, 'main.py')}"
Icon={os.path.join(self.install_path, 'icon.png')}
Terminal=false
Type=Application
Categories=Network;System;
"""
                
                app_path = os.path.join(app_dir, 'netpulse.desktop')
                with open(app_path, 'w') as f:
                    f.write(desktop_file)
                
                self.log_message("Application entry created")
                
        except Exception as e:
            self.log_message(f"Could not create Start Menu entry: {str(e)}")
    
    def setup_auto_update(self):
        """Setup auto-update configuration"""
        try:
            update_config = {
                'enabled': True,
                'check_on_startup': True,
                'update_url': 'https://github.com/kyywes/NetPulse/releases/latest',
                'last_check': None,
                'auto_install': True
            }
            
            config_file = os.path.join(self.install_path, 'config', 'update.json')
            with open(config_file, 'w') as f:
                json.dump(update_config, f, indent=2)
            
            self.log_message("Auto-update configured")
        except Exception as e:
            self.log_message(f"Could not setup auto-update: {str(e)}")
    
    def add_to_system_path(self):
        """Add NetPulse to system PATH"""
        try:
            if sys.platform == "win32":
                # Add to Windows PATH
                import winreg
                
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                    try:
                        current_path, _ = winreg.QueryValueEx(key, 'PATH')
                    except FileNotFoundError:
                        current_path = ''
                    
                    if self.install_path not in current_path:
                        new_path = f"{current_path};{self.install_path}" if current_path else self.install_path
                        winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                        self.log_message("Added to system PATH")
            else:
                # Add to shell profile
                shell_profile = os.path.expanduser('~/.bashrc')
                if not os.path.exists(shell_profile):
                    shell_profile = os.path.expanduser('~/.profile')
                
                path_line = f'export PATH="$PATH:{self.install_path}"\n'
                
                with open(shell_profile, 'a') as f:
                    f.write(f'\n# NetPulse PATH\n{path_line}')
                
                self.log_message("Added to shell profile")
                
        except Exception as e:
            self.log_message(f"Could not add to PATH: {str(e)}")
    
    def create_uninstaller(self):
        """Create uninstaller"""
        try:
            uninstaller_script = f'''#!/usr/bin/env python3
"""NetPulse Uninstaller"""

import os
import sys
import shutil
import tkinter as tk
from tkinter import messagebox

def uninstall_netpulse():
    """Uninstall NetPulse"""
    install_path = "{self.install_path}"
    
    result = messagebox.askyesno(
        "Uninstall NetPulse",
        f"Are you sure you want to uninstall NetPulse from:\\n{install_path}?"
    )
    
    if result:
        try:
            # Remove installation directory
            if os.path.exists(install_path):
                shutil.rmtree(install_path)
            
            # Remove shortcuts
            desktop_shortcut = os.path.join(os.path.expanduser('~'), 'Desktop', 'NetPulse.lnk')
            if os.path.exists(desktop_shortcut):
                os.remove(desktop_shortcut)
            
            messagebox.showinfo("Success", "NetPulse has been uninstalled successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to uninstall NetPulse: {{str(e)}}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    uninstall_netpulse()
'''
            
            uninstaller_path = os.path.join(self.install_path, 'uninstall.py')
            with open(uninstaller_path, 'w') as f:
                f.write(uninstaller_script)
            
            self.log_message("Uninstaller created")
        except Exception as e:
            self.log_message(f"Could not create uninstaller: {str(e)}")
    
    def log_message(self, message):
        """Log installation message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.root.after(0, self._append_log, log_entry)
    
    def _append_log(self, message):
        """Append message to log (thread-safe)"""
        if hasattr(self, 'install_log'):
            self.install_log.insert('end', message)
            self.install_log.see('end')
    
    def update_progress(self, value, status):
        """Update progress bar and status"""
        self.root.after(0, self._update_progress, value, status)
    
    def _update_progress(self, value, status):
        """Update progress (thread-safe)"""
        if hasattr(self, 'install_progress_var'):
            self.install_progress_var.set(value)
            self.install_status_var.set(status)
    
    def installation_complete(self):
        """Handle successful installation"""
        self.current_step += 1
        self.show_step()
        
        # Re-enable finish button
        self.next_button.config(state='normal')
    
    def installation_failed(self, error):
        """Handle installation failure"""
        messagebox.showerror("Installation Failed", 
                           f"Installation failed with error:\n{error}\n\nPlease check the log for details.")
        self.next_button.config(state='normal', text="Retry", command=self.start_installation)
    
    def finish_install(self):
        """Finish installation and launch app if requested"""
        if self.launch_app.get():
            try:
                main_script = os.path.join(self.install_path, 'main.py')
                subprocess.Popen([sys.executable, main_script], cwd=self.install_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not launch NetPulse: {str(e)}")
        
        self.root.destroy()
    
    def cancel_install(self):
        """Cancel installation"""
        result = messagebox.askyesno("Cancel Installation", 
                                   "Are you sure you want to cancel the installation?")
        if result:
            self.root.destroy()
    
    def run(self):
        """Run the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    installer = NetPulseInstaller()
    installer.run()