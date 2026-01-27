#!/usr/bin/env python3
"""
Enhanced SNMP Scanner with Walk Function and MIB Database
Supports: Cisco, UniFi, Huawei with vendor-specific OIDs
"""

import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

try:
    from pysnmp.hlapi import *
    SNMP_AVAILABLE = True
except ImportError:
    SNMP_AVAILABLE = False
    print("⚠️  pysnmp nicht installiert. Installiere mit:")
    print("    pip3 install pysnmp --break-system-packages")


class SNMPScanner:
    """Enhanced SNMP Scanner with MIB database and walk functionality"""
    
    def __init__(self, mib_database_path: str = "snmp_mib_database.json"):
        self.mib_db = self._load_mib_database(mib_database_path)
        self.results = {}
        
    def _load_mib_database(self, path: str) -> Dict:
        """Load the MIB database"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  MIB Database nicht gefunden: {path}")
            return {"vendors": {}, "common_queries": {}}
    
    def snmp_get(self, host: str, oid: str, community: str = "public", 
                 port: int = 161, timeout: int = 5) -> Optional[str]:
        """
        Einzelner SNMP GET Request
        
        Args:
            host: Target IP/Hostname
            oid: SNMP OID (z.B. "1.3.6.1.2.1.1.1.0")
            community: SNMP Community String
            port: SNMP Port (default: 161)
            timeout: Timeout in Sekunden
            
        Returns:
            Value als String oder None bei Fehler
        """
        if not SNMP_AVAILABLE:
            return None
            
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=1),  # SNMPv2c
                UdpTransportTarget((host, port), timeout=timeout),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if errorIndication:
                print(f"❌ SNMP Error: {errorIndication}")
                return None
            elif errorStatus:
                print(f"❌ SNMP Error: {errorStatus.prettyPrint()}")
                return None
            else:
                for varBind in varBinds:
                    return str(varBind[1])
                    
        except Exception as e:
            print(f"❌ Exception bei SNMP GET {host}:{oid} - {e}")
            return None
    
    def snmp_walk(self, host: str, oid: str, community: str = "public",
                  port: int = 161, timeout: int = 5, 
                  max_results: int = 100) -> Dict[str, str]:
        """
        SNMP WALK - Traversiert einen OID-Baum
        
        Args:
            host: Target IP/Hostname
            oid: Start-OID für Walk
            community: SNMP Community String
            max_results: Maximale Anzahl Results (Schutz vor zu vielen Ergebnissen)
            
        Returns:
            Dictionary mit {oid: value}
        """
        if not SNMP_AVAILABLE:
            return {}
        
        results = {}
        count = 0
        
        try:
            print(f"🔍 SNMP Walk auf {host} - OID: {oid}")
            
            iterator = nextCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=1),
                UdpTransportTarget((host, port), timeout=timeout),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False  # Stop at end of subtree
            )
            
            for errorIndication, errorStatus, errorIndex, varBinds in iterator:
                if errorIndication:
                    print(f"❌ Walk Error: {errorIndication}")
                    break
                elif errorStatus:
                    print(f"❌ Walk Error: {errorStatus.prettyPrint()}")
                    break
                else:
                    for varBind in varBinds:
                        oid_str = str(varBind[0])
                        value = str(varBind[1])
                        results[oid_str] = value
                        count += 1
                        
                        if count >= max_results:
                            print(f"⚠️  Max results ({max_results}) erreicht, stoppe Walk")
                            return results
            
            print(f"✅ Walk abgeschlossen: {count} OIDs gefunden")
            return results
            
        except Exception as e:
            print(f"❌ Exception bei SNMP Walk: {e}")
            return results
    
    def detect_vendor(self, host: str, community: str = "public") -> Optional[str]:
        """
        Erkennt den Hersteller anhand von sysObjectID und sysDescr
        
        Returns:
            Vendor name (cisco, ubiquiti, huawei) oder None
        """
        print(f"🔎 Erkenne Vendor für {host}...")
        
        # Hole sysObjectID und sysDescr
        sys_object_id = self.snmp_get(host, "1.3.6.1.2.1.1.2.0", community)
        sys_descr = self.snmp_get(host, "1.3.6.1.2.1.1.1.0", community)
        
        if not sys_object_id and not sys_descr:
            print(f"⚠️  Keine SNMP-Antwort von {host}")
            return None
        
        # Check gegen MIB Database
        for vendor_key, vendor_info in self.mib_db['vendors'].items():
            if vendor_key == 'generic':
                continue
                
            detection = vendor_info.get('detection', {})
            
            # Check sysObjectID prefix
            if sys_object_id:
                prefix = detection.get('sysObjectID_prefix', '')
                if prefix and sys_object_id.startswith(prefix):
                    print(f"✅ Vendor erkannt (ObjectID): {vendor_info['name']}")
                    return vendor_key
            
            # Check sysDescr keywords
            if sys_descr:
                keywords = detection.get('sysDescr_keywords', [])
                for keyword in keywords:
                    if keyword.lower() in sys_descr.lower():
                        print(f"✅ Vendor erkannt (sysDescr): {vendor_info['name']}")
                        return vendor_key
        
        print(f"⚠️  Unbekannter Vendor, verwende Generic MIBs")
        return 'generic'
    
    def get_device_info(self, host: str, vendor: str, community: str = "public") -> Dict:
        """
        Holt grundlegende Device-Informationen basierend auf Vendor
        """
        info = {
            'host': host,
            'vendor': vendor,
            'timestamp': datetime.now().isoformat()
        }
        
        # Hole vendor-spezifische OIDs
        vendor_oids = self.mib_db['vendors'].get(vendor, {}).get('oids', {})
        system_oids = vendor_oids.get('system', {})
        
        for key, oid in system_oids.items():
            value = self.snmp_get(host, oid, community)
            if value:
                info[key] = value
        
        return info
    
    def get_interface_stats(self, host: str, vendor: str, 
                           community: str = "public") -> List[Dict]:
        """
        Holt Interface-Statistiken
        Berechnet Bandwidth-Nutzung für 10G-Interfaces
        """
        interfaces = []
        
        # Walk interface table
        if_table = self.snmp_walk(host, "1.3.6.1.2.1.2.2.1", community, max_results=200)
        
        # Parse interface data
        interface_map = {}
        for oid, value in if_table.items():
            # OID Format: 1.3.6.1.2.1.2.2.1.X.Y
            # X = field type, Y = interface index
            parts = oid.split('.')
            if len(parts) >= 11:
                field_type = parts[10]
                if_index = parts[11] if len(parts) > 11 else None
                
                if if_index not in interface_map:
                    interface_map[if_index] = {'index': if_index}
                
                # Map field types
                field_mapping = {
                    '2': 'ifDescr',
                    '5': 'ifSpeed',
                    '8': 'ifOperStatus',
                    '10': 'ifInOctets',
                    '16': 'ifOutOctets',
                    '14': 'ifInErrors',
                    '20': 'ifOutErrors'
                }
                
                if field_type in field_mapping:
                    interface_map[if_index][field_mapping[field_type]] = value
        
        # Convert to list
        for if_data in interface_map.values():
            # Calculate bandwidth usage for high-speed interfaces
            if 'ifSpeed' in if_data:
                speed_bps = int(if_data['ifSpeed'])
                if_data['ifSpeed_mbps'] = speed_bps / 1_000_000
                
                # For 10G interfaces
                if speed_bps >= 10_000_000_000:
                    if_data['interface_class'] = '10G'
            
            # Status interpretation
            if 'ifOperStatus' in if_data:
                status_map = {'1': 'up', '2': 'down', '3': 'testing'}
                if_data['ifOperStatus_text'] = status_map.get(
                    if_data['ifOperStatus'], 'unknown'
                )
            
            interfaces.append(if_data)
        
        return interfaces
    
    def get_performance_metrics(self, host: str, vendor: str,
                               community: str = "public") -> Dict:
        """
        Holt Performance-Metriken (CPU, Memory, Temperature)
        """
        metrics = {}
        
        vendor_oids = self.mib_db['vendors'].get(vendor, {}).get('oids', {})
        perf_oids = vendor_oids.get('performance', {})
        
        for key, oid in perf_oids.items():
            value = self.snmp_get(host, oid, community)
            if value:
                try:
                    metrics[key] = float(value)
                except:
                    metrics[key] = value
        
        return metrics
    
    def get_wireless_stats(self, host: str, community: str = "public") -> Dict:
        """
        Spezielle Funktion für UniFi Access Points
        Holt Wireless-spezifische Metriken
        """
        wireless = {}
        
        ubiquiti_oids = self.mib_db['vendors']['ubiquiti']['oids']['wireless']
        
        for key, oid in ubiquiti_oids.items():
            value = self.snmp_get(host, oid, community)
            if value:
                try:
                    wireless[key] = int(value)
                except:
                    wireless[key] = value
        
        return wireless
    
    def scan_device(self, host: str, community: str = "public", 
                   full_walk: bool = False) -> Dict:
        """
        Vollständiger Device-Scan
        
        Args:
            host: Target IP
            community: SNMP Community
            full_walk: Wenn True, führe vollständigen Walk durch (langsam!)
            
        Returns:
            Umfassendes Device-Dictionary
        """
        print(f"\n{'='*60}")
        print(f"🎯 Scanne Device: {host}")
        print(f"{'='*60}")
        
        result = {
            'host': host,
            'scan_timestamp': datetime.now().isoformat(),
            'snmp_available': True
        }
        
        # 1. Vendor Detection
        vendor = self.detect_vendor(host, community)
        if not vendor:
            result['snmp_available'] = False
            return result
        
        result['vendor'] = vendor
        result['vendor_name'] = self.mib_db['vendors'][vendor]['name']
        
        # 2. Basic Device Info
        print("📋 Hole Device-Informationen...")
        result['device_info'] = self.get_device_info(host, vendor, community)
        
        # 3. Interface Statistics
        print("📊 Hole Interface-Statistiken...")
        result['interfaces'] = self.get_interface_stats(host, vendor, community)
        
        # 4. Performance Metrics
        print("⚡ Hole Performance-Metriken...")
        result['performance'] = self.get_performance_metrics(host, vendor, community)
        
        # 5. Wireless Stats (für UniFi)
        if vendor == 'ubiquiti':
            print("📡 Hole Wireless-Statistiken...")
            result['wireless'] = self.get_wireless_stats(host, community)
        
        # 6. Full Walk (optional)
        if full_walk:
            print("🔍 Führe vollständigen SNMP Walk durch (kann dauern)...")
            result['full_walk'] = {}
            for tree in self.mib_db.get('snmp_walk_targets', {}).get('trees', []):
                print(f"   Walking: {tree['name']} ({tree['oid']})")
                walk_results = self.snmp_walk(host, tree['oid'], community, max_results=50)
                result['full_walk'][tree['name']] = walk_results
        
        print(f"\n✅ Scan abgeschlossen für {host}")
        return result
    
    def export_results(self, filename: str = "snmp_scan_results.json"):
        """Exportiert Scan-Ergebnisse als JSON"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Ergebnisse exportiert nach: {filename}")


