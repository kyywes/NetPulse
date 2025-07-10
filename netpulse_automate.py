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

    def backup_config(self, marker: str) -> dict:
        """
        Stub placeholder: qui implementerei show running-config via SSH.
        """
        return {"backup config": "Non ancora implementato"}
