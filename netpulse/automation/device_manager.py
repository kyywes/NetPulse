import os
import pyodbc
import requests
import paramiko
import time
import json
from configparser import ConfigParser
from typing import Dict, List, Optional
import threading

# Import credential manager
try:
    from ..core.credential_manager import CredentialManager
except ImportError:
    from netpulse.core.credential_manager import CredentialManager

class DeviceManager:
    """Enhanced device management with secure credential storage"""
    
    def __init__(self, db_config_file: str = None):
        self.db_config_file = db_config_file
        self.conn_str = None
        self.ssh_credentials = None
        self.credential_manager = CredentialManager()
        
        # Initialize database connection
        self._init_database_connection()
        
        # Load SSH credentials
        self._load_ssh_credentials()
    
    def _init_database_connection(self):
        """Initialize database connection with secure credentials"""
        try:
            # First try to get credentials from keyring
            sql_creds = self.credential_manager.get_sql_credentials()
            
            if sql_creds:
                self.conn_str = (
                    f"DRIVER={sql_creds['driver']};"
                    f"SERVER={sql_creds['server']};"
                    f"DATABASE={sql_creds['database']};"
                    f"UID={sql_creds['username']};"
                    f"PWD={sql_creds['password']};"
                    f"Encrypt={sql_creds['encrypt']};"
                    f"TrustServerCertificate={sql_creds['TrustServerCertificate']}"
                )
                print("✓ Database credentials loaded from keyring")
                return
            
            # Fallback to config file if provided
            if self.db_config_file and os.path.isfile(self.db_config_file):
                cfg = ConfigParser()
                cfg.read(self.db_config_file)
                s = cfg["sqlserver"]
                
                self.conn_str = (
                    f"DRIVER={s['driver']};"
                    f"SERVER={s['server']};"
                    f"DATABASE={s['database']};"
                    f"UID={s['username']};"
                    f"PWD={s['password']};"
                    f"Encrypt={s.get('encrypt','no')};"
                    f"TrustServerCertificate={s.get('TrustServerCertificate','yes')}"
                )
                
                # Store credentials in keyring for future use
                self.credential_manager.store_sql_credentials(
                    s['username'], s['password'], s['server'], s['database']
                )
                print("✓ Database credentials loaded from config file and stored in keyring")
                return
            
            # If no credentials available, set up interactively
            print("⚠️  No database credentials found")
            print("Use: python -m netpulse.core.credential_manager --setup")
            
        except Exception as e:
            print(f"✗ Database initialization failed: {e}")
            self.conn_str = None
    
    def _load_ssh_credentials(self):
        """Load SSH credentials from keyring"""
        try:
            self.ssh_credentials = self.credential_manager.get_ssh_credentials()
            if self.ssh_credentials:
                print("✓ SSH credentials loaded from keyring")
            else:
                print("⚠️  No SSH credentials found")
                print("Use: python -m netpulse.core.credential_manager --setup")
        except Exception as e:
            print(f"✗ SSH credential loading failed: {e}")
            self.ssh_credentials = None
    
    def _get_devices(self, marker: str) -> List[Dict]:
        """Get devices from database for a given marker"""
        if not self.conn_str:
            raise Exception("Database connection not configured. Run credential setup.")
        
        try:
            con = pyodbc.connect(self.conn_str)
            cur = con.cursor()
            cur.execute(
                """
                SELECT *
                FROM dbo.v_ListaPL
                WHERE PL = ?
                """,
                marker
            )
            row = cur.fetchone()
            con.close()
            
            if not row:
                return []

            cols = [col[0] for col in cur.description]
            devs = []
            for idx, col in enumerate(cols):
                if col.upper().startswith("IP_"):
                    ip = row[idx]
                    if ip and str(ip).strip():
                        role = col[3:].replace("_", " ").title()
                        devs.append({"role": role, "host": str(ip).strip()})
            return devs
            
        except Exception as e:
            raise Exception(f"Database query failed: {e}")
    
    def _ssh_command(self, host: str, command: str, timeout: int = 30) -> str:
        """Execute SSH command on remote host with stored credentials"""
        if not self.ssh_credentials:
            return "SSH Error: No SSH credentials configured"
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Use stored credentials
            if self.ssh_credentials.get('key_file'):
                # Use key file authentication
                ssh.connect(
                    host, 
                    username=self.ssh_credentials['username'],
                    key_filename=self.ssh_credentials['key_file'],
                    timeout=timeout
                )
            else:
                # Use password authentication
                ssh.connect(
                    host,
                    username=self.ssh_credentials['username'], 
                    password=self.ssh_credentials['password'],
                    timeout=timeout
                )
            
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            ssh.close()
            
            if error:
                return f"Command output: {output}\nError: {error}"
            return output
            
        except Exception as e:
            return f"SSH Error: {str(e)}"

    def connect_devices(self, marker: str) -> Dict:
        """HTTP GET on each device IP to check connectivity"""
        try:
            devs = self._get_devices(marker)
        except Exception as e:
            return {"error": str(e)}

        results = {}
        for dev in devs:
            url = f"http://{dev['host']}"
            try:
                r = requests.get(url, timeout=5)
                results[dev["role"]] = f"UP ({r.status_code})"
            except Exception as e:
                results[dev["role"]] = f"DOWN ({type(e).__name__})"
        return {"connect devices": results}

    def show_pai_version(self, marker: str) -> Dict:
        """SSH to each device to get PAI-PL version"""
        try:
            devs = self._get_devices(marker)
        except Exception as e:
            return {"error": str(e)}

        results = {}
        for dev in devs:
            ip = dev["host"]
            role = dev["role"]
            try:
                output = self._ssh_command(ip, "./PAI-PL_USR v")
                results[role] = output or "<no output>"
            except Exception as e:
                results[role] = f"SSH Error: {e}"
        return {"pai-pl version": results}

    def data(self, marker: str, new_date: str = None) -> Dict:
        """
        Enhanced data command - manages system date and navigation
        If new_date=None just runs 'cd .. && ls' + 'date',
        otherwise it adds 'date -s new_date'.
        """
        try:
            devs = self._get_devices(marker)
        except Exception as e:
            return {"error": str(e)}

        cpu = [d for d in devs if d["role"].lower() == "cpu b"]
        if not cpu:
            return {"error": f"No CPU B for PL {marker}"}

        results = {}
        for d in cpu:
            h = d["host"]
            
            # Execute commands
            nav = self._ssh_command(h, "cd .. && ls")
            cur = self._ssh_command(h, "date")
            seto = ""
            
            if new_date:
                # Validate date format before setting
                try:
                    # Basic date validation - you can enhance this
                    if len(new_date.split()) >= 2:  # Basic check for date format
                        seto = self._ssh_command(h, f'date -s "{new_date}"')
                    else:
                        seto = "Error: Invalid date format. Use format like 'YYYY-MM-DD HH:MM:SS'"
                except:
                    seto = "Error: Failed to parse date format"
            
            results[d["role"]] = {
                "navigation": nav,
                "current_date": cur,
                "set_date": seto
            }
            
        return {"data_pai_pl": results}

    def mcu(self, marker: str, action: str = "status", config_file: str = "CONFIGURAZIONE") -> Dict:
        """
        Enhanced MCU management command - focused on CONFIGURAZIONE status and mcu= parameter
        Actions: status, change_mcu_value
        """
        try:
            devs = self._get_devices(marker)
        except Exception as e:
            return {"error": str(e)}

        # Look for MCU devices (CPU B or specific MCU devices)
        mcu_devices = [d for d in devs if any(keyword in d["role"].lower() 
                                            for keyword in ["cpu b", "mcu", "controller"])]
        
        if not mcu_devices:
            return {"error": f"No MCU/Controller devices found for PL {marker}"}

        results = {}
        
        for device in mcu_devices:
            host = device["host"]
            role = device["role"]
            
            try:
                if action.lower() == "status":
                    # Get MCU status
                    status_cmd = f"cat {config_file} | grep -i mcu"
                    status_output = self._ssh_command(host, status_cmd)
                    
                    # Get additional system info
                    system_info = self._ssh_command(host, "ps aux | grep -i mcu")
                    uptime = self._ssh_command(host, "uptime")
                    
                    results[role] = {
                        "action": "status",
                        "config_status": status_output,
                        "system_processes": system_info,
                        "uptime": uptime,
                        "timestamp": self._ssh_command(host, "date")
                    }
                
                elif action.lower() == "enable":
                    # Enable MCU
                    backup_cmd = f"cp {config_file} {config_file}.backup.$(date +%Y%m%d_%H%M%S)"
                    backup_result = self._ssh_command(host, backup_cmd)
                    
                    # Enable MCU in configuration
                    enable_cmd = f"sed -i 's/MCU_ENABLE=.*$/MCU_ENABLE=true/g' {config_file}"
                    enable_result = self._ssh_command(host, enable_cmd)
                    
                    # Verify change
                    verify_cmd = f"grep MCU_ENABLE {config_file}"
                    verify_result = self._ssh_command(host, verify_cmd)
                    
                    results[role] = {
                        "action": "enable",
                        "backup": backup_result,
                        "enable_result": enable_result,
                        "verification": verify_result,
                        "timestamp": self._ssh_command(host, "date")
                    }
                
                elif action.lower() == "disable":
                    # Disable MCU
                    backup_cmd = f"cp {config_file} {config_file}.backup.$(date +%Y%m%d_%H%M%S)"
                    backup_result = self._ssh_command(host, backup_cmd)
                    
                    # Disable MCU in configuration
                    disable_cmd = f"sed -i 's/MCU_ENABLE=.*$/MCU_ENABLE=false/g' {config_file}"
                    disable_result = self._ssh_command(host, disable_cmd)
                    
                    # Verify change
                    verify_cmd = f"grep MCU_ENABLE {config_file}"
                    verify_result = self._ssh_command(host, verify_cmd)
                    
                    results[role] = {
                        "action": "disable",
                        "backup": backup_result,
                        "disable_result": disable_result,
                        "verification": verify_result,
                        "timestamp": self._ssh_command(host, "date")
                    }
                
                elif action.lower() == "config":
                    # View/edit configuration
                    config_content = self._ssh_command(host, f"cat {config_file}")
                    mcu_config = self._ssh_command(host, f"grep -A 5 -B 5 -i mcu {config_file}")
                    
                    results[role] = {
                        "action": "config",
                        "full_config": config_content,
                        "mcu_section": mcu_config,
                        "file_info": self._ssh_command(host, f"ls -la {config_file}"),
                        "timestamp": self._ssh_command(host, "date")
                    }
                
                elif action.lower() == "restart":
                    # Restart MCU service
                    status_before = self._ssh_command(host, "ps aux | grep -i mcu")
                    
                    # Try different restart methods
                    restart_commands = [
                        "systemctl restart mcu",
                        "service mcu restart", 
                        "/etc/init.d/mcu restart",
                        "killall -HUP mcu"
                    ]
                    
                    restart_results = []
                    for cmd in restart_commands:
                        result = self._ssh_command(host, cmd)
                        restart_results.append(f"{cmd}: {result}")
                        if "error" not in result.lower():
                            break
                    
                    # Wait and check status
                    time.sleep(2)
                    status_after = self._ssh_command(host, "ps aux | grep -i mcu")
                    
                    results[role] = {
                        "action": "restart",
                        "status_before": status_before,
                        "restart_attempts": restart_results,
                        "status_after": status_after,
                        "timestamp": self._ssh_command(host, "date")
                    }
                
                else:
                    results[role] = {
                        "error": f"Unknown action: {action}. Available: status, enable, disable, config, restart"
                    }
                    
            except Exception as e:
                results[role] = {
                    "error": f"MCU operation failed: {str(e)}"
                }
        
        return {"mcu_management": results}

    def change_mcu_value(self, marker: str, new_mcu_value: str) -> dict:
        """Change the mcu= value in CONFIGURAZIONE file"""
        try:
            devs = self._get_devices(marker)
        except Exception as e:
            return {"error": str(e)}

        # Look for MCU devices
        mcu_devices = [d for d in devs if any(keyword in d["role"].lower() 
                                            for keyword in ["cpu b", "mcu", "controller"])]
        
        if not mcu_devices:
            return {"error": f"No MCU/Controller devices found for PL {marker}"}

        results = {"marker": marker, "new_value": new_mcu_value, "devices": {}}
        
        for device in mcu_devices:
            host = device["host"]
            role = device["role"]
            
            try:
                # Create backup first
                backup_cmd = f"cp CONFIGURAZIONE CONFIGURAZIONE.backup.$(date +%Y%m%d_%H%M%S)"
                backup_result = self._ssh_command(host, backup_cmd)
                
                # Change mcu= value
                change_cmd = f"sed -i 's/mcu=.*$/mcu={new_mcu_value}/g' CONFIGURAZIONE"
                change_result = self._ssh_command(host, change_cmd)
                
                # Verify change
                verify_cmd = "grep 'mcu=' CONFIGURAZIONE"
                verify_result = self._ssh_command(host, verify_cmd)
                
                results["devices"][role] = {
                    "action": "change_mcu_value",
                    "host": host,
                    "backup_result": backup_result,
                    "change_result": change_result,
                    "verification": verify_result,
                    "timestamp": self._ssh_command(host, "date")
                }
                
            except Exception as e:
                results["devices"][role] = {
                    "action": "change_mcu_value",
                    "error": str(e)
                }
        
        return results
    def _get_kilometric_info(self, marker: str) -> dict:
        """Get kilometric information from database"""
        try:
            query = """
            SELECT TOP 1 
                Codice_Stazione,
                Km_Inizio,
                Km_Fine,
                Descrizione
            FROM Stazioni 
            WHERE Codice_Stazione LIKE ?
            """
            
            if self.conn_str:
                with pyodbc.connect(self.conn_str) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, (f"%{marker}%",))
                    row = cursor.fetchone()
                    
                    if row:
                        return {
                            "code": row[0],
                            "km_start": row[1],
                            "km_end": row[2],
                            "description": row[3],
                            "kilometric_parameter": f"{row[1]}+{row[2]}" if row[1] and row[2] else "Unknown"
                        }
            
            return {"error": "No kilometric information found"}
            
        except Exception as e:
            return {"error": f"Database query failed: {str(e)}"}

    def advanced_mcu_config(self, marker: str, config_updates: dict = None) -> dict:
        """
        Advanced MCU configuration management
        config_updates: dict of configuration key-value pairs to update
        """
        try:
            devs = self._get_devices(marker)
        except Exception as e:
            return {"error": str(e)}

        mcu_devices = [d for d in devs if any(keyword in d["role"].lower() 
                                            for keyword in ["cpu b", "mcu", "controller"])]
        
        if not mcu_devices:
            return {"error": f"No MCU/Controller devices found for PL {marker}"}

        results = {}
        
        for device in mcu_devices:
            host = device["host"]
            role = device["role"]
            
            try:
                # Create timestamped backup
                backup_cmd = f"cp CONFIGURATION CONFIGURATION.backup.$(date +%Y%m%d_%H%M%S)"
                backup_result = self._ssh_command(host, backup_cmd)
                
                # Read current configuration
                current_config = self._ssh_command(host, "cat CONFIGURATION")
                
                updates_applied = []
                
                if config_updates:
                    for key, value in config_updates.items():
                        # Update configuration
                        update_cmd = f"sed -i 's/^{key}=.*$/{key}={value}/g' CONFIGURATION"
                        update_result = self._ssh_command(host, update_cmd)
                        
                        # Verify update
                        verify_cmd = f"grep '^{key}=' CONFIGURATION"
                        verify_result = self._ssh_command(host, verify_cmd)
                        
                        updates_applied.append({
                            "key": key,
                            "value": value,
                            "update_result": update_result,
                            "verification": verify_result
                        })
                
                # Get updated configuration
                updated_config = self._ssh_command(host, "cat CONFIGURATION")
                
                # Get configuration diff
                diff_cmd = "diff CONFIGURATION.backup.$(ls -t CONFIGURATION.backup.* | head -1 | cut -d'.' -f3-) CONFIGURATION"
                diff_result = self._ssh_command(host, diff_cmd)
                
                results[role] = {
                    "backup_result": backup_result,
                    "current_config": current_config,
                    "updates_applied": updates_applied,
                    "updated_config": updated_config,
                    "configuration_diff": diff_result,
                    "timestamp": self._ssh_command(host, "date")
                }
                
            except Exception as e:
                results[role] = {
                    "error": f"Advanced MCU config failed: {str(e)}"
                }
        
        return {"advanced_mcu_config": results}

    def backup_config(self, marker: str, config_type: str = "running") -> dict:
        """
        Enhanced configuration backup with multiple options
        config_type: running, startup, full, mcu
        """
        try:
            devs = self._get_devices(marker)
        except Exception as e:
            return {"error": str(e)}

        results = {}
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        for device in devs:
            host = device["host"]
            role = device["role"]
            
            try:
                backup_results = {}
                
                if config_type == "running" or config_type == "full":
                    # Backup running configuration
                    running_cmd = "show running-config"
                    running_backup = self._ssh_command(host, running_cmd)
                    
                    # Save to file
                    save_cmd = f"echo '{running_backup}' > /tmp/running-config-{timestamp}.txt"
                    save_result = self._ssh_command(host, save_cmd)
                    
                    backup_results["running_config"] = {
                        "content": running_backup,
                        "saved_to": f"/tmp/running-config-{timestamp}.txt",
                        "save_result": save_result
                    }
                
                if config_type == "startup" or config_type == "full":
                    # Backup startup configuration
                    startup_cmd = "show startup-config"
                    startup_backup = self._ssh_command(host, startup_cmd)
                    
                    # Save to file
                    save_cmd = f"echo '{startup_backup}' > /tmp/startup-config-{timestamp}.txt"
                    save_result = self._ssh_command(host, save_cmd)
                    
                    backup_results["startup_config"] = {
                        "content": startup_backup,
                        "saved_to": f"/tmp/startup-config-{timestamp}.txt",
                        "save_result": save_result
                    }
                
                if config_type == "mcu" or config_type == "full":
                    # Backup MCU configuration
                    mcu_config = self._ssh_command(host, "cat CONFIGURATION")
                    
                    # Save MCU config
                    save_cmd = f"cp CONFIGURATION /tmp/CONFIGURATION-{timestamp}.backup"
                    save_result = self._ssh_command(host, save_cmd)
                    
                    backup_results["mcu_config"] = {
                        "content": mcu_config,
                        "saved_to": f"/tmp/CONFIGURATION-{timestamp}.backup", 
                        "save_result": save_result
                    }
                
                if config_type == "full":
                    # Additional system files
                    system_files = [
                        "/etc/network/interfaces",
                        "/etc/hosts",
                        "/etc/resolv.conf",
                        "/proc/version",
                        "/proc/meminfo"
                    ]
                    
                    system_backup = {}
                    for file_path in system_files:
                        content = self._ssh_command(host, f"cat {file_path}")
                        backup_file = f"/tmp/{file_path.replace('/', '_')}-{timestamp}.backup"
                        save_cmd = f"cp {file_path} {backup_file}"
                        save_result = self._ssh_command(host, save_cmd)
                        
                        system_backup[file_path] = {
                            "content": content,
                            "backup_file": backup_file,
                            "save_result": save_result
                        }
                    
                    backup_results["system_files"] = system_backup
                
                # Create archive of all backups
                archive_cmd = f"tar -czf /tmp/full-backup-{role}-{timestamp}.tar.gz /tmp/*{timestamp}*"
                archive_result = self._ssh_command(host, archive_cmd)
                
                backup_results["archive"] = {
                    "archive_file": f"/tmp/full-backup-{role}-{timestamp}.tar.gz",
                    "archive_result": archive_result,
                    "timestamp": timestamp
                }
                
                results[role] = backup_results
                
            except Exception as e:
                results[role] = {
                    "error": f"Backup failed: {str(e)}"
                }
        
        return {"backup_config": results}
    
    def setup_credentials(self):
        """Setup credentials interactively"""
        return self.credential_manager.setup_credentials_interactive()
    
    def test_connection(self) -> Dict[str, bool]:
        """Test database and SSH connections"""
        results = {
            "database": False,
            "ssh": False,
            "keyring": False
        }
        
        # Test keyring
        try:
            keyring_test = self.credential_manager.test_keyring_backend()
            results["keyring"] = keyring_test["keyring_available"]
        except:
            pass
        
        # Test database
        if self.conn_str:
            try:
                con = pyodbc.connect(self.conn_str)
                con.close()
                results["database"] = True
            except:
                pass
        
        # Test SSH (basic test)
        if self.ssh_credentials:
            results["ssh"] = True
        
        return results