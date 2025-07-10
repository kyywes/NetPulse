import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading

class ConfigManager:
    """Centralized configuration and data management"""
    
    def __init__(self, app_dir: str = None):
        self.app_dir = app_dir or os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(self.app_dir, 'config')
        self.data_dir = os.path.join(self.app_dir, 'data')
        self.db_path = os.path.join(self.data_dir, 'netpulse.db')
        self.config_file = os.path.join(self.config_dir, 'settings.json')
        self.lock = threading.Lock()
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Load default settings
        self.settings = self._load_settings()
    
    def _init_database(self):
        """Initialize SQLite database for history and favorites"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    execution_time REAL,
                    success BOOLEAN,
                    output TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    command TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS device_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    host TEXT NOT NULL,
                    device_type TEXT,
                    credentials TEXT,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    command TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    schedule_type TEXT NOT NULL,
                    schedule_value TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    last_run DATETIME,
                    next_run DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load application settings"""
        default_settings = {
            'theme': 'dark',
            'auto_save_history': True,
            'max_history_entries': 1000,
            'default_ping_count': 4,
            'default_timeout': 30,
            'export_format': 'txt',
            'auto_update': True,
            'show_splash': True,
            'window_geometry': '1200x800',
            'recent_commands': [],
            'ui_settings': {
                'show_timestamps': True,
                'show_execution_time': True,
                'auto_scroll': True,
                'word_wrap': True
            },
            'network_settings': {
                'ping_interval': 1,
                'max_concurrent_scans': 50,
                'port_scan_timeout': 3,
                'bandwidth_test_duration': 10
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
            except (json.JSONDecodeError, IOError):
                pass
        
        return default_settings
    
    def save_settings(self):
        """Save current settings to file"""
        with self.lock:
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(self.settings, f, indent=2)
            except IOError:
                pass
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_setting(self, key: str, value: Any):
        """Set a setting value"""
        keys = key.split('.')
        setting_dict = self.settings
        
        for k in keys[:-1]:
            if k not in setting_dict:
                setting_dict[k] = {}
            setting_dict = setting_dict[k]
        
        setting_dict[keys[-1]] = value
        self.save_settings()
    
    def add_to_history(self, command: str, parameters: str, execution_time: float = 0, 
                      success: bool = True, output: str = "") -> int:
        """Add command to history"""
        if not self.get_setting('auto_save_history', True):
            return -1
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO command_history 
                (command, parameters, execution_time, success, output)
                VALUES (?, ?, ?, ?, ?)
            ''', (command, parameters, execution_time, success, output))
            
            # Cleanup old entries
            max_entries = self.get_setting('max_history_entries', 1000)
            conn.execute('''
                DELETE FROM command_history 
                WHERE id NOT IN (
                    SELECT id FROM command_history 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                )
            ''', (max_entries,))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get command history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM command_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_favorite(self, name: str, command: str, parameters: str, 
                    description: str = "") -> int:
        """Add command to favorites"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO favorites (name, command, parameters, description)
                VALUES (?, ?, ?, ?)
            ''', (name, command, parameters, description))
            conn.commit()
            return cursor.lastrowid
    
    def get_favorites(self) -> List[Dict]:
        """Get all favorites"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM favorites 
                ORDER BY name
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def remove_favorite(self, favorite_id: int):
        """Remove a favorite"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM favorites WHERE id = ?', (favorite_id,))
            conn.commit()
    
    def add_device_profile(self, name: str, host: str, device_type: str = "",
                          credentials: str = "", description: str = "") -> int:
        """Add device profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO device_profiles 
                (name, host, device_type, credentials, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, host, device_type, credentials, description))
            conn.commit()
            return cursor.lastrowid
    
    def get_device_profiles(self) -> List[Dict]:
        """Get all device profiles"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM device_profiles 
                ORDER BY name
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def clear_history(self):
        """Clear command history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM command_history')
            conn.commit()
    
    def get_recent_commands(self, limit: int = 10) -> List[str]:
        """Get recent unique commands"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT DISTINCT parameters FROM command_history 
                WHERE success = 1 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [row[0] for row in cursor.fetchall()]
    
    def export_data(self, file_path: str, data_type: str = 'history'):
        """Export data to file"""
        if data_type == 'history':
            data = self.get_history(limit=10000)
        elif data_type == 'favorites':
            data = self.get_favorites()
        elif data_type == 'profiles':
            data = self.get_device_profiles()
        else:
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except IOError:
            return False