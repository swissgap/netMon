# 🔍 SNMP Monitoring - Vollständige Anleitung

## 📊 Überblick

Das erweiterte SNMP-Monitoring-System bietet:

### ✅ Features
- **SNMP Walk**: Automatische OID-Erkennung
- **MIB Database (SoT)**: Vordefinierte OIDs für Cisco, UniFi, Huawei
- **Auto-Vendor-Detection**: Automatische Hersteller-Erkennung
- **Performance Monitoring**: CPU, Memory, Temperature, Bandwidth
- **Wireless Stats**: Client-Counts, Channel-Auslastung (UniFi)
- **10G Interface Monitoring**: Spezielle Überwachung für High-Speed-Links

---

## 🚀 Quick Start

### 1. Installation

```bash
# SNMP Library installieren
pip3 install pysnmp --break-system-packages

# Oder mit npm
npm run install-python-deps
```

### 2. SNMP auf Geräten aktivieren

#### Cisco IOS/IOS-XE
```
! SNMP v2c konfigurieren
configure terminal
snmp-server community public RO
snmp-server location "Gaming Day"
snmp-server contact "admin@example.com"
end
write memory
```

#### UniFi Controller (für APs)
1. Öffne UniFi Controller
2. Settings → Services
3. SNMP aktivieren
4. Community String setzen (z.B. "public")

#### Huawei VRP
```
<Huawei> system-view
[Huawei] snmp-agent
[Huawei] snmp-agent community read public
[Huawei] snmp-agent sys-info location Gaming-Day
[Huawei] quit
<Huawei> save
```

### 3. Konfiguration anpassen

Editiere `snmp_config.json`:

```json
{
  "devices": [
    {
      "host": "192.168.1.1",
      "name": "Main Router",
      "community": "public",
      "expected_vendor": "cisco",
      "enabled": true
    }
  ]
}
```

### 4. SNMP Scanner ausführen

```bash
python3 snmp_scanner.py
```

---

## 📚 MIB Database (Source of Truth)

### Struktur

Die `snmp_mib_database.json` enthält:

```
├── vendors/
│   ├── cisco/
│   │   ├── detection (Vendor-Erkennung)
│   │   ├── oids/
│   │   │   ├── system
│   │   │   ├── performance
│   │   │   ├── interfaces
│   │   │   └── routing
│   ├── ubiquiti/
│   │   ├── wireless (UniFi-spezifisch)
│   │   └── clients
│   ├── huawei/
│   │   ├── optical (SFP-Monitoring)
│   │   └── power
│   └── generic/ (RFC-Standard MIBs)
│
├── common_queries/ (Vordefinierte Abfragen)
└── snmp_walk_targets/ (Walk-Empfehlungen)
```

### Wichtigste OIDs

#### System-Info (alle Geräte)
```python
sysDescr    = "1.3.6.1.2.1.1.1.0"    # Gerätebeschreibung
sysUpTime   = "1.3.6.1.2.1.1.3.0"    # Uptime
sysName     = "1.3.6.1.2.1.1.5.0"    # Hostname
sysLocation = "1.3.6.1.2.1.1.6.0"    # Standort
```

#### Cisco Performance
```python
cpu_5sec = "1.3.6.1.4.1.9.9.109.1.1.1.1.6.1"  # CPU 5 Sekunden
memory   = "1.3.6.1.4.1.9.9.48.1.1.1.5.1"     # Memory Used
```

#### UniFi Wireless
```python
clientCount     = "1.3.6.1.4.1.41112.1.6.1.2.1.15"
clientCount_2g  = "1.3.6.1.4.1.41112.1.6.3.1.3"
clientCount_5g  = "1.3.6.1.4.1.41112.1.6.3.1.4"
```

#### Interface Bandwidth (alle)
```python
ifInOctets  = "1.3.6.1.2.1.2.2.1.10"   # Bytes In
ifOutOctets = "1.3.6.1.2.1.2.2.1.16"   # Bytes Out
ifSpeed     = "1.3.6.1.2.1.2.2.1.5"    # Interface Speed
```

---

## 🔧 Verwendung

### Einfacher SNMP GET

```python
from snmp_scanner import SNMPScanner

scanner = SNMPScanner()

# Hole System Name
sys_name = scanner.snmp_get("192.168.1.1", "1.3.6.1.2.1.1.5.0", "public")
print(f"System Name: {sys_name}")
```

### SNMP Walk

```python
# Walk über alle Interfaces
interfaces = scanner.snmp_walk("192.168.1.1", "1.3.6.1.2.1.2.2.1", "public")

for oid, value in interfaces.items():
    print(f"{oid}: {value}")
```

### Vendor Detection

```python
vendor = scanner.detect_vendor("192.168.1.1", "public")
print(f"Detected: {vendor}")  # z.B. "cisco"
```

### Full Device Scan

```python
# Vollständiger Scan mit allen Metriken
result = scanner.scan_device("192.168.1.1", "public")

print(f"Vendor: {result['vendor_name']}")
print(f"CPU: {result['performance'].get('cpu_usage')}%")
print(f"Interfaces: {len(result['interfaces'])}")
```

