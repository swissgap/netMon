#!/usr/bin/env python3
"""
Network Scanner V3 - NO DEMO DATA
100% Real Discovery - Kein Fallback zu simulierten Daten!
"""

import subprocess
import json
import socket
import time
from datetime import datetime
from typing import Dict, List, Optional
import ipaddress

class NetworkScanner:
    """
    Network Scanner - NUR echte Discovery
    KEINE Demo-Daten, KEINE Simulation!
    """
    
    def __init__(self, network_range: str = None):
        self.network_range = network_range or self._detect_network_range()
        self.devices = {}
        
    def _detect_network_range(self) -> str:
        """Auto-detect local network range"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            parts = local_ip.split('.')
            network = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            print(f"🔍 Auto-detected network: {network}")
            return network
        except:
            print("⚠️  Could not auto-detect network, using 192.168.1.0/24")
            return "192.168.1.0/24"
    
    def discover_devices(self) -> Dict[str, Dict]:
        """
        Discover devices - ONLY real methods, NO fake data!
        """
        print(f"\n🔍 Discovering devices in {self.network_range}...")
        discovered = {}
        
        # Try ARP scan first (requires root)
        arp_devices = self._arp_scan()
        if arp_devices:
            discovered.update(arp_devices)
            print(f"✅ ARP scan: {len(arp_devices)} devices found")
        
        # Fallback to ping sweep
        if not discovered:
            print("💡 ARP scan unavailable, using ping sweep...")
            ping_devices = self._ping_sweep()
            discovered.update(ping_devices)
            print(f"✅ Ping sweep: {len(ping_devices)} devices found")
        
        return discovered
    
    def _arp_scan(self) -> Dict:
        """ARP scan for quick discovery"""
        devices = {}
        try:
            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                # Parse: hostname (ip) at mac
                if '(' in line and ')' in line:
                    parts = line.split()
                    ip = line.split('(')[1].split(')')[0]
                    
                    if self._is_valid_ip(ip) and self._is_in_range(ip):
                        hostname = parts[0] if parts[0] != '?' else None
                        mac = None
                        
                        # Extract MAC
                        for part in parts:
                            if ':' in part and len(part) == 17:
                                mac = part
                                break
                        
                        devices[ip] = {
                            'hostname': hostname or self._resolve_hostname(ip),
                            'mac': mac,
                            'discovery_method': 'arp'
                        }
        except:
            pass
        
        return devices
    
    def _ping_sweep(self) -> Dict:
        """Ping sweep for discovery"""
        devices = {}
        
        try:
            network = ipaddress.ip_network(self.network_range)
            count = 0
            
            print("⏳ Running ping sweep (may take 1-2 min)...")
            
            for ip in network.hosts():
                ip_str = str(ip)
                
                if self._is_alive(ip_str):
                    devices[ip_str] = {
                        'hostname': self._resolve_hostname(ip_str),
                        'discovery_method': 'ping'
                    }
                    count += 1
                    if count % 5 == 0:
                        print(f"   ... {count} devices found")
                
        except Exception as e:
            print(f"⚠️  Ping sweep error: {e}")
        
        return devices
    
    def _is_alive(self, ip: str, timeout: int = 1) -> bool:
        """Check if host responds to ping"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout), ip],
                capture_output=True,
                timeout=timeout + 1
            )
            return result.returncode == 0
        except:
            return False
    
    def _resolve_hostname(self, ip: str) -> str:
        """Resolve hostname via DNS"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return f"device-{ip.split('.')[-1]}"
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address"""
        try:
            ipaddress.ip_address(ip)
            return True
        except:
            return False
    
    def _is_in_range(self, ip: str) -> bool:
        """Check if IP is in network range"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            network = ipaddress.ip_network(self.network_range)
            return ip_obj in network
        except:
            return False
    
    def classify_device(self, ip: str, device_info: Dict) -> str:
        """
        Classify device type based on REAL indicators
        NO hardcoded fake classifications!
        """
        hostname = device_info.get('hostname', '').lower()
        
        # Based on real hostname patterns
        if any(x in hostname for x in ['router', 'gateway', 'gw-', 'rt-']):
            return 'router'
        elif any(x in hostname for x in ['switch', 'sw-']):
            return 'switch'
        elif any(x in hostname for x in ['ap-', 'wap', 'wifi', 'unifi', 'access']):
            return 'wlan_ap'
        elif any(x in hostname for x in ['nas', 'storage']):
            return 'nas'
        elif any(x in hostname for x in ['desktop', 'laptop', 'pc-', 'workstation']):
            return 'pc'
        else:
            return 'unknown'
    
    def get_basic_metrics(self, ip: str) -> Dict:
        """
        Get ONLY real, measurable metrics
        NO fake/simulated data!
        """
        metrics = {
            'status': 'online',
            'last_seen': datetime.now().isoformat()
        }
        
        # Measure real ping time
        try:
            result = subprocess.run(
                ['ping', '-c', '1', ip],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # Extract ping time
                import re
                match = re.search(r'time=([\d.]+)', result.stdout)
                if match:
                    metrics['response_time'] = float(match.group(1))
        except:
            pass
        
        return metrics
    
    def scan_network(self) -> Dict:
        """
        Full network scan - ONLY real discovery
        """
        print("\n" + "="*60)
        print("🔍 NETWORK SCANNER V3 - Real Discovery Only")
        print("="*60)
        
        # Discover devices
        discovered = self.discover_devices()
        
        if not discovered:
            print("\n⚠️  NO DEVICES FOUND!")
            print("\nPossible reasons:")
            print("  - Not running as root (ARP scan needs root)")
            print("  - Firewall blocking ICMP")
            print("  - Wrong network range")
            print("  - No devices on network")
            print("\nTry:")
            print("  - sudo python3 network_scanner.py")
            print("  - Specify network: python3 network_scanner.py 10.0.0.0/24")
            return {}
        
        # Classify and get metrics
        print(f"\n📊 Processing {len(discovered)} devices...")
        
        for ip, device_info in discovered.items():
            # Classify
            device_type = self.classify_device(ip, device_info)
            device_info['type'] = device_type
            
            # Get real metrics
            metrics = self.get_basic_metrics(ip)
            device_info['metrics'] = metrics
            
            self.devices[ip] = device_info
        
        return self.devices
    
    def export_to_json(self, filename: str = 'network_data.json'):
        """Export to JSON - compatible format"""
        
        if not self.devices:
            print("\n⚠️  NO DEVICES TO EXPORT!")
            print("Run scan_network() first or check if devices were found.")
            return None
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'network_range': self.network_range,
            'total_devices': len(self.devices),
            'devices': self.devices,
            'summary': self._generate_summary(),
            'scan_method': 'network_scanner_v3_real_only',
            'has_demo_data': False  # IMPORTANT FLAG
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Exported to: {filename}")
        return filename
    
    def _generate_summary(self) -> Dict:
        """Generate summary"""
        summary = {
            'by_type': {},
            'online_devices': 0
        }
        
        for device in self.devices.values():
            dev_type = device.get('type', 'unknown')
            summary['by_type'][dev_type] = summary['by_type'].get(dev_type, 0) + 1
            
            if device.get('metrics', {}).get('status') == 'online':
                summary['online_devices'] += 1
        
        return summary


def main():
    import sys
    
    print("="*60)
    print("🔍 NETWORK SCANNER V3")
    print("="*60)
    print()
    print("⚠️  NO DEMO DATA MODE")
    print("✅  Only real device discovery")
    print("✅  Only real metrics")
    print()
    
    # Get network range from args if provided
    network_range = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create scanner
    scanner = NetworkScanner(network_range)
    
    # Scan
    devices = scanner.scan_network()
    
    if not devices:
        print("\n❌ No devices found - cannot create network_data.json")
        print("\n💡 For testing without real devices, use smart_scanner.py")
        print("   It has better discovery methods (ARP scan, SNMP, etc.)")
        sys.exit(1)
    
    # Show results
    print("\n" + "="*60)
    print("📊 DISCOVERED DEVICES")
    print("="*60)
    
    for ip, device in devices.items():
        icon = {
            'router': '🌐',
            'switch': '🔀',
            'wlan_ap': '📡',
            'pc': '💻',
            'nas': '💾',
            'unknown': '❓'
        }.get(device['type'], '❓')
        
        print(f"{icon} {ip:15} | {device['type']:10} | {device['hostname']}")
    
    # Export
    scanner.export_to_json()
    
    print("\n✅ Scan complete!")
    print("\n💡 For better results with SNMP data, use:")
    print("   python3 smart_scanner.py")


if __name__ == "__main__":
    main()
