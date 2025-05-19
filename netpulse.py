import subprocess
import socket
import ipaddress
import threading
import os

class NetPulse:
    def __init__(self):
        self.ping_process = None
        self.lock = threading.Lock()

    def ping(self, target, count=4):
        """Genera output riga per riga del comando ping."""
        flag = "-n" if os.name == "nt" else "-c"
        cmd = ["ping", flag, str(count), target]
        with self.lock:
            self.ping_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in self.ping_process.stdout:
            yield line.strip(), None
        self.ping_process.wait()

    def stop_ping(self):
        with self.lock:
            if self.ping_process:
                self.ping_process.terminate()
                self.ping_process = None

    def scan_network(self, network_cidr):
        """Ritorna dict con chiave 'network' e lista di 'hosts'."""
        net = ipaddress.IPv4Network(network_cidr, strict=False)
        return {"network": str(net), "hosts": [str(ip) for ip in net.hosts()]}
