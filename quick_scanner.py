#!/usr/bin/env python3
"""
Quick Scanner - Fast Discovery (5-10 Sekunden)
Scannt nur wichtige IPs: .1, .10, .11, .20-30, .100-110, .254
"""

import json
import subprocess
import socket
from datetime import datetime
from typing import Dict

class QuickScanner:
    """Schneller Scanner für wichtige IPs"""
    
    def __init__(self, network_base: str = None):
        if network_base:
            self.network_base = network_base
        else:
            # Auto-detect
            self.network_base = self._detect_network_base()
        
        # Wichtige IPs die normalerweise Geräte sind
        self.important_ips = [
            1,    # Router/Gateway
            2, 3, 4, 5,  # Core Network Devices
            10, 11, 12, 13, 14, 15,  # APs
            20, 21, 22, 23, 24, 25,  # Clients/Consoles
            30, 31, 32,  # More devices
            50, 51, 52,  # PCs
            100, 101, 102,  # Server Range
            254  # Alternate Gateway
        ]
    
    def _detect_network_base(self) -> str:
        """Erkennt Netzwerk-Base (z.B. 192.168.200)"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            parts = local_ip.split('.')
            base = f"{parts[0]}.{parts[1]}.{parts[2]}"
            print(f"🔍 Erkanntes Netzwerk: {base}.0/24")
            return base
        except:
            return "192.168.1"
    
    def _is_alive(self, ip: str) -> bool:
        """Quick ping check"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                capture_output=True,
                timeout=2,
                check=False
            )
            return result.returncode == 0
        except:
            return False
    
    def _resolve_hostname(self, ip: str) -> str:
        """Resolve hostname"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return f"device-{ip.split('.')[-1]}"
    
    def _detect_type(self, ip: str, hostname: str) -> str:
        """Simple type detection"""
        hostname_lower = hostname.lower()
        
        if any(x in hostname_lower for x in ['router', 'gateway', 'gw']):
            return 'router'
        elif any(x in hostname_lower for x in ['switch', 'sw']):
            return 'switch'
        elif any(x in hostname_lower for x in ['ap', 'unifi', 'access']):
            return 'wlan_ap'
        elif any(x in hostname_lower for x in ['pc', 'desktop', 'laptop', 'workstation']):
            return 'pc'
        elif any(x in hostname_lower for x in ['ps4', 'ps5', 'xbox', 'playstation', 'nintendo']):
            return 'gaming_console'
        
        # Guess by IP range
        last_octet = int(ip.split('.')[-1])
        if last_octet <= 10:
            return 'router'
        elif 10 < last_octet <= 20:
            return 'wlan_ap'
        elif 20 < last_octet <= 50:
            return 'gaming_console'
        else:
            return 'unknown'
    
    def quick_scan(self) -> Dict:
        """Schneller Scan nur wichtiger IPs"""
        print("\n" + "="*60)
        print("⚡ QUICK SCANNER - Schnelle Discovery")
        print("="*60)
        print(f"Scanne {len(self.important_ips)} wichtige IPs...")
        print()
        
        devices = {}
        found = 0
        
        for last_octet in self.important_ips:
            ip = f"{self.network_base}.{last_octet}"
            
            print(f"Testing {ip}...", end='\r')
            
            if self._is_alive(ip):
                hostname = self._resolve_hostname(ip)
                device_type = self._detect_type(ip, hostname)
                
                devices[ip] = {
                    'hostname': hostname,
                    'type': device_type,
                    'discovery_method': 'quick_ping',
                    'metrics': {
                        'status': 'online',
                        'last_seen': datetime.now().isoformat()
                    }
                }
                
                found += 1
                icon = {
                    'router': '🌐',
                    'switch': '🔀',
                    'wlan_ap': '📡',
                    'gaming_console': '🎮',
                    'pc': '💻',
                    'unknown': '❓'
                }.get(device_type, '❓')
                
                print(f"✅ {icon} {ip:15} | {device_type:15} | {hostname}")
        
        print(f"\n{'='*60}")
        print(f"✅ Quick Scan abgeschlossen: {found} Geräte gefunden")
        
        return devices
    
    def export_to_json(self, devices: Dict, filename: str = 'network_data.json'):
        """Export im kompatiblen Format"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'network_range': f"{self.network_base}.0/24",
            'total_devices': len(devices),
            'devices': devices,
            'summary': {
                'by_type': {},
                'scan_method': 'quick_scanner'
            },
            'scan_method': 'quick_scanner',
            'auto_discovered': True
        }
        
        # Count by type
        for device in devices.values():
            dev_type = device.get('type', 'unknown')
            output['summary']['by_type'][dev_type] = \
                output['summary']['by_type'].get(dev_type, 0) + 1
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Exportiert: {filename}")
        return filename


def main():
    print("="*70)
    print("⚡ QUICK SCANNER - 10 Sekunden Discovery")
    print("="*70)
    print()
    print("Scannt nur wichtige IP-Ranges:")
    print("  • .1-5 (Gateway/Router)")
    print("  • .10-15 (Access Points)")
    print("  • .20-32 (Consoles/Clients)")
    print("  • .50-52 (PCs)")
    print("  • .100-102 (Server)")
    print("  • .254 (Alt Gateway)")
    print()
    
    scanner = QuickScanner()
    devices = scanner.quick_scan()
    scanner.export_to_json(devices)
    
    print("\n🎯 Fertig!")
    print("   Dashboard starten: npm run start:server-only")
    print("   Oder voller Scan: python3 smart_scanner.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan abgebrochen!")
        exit(0)
