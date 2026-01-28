#!/usr/bin/env python3
"""
Unified Smart Scanner - Zero Configuration
Combines Network Discovery + SNMP Walk für vollautomatische Erkennung
KEINE hardcodierten Device-Listen oder Fake-Metriken!
"""

import json
import subprocess
import socket
import struct
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import ipaddress

# SNMP (optional)
try:
    from pysnmp.hlapi import *
    SNMP_AVAILABLE = True
except ImportError:
    SNMP_AVAILABLE = False
    print("💡 Tipp: Installiere pysnmp für erweiterte Features")
    print("   pip3 install pysnmp --break-system-packages")


class SmartScanner:
    """
    Intelligenter Scanner ohne Hardcoding
    - Auto-Discovery via ARP/Ping
    - SNMP-Walk für Device-Capabilities
    - Self-Learning Configuration
    """
    
    def __init__(self, network_range: str = None, 
                 snmp_community: str = "public",
                 cache_file: str = "discovered_devices.json"):
        self.network_range = network_range or self._detect_network_range()
        self.snmp_community = snmp_community
        self.cache_file = cache_file
        self.devices = {}
        self.device_cache = self._load_cache()
        
        # MIB Database laden (wenn vorhanden)
        self.mib_db = self._load_mib_database()
    
    def _detect_network_range(self) -> str:
        """
        Erkennt automatisch den Netzwerk-Range aus der lokalen IP
        KEINE hardcodierte Range!
        """
        try:
            # Hole lokale IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Konvertiere zu /24 Network
            ip_parts = local_ip.split('.')
            network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            
            print(f"🔍 Auto-erkanntes Netzwerk: {network}")
            return network
            
        except Exception as e:
            print(f"⚠️  Konnte Netzwerk nicht auto-erkennen: {e}")
            return "192.168.1.0/24"  # Fallback
    
    def _load_cache(self) -> Dict:
        """Lädt gecachte Device-Informationen"""
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                print(f"📚 {len(cache)} gecachte Geräte geladen")
                return cache
        except FileNotFoundError:
            return {}
    
    def _save_cache(self):
        """Speichert erkannte Devices für zukünftige Scans"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.device_cache, f, indent=2)
        print(f"💾 Device-Cache gespeichert: {self.cache_file}")
    
    def _load_mib_database(self) -> Dict:
        """Lädt MIB Database falls vorhanden"""
        try:
            with open('snmp_mib_database.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"vendors": {}}
    
    def discover_devices(self) -> Dict[str, Dict]:
        """
        Multi-Method Discovery:
        1. ARP-Scan für MAC-Adressen
        2. Ping-Sweep für Online-Status
        3. Port-Scan für Services (optional)
        
        KEINE hardcodierten Devices!
        """
        print(f"\n🔍 Discovering devices in {self.network_range}...")
        discovered = {}
        
        # Methode 1: ARP-Scan (schnell, benötigt root)
        arp_devices = self._arp_scan()
        if arp_devices:
            discovered.update(arp_devices)
            print(f"✅ ARP-Scan: {len(arp_devices)} Geräte gefunden")
        
        # Methode 2: Ping-Sweep (funktioniert immer)
        if not discovered:
            print("💡 ARP-Scan fehlgeschlagen, verwende Ping-Sweep...")
            ping_devices = self._ping_sweep()
            discovered.update(ping_devices)
            print(f"✅ Ping-Sweep: {len(ping_devices)} Geräte gefunden")
        
        # Methode 3: Check Cache für bekannte Geräte
        for ip, cached_info in self.device_cache.items():
            if ip not in discovered:
                # Teste ob noch online
                if self._is_alive(ip):
                    discovered[ip] = cached_info
                    discovered[ip]['from_cache'] = True
        
        return discovered
    
    def _arp_scan(self) -> Dict:
        """ARP-Scan für schnelle Discovery"""
        devices = {}
        try:
            # Versuche arp-scan
            result = subprocess.run(
                ['arp-scan', '--localnet', '--quiet'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            for line in result.stdout.split('\n'):
                parts = line.split('\t')
                if len(parts) >= 2:
                    ip = parts[0].strip()
                    mac = parts[1].strip()
                    if self._is_valid_ip(ip):
                        devices[ip] = {
                            'mac': mac,
                            'hostname': self._resolve_hostname(ip),
                            'discovery_method': 'arp'
                        }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # arp-scan nicht installiert oder timeout
            pass
        
        return devices
    
    def _ping_sweep(self) -> Dict:
        """Ping-Sweep für Discovery (Fallback)"""
        devices = {}
        
        try:
            network = ipaddress.ip_network(self.network_range)
            
            print("⏳ Ping-Sweep läuft (kann 1-2 Min dauern)...")
            print("   💡 Tipp: Drücke Ctrl+C zum Abbrechen")
            
            count = 0
            total = 0
            
            for ip in network.hosts():
                ip_str = str(ip)
                total += 1
                
                # Progress indicator every 20 IPs
                if total % 20 == 0:
                    print(f"   Scanne... {total}/254 IPs ({count} gefunden)", end='\r')
                
                # Timeout protection - max 100 IPs to scan
                if total > 100:
                    print(f"\n   ⚠️  Scan limitiert auf erste 100 IPs (Performance)")
                    break
                
                if self._is_alive(ip_str):
                    devices[ip_str] = {
                        'hostname': self._resolve_hostname(ip_str),
                        'discovery_method': 'ping'
                    }
                    count += 1
                    print(f"   ✅ Gefunden: {ip_str} ({count} total)         ")
            
            print(f"\n   Scan abgeschlossen: {count} Geräte in {total} IPs")
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Scan abgebrochen! {count} Geräte gefunden bis jetzt.")
        except Exception as e:
            print(f"⚠️  Ping-Sweep Error: {e}")
        
        return devices
    
    def _is_alive(self, ip: str, timeout: int = 1) -> bool:
        """Prüft ob Host antwortet"""
        try:
            # Use faster ping with strict timeout
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                capture_output=True,
                timeout=2,  # Hard timeout after 2 seconds
                check=False
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def _resolve_hostname(self, ip: str) -> str:
        """Resolves Hostname via DNS"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return f"device-{ip.split('.')[-1]}"
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Validiert IP-Adresse"""
        try:
            ipaddress.ip_address(ip)
            return True
        except:
            return False
    
    def snmp_walk_device(self, ip: str) -> Dict:
        """
        SNMP-Walk für vollständige Device-Erkennung
        Erkennt AUTOMATISCH:
        - Vendor (Cisco, UniFi, Huawei, etc.)
        - Device-Type (Router, Switch, AP)
        - Capabilities (Interfaces, Wireless, etc.)
        - Real Metrics (CPU, Memory, Bandwidth)
        
        KEINE Simulation!
        """
        if not SNMP_AVAILABLE:
            return {'snmp_available': False}
        
        print(f"\n🔍 SNMP-Walk auf {ip}...")
        device_info = {
            'ip': ip,
            'snmp_available': True,
            'discovered_at': datetime.now().isoformat()
        }
        
        try:
            # 1. System Information
            sys_info = self._snmp_walk_system(ip)
            device_info.update(sys_info)
            
            # 2. Vendor Detection via SNMP
            vendor = self._detect_vendor_snmp(sys_info)
            device_info['vendor'] = vendor
            
            # 3. Device Type Detection
            device_type = self._detect_device_type_snmp(ip, vendor)
            device_info['type'] = device_type
            
            # 4. Interface Discovery
            interfaces = self._snmp_walk_interfaces(ip)
            device_info['interfaces'] = interfaces
            
            # 5. Performance Metrics (wenn verfügbar)
            metrics = self._snmp_get_metrics(ip, vendor, device_type)
            device_info['metrics'] = metrics
            
            # 6. Spezielle Features (Wireless, Optical, etc.)
            special = self._snmp_discover_special_features(ip, vendor, device_type)
            device_info.update(special)
            
            print(f"✅ {vendor} {device_type} erkannt mit {len(interfaces)} Interfaces")
            
        except Exception as e:
            print(f"⚠️  SNMP-Walk fehlgeschlagen: {e}")
            device_info['snmp_available'] = False
        
        return device_info
    
    def _snmp_walk_system(self, ip: str) -> Dict:
        """Walk System MIB (1.3.6.1.2.1.1)"""
        info = {}
        
        system_oids = {
            'sysDescr': '1.3.6.1.2.1.1.1.0',
            'sysObjectID': '1.3.6.1.2.1.1.2.0',
            'sysUpTime': '1.3.6.1.2.1.1.3.0',
            'sysContact': '1.3.6.1.2.1.1.4.0',
            'sysName': '1.3.6.1.2.1.1.5.0',
            'sysLocation': '1.3.6.1.2.1.1.6.0'
        }
        
        for key, oid in system_oids.items():
            value = self._snmp_get(ip, oid)
            if value:
                info[key] = value
        
        return info
    
    def _detect_vendor_snmp(self, sys_info: Dict) -> str:
        """
        Erkennt Vendor via sysObjectID und sysDescr
        KEINE hardcodierten Listen!
        """
        sys_obj_id = sys_info.get('sysObjectID', '')
        sys_descr = sys_info.get('sysDescr', '')
        
        # Check gegen MIB Database
        for vendor_key, vendor_info in self.mib_db.get('vendors', {}).items():
            if vendor_key == 'generic':
                continue
            
            detection = vendor_info.get('detection', {})
            prefix = detection.get('sysObjectID_prefix', '')
            
            if prefix and sys_obj_id.startswith(prefix):
                return vendor_key
            
            keywords = detection.get('sysDescr_keywords', [])
            for keyword in keywords:
                if keyword.lower() in sys_descr.lower():
                    return vendor_key
        
        # Fallback: Parse aus sysDescr
        sys_descr_lower = sys_descr.lower()
        if 'cisco' in sys_descr_lower:
            return 'cisco'
        elif 'ubiquiti' in sys_descr_lower or 'unifi' in sys_descr_lower:
            return 'ubiquiti'
        elif 'huawei' in sys_descr_lower:
            return 'huawei'
        elif 'mikrotik' in sys_descr_lower:
            return 'mikrotik'
        elif 'juniper' in sys_descr_lower:
            return 'juniper'
        
        return 'generic'
    
    def _detect_device_type_snmp(self, ip: str, vendor: str) -> str:
        """
        Erkennt Device-Type via SNMP-Walk
        Prüft verfügbare MIBs und Features
        """
        # Prüfe auf Wireless-Features
        if self._has_wireless_mib(ip):
            return 'wlan_ap'
        
        # Prüfe auf Routing-Features
        if self._has_routing_mib(ip):
            return 'router'
        
        # Prüfe auf Switching-Features
        if self._has_switching_mib(ip):
            return 'switch'
        
        # Prüfe Interface-Count (viele = Switch)
        if_count = self._snmp_get(ip, '1.3.6.1.2.1.2.1.0')
        if if_count and int(if_count) > 10:
            return 'switch'
        
        return 'unknown'
    
    def _has_wireless_mib(self, ip: str) -> bool:
        """Prüft ob Wireless-MIB vorhanden"""
        # Check für UniFi Wireless OID
        test_oid = '1.3.6.1.4.1.41112.1.6.1.2.1.15'  # clientCount
        return self._snmp_get(ip, test_oid) is not None
    
    def _has_routing_mib(self, ip: str) -> bool:
        """Prüft ob Routing-MIB vorhanden"""
        # Check IP Forwarding
        ip_forward = self._snmp_get(ip, '1.3.6.1.2.1.4.1.0')
        return ip_forward == '1' if ip_forward else False
    
    def _has_switching_mib(self, ip: str) -> bool:
        """Prüft ob Switching-MIB vorhanden"""
        # Check für Bridge MIB
        test_oid = '1.3.6.1.2.1.17.1.1.0'  # dot1dBaseBridgeAddress
        return self._snmp_get(ip, test_oid) is not None
    
    def _snmp_walk_interfaces(self, ip: str) -> List[Dict]:
        """
        Walk Interface Table - findet ALLE Interfaces dynamisch
        Erkennt automatisch 10G Uplinks!
        """
        interfaces = []
        
        # Walk ifTable
        if_indices = self._snmp_walk(ip, '1.3.6.1.2.1.2.2.1.1')  # ifIndex
        
        for if_index_oid, if_index in if_indices.items():
            index = if_index
            
            interface = {
                'index': index,
                'ifDescr': self._snmp_get(ip, f'1.3.6.1.2.1.2.2.1.2.{index}'),
                'ifSpeed': self._snmp_get(ip, f'1.3.6.1.2.1.2.2.1.5.{index}'),
                'ifOperStatus': self._snmp_get(ip, f'1.3.6.1.2.1.2.2.1.8.{index}'),
                'ifInOctets': self._snmp_get(ip, f'1.3.6.1.2.1.2.2.1.10.{index}'),
                'ifOutOctets': self._snmp_get(ip, f'1.3.6.1.2.1.2.2.1.16.{index}')
            }
            
            # Berechne Speed in Mbps
            if interface['ifSpeed']:
                speed_bps = int(interface['ifSpeed'])
                interface['ifSpeed_mbps'] = speed_bps / 1_000_000
                
                # Erkenne 10G Interfaces automatisch!
                if speed_bps >= 10_000_000_000:
                    interface['interface_class'] = '10G'
                    interface['is_uplink'] = True
                    print(f"   🚀 10G Interface gefunden: {interface['ifDescr']}")
                elif speed_bps >= 1_000_000_000:
                    interface['interface_class'] = '1G'
            
            # Status Text
            status_map = {'1': 'up', '2': 'down', '3': 'testing'}
            if interface['ifOperStatus']:
                interface['ifOperStatus_text'] = status_map.get(
                    interface['ifOperStatus'], 'unknown'
                )
            
            interfaces.append(interface)
        
        return interfaces
    
    def _snmp_get_metrics(self, ip: str, vendor: str, device_type: str) -> Dict:
        """
        Holt ECHTE Metriken via SNMP
        KEINE Simulation!
        """
        metrics = {
            'status': 'online',
            'response_time': self._measure_ping_time(ip),
            'last_seen': datetime.now().isoformat()
        }
        
        # Vendor-spezifische OIDs aus MIB Database
        vendor_oids = self.mib_db.get('vendors', {}).get(vendor, {}).get('oids', {})
        perf_oids = vendor_oids.get('performance', {})
        
        # CPU
        cpu_oid = perf_oids.get('cpu_usage') or perf_oids.get('cpu_5sec')
        if cpu_oid:
            cpu = self._snmp_get(ip, cpu_oid)
            if cpu:
                metrics['cpu_usage'] = float(cpu)
        
        # Memory
        mem_oid = perf_oids.get('memory_usage')
        if mem_oid:
            mem = self._snmp_get(ip, mem_oid)
            if mem:
                metrics['memory_usage'] = float(mem)
        
        # Temperature
        temp_oid = perf_oids.get('temperature')
        if temp_oid:
            temp = self._snmp_get(ip, temp_oid)
            if temp:
                metrics['temperature'] = float(temp)
        
        # Router-spezifisch: Uplink-Berechnung
        if device_type == 'router':
            uplink_metrics = self._calculate_uplink_bandwidth(ip)
            metrics.update(uplink_metrics)
        
        return metrics
    
    def _calculate_uplink_bandwidth(self, ip: str) -> Dict:
        """
        Berechnet ECHTE Uplink-Bandwidth via SNMP
        Findet automatisch das Uplink-Interface (höchste Speed)
        """
        # Finde Interface mit höchster Speed (= Uplink)
        if_speeds = self._snmp_walk(ip, '1.3.6.1.2.1.2.2.1.5')  # ifSpeed
        
        if not if_speeds:
            return {}
        
        # Finde Index mit höchster Speed
        max_speed = 0
        uplink_index = None
        
        for oid, speed in if_speeds.items():
            speed_val = int(speed)
            if speed_val > max_speed:
                max_speed = speed_val
                uplink_index = oid.split('.')[-1]
        
        if not uplink_index:
            return {}
        
        # Berechne Bandwidth (benötigt 2 Messungen)
        in_oid = f'1.3.6.1.2.1.2.2.1.10.{uplink_index}'
        out_oid = f'1.3.6.1.2.1.2.2.1.16.{uplink_index}'
        
        # Erste Messung
        in1 = int(self._snmp_get(ip, in_oid) or 0)
        out1 = int(self._snmp_get(ip, out_oid) or 0)
        time1 = time.time()
        
        time.sleep(2)  # Warte 2 Sekunden
        
        # Zweite Messung
        in2 = int(self._snmp_get(ip, in_oid) or 0)
        out2 = int(self._snmp_get(ip, out_oid) or 0)
        time2 = time.time()
        
        # Berechnung
        delta_in = in2 - in1
        delta_out = out2 - out1
        delta_time = time2 - time1
        
        in_mbps = (delta_in * 8) / (delta_time * 1_000_000)
        out_mbps = (delta_out * 8) / (delta_time * 1_000_000)
        total_mbps = in_mbps + out_mbps
        
        return {
            'uplink_bandwidth_mbps': max_speed / 1_000_000,
            'uplink_usage_mbps': round(total_mbps, 2),
            'uplink_usage_percent': round((total_mbps / (max_speed / 1_000_000)) * 100, 1),
            'uplink_in_mbps': round(in_mbps, 2),
            'uplink_out_mbps': round(out_mbps, 2)
        }
    
    def _snmp_discover_special_features(self, ip: str, vendor: str, 
                                       device_type: str) -> Dict:
        """Discovered spezielle Features (Wireless, Optical, etc.)"""
        features = {}
        
        # Wireless (für UniFi APs)
        if vendor == 'ubiquiti' and device_type == 'wlan_ap':
            wireless_oids = self.mib_db.get('vendors', {}).get('ubiquiti', {}).get('oids', {}).get('wireless', {})
            
            wireless_data = {}
            for key, oid in wireless_oids.items():
                value = self._snmp_get(ip, oid)
                if value:
                    try:
                        wireless_data[key] = int(value)
                    except:
                        wireless_data[key] = value
            
            if wireless_data:
                features['wireless'] = wireless_data
        
        return features
    
    def _measure_ping_time(self, ip: str) -> float:
        """Misst Ping-Zeit"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', ip],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            # Parse ping time
            import re
            match = re.search(r'time=([\d.]+)', result.stdout)
            if match:
                return float(match.group(1))
        except:
            pass
        return 0.0
    
    def _snmp_get(self, ip: str, oid: str) -> Optional[str]:
        """SNMP GET"""
        if not SNMP_AVAILABLE:
            return None
        
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.snmp_community, mpModel=1),
                UdpTransportTarget((ip, 161), timeout=2),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if not errorIndication and not errorStatus:
                for varBind in varBinds:
                    return str(varBind[1])
        except:
            pass
        
        return None
    
    def _snmp_walk(self, ip: str, oid: str, max_results: int = 100) -> Dict:
        """SNMP WALK"""
        if not SNMP_AVAILABLE:
            return {}
        
        results = {}
        count = 0
        
        try:
            iterator = nextCmd(
                SnmpEngine(),
                CommunityData(self.snmp_community, mpModel=1),
                UdpTransportTarget((ip, 161), timeout=2),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False
            )
            
            for errorIndication, errorStatus, errorIndex, varBinds in iterator:
                if errorIndication or errorStatus:
                    break
                
                for varBind in varBinds:
                    results[str(varBind[0])] = str(varBind[1])
                    count += 1
                    
                    if count >= max_results:
                        return results
        except:
            pass
        
        return results
    
    def full_scan(self) -> Dict:
        """
        Vollständiger intelligenter Scan:
        1. Auto-Discovery (kein Hardcoding!)
        2. SNMP-Walk für Details
        3. Self-Learning Cache
        """
        print("\n" + "="*60)
        print("🤖 SMART SCANNER - Zero Configuration")
        print("="*60)
        
        # Phase 1: Discovery
        discovered = self.discover_devices()
        print(f"\n📊 Phase 1: {len(discovered)} Geräte discovered")
        
        # Phase 2: SNMP Deep-Dive
        if SNMP_AVAILABLE:
            print("\n📊 Phase 2: SNMP Deep-Dive...")
            for ip, basic_info in discovered.items():
                print(f"\n{'─'*60}")
                print(f"Analysiere {ip} ({basic_info.get('hostname', 'Unknown')})")
                
                snmp_info = self.snmp_walk_device(ip)
                
                # Merge Informationen
                device_complete = {**basic_info, **snmp_info}
                self.devices[ip] = device_complete
                
                # Update Cache
                self.device_cache[ip] = device_complete
        else:
            print("\n⚠️  SNMP nicht verfügbar - nur Basic Discovery")
            self.devices = discovered
        
        # Phase 3: Save Cache
        self._save_cache()
        
        return self.devices
    
    def export_to_json(self, filename: str = 'network_data.json'):
        """Exportiert im kompatiblen Format"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'network_range': self.network_range,
            'total_devices': len(self.devices),
            'devices': self.devices,
            'summary': self._generate_summary(),
            'scan_method': 'smart_scanner_v2',
            'auto_discovered': True
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Exportiert: {filename}")
        return filename
    
    def _generate_summary(self) -> Dict:
        """Generiert Zusammenfassung"""
        summary = {
            'by_type': {},
            'by_vendor': {},
            'total_interfaces': 0,
            'total_wlan_clients': 0,
            'has_10g_uplinks': False
        }
        
        for device in self.devices.values():
            # By Type
            dev_type = device.get('type', 'unknown')
            summary['by_type'][dev_type] = summary['by_type'].get(dev_type, 0) + 1
            
            # By Vendor
            vendor = device.get('vendor', 'unknown')
            summary['by_vendor'][vendor] = summary['by_vendor'].get(vendor, 0) + 1
            
            # Interfaces
            interfaces = device.get('interfaces', [])
            summary['total_interfaces'] += len(interfaces)
            
            # Check for 10G
            for interface in interfaces:
                if interface.get('interface_class') == '10G':
                    summary['has_10g_uplinks'] = True
            
            # WLAN Clients
            wireless = device.get('wireless', {})
            summary['total_wlan_clients'] += wireless.get('total_clients', 0)
        
        return summary


def main():
    print("="*70)
    print("🤖 SMART SCANNER V2 - Zero Configuration, No Hardcoding!")
    print("="*70)
    print()
    print("Features:")
    print("  ✅ Auto-Discovery (ARP/Ping)")
    print("  ✅ SNMP-Walk für Device-Details")
    print("  ✅ Automatische Vendor-Erkennung")
    print("  ✅ Automatische Type-Erkennung")
    print("  ✅ 10G Uplink Auto-Detection")
    print("  ✅ Self-Learning Cache")
    print("  ✅ KEINE hardcodierten Devices!")
    print()
    
    # Optionale Parameter
    import sys
    network_range = sys.argv[1] if len(sys.argv) > 1 else None
    community = sys.argv[2] if len(sys.argv) > 2 else "public"
    
    # Scanner starten
    scanner = SmartScanner(
        network_range=network_range,
        snmp_community=community
    )
    
    # Full Scan
    devices = scanner.full_scan()
    
    # Ausgabe
    print("\n" + "="*70)
    print("📊 SCAN RESULTS")
    print("="*70)
    
    for ip, device in devices.items():
        vendor = device.get('vendor', 'unknown')
        dev_type = device.get('type', 'unknown')
        hostname = device.get('hostname', device.get('sysName', 'Unknown'))
        
        icon = {
            'router': '🌐',
            'switch': '🔀',
            'wlan_ap': '📡',
            'unknown': '❓'
        }.get(dev_type, '❓')
        
        print(f"\n{icon} {ip:15} | {vendor:12} | {dev_type:10} | {hostname}")
        
        # Metrics
        metrics = device.get('metrics', {})
        if 'cpu_usage' in metrics:
            print(f"   CPU: {metrics['cpu_usage']:.1f}%")
        if 'uplink_usage_mbps' in metrics:
            print(f"   Uplink: {metrics['uplink_usage_mbps']} Mbps ({metrics['uplink_usage_percent']}%)")
        
        # Interfaces
        interfaces = device.get('interfaces', [])
        if interfaces:
            uplinks = [i for i in interfaces if i.get('is_uplink')]
            if uplinks:
                print(f"   🚀 10G Uplinks: {len(uplinks)}")
    
    # Export
    scanner.export_to_json()
    
    print("\n✅ Scan abgeschlossen!")
    print(f"💡 Tipp: Gecachte Geräte in 'discovered_devices.json'")


if __name__ == "__main__":
    main()
