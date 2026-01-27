#!/usr/bin/env python3
"""
Epic Gaming Day Network Scanner
Automatische Erkennung und Klassifizierung von Netzwerkgeräten
"""

import subprocess
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
import socket
import struct

class NetworkScanner:
    def __init__(self, network_range: str = "192.168.1.0/24"):
        self.network_range = network_range
        self.devices = {}
        
        # Device fingerprints für automatische Erkennung
        self.device_signatures = {
            'router': {
                'ports': [80, 443, 8080, 22],
                'keywords': ['router', 'gateway', 'fritz', 'asus', 'netgear', 'tp-link'],
                'mac_prefixes': ['00:50:56', '00:0C:29']  # Beispiele
            },
            'switch': {
                'ports': [80, 443, 23],
                'keywords': ['switch', 'cisco', 'juniper', 'aruba'],
                'mac_prefixes': []
            },
            'wlan_ap': {
                'ports': [80, 443, 22, 8443],
                'keywords': ['ap', 'access', 'unifi', 'aruba', 'cisco', 'ubiquiti', 'aironet'],
                'mac_prefixes': ['00:27:22', 'F0:9F:C2', '24:5A:4C']  # UniFi, Ubiquiti
            },
            'gaming_console': {
                'ports': [9100, 9103],
                'keywords': ['playstation', 'xbox', 'nintendo', 'ps4', 'ps5', 'switch'],
                'mac_prefixes': ['00:1F:EA', '7C:ED:8D', '98:B6:E9']  # Sony, Microsoft
            },
            'pc': {
                'ports': [445, 135, 139, 3389],
                'keywords': ['desktop', 'laptop', 'workstation'],
                'mac_prefixes': []
            },
            'nas': {
                'ports': [445, 139, 548, 2049, 5000],
                'keywords': ['nas', 'synology', 'qnap', 'storage'],
                'mac_prefixes': []
            }
        }

    def scan_network(self) -> Dict:
        """Scannt das Netzwerk und identifiziert Geräte"""
        print(f"🔍 Scanne Netzwerk: {self.network_range}")
        
        # Simulierte Netzwerk-Scan Ergebnisse (in Produktion: nmap oder ähnliches)
        discovered_devices = self._discover_devices()
        
        for ip, device_info in discovered_devices.items():
            device_type = self._identify_device_type(device_info)
            device_info['type'] = device_type
            device_info['metrics'] = self._get_device_metrics(ip, device_type)
            self.devices[ip] = device_info
            
        return self.devices

    def _discover_devices(self) -> Dict:
        """Simuliert Device Discovery (in Produktion: ARP scan + Port scan)"""
        # Simulierte Geräte für Demo
        return {
            '192.168.1.1': {
                'hostname': 'Fritz!Box Router',
                'mac': '00:50:56:C0:00:01',
                'open_ports': [80, 443, 22],
                'vendor': 'AVM'
            },
            '192.168.1.2': {
                'hostname': 'Core Switch',
                'mac': '00:1A:2B:3C:4D:5E',
                'open_ports': [80, 443, 23],
                'vendor': 'Cisco'
            },
            '192.168.1.10': {
                'hostname': 'UniFi AP Pro',
                'mac': '00:27:22:AB:CD:EF',
                'open_ports': [80, 443, 22, 8443],
                'vendor': 'Ubiquiti'
            },
            '192.168.1.11': {
                'hostname': 'UniFi AP Gaming Zone',
                'mac': '00:27:22:AB:CD:F0',
                'open_ports': [80, 443, 22, 8443],
                'vendor': 'Ubiquiti'
            },
            '192.168.1.20': {
                'hostname': 'PlayStation 5',
                'mac': '00:1F:EA:12:34:56',
                'open_ports': [9100, 9103],
                'vendor': 'Sony'
            },
            '192.168.1.21': {
                'hostname': 'Xbox Series X',
                'mac': '7C:ED:8D:AB:CD:EF',
                'open_ports': [3074],
                'vendor': 'Microsoft'
            },
            '192.168.1.50': {
                'hostname': 'Gaming PC Alpha',
                'mac': '98:B6:E9:11:22:33',
                'open_ports': [445, 3389],
                'vendor': 'Intel'
            }
        }

    def _identify_device_type(self, device_info: Dict) -> str:
        """Identifiziert den Gerätetyp basierend auf Fingerprints"""
        hostname = device_info.get('hostname', '').lower()
        mac = device_info.get('mac', '')
        open_ports = device_info.get('open_ports', [])
        
        scores = {}
        
        for dev_type, signature in self.device_signatures.items():
            score = 0
            
            # Check keywords in hostname
            for keyword in signature['keywords']:
                if keyword in hostname:
                    score += 10
                    
            # Check MAC prefix
            for prefix in signature['mac_prefixes']:
                if mac.upper().startswith(prefix.upper()):
                    score += 15
                    
            # Check open ports
            matching_ports = set(open_ports) & set(signature['ports'])
            score += len(matching_ports) * 5
            
            scores[dev_type] = score
        
        # Return type with highest score
        if scores:
            best_match = max(scores.items(), key=lambda x: x[1])
            if best_match[1] > 0:
                return best_match[0]
        
        return 'unknown'

    def _get_device_metrics(self, ip: str, device_type: str) -> Dict:
        """Holt Metriken für verschiedene Gerätetypen"""
        metrics = {
            'status': 'online',
            'response_time': round(2.5 + (hash(ip) % 10) / 10, 2),
            'last_seen': datetime.now().isoformat()
        }
        
        if device_type == 'router':
            metrics.update({
                'uplink_bandwidth_mbps': 10000,  # 10 Gbit/s
                'uplink_usage_mbps': 3847 + (hash(ip) % 1000),
                'uplink_usage_percent': round((3847 + (hash(ip) % 1000)) / 10000 * 100, 1),
                'wan_ip': '203.0.113.42',
                'active_connections': 1247
            })
            
        elif device_type == 'wlan_ap':
            metrics.update({
                'clients_2ghz': 8 + (hash(ip) % 5),
                'clients_5ghz': 15 + (hash(ip) % 10),
                'total_clients': 23 + (hash(ip) % 15),
                'channel_utilization_2ghz': 45 + (hash(ip) % 30),
                'channel_utilization_5ghz': 62 + (hash(ip) % 25),
                'tx_rate_mbps': 850 + (hash(ip) % 500),
                'rx_rate_mbps': 720 + (hash(ip) % 400)
            })
            
        elif device_type == 'gaming_console':
            metrics.update({
                'download_mbps': 450 + (hash(ip) % 200),
                'upload_mbps': 95 + (hash(ip) % 50),
                'latency_ms': 8 + (hash(ip) % 5),
                'packet_loss': 0.0,
                'gaming_status': 'active' if hash(ip) % 2 == 0 else 'idle'
            })
            
        return metrics

    def export_to_json(self, filename: str = 'network_data.json'):
        """Exportiert die Scan-Ergebnisse als JSON"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'network_range': self.network_range,
            'total_devices': len(self.devices),
            'devices': self.devices,
            'summary': self._generate_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        return filename

    def _generate_summary(self) -> Dict:
        """Generiert eine Zusammenfassung der Scan-Ergebnisse"""
        summary = {
            'by_type': {},
            'total_wlan_clients': 0,
            'total_uplink_usage_mbps': 0
        }
        
        for device in self.devices.values():
            dev_type = device['type']
            summary['by_type'][dev_type] = summary['by_type'].get(dev_type, 0) + 1
            
            metrics = device.get('metrics', {})
            if 'total_clients' in metrics:
                summary['total_wlan_clients'] += metrics['total_clients']
            if 'uplink_usage_mbps' in metrics:
                summary['total_uplink_usage_mbps'] = metrics['uplink_usage_mbps']
                
        return summary

def main():
    scanner = NetworkScanner("192.168.1.0/24")
    
    print("=" * 60)
    print("🎮 EPIC GAMING DAY NETWORK SCANNER")
    print("=" * 60)
    
    devices = scanner.scan_network()
    
    print(f"\n✅ {len(devices)} Geräte gefunden!\n")
    
    for ip, device in devices.items():
        icon = {
            'router': '🌐',
            'switch': '🔀',
            'wlan_ap': '📡',
            'gaming_console': '🎮',
            'pc': '💻',
            'nas': '💾',
            'unknown': '❓'
        }.get(device['type'], '❓')
        
        print(f"{icon} {device['type'].upper():15} | {ip:15} | {device['hostname']}")
    
    # Export data
    filename = scanner.export_to_json()
    print(f"\n💾 Daten exportiert nach: {filename}")
    
    return scanner

if __name__ == "__main__":
    main()
