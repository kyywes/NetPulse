import subprocess
import threading
import platform
import ipaddress
import json

class NetPulse:
    def __init__(self):
        self._ping_process = None

    def ping(self, host: str, count: int = 4, continuous: bool = False, callback=None):
        """
        Esegue ping su `host`.
        Se `continuous` usa -t (Windows) o senza -c (Unix).
        Chiama `callback(line)` per ogni riga di output.
        """
        system = platform.system()
        if system == "Windows":
            cmd = ["ping", host]
            if continuous:
                cmd += ["-t"]
            else:
                cmd += ["-n", str(count)]
        else:
            cmd = ["ping", host]
            if not continuous:
                cmd += ["-c", str(count)]
        self._ping_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in self._ping_process.stdout:
            line = line.rstrip()
            if callback:
                callback(line)
        self._ping_process.wait()

    def stop_ping(self):
        """Termina il processo di ping in corso (se esiste)."""
        if self._ping_process and self._ping_process.poll() is None:
            self._ping_process.terminate()

    def traceroute(self, host: str) -> dict:
        """
        Esegue traceroute (Windows: tracert).
        Ritorna dict con chiave 'output'.
        """
        cmd = ["tracert", host] if platform.system() == "Windows" else ["traceroute", host]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        output = proc.stdout if proc.returncode == 0 else proc.stderr
        return {"output": output}

    def nslookup(self, host: str) -> dict:
        """
        Esegue nslookup su `host`.
        Ritorna dict di righe chiave=valore, o 'output' se non parsabile.
        """
        proc = subprocess.run(["nslookup", host], capture_output=True, text=True)
        data = {}
        for line in proc.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip()
        return data or {"output": proc.stdout}

    def calc_subnet_info(self, cidr: str) -> dict:
        """
        Calcola network address, broadcast, netmask, numero di indirizzi,
        e restituisce i primi 10 host.
        """
        net = ipaddress.ip_network(cidr, strict=False)
        return {
            "network_address": str(net.network_address),
            "broadcast_address": str(net.broadcast_address),
            "netmask": str(net.netmask),
            "num_addresses": net.num_addresses,
            "hosts_sample": [str(ip) for ip in list(net.hosts())[:10]]
        }

    def scan_network(self, cidr: str) -> dict:
        """
        Ping sweep degli host nel CIDR. Ritorna la lista di host raggiungibili.
        """
        net = ipaddress.ip_network(cidr, strict=False)
        alive = []
        lock = threading.Lock()

        def worker(ip):
            args = []
            if platform.system() == "Windows":
                args = ["ping", "-n", "1", "-w", "1000", str(ip)]
            else:
                args = ["ping", "-c", "1", "-W", "1", str(ip)]
            res = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                with lock:
                    alive.append(str(ip))

        threads = []
        for ip in net.hosts():
            t = threading.Thread(target=worker, args=(ip,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        return {"alive_hosts": alive}

    def format_output(self, data) -> str:
        """
        Se `data` è dict o list, lo serializza in JSON indentato;
        altrimenti converte in stringa.
        """
        try:
            return json.dumps(data, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(data)
