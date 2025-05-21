import yaml
import os
import paramiko
from scrapli import Scrapli
from concurrent.futures import ThreadPoolExecutor


class NetPulseAutomate:
    def __init__(self, inventory_file: str):
        with open(inventory_file, "r") as f:
            data = yaml.safe_load(f)
        self.inventory = data

    def show_version(self) -> dict:
        results = {}
        def _run_net(device, p):
            with Scrapli(
                host=p["host"],
                auth_username=p["username"],
                auth_password=p["password"],
                platform=p["platform"],
                transport="paramiko",
                auth_strict_key=False
            ) as conn:
                r = conn.send_command("show version")
                return device, r.result

        net_devs = {d:p for d,p in self.inventory.items() if p.get("type") != "linux"}
        with ThreadPoolExecutor(max_workers=len(net_devs)) as ex:
            futures = [ex.submit(_run_net, d, p) for d,p in net_devs.items()]
            for f in futures:
                dev, out = f.result()
                results[dev] = out
        return {"show version": results}

    def backup_config(self) -> dict:
        results = {}
        os.makedirs("backups", exist_ok=True)
        def _run_backup(device, p):
            with Scrapli(
                host=p["host"],
                auth_username=p["username"],
                auth_password=p["password"],
                platform=p["platform"],
                transport="paramiko",
                auth_strict_key=False
            ) as conn:
                r = conn.send_command("show running-config")
                fname = f"backups/{device}_config.txt"
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(r.result)
                return device, "OK"

        net_devs = {d:p for d,p in self.inventory.items() if p.get("type") != "linux"}
        with ThreadPoolExecutor(max_workers=len(net_devs)) as ex:
            futures = [ex.submit(_run_backup, d, p) for d,p in net_devs.items()]
            for f in futures:
                dev, status = f.result()
                results[dev] = status
        return {"backup config": results}

    def show_pai_version(self) -> dict:
        results = {}
        linux_devs = {d:p for d,p in self.inventory.items() if p.get("type") == "linux"}
        for device, p in linux_devs.items():
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=p["host"],
                            username=p["username"],
                            password=p["password"],
                            timeout=10)
                stdin, stdout, stderr = ssh.exec_command("./PAI-PL_USR v")
                out = stdout.read().decode().strip()
                ssh.close()
                results[device] = out
            except Exception as e:
                results[device] = f"Error: {e}"
        return {"pai-pl version": results}
