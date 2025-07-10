import subprocess
import socket
import ipaddress
import threading
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional, Callable
import psutil
import platform

class NetworkTools:
    """Enhanced network tools with modern features"""
    
    def __init__(self):
        self.ping_process = None
        self.lock = threading.Lock()
        self.scan_active = False
        self.stop_scan = False
    
    def stop_ping(self):
        """Stop active ping process"""
        with self.lock:
            if self.ping_process and self.ping_process.poll() is None:
                self.ping_process.terminate()
                self.ping_process = None
    
    def format_output(self, data: dict) -> str:
        """Format output data for display"""
        if not isinstance(data, dict):
            return str(data)
        
        lines = []
        for k, v in data.items():
            if isinstance(v, dict):
                lines.append(f"{k.replace('_', ' ').title()}:")
                for sk, sv in v.items():
                    lines.append(f"  {sk.replace('_', ' ').title()}: {sv}")
            elif isinstance(v, list):
                lines.append(f"{k.replace('_', ' ').title()}:")
                for item in v:
                    if isinstance(item, dict):
                        for ik, iv in item.items():
                            lines.append(f"  {ik.replace('_', ' ').title()}: {iv}")
                    else:
                        lines.append(f"  - {item}")
            else:
                label = k.replace("_", " ").title()
                val = "Yes" if v is True else "No" if v is False else v
                lines.append(f"{label}: {val}")
        
        return "\n".join(lines)
    
    def ping(self, host: str, count: int = 4, continuous: bool = False, 
             callback: Optional[Callable] = None) -> Dict:
        """Enhanced ping with better output parsing"""
        try:
            if continuous:
                cmd = ["ping", "-t", host] if platform.system().lower() == "windows" else ["ping", host]
            else:
                cmd = ["ping", "-n", str(count), host] if platform.system().lower() == "windows" else ["ping", "-c", str(count), host]
            
            self.stop_ping()
            
            with self.lock:
                self.ping_process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                    text=True, bufsize=1
                )
            
            output_lines = []
            stats = {'sent': 0, 'received': 0, 'lost': 0, 'min_time': None, 'max_time': None, 'avg_time': None}
            
            for raw in self.ping_process.stdout:
                line = raw.rstrip()
                if line:
                    output_lines.append(line)
                    
                    # Parse statistics
                    if "time=" in line.lower():
                        stats['received'] += 1
                        try:
                            time_part = line.split("time=")[1].split()[0]
                            time_ms = float(time_part.replace("ms", ""))
                            if stats['min_time'] is None or time_ms < stats['min_time']:
                                stats['min_time'] = time_ms
                            if stats['max_time'] is None or time_ms > stats['max_time']:
                                stats['max_time'] = time_ms
                        except:
                            pass
                    
                    if callback:
                        callback(line)
            
            self.ping_process.wait()
            
            # Calculate packet loss
            if not continuous:
                stats['sent'] = count
                stats['lost'] = stats['sent'] - stats['received']
                stats['loss_percent'] = (stats['lost'] / stats['sent']) * 100 if stats['sent'] > 0 else 0
            
            return {
                "host": host,
                "success": True,
                "output": "\n".join(output_lines),
                "statistics": stats
            }
            
        except Exception as e:
            return {"host": host, "success": False, "error": str(e)}
    
    def traceroute(self, host: str, max_hops: int = 30) -> Dict:
        """Enhanced traceroute with hop analysis"""
        try:
            cmd = ["tracert", "-h", str(max_hops), host] if platform.system().lower() == "windows" else ["traceroute", "-m", str(max_hops), host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Parse traceroute output
            lines = result.stdout.strip().split('\n')
            hops = []
            
            for line in lines:
                if line.strip() and not line.startswith("Tracing") and not line.startswith("over"):
                    try:
                        # Basic hop parsing (can be enhanced)
                        parts = line.strip().split()
                        if len(parts) >= 2 and parts[0].isdigit():
                            hop_num = int(parts[0])
                            hops.append({"hop": hop_num, "line": line.strip()})
                    except:
                        continue
            
            return {
                "host": host,
                "max_hops": max_hops,
                "hops": hops,
                "output": result.stdout.strip(),
                "success": True
            }
            
        except Exception as e:
            return {"host": host, "error": str(e), "success": False}
    
    def nslookup(self, domain: str) -> Dict:
        """Enhanced DNS lookup with multiple record types"""
        try:
            results = {}
            
            # A record
            try:
                hostname, aliases, addresses = socket.gethostbyname_ex(domain)
                results['A_records'] = addresses
                results['aliases'] = aliases
                results['canonical_name'] = hostname
            except:
                pass
            
            # Reverse DNS
            try:
                if self._is_ip_address(domain):
                    reverse_name = socket.gethostbyaddr(domain)[0]
                    results['reverse_dns'] = reverse_name
            except:
                pass
            
            # Additional DNS record types using system commands
            record_types = ['MX', 'TXT', 'NS', 'CNAME']
            for record_type in record_types:
                try:
                    if platform.system().lower() == "windows":
                        cmd = f"nslookup -type={record_type} {domain}"
                    else:
                        cmd = f"dig {domain} {record_type} +short"
                    
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    if result.stdout.strip():
                        results[f'{record_type}_records'] = result.stdout.strip().split('\n')
                except:
                    pass
            
            return {
                "domain": domain,
                "records": results,
                "success": True
            }
            
        except Exception as e:
            return {"domain": domain, "error": str(e), "success": False}
    
    def port_scan(self, host: str, ports: str = "1-1000", timeout: int = 3, 
                 callback: Optional[Callable] = None) -> Dict:
        """Advanced port scanner with multi-threading"""
        try:
            # Parse port range
            open_ports = []
            closed_ports = []
            
            if '-' in ports:
                start, end = map(int, ports.split('-'))
                port_list = range(start, end + 1)
            else:
                port_list = [int(p.strip()) for p in ports.split(',')]
            
            self.stop_scan = False
            
            def scan_port(port):
                if self.stop_scan:
                    return None
                    
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(timeout)
                        result = sock.connect_ex((host, port))
                        
                        if result == 0:
                            # Try to get service name
                            try:
                                service = socket.getservbyport(port)
                            except:
                                service = "unknown"
                            
                            port_info = {"port": port, "service": service, "status": "open"}
                            open_ports.append(port_info)
                            
                            if callback:
                                callback(f"Port {port} is open ({service})")
                            
                            return port_info
                        else:
                            closed_ports.append(port)
                            return None
                            
                except Exception as e:
                    return None
            
            # Multi-threaded scanning
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = {executor.submit(scan_port, port): port for port in port_list}
                
                for future in as_completed(futures):
                    if self.stop_scan:
                        break
                    
                    try:
                        result = future.result()
                    except Exception as e:
                        continue
            
            return {
                "host": host,
                "ports_scanned": len(port_list),
                "open_ports": open_ports,
                "open_count": len(open_ports),
                "closed_count": len(closed_ports),
                "success": True
            }
            
        except Exception as e:
            return {"host": host, "error": str(e), "success": False}
    
    def network_discovery(self, network: str, timeout: int = 3,
                         callback: Optional[Callable] = None) -> Dict:
        """Network discovery with host detection"""
        try:
            net = ipaddress.IPv4Network(network, strict=False)
            alive_hosts = []
            
            self.stop_scan = False
            
            def ping_host(ip):
                if self.stop_scan:
                    return None
                    
                try:
                    if platform.system().lower() == "windows":
                        cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), str(ip)]
                    else:
                        cmd = ["ping", "-c", "1", "-W", str(timeout), str(ip)]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 1)
                    
                    if result.returncode == 0:
                        # Try to get hostname
                        try:
                            hostname = socket.gethostbyaddr(str(ip))[0]
                        except:
                            hostname = "unknown"
                        
                        host_info = {"ip": str(ip), "hostname": hostname, "status": "alive"}
                        alive_hosts.append(host_info)
                        
                        if callback:
                            callback(f"Found host: {ip} ({hostname})")
                        
                        return host_info
                    
                except Exception as e:
                    pass
                
                return None
            
            # Multi-threaded host discovery
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = {executor.submit(ping_host, ip): ip for ip in net.hosts()}
                
                for future in as_completed(futures):
                    if self.stop_scan:
                        break
                    
                    try:
                        result = future.result()
                    except Exception as e:
                        continue
            
            return {
                "network": str(net),
                "hosts_scanned": len(list(net.hosts())),
                "alive_hosts": alive_hosts,
                "alive_count": len(alive_hosts),
                "success": True
            }
            
        except Exception as e:
            return {"network": network, "error": str(e), "success": False}
    
    def bandwidth_test(self, host: str = "8.8.8.8", duration: int = 10,
                      callback: Optional[Callable] = None) -> Dict:
        """Basic bandwidth test using ping statistics"""
        try:
            if callback:
                callback("Starting bandwidth test...")
            
            # Use ping to estimate bandwidth
            ping_results = []
            start_time = time.time()
            
            while time.time() - start_time < duration:
                result = self.ping(host, count=1)
                if result.get('success') and result.get('statistics'):
                    stats = result['statistics']
                    if stats['min_time'] is not None:
                        ping_results.append(stats['min_time'])
                
                if callback:
                    callback(f"Testing... {int(time.time() - start_time)}/{duration}s")
                
                time.sleep(1)
            
            if ping_results:
                avg_latency = sum(ping_results) / len(ping_results)
                min_latency = min(ping_results)
                max_latency = max(ping_results)
                jitter = max_latency - min_latency
                
                # Basic quality assessment
                if avg_latency < 50:
                    quality = "Excellent"
                elif avg_latency < 100:
                    quality = "Good"
                elif avg_latency < 200:
                    quality = "Fair"
                else:
                    quality = "Poor"
                
                return {
                    "host": host,
                    "duration": duration,
                    "avg_latency": avg_latency,
                    "min_latency": min_latency,
                    "max_latency": max_latency,
                    "jitter": jitter,
                    "quality": quality,
                    "samples": len(ping_results),
                    "success": True
                }
            else:
                return {
                    "host": host,
                    "error": "No successful pings during test",
                    "success": False
                }
                
        except Exception as e:
            return {"host": host, "error": str(e), "success": False}
    
    def get_network_interfaces(self) -> Dict:
        """Get network interface information"""
        try:
            interfaces = {}
            
            for interface, addresses in psutil.net_if_addrs().items():
                interface_info = {
                    "name": interface,
                    "addresses": []
                }
                
                for addr in addresses:
                    addr_info = {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    }
                    interface_info["addresses"].append(addr_info)
                
                # Get interface statistics
                try:
                    stats = psutil.net_if_stats()[interface]
                    interface_info["stats"] = {
                        "is_up": stats.isup,
                        "duplex": str(stats.duplex),
                        "speed": stats.speed,
                        "mtu": stats.mtu
                    }
                except:
                    pass
                
                interfaces[interface] = interface_info
            
            return {
                "interfaces": interfaces,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def stop_all_scans(self):
        """Stop all active scans"""
        self.stop_scan = True
        self.stop_ping()
    
    def _is_ip_address(self, text: str) -> bool:
        """Check if text is a valid IP address"""
        try:
            ipaddress.ip_address(text)
            return True
        except ValueError:
            return False
    
    def calc_subnet_info(self, input_str: str) -> Dict:
        """Calculate subnet information with enhanced details"""
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
                "ip_address": str(ip),
                "subnet_mask": str(net.netmask),
                "wildcard_mask": str(wildcard),
                "cidr_notation": str(net),
                "network_address": str(net.network_address),
                "broadcast_address": str(net.broadcast_address),
                "first_usable": str(hosts[0]) if hosts else "N/A",
                "last_usable": str(hosts[-1]) if hosts else "N/A",
                "usable_host_count": len(hosts),
                "total_addresses": net.num_addresses,
                "ip_class": self._get_ip_class(ip),
                "is_private": ip.is_private,
                "is_multicast": ip.is_multicast,
                "is_reserved": ip.is_reserved,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _get_ip_class(self, ip: ipaddress.IPv4Address) -> str:
        """Get IP address class"""
        first_octet = int(str(ip).split(".")[0])
        
        if 1 <= first_octet <= 126:
            return "A"
        elif 128 <= first_octet <= 191:
            return "B"
        elif 192 <= first_octet <= 223:
            return "C"
        elif 224 <= first_octet <= 239:
            return "D (Multicast)"
        elif 240 <= first_octet <= 255:
            return "E (Experimental)"
        else:
            return "Unknown"
    
    def scan_network(self, network_cidr: str) -> Dict:
        """Enhanced network scan with host discovery"""
        return self.network_discovery(network_cidr)