def main():
    """Beispiel-Verwendung"""
    
    if not SNMP_AVAILABLE:
        print("\n❌ pysnmp ist nicht installiert!")
        print("Installiere mit: pip3 install pysnmp --break-system-packages")
        return
    
    print("=" * 60)
    print("🎮 ENHANCED SNMP SCANNER with Walk & MIB Database")
    print("=" * 60)
    print()
    
    scanner = SNMPScanner()
    
    # Beispiel-Geräte (ersetze mit deinen IPs)
    devices = [
        {'host': '192.168.1.1', 'name': 'Router'},
        {'host': '192.168.1.10', 'name': 'UniFi AP'},
        {'host': '192.168.1.2', 'name': 'Switch'}
    ]
    
    community = "public"  # SNMP Community String
    
    results = {}
    
    for device in devices:
        host = device['host']
        name = device['name']
        
        print(f"\n{'='*60}")
        print(f"Teste {name} ({host})...")
        print(f"{'='*60}")
        
        # Quick test: Ist SNMP erreichbar?
        sys_name = scanner.snmp_get(host, "1.3.6.1.2.1.1.5.0", community, timeout=2)
        
        if sys_name:
            print(f"✅ SNMP erreichbar - System Name: {sys_name}")
            
            # Full scan
            result = scanner.scan_device(host, community, full_walk=False)
            results[host] = result
            
            # Print Summary
            print(f"\n📊 Zusammenfassung:")
            print(f"   Vendor: {result.get('vendor_name', 'Unknown')}")
            if 'performance' in result:
                perf = result['performance']
                if 'cpu_usage' in perf or 'cpu_5sec' in perf:
                    cpu = perf.get('cpu_usage', perf.get('cpu_5sec', 'N/A'))
                    print(f"   CPU: {cpu}%")
                if 'memory_usage' in perf:
                    print(f"   Memory: {perf['memory_usage']}%")
            if 'interfaces' in result:
                print(f"   Interfaces: {len(result['interfaces'])}")
        else:
            print(f"❌ SNMP nicht erreichbar auf {host}")
            print(f"   Prüfe:")
            print(f"   - Ist SNMP aktiviert?")
            print(f"   - Ist Community String korrekt? (aktuell: '{community}')")
            print(f"   - Firewall-Regeln?")
    
    # Export
    if results:
        scanner.results = results
        scanner.export_results()
        
        # Integration mit network_data.json
        print("\n🔄 Integriere mit network_data.json...")
        try:
            with open('network_data.json', 'r') as f:
                network_data = json.load(f)
            
            # Merge SNMP data
            for ip, snmp_data in results.items():
                if ip in network_data['devices']:
                    network_data['devices'][ip]['snmp_data'] = snmp_data
                    network_data['devices'][ip]['snmp_enabled'] = True
                    print(f"✅ SNMP-Daten zu {ip} hinzugefügt")
            
            with open('network_data.json', 'w') as f:
                json.dump(network_data, f, indent=2)
            
            print("✅ network_data.json aktualisiert")
            
        except FileNotFoundError:
            print("⚠️  network_data.json nicht gefunden")
    else:
        print("\n⚠️  Keine SNMP-Ergebnisse zum Exportieren")
    
    print("\n🎯 Scan abgeschlossen!")
    print("\nTipps:")
    print("- Editiere snmp_config.json für deine Geräte")
    print("- Setze die korrekten SNMP Community Strings")
    print("- Für Full Walk: scanner.scan_device(host, community, full_walk=True)")


if __name__ == "__main__":
    main()
