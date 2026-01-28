#!/usr/bin/env python3
"""
Kali Tools Scanner - Zero Configuration
Kombiniert die besten Kali Linux Tools:
- arp-scan (Fast Discovery + MAC Vendor 48k DB)
- masscan (Ultra-fast Port Scanning)
- nmap (Service Detection + OS Fingerprinting)
- netdiscover (Alternative ARP)
"""

import subprocess
import json
import re
import socket
from datetime import datetime
from typing import Dict, List, Optional
import sys

class KaliScanner:
    """
    Zero-Config Scanner mit Kali Linux Tools
    Erkennt automatisch: Interface, Network, Devices
    """
    
    def __init__(self):
        self.interface = None
        self.network = None
        self.devices = {}
        
        # Check welche Tools verfügbar sind
        self.available_tools = self._check_tools()
        
        print("🔍 Kali Tools Scanner - Zero Configuration")
        print(f"   Available: {', '.join(self.available_tools.keys())}")
    
    def _check_tools(self) -> Dict[str, bool]:
        """Check welche Kali Tools installiert sind"""
        tools = {
            'arp-scan': self._command_exists('arp-scan'),
            'masscan': self._command_exists('masscan'),
            'nmap': self._command_exists('nmap'),
            'netdiscover': self._command_exists('netdiscover'),
            'fping': self._command_exists('fping'),
        }
        
        for tool, available in tools.items():
            status = '✅' if available else '❌'
            print(f"   {status} {tool}")
        
        return {k: v for k, v in tools.items() if v}
    
    def _command_exists(self, cmd: str) -> bool:
        """Check ob Command existiert"""
        try:
            result = subprocess.run(
                ['which', cmd],
                capture_output=True,
                timeout=1
            )
            return result.returncode == 0
        except:
            return False
    
    def _detect_interface(self) -> str:
        """Auto-detect active network interface"""
        try:
            # Methode 1: Via default route
            result = subprocess.run(
                ['ip', 'route', 'get', '8.8.8.8'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            match = re.search(r'dev (\S+)', result.stdout)
            if match:
                return match.group(1)
            
            # Methode 2: First non-loopback interface
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                match = re.search(r'^\d+: (\S+):', line)
                if match and match.group(1) not in ['lo', 'docker0']:
                    return match.group(1)
        
        except Exception as e:
            print(f"⚠️  Interface detection failed: {e}")
        
        return 'eth0'  # Fallback
    
    def _detect_network(self, interface: str) -> str:
        """Auto-detect network range"""
        try:
            result = subprocess.run(
                ['ip', 'addr', 'show', interface],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            # Parse CIDR
            match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', result.stdout)
            if match:
                ip = match.group(1)
                cidr = match.group(2)
                
                # Convert to network address
                parts = ip.split('.')
                if cidr == '24':
                    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
                elif cidr == '16':
                    return f"{parts[0]}.{parts[1]}.0.0/16"
        
        except Exception as e:
            print(f"⚠️  Network detection failed: {e}")
        
        return "192.168.1.0/24"  # Fallback
    
    def arp_scan_discovery(self) -> Dict:
        """
        Phase 1: Fast Discovery mit arp-scan
        Schnellste und genaueste Methode
        """
        print("\n" + "="*70)
        print("📡 PHASE 1: ARP DISCOVERY")
        print("="*70)
        
        devices = {}
        
        if 'arp-scan' in self.available_tools:
            print("Method: arp-scan (48,000 vendor database)")
            devices = self._arp_scan()
        elif 'netdiscover' in self.available_tools:
            print("Method: netdiscover (fallback)")
            devices = self._netdiscover()
        else:
            print("⚠️  No ARP tool available, using fping")
            devices = self._fping_scan()
        
        print(f"✅ Found {len(devices)} devices")
        return devices
    
    def _arp_scan(self) -> Dict:
        """arp-scan implementation"""
        devices = {}
        
        try:
            # arp-scan with best options
            cmd = [
                'arp-scan',
                '--localnet',       # Auto-detect network
                '--quiet',          # Machine-readable output
                '--retry=3',        # Retry 3 times
                '--timeout=500'     # 500ms timeout
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for line in result.stdout.split('\n'):
                # Format: IP\tMAC\tVendor
                parts = line.split('\t')
                if len(parts) >= 3:
                    ip = parts[0].strip()
                    mac = parts[1].strip().upper()
                    vendor = parts[2].strip()
                    
                    try:
                        # Validate IP
                        socket.inet_aton(ip)
                        
                        devices[ip] = {
                            'ip': ip,
                            'mac': mac,
                            'vendor': vendor,
                            'hostname': self._resolve_hostname(ip),
                            'method': 'arp-scan'
                        }
                        
                        print(f"  {ip:15} | {mac:17} | {vendor}")
                    except:
                        pass
        
        except subprocess.TimeoutExpired:
            print("  ⚠️  arp-scan timeout")
        except Exception as e:
            print(f"  ⚠️  arp-scan failed: {e}")
        
        return devices
    
    def _netdiscover(self) -> Dict:
        """netdiscover implementation"""
        devices = {}
        
        try:
            cmd = [
                'netdiscover',
                '-i', self.interface,
                '-P',  # Print results
                '-N',  # Do not print header
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Run for 10 seconds
            try:
                output, _ = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                output, _ = process.communicate()
            
            # Parse output
            for line in output.split('\n'):
                parts = line.split()
                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[1].upper()
                    vendor = ' '.join(parts[2:])
                    
                    devices[ip] = {
                        'ip': ip,
                        'mac': mac,
                        'vendor': vendor,
                        'hostname': self._resolve_hostname(ip),
                        'method': 'netdiscover'
                    }
                    
                    print(f"  {ip:15} | {mac:17} | {vendor}")
        
        except Exception as e:
            print(f"  ⚠️  netdiscover failed: {e}")
        
        return devices
    
    def _fping_scan(self) -> Dict:
        """fping fallback (kein MAC/Vendor)"""
        devices = {}
        
        try:
            cmd = ['fping', '-g', self.network, '-a', '-q', '-r', '1']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            for ip in result.stdout.split('\n'):
                ip = ip.strip()
                if ip:
                    devices[ip] = {
                        'ip': ip,
                        'hostname': self._resolve_hostname(ip),
                        'method': 'fping'
                    }
                    print(f"  {ip:15}")
        
        except Exception as e:
            print(f"  ⚠️  fping failed: {e}")
        
        return devices
    
    def masscan_ports(self, devices: Dict) -> Dict:
        """
        Phase 2: Fast Port Scan mit masscan
        Scannt wichtigste Ports in Sekunden
        """
        if 'masscan' not in self.available_tools:
            print("\n⚠️  masscan not available, skipping port scan")
            return devices
        
        print("\n" + "="*70)
        print("🔎 PHASE 2: PORT SCANNING (masscan)")
        print("="*70)
        
        if not devices:
            return devices
        
        # Target IPs
        ips = ','.join(devices.keys())
        
        try:
            # masscan command
            cmd = [
                'masscan',
                ips,
                '-p21-10000',     # Port range
                '--rate=2000',    # Packets per second
                '-oJ', '-'        # JSON output to stdout
            ]
            
            print(f"Scanning {len(devices)} devices...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse masscan JSON output
            for line in result.stdout.split('\n'):
                line = line.strip().rstrip(',')
                if line and line.startswith('{'):
                    try:
                        data = json.loads(line)
                        ip = data['ip']
                        port = data['ports'][0]['port']
                        
                        if ip in devices:
                            if 'open_ports' not in devices[ip]:
                                devices[ip]['open_ports'] = []
                            devices[ip]['open_ports'].append(port)
                    except:
                        pass
            
            # Print results
            for ip, device in devices.items():
                ports = device.get('open_ports', [])
                if ports:
                    print(f"  {ip:15} | {len(ports):2} ports | {ports[:5]}")
        
        except subprocess.TimeoutExpired:
            print("  ⚠️  masscan timeout")
        except Exception as e:
            print(f"  ⚠️  masscan failed: {e}")
        
        return devices
    
    def nmap_services(self, devices: Dict) -> Dict:
        """
        Phase 3: Service Detection mit nmap
        Identifiziert Services und OS
        """
        if 'nmap' not in self.available_tools:
            print("\n⚠️  nmap not available, skipping service detection")
            return devices
        
        print("\n" + "="*70)
        print("🏷️  PHASE 3: SERVICE DETECTION (nmap)")
        print("="*70)
        
        if not devices:
            return devices
        
        # Target IPs (max 10 for speed)
        target_ips = list(devices.keys())[:10]
        ips = ' '.join(target_ips)
        
        try:
            cmd = f'nmap -sV -T4 --top-ports 100 {ips}'
            
            print(f"Scanning {len(target_ips)} devices...")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Simple parsing (in production: use python-libnmap)
            current_ip = None
            for line in result.stdout.split('\n'):
                # Find IP
                ip_match = re.search(r'Nmap scan report for .*?\(?([\d.]+)\)?', line)
                if ip_match:
                    current_ip = ip_match.group(1)
                    continue
                
                # Find open ports
                port_match = re.search(r'^(\d+)/tcp\s+open\s+(\S+)', line)
                if port_match and current_ip and current_ip in devices:
                    port = int(port_match.group(1))
                    service = port_match.group(2)
                    
                    if 'services' not in devices[current_ip]:
                        devices[current_ip]['services'] = {}
                    
                    devices[current_ip]['services'][port] = service
            
            # Print results
            for ip in target_ips:
                if ip in devices:
                    services = devices[ip].get('services', {})
                    if services:
                        print(f"  {ip:15} | {list(services.values())[:3]}")
        
        except subprocess.TimeoutExpired:
            print("  ⚠️  nmap timeout")
        except Exception as e:
            print(f"  ⚠️  nmap failed: {e}")
        
        return devices
    
    def classify_devices(self, devices: Dict) -> Dict:
        """
        Phase 4: Multi-Factor Device Classification
        """
        print("\n" + "="*70)
        print("🎯 PHASE 4: DEVICE CLASSIFICATION")
        print("="*70)
        
        for ip, device in devices.items():
            device['type'] = self._classify_device(device)
            
            icon = self._get_icon(device['type'])
            print(f"  {icon} {ip:15} | {device['type']:15} | "
                  f"{device.get('hostname', 'unknown')}")
        
        return devices
    
    def _classify_device(self, device: Dict) -> str:
        """Multi-factor classification logic"""
        
        # Factor 1: MAC Vendor
        vendor = device.get('vendor', '').lower()
        
        vendor_map = {
            'cisco': 'router',
            'juniper': 'router',
            'ubiquiti': 'wlan_ap',
            'mikrotik': 'router',
            'playstation': 'gaming_console',
            'xbox': 'gaming_console',
            'nintendo': 'gaming_console',
            'synology': 'nas',
            'qnap': 'nas',
            'raspberry': 'raspberry_pi',
        }
        
        for key, value in vendor_map.items():
            if key in vendor:
                return value
        
        # Factor 2: Port-based
        ports = set(device.get('open_ports', []))
        
        if 3074 in ports or 9100 in ports:
            return 'gaming_console'
        elif 8443 in ports and 10001 in ports:
            return 'wlan_ap'
        elif 631 in ports:
            return 'printer'
        elif 139 in ports and 445 in ports:
            return 'nas'
        elif 161 in ports and (22 in ports or 23 in ports):
            return 'router'
        
        # Factor 3: Hostname
        hostname = device.get('hostname', '').lower()
        
        if any(x in hostname for x in ['router', 'gw', 'gateway']):
            return 'router'
        elif any(x in hostname for x in ['ap', 'unifi']):
            return 'wlan_ap'
        elif any(x in hostname for x in ['switch', 'sw']):
            return 'switch'
        
        return 'unknown'
    
    def _resolve_hostname(self, ip: str) -> str:
        """DNS hostname resolution"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return f"device-{ip.split('.')[-1]}"
    
    def _get_icon(self, device_type: str) -> str:
        """Device icon"""
        icons = {
            'router': '🌐',
            'switch': '🔀',
            'wlan_ap': '📡',
            'gaming_console': '🎮',
            'nas': '💾',
            'printer': '🖨️',
            'raspberry_pi': '🥧',
            'pc': '💻',
            'unknown': '❓'
        }
        return icons.get(device_type, '❓')
    
    def full_scan(self) -> Dict:
        """Vollständiger Zero-Config Scan"""
        print("\n" + "="*70)
        print("🚀 KALI TOOLS SCANNER - Zero Configuration")
        print("="*70)
        
        # Auto-detect everything
        self.interface = self._detect_interface()
        self.network = self._detect_network(self.interface)
        
        print(f"Interface: {self.interface}")
        print(f"Network: {self.network}")
        
        # Phase 1: Discovery
        devices = self.arp_scan_discovery()
        
        # Phase 2: Port Scan
        if devices:
            devices = self.masscan_ports(devices)
        
        # Phase 3: Service Detection
        if devices:
            devices = self.nmap_services(devices)
        
        # Phase 4: Classification
        if devices:
            devices = self.classify_devices(devices)
        
        self.devices = devices
        return devices
    
    def export_results(self, filename: str = 'network_data.json'):
        """Export to dashboard format"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'network_range': self.network,
            'total_devices': len(self.devices),
            'devices': {},
            'summary': self._generate_summary(),
            'scan_method': 'kali_tools_scanner',
            'tools_used': list(self.available_tools.keys()),
            'auto_discovered': True
        }
        
        # Convert to dashboard format
        for ip, device in self.devices.items():
            output['devices'][ip] = {
                'hostname': device.get('hostname', f'device-{ip.split(".")[-1]}'),
                'mac': device.get('mac', ''),
                'vendor': device.get('vendor', 'Unknown'),
                'type': device.get('type', 'unknown'),
                'open_ports': device.get('open_ports', []),
                'services': device.get('services', {}),
                'metrics': {
                    'status': 'online',
                    'last_seen': datetime.now().isoformat(),
                    'port_count': len(device.get('open_ports', []))
                },
                'discovery_method': device.get('method', 'kali_tools')
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
            dev_type = device.get('type', 'unknown')
            summary['by_type'][dev_type] = summary['by_type'].get(dev_type, 0) + 1
            
            # By vendor
            vendor = device.get('vendor', 'Unknown')
            summary['by_vendor'][vendor] = summary['by_vendor'].get(vendor, 0) + 1
            
            # Total ports
            summary['total_ports'] += len(device.get('open_ports', []))
        
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
    print("="*70)
    print("🚀 KALI TOOLS SCANNER - Zero Configuration")
    print("   Kombiniert: arp-scan + masscan + nmap")
    print("="*70)
    print()
    
    # Check if running as root
    import os
    if os.geteuid() != 0:
        print("⚠️  WARNING: Not running as root")
        print("   Some tools may not work properly")
        print("   Run with: sudo python3 kali_scanner.py")
        print()
    
    scanner = KaliScanner()
    
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
        sys.exit(0)