### Full Walk (Discovery)

```python
# Mit vollständigem Walk (langsam, für Discovery)
result = scanner.scan_device("192.168.1.1", "public", full_walk=True)

# Zeigt alle verfügbaren OIDs
for tree_name, oids in result['full_walk'].items():
    print(f"\n{tree_name}:")
    for oid, value in oids.items():
        print(f"  {oid}: {value}")
```

---

## 🎯 Use Cases

### 1. 10G Uplink Monitoring

```python
# Hole Interface-Statistiken
interfaces = scanner.get_interface_stats("192.168.1.1", "cisco", "public")

# Finde 10G Interface
for interface in interfaces:
    if interface.get('interface_class') == '10G':
        print(f"10G Interface gefunden: {interface['ifDescr']}")
        print(f"  In:  {interface['ifInOctets']} Bytes")
        print(f"  Out: {interface['ifOutOctets']} Bytes")
        
        # Bandwidth-Berechnung (braucht 2 Messungen)
        # Delta Bytes / Delta Time * 8 / 1000000 = Mbps
```

**Automatische Integration:**
Der Scanner kann mit `network_scanner.py` kombiniert werden:

```python
# In network_scanner.py einbauen:
if device['type'] == 'router':
    snmp_data = snmp_scanner.scan_device(ip, community)
    device['metrics'].update({
        'uplink_usage_mbps': calculate_bandwidth(snmp_data),
        'cpu_usage': snmp_data['performance']['cpu_usage']
    })
```

### 2. UniFi AP Monitoring

```python
# Spezielle Wireless-Stats
wireless = scanner.get_wireless_stats("192.168.1.10", "public")

print(f"Clients 2.4GHz: {wireless.get('clientCount_2ghz')}")
print(f"Clients 5GHz:   {wireless.get('clientCount_5ghz')}")
print(f"Channel 2.4:    {wireless.get('channel_2ghz')}")
print(f"Channel 5:      {wireless.get('channel_5ghz')}")
```

### 3. Multi-Device Monitoring

```python
devices = [
    {'host': '192.168.1.1', 'name': 'Router'},
    {'host': '192.168.1.10', 'name': 'AP 1'},
    {'host': '192.168.1.11', 'name': 'AP 2'}
]

results = {}
for device in devices:
    result = scanner.scan_device(device['host'], 'public')
    results[device['name']] = result
    
# Export
scanner.results = results
scanner.export_results()
```

---

## 🔄 Integration mit Dashboard

### Methode 1: Direct Integration

Modifiziere `advanced_scanner.py`:

```python
def collect_metrics(self):
    # ... existing code ...
    
    # Add SNMP scanner
    snmp_scanner = SNMPScanner()
    
    for ip, device in self.devices.items():
        if device.get('snmp_enabled'):
            snmp_data = snmp_scanner.scan_device(ip, 'public')
            device['snmp_metrics'] = snmp_data
```

### Methode 2: Separate Service

```bash
# Terminal 1: SNMP Scanner (alle 60s)
while true; do
    python3 snmp_scanner.py
    sleep 60
done

# Terminal 2: Dashboard Server
npm start
```

### Methode 3: Scheduled Task

```bash
# Crontab eintragen
*/1 * * * * cd /path/to/project && python3 snmp_scanner.py
```

---

## 📈 Bandwidth-Berechnung

### Theorie

Bandwidth in Mbps = (Delta Bytes × 8) / (Delta Seconds × 1,000,000)

### Implementierung

```python
import time

def calculate_bandwidth(host, interface_oid, community, interval=10):
    """
    Berechnet Bandwidth-Nutzung über ein Intervall
    
    Args:
        host: Target IP
        interface_oid: OID des Interfaces (ifInOctets oder ifOutOctets)
        interval: Messintervall in Sekunden
    
    Returns:
        Bandwidth in Mbps
    """
    scanner = SNMPScanner()
    
    # Erste Messung
    bytes1 = int(scanner.snmp_get(host, interface_oid, community))
    time1 = time.time()
    
    # Warte
    time.sleep(interval)
    
    # Zweite Messung
    bytes2 = int(scanner.snmp_get(host, interface_oid, community))
    time2 = time.time()
    
    # Berechnung
    delta_bytes = bytes2 - bytes1
    delta_time = time2 - time1
    
    mbps = (delta_bytes * 8) / (delta_time * 1_000_000)
    
    return round(mbps, 2)

# Verwendung
uplink_in = calculate_bandwidth("192.168.1.1", "1.3.6.1.2.1.2.2.1.10.1", "public")
uplink_out = calculate_bandwidth("192.168.1.1", "1.3.6.1.2.1.2.2.1.16.1", "public")

print(f"Uplink Usage: {uplink_in} Mbps IN, {uplink_out} Mbps OUT")
print(f"Total: {uplink_in + uplink_out} Mbps")
```

### 64-bit Counter für >4 Gbps

Für High-Speed Interfaces (>1G) verwende 64-bit Counter:

