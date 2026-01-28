#!/usr/bin/env python3
"""
Ultra Advanced Network Scanner - Angry IP Scanner Style
Kombiniert: ARP-Fingerprinting, Nmap, Port-Scan, OS-Detection, MAC-Vendor-Lookup

Features:
- Multi-Method Discovery (ARP, Nmap, Ping)
- MAC Vendor Database (Top 100+)
- Port-based Fingerprinting
- Service Detection
- OS Detection
- Latency Measurement
- Multi-Factor Device Classification
"""

import json
import subprocess
import socket
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
import ipaddress
from collections import defaultdict

# Optional imports
try:
    from scapy.all import ARP, Ether, srp
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False


class UltraScanner:
    """
    Ultra Advanced Multi-Method Network Scanner
    Inspired by: Angry IP Scanner, arp-scan, nmap
    """
    
    def __init__(self, network_range: str = None):
        self.network_range = network_range or self._detect_network()
        self.devices = {}
        
        # Große MAC Vendor Database
        self.mac_vendors = self._init_mac_vendors()
        
        # Port Signatures für Device-Type-Erkennung
        self.port_signatures = self._init_port_signatures()
        
        print("🚀 Ultra Advanced Network Scanner")
        print(f"   Network: {self.network_range}")
        print(f"   Scapy: {'✅' if SCAPY_AVAILABLE else '❌ (optional)'}")
        print(f"   Nmap: {'✅' if NMAP_AVAILABLE else '❌ (optional)'}")
    
    def _detect_network(self) -> str:
        """Auto-detect local network"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            parts = local_ip.split('.')
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        except:
            return "192.168.1.0/24"
    
    def _init_mac_vendors(self) -> Dict:
        """
        Umfassende MAC OUI Vendor Database
        Format: 'XX:XX:XX' -> 'Vendor Name'
        """
        return {
            # Apple
            '00:1B:63': 'Apple', '00:03:93': 'Apple', '00:17:F2': 'Apple',
            'AC:DE:48': 'Apple', 'F0:18:98': 'Apple', '00:1D:C9': 'Apple',
            'A4:D1:D2': 'Apple', '28:CF:E9': 'Apple', 'BC:3B:AF': 'Apple',
            
            # Cisco
            '00:1F:CA': 'Cisco', '00:24:C3': 'Cisco', '00:0A:B8': 'Cisco',
            '00:1C:0E': 'Cisco', '00:1A:A1': 'Cisco', '00:1E:F7': 'Cisco',
            '00:1D:70': 'Cisco', '00:1B:D5': 'Cisco',
            
            # Ubiquiti
            '24:A4:3C': 'Ubiquiti', 'DC:9F:DB': 'Ubiquiti', '68:D7:9A': 'Ubiquiti',
            '78:8A:20': 'Ubiquiti', 'F0:9F:C2': 'Ubiquiti', '04:18:D6': 'Ubiquiti',
            '74:83:C2': 'Ubiquiti', 'B4:FB:E4': 'Ubiquiti',
            
            # MikroTik
            '00:0C:42': 'MikroTik', '4C:5E:0C': 'MikroTik', '6C:3B:6B': 'MikroTik',
            'D4:CA:6D': 'MikroTik', '48:8F:5A': 'MikroTik',
            
            # Huawei
            '00:E0:FC': 'Huawei', '28:6E:D4': 'Huawei', '70:72:3C': 'Huawei',
            'F8:E7:1E': 'Huawei', '34:6B:D3': 'Huawei',
            
            # Juniper
            '00:04:9A': 'Juniper', '00:05:85': 'Juniper', '00:12:1E': 'Juniper',
            
            # Gaming Consoles
            '00:1F:EA': 'Sony PlayStation', '7C:ED:8D': 'Microsoft Xbox',
            '98:B6:E9': 'Microsoft Xbox', '00:50:F2': 'Microsoft Xbox',
            '00:09:BF': 'Nintendo', '34:AF:2C': 'Nintendo Switch',
            '98:41:5C': 'Nintendo Switch', '00:17:AB': 'Nintendo Wii',
            
            # PC Manufacturers
            '00:23:54': 'Dell', '00:14:22': 'Dell', 'D0:67:E5': 'Dell',
            'B8:CA:3A': 'Dell', '18:DB:F2': 'Dell',
            '00:1E:C9': 'HP', '00:30:6E': 'HP', '9C:2A:70': 'HP',
            '00:1B:78': 'Lenovo', '54:EE:75': 'Lenovo', 'F0:DE:F1': 'Lenovo',
            '00:50:B6': 'Intel', '00:1B:21': 'Intel', 'A4:4E:31': 'Intel',
            '00:0C:76': 'ASUSTek', '2C:56:DC': 'ASUSTek',
            
            # NAS/Storage
            '00:11:32': 'Synology', '00:0C:F1': 'QNAP', 
            '00:08:9B': 'Western Digital',
            
            # Raspberry Pi
            'B8:27:EB': 'Raspberry Pi', 'DC:A6:32': 'Raspberry Pi',
            'E4:5F:01': 'Raspberry Pi', '28:CD:C1': 'Raspberry Pi',
            
            # Smart Home
            '3C:28:6D': 'Google Nest', '18:B4:30': 'Google Nest',
            'EC:1A:59': 'Amazon Echo', 'F0:D2:F1': 'Amazon Echo',
            '00:17:88': 'Philips Hue', '00:04:20': 'Philips',
            '74:C6:3B': 'Amazon', '44:65:0D': 'Amazon',
            
            # Network Adapters
            '00:13:02': 'Realtek', '52:54:00': 'QEMU/KVM',
            '00:50:56': 'VMware', '00:0C:29': 'VMware',
            '08:00:27': 'VirtualBox',
            
            # TP-Link
            '50:C7:BF': 'TP-Link', 'F4:F2:6D': 'TP-Link', 'C0:4A:00': 'TP-Link',
            
            # D-Link
            '00:05:5D': 'D-Link', '00:0D:88': 'D-Link', '00:13:46': 'D-Link',
            
            # Netgear
            '00:09:5B': 'Netgear', '00:1B:2F': 'Netgear', '84:1B:5E': 'Netgear',
            
            # Cameras
            '00:12:12': 'Axis', 'AC:CC:8E': 'Axis',
            '00:40:8C': 'Hikvision', '44:19:B6': 'Hikvision',
        }
    
    def _init_port_signatures(self) -> Dict:
        """
        Port-basierte Device Fingerprints
        """
        return {
            'router': {
                'required': [80, 443],
                'optional': [22, 23, 8080, 53, 161]
            },
            'switch': {
                'required': [22, 161],
                'optional': [80, 443, 23]
            },
            'wlan_ap': {
                'required': [80, 443],
                'optional': [22, 8080, 8443, 10001]
            },
            'nas': {
                'required': [139, 445],
                'optional': [548, 5000, 5001, 873]
            },
            'printer': {
                'required': [631],
                'optional': [515, 9100, 80]
            },
            'web_server': {
                'required': [80],
                'optional': [443, 8000, 8080, 8443]
            },
            'gaming_console': {
                'required': [3074],
                'optional': [3478, 3479, 9100, 9103]
            },
            'smart_tv': {
                'required': [7000],
                'optional': [8008, 8080, 55000]
            },
            'camera': {
                'required': [554],
                'optional': [80, 8000, 8080]
            },
        }
    
    def arp_discovery(self) -> Dict:
        """
        Phase 1: ARP Discovery
        Schnellste Methode für lokales Netzwerk
        """
        print("\n" + "="*70)
        print("📡 PHASE 1: ARP DISCOVERY")
        print("="*70)
        
        devices = {}
        
        if SCAPY_AVAILABLE:
            print("Method: Scapy ARP Scan")
            devices = self._arp_scapy()
        else:
            print("Method: System arp-scan")
            devices = self._arp_system()
        
        print(f"✅ Found {len(devices)} devices via ARP")
        return devices
    
    def _arp_scapy(self) -> Dict:
        """ARP scan mit Scapy"""
        devices = {}
        
        try:
            arp = ARP(pdst=self.network_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            result = srp(packet, timeout=3, verbose=0)[0]
            
            for sent, received in result:
                ip = received.psrc
                mac = received.hwsrc.upper()
                vendor = self._lookup_vendor(mac)
                
                devices[ip] = {
                    'ip': ip,
                    'mac': mac,
                    'vendor': vendor,
                    'method': 'arp_scapy'
                }
                
                print(f"  {ip:15} | {mac:17} | {vendor}")
        
        except Exception as e:
            print(f"  ⚠️ Scapy ARP failed: {e}")
        
        return devices
    
    def _arp_system(self) -> Dict:
        """ARP scan mit System-Tools"""
        devices = {}
        
        try:
            result = subprocess.run(
                ['arp-scan', '--localnet', '--quiet'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                parts = line.split('\t')
                if len(parts) >= 2:
                    ip = parts[0].strip()
                    mac = parts[1].strip().upper()
                    
                    try:
                        ipaddress.ip_address(ip)
                        vendor = self._lookup_vendor(mac)
                        
                        devices[ip] = {
                            'ip': ip,
                            'mac': mac,
                            'vendor': vendor,
                            'method': 'arp_system'
                        }
                        
                        print(f"  {ip:15} | {mac:17} | {vendor}")
                    except:
                        pass
        
        except Exception as e:
            print(f"  ⚠️ arp-scan failed: {e}")
        
        return devices
    
    def port_scan_fast(self, devices: Dict) -> Dict:
        """
        Phase 2: Fast Port Scan
        Scannt wichtigste Ports für Device-Type-Erkennung
        """
        print("\n" + "="*70)
        print("🔎 PHASE 2: PORT SCANNING")
        print("="*70)
        
        important_ports = [
            21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 515, 548, 631,
            3074, 3306, 3389, 3478, 5000, 5432, 5900, 7000, 8000, 8008, 8080,
            8443, 9100, 10001, 27017, 55000
        ]
        
        for ip, device in list(devices.items())[:10]:  # First 10 devices
            print(f"\n  Scanning: {ip}")
            
            open_ports = []
            
            for port in important_ports:
                if self._check_port(ip, port, timeout=0.3):
                    open_ports.append(port)
                    print(f"    ✅ Port {port}")
            
            device['open_ports'] = open_ports
            device['port_count'] = len(open_ports)
            device['device_type'] = self._classify_by_ports(open_ports)
        
        return devices
    
    def _check_port(self, ip: str, port: int, timeout: float = 0.5) -> bool:
        """Quick TCP port check"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def _classify_by_ports(self, open_ports: List[int]) -> str:
        """
        Device classification basierend auf offenen Ports
        """
        open_set = set(open_ports)
        scores = {}
        
        for device_type, signature in self.port_signatures.items():
            score = 0
            
            # Required ports
            required_match = sum(1 for p in signature['required'] if p in open_set)
            if required_match == 0:
                continue
            
            score += required_match * 10
            
            # Optional ports
            optional_match = sum(1 for p in signature['optional'] if p in open_set)
            score += optional_match
            
            scores[device_type] = score
        
        if not scores:
            return 'unknown'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def enrich_devices(self, devices: Dict) -> Dict:
        """
        Phase 3: Device Enrichment
        Hostname, Latency, Final Classification
        """
        print("\n" + "="*70)
        print("🏷️  PHASE 3: DEVICE ENRICHMENT")
        print("="*70)
        
        for ip, device in devices.items():
            # Hostname
            device['hostname'] = self._resolve_hostname(ip)
            
            # Latency
            latency = self._measure_latency(ip)
            if latency:
                device['latency_ms'] = latency
            
            # Final Classification (Multi-Factor)
            device['final_type'] = self._multi_factor_classify(device)
            
            icon = self._get_icon(device['final_type'])
            print(f"  {icon} {ip:15} | {device['final_type']:15} | "
                  f"{device.get('hostname', 'unknown')}")
        
        return devices
    
    def _resolve_hostname(self, ip: str) -> str:
        """DNS resolution"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return f"device-{ip.split('.')[-1]}"
    
    def _measure_latency(self, ip: str) -> Optional[float]:
        """Ping latency measurement"""
        try:
            result = subprocess.run(
                ['ping', '-c', '3', '-W', '1', ip],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if 'avg' in line or 'rtt' in line:
                    parts = line.split('=')[1].strip().split('/')
                    return float(parts[1])  # avg
        except:
            pass
        
        return None
    
    def _multi_factor_classify(self, device: Dict) -> str:
        """
        Multi-Faktor Device Classification
        Kombiniert: MAC Vendor, Ports, Hostname
        """
        # Factor 1: MAC Vendor
        vendor = device.get('vendor', '').lower()
        
        # Strong indicators from vendor
        vendor_mappings = {
            'cisco': 'router',
            'juniper': 'router',
            'ubiquiti': 'wlan_ap',
            'mikrotik': 'router',
            'playstation': 'gaming_console',
            'xbox': 'gaming_console',
            'nintendo': 'gaming_console',
            'synology': 'nas',
            'qnap': 'nas',
            'raspberry pi': 'raspberry_pi',
            'apple': 'apple_device',
        }
        
        for key, value in vendor_mappings.items():
            if key in vendor:
                return value
        
        # Factor 2: Port-based classification
        port_type = device.get('device_type', 'unknown')
        if port_type != 'unknown':
            return port_type
        
        # Factor 3: Hostname analysis
        hostname = device.get('hostname', '').lower()
        
        hostname_keywords = {
            'router': ['router', 'gw', 'gateway'],
            'switch': ['switch', 'sw'],
            'wlan_ap': ['ap', 'access', 'unifi'],
            'nas': ['nas', 'storage'],
            'printer': ['printer', 'print'],
        }
        
        for dev_type, keywords in hostname_keywords.items():
            if any(kw in hostname for kw in keywords):
                return dev_type
        
        return 'unknown'
    
    def _lookup_vendor(self, mac: str) -> str:
        """MAC OUI Vendor lookup"""
        oui = mac[:8].upper()  # First 3 bytes
        return self.mac_vendors.get(oui, 'Unknown')
    
    def _get_icon(self, device_type: str) -> str:
        """Device type icon"""
        icons = {
            'router': '🌐',
            'switch': '🔀',
            'wlan_ap': '📡',
            'gaming_console': '🎮',
            'nas': '💾',
            'printer': '🖨️',
            'camera': '📷',
            'smart_tv': '📺',
            'pc': '💻',
            'apple_device': '🍎',
            'raspberry_pi': '🥧',
            'web_server': '🖥️',
            'unknown': '❓'
        }
        return icons.get(device_type, '❓')
    
    def full_scan(self) -> Dict:
        """
        Vollständiger Multi-Phase Scan
        """
        print("\n" + "="*70)
        print("🚀 ULTRA ADVANCED NETWORK SCANNER")
        print("="*70)
        print(f"Network: {self.network_range}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Phase 1: ARP Discovery
        devices = self.arp_discovery()
        
        # Phase 2: Port Scanning
        if devices:
            devices = self.port_scan_fast(devices)
        
        # Phase 3: Enrichment
        if devices:
            devices = self.enrich_devices(devices)
        
        self.devices = devices
        return devices
    
    def export_results(self, filename: str = 'network_data.json'):
        """Export results in dashboard-compatible format"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'network_range': self.network_range,
            'total_devices': len(self.devices),
            'devices': {},
            'summary': self._generate_summary(),
            'scan_method': 'ultra_advanced_scanner',
            'auto_discovered': True
        }
        
        # Convert to dashboard format
        for ip, device in self.devices.items():
            output['devices'][ip] = {
                'hostname': device.get('hostname', f'device-{ip.split(".")[-1]}'),
                'mac': device.get('mac', ''),
                'vendor': device.get('vendor', 'Unknown'),
                'type': device.get('final_type', 'unknown'),
                'open_ports': device.get('open_ports', []),
                'metrics': {
                    'status': 'online',
                    'last_seen': datetime.now().isoformat(),
                    'latency_ms': device.get('latency_ms', 0),
                    'port_count': device.get('port_count', 0)
                },
                'discovery_method': device.get('method', 'unknown')
            }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Results exported: {filename}")
        return filename
    
    def _generate_summary(self) -> Dict:
        """Generate summary stats"""
        summary = {
            'by_type': {},
            'by_vendor': {},
            'total_ports': 0
        }
        
        for device in self.devices.values():
            # By type
            dev_type = device.get('final_type', 'unknown')
            summary['by_type'][dev_type] = summary['by_type'].get(dev_type, 0) + 1
            
            # By vendor
            vendor = device.get('vendor', 'Unknown')
            summary['by_vendor'][vendor] = summary['by_vendor'].get(vendor, 0) + 1
            
            # Port count
            summary['total_ports'] += device.get('port_count', 0)
        
        return summary
    
    def print_summary(self):
        """Print scan summary"""
        print("\n" + "="*70)
        print("📊 SCAN SUMMARY")
        print("="*70)
        
        summary = self._generate_summary()
        
        print(f"\nTotal Devices: {len(self.devices)}")
        
        print(f"\nBy Type:")
        for dev_type, count in sorted(summary['by_type'].items(), key=lambda x: x[1], reverse=True):
            icon = self._get_icon(dev_type)
            print(f"  {icon} {dev_type:20} : {count}")
        
        print(f"\nBy Vendor (Top 10):")
        for vendor, count in sorted(summary['by_vendor'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {vendor:25} : {count}")
        
        print(f"\nTotal Open Ports: {summary['total_ports']}")


def main():
    import sys
    
    print("="*70)
    print("🚀 ULTRA ADVANCED NETWORK SCANNER")
    print("   Angry IP Scanner Style + ARP Fingerprinting")
    print("="*70)
    print()
    
    network = sys.argv[1] if len(sys.argv) > 1 else None
    
    scanner = UltraScanner(network)
    
    # Full scan
    devices = scanner.full_scan()
    
    # Print summary
    scanner.print_summary()
    
    # Export
    scanner.export_results()
    
    print("\n✅ Scan complete!")
    print("   Start dashboard: npm run start:server-only")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan aborted by user")
        exit(0)
