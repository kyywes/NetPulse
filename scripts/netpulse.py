import subprocess
import socket
import ipaddress
import threading

class NetPulse:
    def __init__(self):
        self.ping_process = None
        self.lock = threading.Lock()

    def stop_ping(self):
        with self.lock:
            if self.ping_process and self.ping_process.poll() is None:
                self.ping_process.terminate()
                self.ping_process = None

    def format_output(self, data: dict) -> str:
        if not isinstance(data, dict):
            return str(data)
        lines = []
        for k, v in data.items():
            if isinstance(v, dict):
                lines.append(f"{k.capitalize()}:")
                for sk, sv in v.items():
                    lines.append(f"  {sk}: {sv}")
            elif isinstance(v, list):
                lines.append(f"{k.capitalize()}:")
                for item in v:
                    lines.append(f"  - {item}")
            else:
                label = k.replace("_", " ").capitalize()
                val = "Yes" if v is True else "No" if v is False else v
                lines.append(f"{label}: {val}")
        return "\n".join(lines)

    def ping(self, host, count=4, continuous=False, callback=None):
        try:
            cmd = ["ping", "-t", host] if continuous else ["ping", "-n", str(count), host]
            self.stop_ping()
            with self.lock:
                self.ping_process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
                )
            for raw in self.ping_process.stdout:
                line = raw.rstrip()
                if callback and line:
                    callback(line)
            self.ping_process.wait()
            return {"host": host, "success": True, "output": "Ping completato."}
        except Exception as e:
            return {"host": host, "success": False, "error": str(e)}

    def traceroute(self, host):
        try:
            r = subprocess.run(["tracert", host], capture_output=True, text=True, timeout=30)
            return {"host": host, "output": r.stdout.strip()}
        except Exception as e:
            return {"host": host, "error": str(e)}

    def nslookup(self, domain):
        try:
            h, a, addrs = socket.gethostbyname_ex(domain)
            return {"domain": domain, "hostname": h, "aliases": a, "addresses": addrs}
        except Exception as e:
            return {"domain": domain, "error": str(e)}

    def calc_subnet_info(self, input_str):
        try:
            if "/" in input_str:
                net = ipaddress.IPv4Network(input_str, strict=False)
                ip = net.network_address
            else:
                ip_str, mask_str = input_str.split()
                net = ipaddress.IPv4Network(f"{ip_str}/{mask_str}", strict=False)
                ip = ipaddress.IPv4Address(ip_str)
            wildcard = ipaddress.IPv4Address(int(net.hostmask))
            hosts = list(net.hosts())
            return {
                "ip address": str(ip),
                "subnet mask": str(net.netmask),
                "wildcard mask": str(wildcard),
                "cidr notation": str(net),
                "network address": str(net.network_address),
                "broadcast address": str(net.broadcast_address),
                "first usable": str(hosts[0]) if hosts else "N/A",
                "last usable": str(hosts[-1]) if hosts else "N/A",
                "usable host count": len(hosts),
                "ip class": self.get_ip_class(ip),
                "is private": ip.is_private
            }
        except Exception as e:
            return {"error": str(e)}

    def get_ip_class(self, ip):
        fo = int(str(ip).split(".")[0])
        if 1 <= fo <= 126: return "A"
        if 128 <= fo <= 191: return "B"
        if 192 <= fo <= 223: return "C"
        if 224 <= fo <= 239: return "D (Multicast)"
        if 240 <= fo <= 255: return "E (Experimental)"
        return "Unknown"

    def scan_network(self, network_cidr):
        net = ipaddress.IPv4Network(network_cidr, strict=False)
        return {"network": str(net), "hosts": [str(ip) for ip in net.hosts()]}