```python
# 32-bit (Standard, max ~4 Gbps)
ifInOctets = "1.3.6.1.2.1.2.2.1.10.X"

# 64-bit (für High-Speed)
ifHCInOctets = "1.3.6.1.2.1.31.1.1.1.6.X"
ifHCOutOctets = "1.3.6.1.2.1.31.1.1.1.10.X"
```

---

## 🛠️ Troubleshooting

### SNMP nicht erreichbar

```bash
# Test mit snmpwalk (falls installiert)
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.1

# Test mit Python
python3 -c "
from snmp_scanner import SNMPScanner
s = SNMPScanner()
print(s.snmp_get('192.168.1.1', '1.3.6.1.2.1.1.5.0', 'public'))
"
```

**Checkliste:**
- ✅ SNMP auf Gerät aktiviert?
- ✅ Community String korrekt?
- ✅ Firewall erlaubt UDP 161?
- ✅ SNMP Listen auf richtigem Interface?
- ✅ ACL/Source-Filter konfiguriert?

### Timeout-Probleme

```python
# Erhöhe Timeout
result = scanner.snmp_get(host, oid, community, timeout=10)

# Oder global in snmp_config.json
"default_timeout": 10
```

### Keine Vendor-Erkennung

```python
# Debug: Zeige was zurückkommt
sys_obj = scanner.snmp_get(host, "1.3.6.1.2.1.1.2.0", community)
sys_desc = scanner.snmp_get(host, "1.3.6.1.2.1.1.1.0", community)

print(f"sysObjectID: {sys_obj}")
print(f"sysDescr: {sys_desc}")

# Manuell in MIB Database nachschlagen
```

### Walk zu langsam

```python
# Limitiere Ergebnisse
walk_result = scanner.snmp_walk(host, oid, max_results=50)

# Oder nur spezifische OID-Trees walken
interfaces = scanner.snmp_walk(host, "1.3.6.1.2.1.2.2.1", max_results=100)
```

### Counter-Wrap (32-bit Overflow)

Bei >4 Gbps Interfaces wrappen 32-bit Counter:

```python
# Lösung: 64-bit Counter verwenden
HC_IN = "1.3.6.1.2.1.31.1.1.1.6"   # High-Capacity In
HC_OUT = "1.3.6.1.2.1.31.1.1.1.10"  # High-Capacity Out

# Oder Wrap erkennen und korrigieren
if bytes2 < bytes1:
    # Counter wrapped
    delta = (2**32 - bytes1) + bytes2
```

---

## 📝 Best Practices

### 1. Community Strings
- ❌ Nicht "public" in Production verwenden
- ✅ Verwende komplexe Strings: "r3@d0nly_2024!"
- ✅ SNMPv3 mit Auth+Priv wenn möglich

### 2. Polling-Intervalle
- **Router/Switches**: 30-60 Sekunden
- **APs**: 30 Sekunden (wegen Client-Fluktuation)
- **10G Uplinks**: 10-30 Sekunden (höhere Dynamik)

### 3. Performance
- ✅ SNMP Walk nur für Discovery, nicht für Monitoring
- ✅ Nutze spezifische OIDs statt Walk
- ✅ Batch multiple OIDs in einem Request (getBulk)

### 4. Security
- ✅ ACL/Filter auf SNMP-Source-IPs
- ✅ Read-Only Community verwenden
- ✅ SNMPv3 für sensitive Umgebungen
- ✅ Community Strings nicht in Git committen

### 5. Monitoring
```python
# Setze Alerts für kritische Metriken
if cpu_usage > 80:
    send_alert("High CPU on device")

if bandwidth_percent > 90:
    send_alert("Uplink almost saturated")
```

---

## 🎮 Gaming Day Optimierung

### Empfohlene Metriken

**Router (10G Uplink):**
- Bandwidth In/Out (10s Intervall)
- CPU Usage
- Active Connections
- Interface Errors

**UniFi APs:**
- Client Count (2.4 + 5 GHz)
- Channel Utilization
- TX/RX Rates
- Signal Strength

**Switches:**
- Interface Status
- Port Errors
- CPU Usage

### Dashboard-Integration

```javascript
// Im Dashboard: Fetch SNMP data
fetch('/api/snmp/device/192.168.1.1')
    .then(res => res.json())
    .then(data => {
        updateUplinkChart(data.bandwidth);
        updateCPUGauge(data.cpu);
    });
```

---

## 📚 Weitere Ressourcen

### MIB Browser
- **Online**: http://www.oid-info.com/
- **Tools**: iReasoning MIB Browser, SnmpB

### SNMP Testing
```bash
# Install snmp tools
sudo apt install snmp snmp-mibs-downloader

# Test commands
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.5.0
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.2.2.1
snmptable -v2c -c public 192.168.1.1 IF-MIB::ifTable
```

### Vendor MIBs Download
- **Cisco**: https://snmp.cloudapps.cisco.com/Support/SNMP/do/BrowseMIB.do
- **Ubiquiti**: https://dl.ubnt.com/datasheets/unifi/UniFi_SNMP_MIB_v4.pdf
- **Huawei**: https://support.huawei.com/ → MIBs

---

**Happy Monitoring! 🎯**
