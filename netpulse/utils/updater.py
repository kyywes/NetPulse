#!/usr/bin/env python3
"""
Enhanced NetPulse Auto-Update System
Robust, secure, and user-friendly automatic updates
"""

import os
import sys
import json
import shutil
import tempfile
import zipfile
import hashlib
import subprocess
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import requests
from pathlib import Path

# Optional GUI imports
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    print("GUI components not available - UpdateManager will run in headless mode")

class UpdateManager:
    """Professional update management system"""
    
    def __init__(self, app_path: str = None):
        self.app_path = app_path or os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.app_path, 'config', 'update.json')
        self.backup_dir = os.path.join(self.app_path, 'backup')
        self.temp_dir = None
        
        # Update configuration
        self.config = self.load_config()
        
        # GitHub configuration
        self.github_owner = "kyywes"
        self.github_repo = "NetPulse"
        self.github_api_url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo}/releases/latest"
        self.github_download_url = f"https://github.com/{self.github_owner}/{self.github_repo}/archive/refs/heads/main.zip"
        
        # Current version
        self.current_version = self.get_current_version()
        
        # Update UI
        self.update_window = None
        self.progress_var = None
        self.status_var = None
        self.log_text = None
        
    def load_config(self) -> Dict:
        """Load update configuration"""
        default_config = {
            'enabled': True,
            'check_on_startup': True,
            'auto_install': True,
            'backup_before_update': True,
            'max_backups': 3,
            'update_channel': 'stable',
            'last_check': None,
            'last_update': None,
            'check_interval_hours': 24,
            'download_timeout': 300,
            'github_token': None  # For private repos or higher rate limits
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    default_config.update(saved_config)
            except (json.JSONDecodeError, IOError):
                pass
        
        return default_config
    
    def save_config(self):
        """Save update configuration"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            pass
    
    def get_current_version(self) -> str:
        """Get current application version"""
        version_file = os.path.join(self.app_path, 'version.txt')
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    return f.read().strip()
            except IOError:
                pass
        return "2.0.0"  # Default version
    
    def should_check_for_updates(self) -> bool:
        """Check if we should check for updates"""
        if not self.config.get('enabled', True):
            return False
        
        if not self.config.get('check_on_startup', True):
            return False
        
        last_check = self.config.get('last_check')
        if not last_check:
            return True
        
        try:
            last_check_time = datetime.fromisoformat(last_check)
            check_interval = timedelta(hours=self.config.get('check_interval_hours', 24))
            return datetime.now() - last_check_time > check_interval
        except ValueError:
            return True
    
    def check_for_updates(self, show_ui: bool = True) -> Optional[Dict]:
        """Check for available updates"""
        try:
            self.log_message("Checking for updates...")
            
            # Update last check time
            self.config['last_check'] = datetime.now().isoformat()
            self.save_config()
            
            # Check GitHub releases
            headers = {}
            if self.config.get('github_token'):
                headers['Authorization'] = f"token {self.config['github_token']}"
            
            response = requests.get(self.github_api_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            release_info = response.json()
            
            # Extract version information
            latest_version = release_info.get('tag_name', '').lstrip('v')
            if not latest_version:
                latest_version = release_info.get('name', '').lstrip('v')
            
            if not latest_version:
                self.log_message("Could not determine latest version")
                return None
            
            # Compare versions
            if self.is_newer_version(latest_version, self.current_version):
                update_info = {
                    'version': latest_version,
                    'name': release_info.get('name', f'NetPulse {latest_version}'),
                    'body': release_info.get('body', 'No release notes available'),
                    'published_at': release_info.get('published_at'),
                    'download_url': self.github_download_url,
                    'assets': release_info.get('assets', [])
                }
                
                self.log_message(f"Update available: {latest_version}")
                
                if show_ui and HAS_GUI:
                    self.show_update_dialog(update_info)
                
                return update_info
            else:
                self.log_message("No updates available")
                if show_ui and HAS_GUI:
                    messagebox.showinfo("No Updates", "NetPulse is up to date!")
                return None
                
        except requests.RequestException as e:
            self.log_message(f"Update check failed: {str(e)}")
            if show_ui and HAS_GUI:
                messagebox.showerror("Update Check Failed", 
                                   f"Could not check for updates:\n{str(e)}")
            return None
        except Exception as e:
            self.log_message(f"Unexpected error during update check: {str(e)}")
            return None
    
    def is_newer_version(self, remote: str, current: str) -> bool:
        """Compare version strings"""
        try:
            remote_parts = tuple(int(x) for x in remote.split('.'))
            current_parts = tuple(int(x) for x in current.split('.'))
            
            # Pad shorter version with zeros
            max_len = max(len(remote_parts), len(current_parts))
            remote_parts += (0,) * (max_len - len(remote_parts))
            current_parts += (0,) * (max_len - len(current_parts))
            
            return remote_parts > current_parts
        except ValueError:
            # Fallback to string comparison
            return remote > current
    
    def show_update_dialog(self, update_info: Dict):
        """Show update available dialog"""
        if not HAS_GUI:
            self.log_message("GUI not available - showing update info in console")
            print(f"Update available: {update_info['version']}")
            print(f"Description: {update_info.get('description', 'No description')}")
            return
            
        dialog = tk.Toplevel()
        dialog.title("Update Available")
        dialog.geometry("500x400")
        dialog.configure(bg='#0D1117')
        dialog.grab_set()
        
        # Center dialog
        dialog.transient()
        dialog.geometry("+%d+%d" % (dialog.winfo_screenwidth()//2 - 250, 
                                   dialog.winfo_screenheight()//2 - 200))
        
        # Header
        header_frame = ttk.Frame(dialog)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header_frame, text="Update Available", 
                 font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        
        ttk.Label(header_frame, 
                 text=f"NetPulse {update_info['version']} is available",
                 font=('Segoe UI', 10)).pack(anchor='w', pady=(5, 0))
        
        # Release notes
        notes_frame = ttk.Frame(dialog)
        notes_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        ttk.Label(notes_frame, text="Release Notes:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        notes_text = tk.Text(notes_frame, wrap='word', height=10, width=50,
                            bg='#161B22', fg='#F9FAFB', font=('Segoe UI', 9),
                            relief='flat', padx=10, pady=10)
        notes_text.pack(fill='both', expand=True)
        notes_text.insert('1.0', update_info['body'])
        notes_text.config(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        def install_update():
            dialog.destroy()
            self.download_and_install_update(update_info)
        
        def remind_later():
            dialog.destroy()
        
        def skip_version():
            self.config['skip_version'] = update_info['version']
            self.save_config()
            dialog.destroy()
        
        ttk.Button(button_frame, text="Install Update", 
                  command=install_update).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Remind Later", 
                  command=remind_later).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Skip This Version", 
                  command=skip_version).pack(side='left')
    
    def download_and_install_update(self, update_info: Dict):
        """Download and install update"""
        self.show_update_progress()
        
        # Start update in separate thread
        update_thread = threading.Thread(
            target=self.perform_update, 
            args=(update_info,), 
            daemon=True
        )
        update_thread.start()
    
    def show_update_progress(self):
        """Show update progress window"""
        if not HAS_GUI:
            self.log_message("GUI not available - showing update progress in console")
            return
            
        self.update_window = tk.Toplevel()
        self.update_window.title("Updating NetPulse")
        self.update_window.geometry("500x300")
        self.update_window.configure(bg='#0D1117')
        self.update_window.grab_set()
        
        # Center window
        self.update_window.transient()
        self.update_window.geometry("+%d+%d" % (self.update_window.winfo_screenwidth()//2 - 250, 
                                               self.update_window.winfo_screenheight()//2 - 150))
        
        # Prevent closing during update
        self.update_window.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Header
        header_frame = ttk.Frame(self.update_window)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header_frame, text="Updating NetPulse", 
                 font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(header_frame, variable=self.progress_var, 
                                      maximum=100)
        progress_bar.pack(fill='x', pady=(10, 0))
        
        # Status
        self.status_var = tk.StringVar(value="Preparing update...")
        ttk.Label(header_frame, textvariable=self.status_var, 
                 font=('Segoe UI', 10)).pack(anchor='w', pady=(5, 0))
        
        # Log
        log_frame = ttk.Frame(self.update_window)
        log_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        ttk.Label(log_frame, text="Update Log:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.log_text = tk.Text(log_frame, wrap='word', height=8, width=50,
                               bg='#161B22', fg='#F9FAFB', font=('Consolas', 8),
                               relief='flat', padx=10, pady=10)
        self.log_text.pack(fill='both', expand=True)
    
    def perform_update(self, update_info: Dict):
        """Perform the actual update"""
        try:
            self.log_message("Starting update process...")
            self.update_progress(0, "Creating backup...")
            
            # Create backup
            if self.config.get('backup_before_update', True):
                self.create_backup()
            
            self.update_progress(20, "Downloading update...")
            
            # Download update
            update_file = self.download_update(update_info['download_url'])
            
            self.update_progress(50, "Extracting update...")
            
            # Extract and prepare update
            extracted_dir = self.extract_update(update_file)
            
            self.update_progress(70, "Installing update...")
            
            # Apply update
            self.apply_update(extracted_dir)
            
            self.update_progress(90, "Finalizing update...")
            
            # Update configuration
            self.config['last_update'] = datetime.now().isoformat()
            self.save_config()
            
            # Cleanup
            self.cleanup_temp_files()
            
            self.update_progress(100, "Update complete!")
            self.log_message("Update completed successfully!")
            
            # Show completion dialog
            self.show_update_complete()
            
        except Exception as e:
            self.log_message(f"Update failed: {str(e)}")
            self.handle_update_failure(str(e))
    
    def create_backup(self):
        """Create backup of current installation"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{self.current_version}_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            self.log_message(f"Creating backup: {backup_name}")
            
            # Copy current installation
            shutil.copytree(self.app_path, backup_path, 
                          ignore=shutil.ignore_patterns('backup', 'temp', '*.pyc', '__pycache__'))
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            self.log_message("Backup created successfully")
            
        except Exception as e:
            self.log_message(f"Backup creation failed: {str(e)}")
            raise
    
    def download_update(self, download_url: str) -> str:
        """Download update file"""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="netpulse_update_")
            update_file = os.path.join(self.temp_dir, "update.zip")
            
            self.log_message(f"Downloading from: {download_url}")
            
            headers = {}
            if self.config.get('github_token'):
                headers['Authorization'] = f"token {self.config['github_token']}"
            
            response = requests.get(download_url, headers=headers, stream=True,
                                  timeout=self.config.get('download_timeout', 300))
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 30 + 20  # 20-50%
                            self.update_progress(progress, f"Downloading... {downloaded // 1024}KB")
            
            self.log_message(f"Downloaded {downloaded} bytes")
            return update_file
            
        except Exception as e:
            self.log_message(f"Download failed: {str(e)}")
            raise
    
    def extract_update(self, update_file: str) -> str:
        """Extract update archive"""
        try:
            extract_dir = os.path.join(self.temp_dir, "extracted")
            
            self.log_message("Extracting update archive...")
            
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the actual content directory
            contents = os.listdir(extract_dir)
            if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
                content_dir = os.path.join(extract_dir, contents[0])
            else:
                content_dir = extract_dir
            
            self.log_message("Update extracted successfully")
            return content_dir
            
        except Exception as e:
            self.log_message(f"Extraction failed: {str(e)}")
            raise
    
    def apply_update(self, source_dir: str):
        """Apply the update to the installation"""
        try:
            self.log_message("Applying update...")
            
            # Files to preserve
            preserve_files = {'config/', 'data/', 'backup/'}
            
            # Copy new files
            for root, dirs, files in os.walk(source_dir):
                # Skip preserve directories
                dirs[:] = [d for d in dirs if not any(d.startswith(p.rstrip('/')) for p in preserve_files)]
                
                rel_path = os.path.relpath(root, source_dir)
                if rel_path == '.':
                    dest_root = self.app_path
                else:
                    dest_root = os.path.join(self.app_path, rel_path)
                
                # Create destination directory
                os.makedirs(dest_root, exist_ok=True)
                
                # Copy files
                for file in files:
                    if not file.endswith(('.pyc', '.pyo')):
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_root, file)
                        shutil.copy2(src_file, dest_file)
            
            # Update version file
            version_file = os.path.join(self.app_path, 'version.txt')
            with open(version_file, 'w') as f:
                f.write(self.get_version_from_source(source_dir))
            
            self.log_message("Update applied successfully")
            
        except Exception as e:
            self.log_message(f"Update application failed: {str(e)}")
            raise
    
    def get_version_from_source(self, source_dir: str) -> str:
        """Get version from source directory"""
        version_file = os.path.join(source_dir, 'version.txt')
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    return f.read().strip()
            except IOError:
                pass
        return "2.0.0"
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.log_message("Temporary files cleaned up")
            except Exception as e:
                self.log_message(f"Could not cleanup temp files: {str(e)}")
    
    def cleanup_old_backups(self):
        """Clean up old backups"""
        try:
            if not os.path.exists(self.backup_dir):
                return
            
            backups = [d for d in os.listdir(self.backup_dir) 
                      if os.path.isdir(os.path.join(self.backup_dir, d)) and d.startswith('backup_')]
            
            max_backups = self.config.get('max_backups', 3)
            
            if len(backups) > max_backups:
                # Sort by modification time (oldest first)
                backups.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)))
                
                # Remove oldest backups
                for backup in backups[:-max_backups]:
                    backup_path = os.path.join(self.backup_dir, backup)
                    shutil.rmtree(backup_path)
                    self.log_message(f"Removed old backup: {backup}")
                    
        except Exception as e:
            self.log_message(f"Could not cleanup old backups: {str(e)}")
    
    def show_update_complete(self):
        """Show update completion dialog"""
        if not HAS_GUI:
            self.log_message("Update complete - restart required")
            print("Update complete! Please restart NetPulse.")
            return
            
        self.update_window.after(0, self._show_completion_dialog)
    
    def _show_completion_dialog(self):
        """Show completion dialog (thread-safe)"""
        if not HAS_GUI:
            return
            
        if self.update_window:
            self.update_window.destroy()
        
        result = messagebox.askyesno(
            "Update Complete",
            "NetPulse has been updated successfully!\n\n"
            "The application needs to be restarted to use the new version.\n\n"
            "Restart NetPulse now?"
        )
        
        if result:
            self.restart_application()
    
    def handle_update_failure(self, error: str):
        """Handle update failure"""
        if not HAS_GUI:
            self.log_message(f"Update failed: {error}")
            print(f"Update failed: {error}")
            return
            
        self.update_window.after(0, self._show_failure_dialog, error)
    
    def _show_failure_dialog(self, error: str):
        """Show failure dialog (thread-safe)"""
        if not HAS_GUI:
            return
            
        if self.update_window:
            self.update_window.destroy()
        
        result = messagebox.askyesnocancel(
            "Update Failed",
            f"The update failed with error:\n{error}\n\n"
            "Would you like to restore from backup?"
        )
        
        if result:
            self.restore_from_backup()
    
    def restore_from_backup(self):
        """Restore from the latest backup"""
        try:
            if not os.path.exists(self.backup_dir):
                messagebox.showerror("Error", "No backups available")
                return
            
            backups = [d for d in os.listdir(self.backup_dir) 
                      if os.path.isdir(os.path.join(self.backup_dir, d)) and d.startswith('backup_')]
            
            if not backups:
                messagebox.showerror("Error", "No backups available")
                return
            
            # Get latest backup
            latest_backup = max(backups, key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)))
            backup_path = os.path.join(self.backup_dir, latest_backup)
            
            # Restore backup
            for item in os.listdir(backup_path):
                src = os.path.join(backup_path, item)
                dst = os.path.join(self.app_path, item)
                
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            messagebox.showinfo("Success", "Backup restored successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not restore backup: {str(e)}")
    
    def restart_application(self):
        """Restart the application"""
        try:
            main_script = os.path.join(self.app_path, 'main.py')
            subprocess.Popen([sys.executable, main_script], cwd=self.app_path)
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("Error", f"Could not restart application: {str(e)}")
    
    def log_message(self, message: str):
        """Log message to console and UI"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        if self.log_text:
            self.log_text.after(0, self._append_log, log_entry + '\n')
    
    def _append_log(self, message: str):
        """Append to log (thread-safe)"""
        self.log_text.insert('end', message)
        self.log_text.see('end')
    
    def update_progress(self, value: float, status: str):
        """Update progress bar and status"""
        if self.progress_var and self.status_var:
            self.progress_var.set(value)
            self.status_var.set(status)

def main():
    """Main function for standalone update check"""
    updater = UpdateManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "check":
            updater.check_for_updates(show_ui=True)
        elif command == "silent":
            updater.check_for_updates(show_ui=False)
        else:
            print("Usage: python updater_enhanced.py [check|silent]")
    else:
        updater.check_for_updates(show_ui=True)

if __name__ == "__main__":
    main()