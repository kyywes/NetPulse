import os
import pyodbc
import requests
import paramiko
import time
import json
from configparser import ConfigParser

class NetPulseAutomate:
    def __init__(self, db_config_file="inventory/db_config.ini"):
        if not os.path.isfile(db_config_file):
            raise FileNotFoundError(f"Config DB non trovato: {db_config_file}")
        cfg = ConfigParser()
        cfg.read(db_config_file)
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

    def _get_devices(self, marker: str) -> list[dict]:
        """
        Legge dalla vista v_ListaPL tutti i campi IP_* per PL = marker.
        """
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

    def connect_devices(self, marker: str) -> dict:
        """HTTP GET su ogni IP_*, restituisce UP/DOWN."""
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

    def show_pai_version(self, marker: str) -> dict:
        """
        SSH su ogni IP_* → ./PAI-PL_USR v
        """
        try:
            devs = self._get_devices(marker)
        except Exception as e:
            return {"error": str(e)}

        results = {}
        for dev in devs:
            ip = dev["host"]
            role = dev["role"]
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, timeout=10)
                stdin, stdout, stderr = ssh.exec_command("./PAI-PL_USR v")
                out = stdout.read().decode().strip() or stderr.read().decode().strip()
                ssh.close()
                results[role] = out or "<no output>"
            except Exception as e:
                results[role] = f"SSH Error: {e}"
        return {"pai-pl version": results}

    def _ssh_command(self, host: str, command: str, timeout: int = 30) -> str:
        """
        Execute SSH command on remote host
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, timeout=timeout)
            
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            ssh.close()
            
            if error:
                return f"Command output: {output}\nError: {error}"
            return output
            
        except Exception as e:
            return f"SSH Error: {str(e)}"

    def data(self, marker: str, new_date: str = None) -> dict:
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

    def mcu(self, marker: str, action: str = "status", config_file: str = "CONFIGURATION") -> dict:
        """
        Enhanced MCU management command
        Actions: status, enable, disable, config, restart
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
