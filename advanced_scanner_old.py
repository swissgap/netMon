#!/usr/bin/env python3
"""
Advanced Network Scanner with SNMP Support
Für echtes Production-Monitoring mit SNMP, SSH, APIs
"""

import subprocess
import json
import socket
import time
from datetime import datetime
from typing import Dict, List, Optional
import re

class AdvancedNetworkScanner:
    """
    Erweiterte Version mit echten Monitoring-Capabilities
    Unterstützt: SNMP, UniFi Controller API, Router APIs
    """
    
    def __init__(self, config_file: str = "monitor_config.json"):
        self.config = self._load_config(config_file)
        self.devices = {}
        
    def _load_config(self, config_file: str) -> Dict:
        """Lädt Konfiguration aus JSON-File"""
        default_config = {
            "network_range": "192.168.1.0/24",
            "snmp": {
                "enabled": False,
                "community": "public",
                "version": "2c"
            },
            "unifi": {
                "enabled": False,
                "controller_url": "https://unifi:8443",
                "username": "",
                "password": "",
                "site": "default"
            },
            "known_devices": {
                "192.168.1.1": {
                    "type": "router",
                    "hostname": "Main Router",
                    "snmp_oid_bandwidth": "1.3.6.1.2.1.2.2.1.10.1"
                },
                "192.168.1.10": {
                    "type": "wlan_ap",
                    "hostname": "UniFi AP",
                    "unifi_managed": True
                }
            }
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            # Erstelle default config
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def get_snmp_data(self, host: str, oid: str) -> Optional[str]:
        """
        Holt SNMP-Daten von einem Gerät
        Benötigt: pip install pysnmp
        """
        if not self.config['snmp']['enabled']:
            return None
            
        try:
            from pysnmp.hlapi import *
            
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.config['snmp']['community']),
                UdpTransportTarget((host, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if errorIndication or errorStatus:
                return None
            
            for varBind in varBinds:
                return str(varBind[1])
                
        except ImportError:
            print("⚠️  pysnmp nicht installiert. Installiere mit: pip install pysnmp")
            return None
        except Exception as e:
            print(f"SNMP Error für {host}: {e}")
            return None
    
    def get_unifi_data(self) -> Dict:
        """
        Holt Daten vom UniFi Controller
        Benötigt: pip install requests
        """
        if not self.config['unifi']['enabled']:
            return {}
        
        try:
            import requests
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            
            base_url = self.config['unifi']['controller_url']
            session = requests.Session()
            
            # Login
            login_data = {
                'username': self.config['unifi']['username'],
                'password': self.config['unifi']['password']
            }
            session.post(f"{base_url}/api/login", json=login_data, verify=False)
            
            # Hole AP-Daten
            site = self.config['unifi']['site']
            response = session.get(f"{base_url}/api/s/{site}/stat/device", verify=False)
            
            if response.status_code == 200:
                devices = response.json()['data']
                
                unifi_data = {}
                for device in devices:
                    if device['type'] == 'uap':  # UniFi Access Point
                        unifi_data[device['ip']] = {
                            'hostname': device.get('name', 'UniFi AP'),
                            'model': device.get('model', 'Unknown'),
                            'clients_2ghz': device.get('num_sta', {}).get('ng', 0),
                            'clients_5ghz': device.get('num_sta', {}).get('na', 0),
                            'total_clients': device.get('num_sta', 0),
                            'uptime': device.get('uptime', 0),
                            'tx_bytes': device.get('tx_bytes', 0),
                            'rx_bytes': device.get('rx_bytes', 0)
                        }
                
                return unifi_data
                
        except ImportError:
            print("⚠️  requests nicht installiert. Installiere mit: pip install requests")
            return {}
        except Exception as e:
            print(f"UniFi API Error: {e}")
            return {}
    
    def scan_with_nmap(self) -> Dict:
        """
        Verwendet nmap für echtes Netzwerk-Scanning
        Benötigt: sudo apt install nmap
        """
        try:
            # Teste ob nmap verfügbar ist
            result = subprocess.run(['nmap', '--version'], 
                                  capture_output=True, 
                                  timeout=5)
            
            if result.returncode != 0:
                raise FileNotFoundError
                
            print("🔍 Führe nmap-Scan durch...")
            
            # Quick Ping Scan
            scan_result = subprocess.run(
                ['nmap', '-sn', '-oG', '-', self.config['network_range']],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            devices = {}
            for line in scan_result.stdout.split('\n'):
                if 'Host:' in line and 'Status: Up' in line:
                    parts = line.split()
                    ip = parts[1]
                    
                    # Versuche Hostname zu resolven
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        hostname = f"Host-{ip.split('.')[-1]}"
                    
                    devices[ip] = {
                        'hostname': hostname,
                        'status': 'online'
                    }
            
            return devices
            
        except FileNotFoundError:
            print("⚠️  nmap nicht gefunden. Verwende Fallback-Methode...")
            return self._fallback_discovery()
        except Exception as e:
            print(f"Nmap Scan Error: {e}")
            return self._fallback_discovery()
    
    def _fallback_discovery(self) -> Dict:
        """Fallback: Nutze bekannte Geräte aus Config"""
        devices = {}
        
        for ip, info in self.config['known_devices'].items():
            # Teste ob Gerät online ist (Ping)
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', ip],
                    capture_output=True,
                    timeout=2
                )
                
                if result.returncode == 0:
                    devices[ip] = {
                        'hostname': info['hostname'],
                        'type': info['type'],
                        'status': 'online'
                    }
            except:
                pass
        
        return devices
    
    def collect_metrics(self) -> Dict:
        """Sammelt alle Metriken von allen Quellen"""
        print("=" * 60)
        print("🎮 ADVANCED NETWORK SCANNER - Production Mode")
        print("=" * 60)
        
        # 1. Discover Devices
        discovered = self.scan_with_nmap()
        print(f"✅ {len(discovered)} Geräte gefunden")
        
        # 2. UniFi Data
        unifi_data = self.get_unifi_data()
        if unifi_data:
            print(f"📡 {len(unifi_data)} UniFi APs abgefragt")
        
        # 3. SNMP Data
        for ip, device in discovered.items():
            # Merge mit known devices
            if ip in self.config['known_devices']:
                device.update(self.config['known_devices'][ip])
            
            # UniFi Data mergen
            if ip in unifi_data:
                device['metrics'] = unifi_data[ip]
                device['type'] = 'wlan_ap'
            
            # SNMP Data holen (z.B. für Router)
            if device.get('type') == 'router' and 'snmp_oid_bandwidth' in device:
                bandwidth = self.get_snmp_data(ip, device['snmp_oid_bandwidth'])
                if bandwidth:
                    device['metrics'] = device.get('metrics', {})
                    device['metrics']['bandwidth_bytes'] = int(bandwidth)
            
            self.devices[ip] = device
        
        return self.devices
    
    def export_to_json(self, filename: str = 'network_data.json'):
        """Exportiert Daten im gleichen Format wie der Basic Scanner"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'network_range': self.config['network_range'],
            'total_devices': len(self.devices),
            'devices': self.devices,
            'summary': self._generate_summary()
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Daten exportiert nach: {filename}")
        return filename
    
    def _generate_summary(self) -> Dict:
        """Generiert Zusammenfassung"""
        summary = {
            'by_type': {},
            'total_wlan_clients': 0,
            'online_devices': 0
        }
        
        for device in self.devices.values():
            dev_type = device.get('type', 'unknown')
            summary['by_type'][dev_type] = summary['by_type'].get(dev_type, 0) + 1
            
            if device.get('status') == 'online':
                summary['online_devices'] += 1
            
            metrics = device.get('metrics', {})
            if 'total_clients' in metrics:
                summary['total_wlan_clients'] += metrics['total_clients']
        
        return summary


def main():
    print("Verwende erweiterten Scanner mit SNMP/API Support")
    print("Konfiguration: monitor_config.json")
    print()
    
    scanner = AdvancedNetworkScanner()
    devices = scanner.collect_metrics()
    scanner.export_to_json()
    
    print(f"\n🎯 Monitoring abgeschlossen!")
    print(f"   Geräte: {len(devices)}")
    print(f"   Öffne gaming_dashboard.html im Browser")

if __name__ == "__main__":
    main()
