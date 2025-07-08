import os
import sys
import time
import subprocess
import platform

import keyring
import pyodbc
import paramiko
from netpulse_core.cli import NetPulse

class NetPulseAutomate:
    def __init__(self):
        # ↓ tutti i parametri SQL vengono letti da Keyring ↓
        server   = keyring.get_password("netpulse-sql", "server")
        database = keyring.get_password("netpulse-sql", "database")
        driver   = keyring.get_password("netpulse-sql", "driver")
        user     = keyring.get_password("netpulse-sql", "username")
        pwd      = keyring.get_password("netpulse-sql", "password")
        if not all((server, database, driver, user, pwd)):
            missing = [k for k,v in [
                ("server", server),
                ("database", database),
                ("driver", driver),
                ("username", user),
                ("password", pwd)
            ] if not v]
            raise RuntimeError(f"Parametri SQL mancanti in Keyring: {missing}")

        conn_str = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={pwd};"
            "Encrypt=no;TrustServerCertificate=yes;"
        )
        self._db = pyodbc.connect(conn_str, timeout=5)

        # ↓ tutte le credenziali SSH da Keyring ↓
        self._ssh_user = keyring.get_password("netpulse-ssh", "username")
        self._ssh_pass = keyring.get_password("netpulse-ssh", "password")
        if not all((self._ssh_user, self._ssh_pass)):
            raise RuntimeError("Credenziali SSH mancanti in Keyring")

        # parametri SSH aggiuntivi (possono venire da env o restare default)
        self._ssh_port    = int(os.getenv("NETPULSE_SSH_PORT",    "22"))
        self._ssh_timeout = int(os.getenv("NETPULSE_SSH_TIMEOUT", "10"))
        self._ssh_retries = int(os.getenv("NETPULSE_SSH_RETRIES","3"))

        # helper ping
        self._ping = NetPulse()

    def _get_devices(self, marker: str) -> list[dict]:
        cur = self._db.cursor()
        cur.execute("SELECT * FROM dbo.v_ListaPL WHERE PL = ?", marker)
        row = cur.fetchone()
        if not row:
            return []
        cols = [c[0] for c in cur.description]
        devs = []
        for idx, col in enumerate(cols):
            if col.upper().startswith("IP_"):
                ip = row[idx]
                if ip and str(ip).strip():
                    role = col[3:].replace("_"," ").title()
                    devs.append({"role": role, "host": str(ip).strip()})
        return devs

    def connect_devices(self, marker: str) -> dict:
        """Ping parallelo di tutti i device del PL."""
        try:
            devs = self._get_devices(marker)
        except Exception as e:
            return {"error": str(e)}

        results = {}
        for d in devs:
            ip = d["host"]
            if platform.system()=="Windows":
                cmd = ["ping","-n","1","-w","1000",ip]
            else:
                cmd = ["ping","-c","1","-W","1",ip]
            code = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            results[f"{d['role']} ({ip})"] = "UP" if code==0 else "DOWN"
        return {"Connect Devices": results}

    def _ssh_command(self, ip: str, cmd: str) -> str:
        last_exc = None
        for _ in range(self._ssh_retries):
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    hostname=ip,
                    port=self._ssh_port,
                    username=self._ssh_user,
                    password=self._ssh_pass,
                    timeout=self._ssh_timeout,
                    allow_agent=False,
                    look_for_keys=False
                )
                stdin, stdout, stderr = client.exec_command(cmd)
                out = stdout.read().decode(errors="ignore").strip()
                err = stderr.read().decode(errors="ignore").strip()
                client.close()
                return "\n".join(filter(None,[out,err])) or "<no output>"
            except Exception as e:
                last_exc = e
                time.sleep(1)
        return f"SSH Error: {last_exc.__class__.__name__}"

    def show_pai(self, marker: str, mode: str) -> dict:
        """Version (mode='v') o Logs (mode='s') via SSH su CPU B."""
        try:
            cpu = [d for d in self._get_devices(marker) if d["role"].lower()=="cpu b"]
        except Exception as e:
            return {"error": str(e)}
        if not cpu:
            return {"error": f"Nessuna CPU B per PL {marker}"}

        flag = "v" if mode=="v" else "s"
        cmd  = f"cd .. && ls && ./PaiPL_USR {flag}"
        key  = "PAI-PL Version" if flag=="v" else "PAI-PL Logs"
        out  = {}
        for c in cpu:
            out[c["role"]] = self._ssh_command(c["host"], cmd)
        return {key: out}

    def data(self, marker: str, new_date: str=None) -> dict:
        """
        Se new_date=None: mostra directory e date corrente.
        Altrimenti: esegue anche date -s new_date via SSH.
        """
        try:
            cpu = [d for d in self._get_devices(marker) if d["role"].lower()=="cpu b"]
        except Exception as e:
            return {"error": str(e)}
        if not cpu:
            return {"error": f"Nessuna CPU B per PL {marker}"}

        res = {}
        for c in cpu:
            nav = self._ssh_command(c["host"], "cd .. && ls")
            cur = self._ssh_command(c["host"], "date")
            seto = ""
            if new_date:
                seto = self._ssh_command(c["host"], f'date -s "{new_date}"')
            res[c["role"]] = {
                "navigation":   nav,
                "current_date": cur,
                "set_date":     seto
            }
        return {"Data PAI-PL": res}

    def configure_mcu(self, marker: str, action: str) -> dict:
        """Abilita/disabilita MCU sulla CPU B via SSH."""
        try:
            cpu = [d for d in self._get_devices(marker) if d["role"].lower()=="cpu b"]
        except Exception as e:
            return {"error": str(e)}
        if not cpu:
            return {"error": f"Nessuna CPU B per PL {marker}"}

        out = {}
        for c in cpu:
            out[c["role"]] = self._ssh_command(c["host"], f"mcu {action}")
        return {"Configura MCU": out}
