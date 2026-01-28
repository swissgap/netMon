# 🎮 EPIC GAMING DAY - Network Monitoring System

Ein vollautomatisches Network Monitoring Dashboard mit intelligenter Geräteerkennung!

## ⚡ Schnellstart (Empfohlen: NPM)

```bash
# 1. Dependencies installieren
npm install

# 2. Server starten (mit Auto-Scan)
npm start

# 3. Dashboard öffnen
open http://localhost:3000
```

**Das war's!** 🎉 Der Server läuft mit Auto-Scanning und WebSocket-Updates!

---

## 🚀 Features

### Automatische Netzwerk-Erkennung
- **Intelligent Device Detection**: Automatische Erkennung und Klassifizierung von:
  - 🌐 Routern
  - 🔀 Switches
  - 📡 WLAN Access Points
  - 🎮 Gaming Consoles (PS5, Xbox, etc.)
  - 💻 PCs/Laptops
  - 💾 NAS-Systemen

### Echtzeit-Monitoring
- **10 Gbit/s Internet Uplink**: Live-Auslastung des Internet-Upstreams
- **WLAN Access Points**: 
  - Client-Anzahl pro AP
  - 2.4 GHz und 5 GHz Kanal-Auslastung
  - Durchsatz-Statistiken
- **Gaming Performance**:
  - Latenz-Monitoring
  - Download/Upload-Geschwindigkeit
  - Gaming-Status (Active/Idle)

### NPM-Powered Features ⚡
- **WebSocket Real-time Updates**: Dashboard aktualisiert sich automatisch ohne Reload
- **REST API**: Programmatischer Zugriff auf alle Netzwerk-Daten
- **Auto-Scanning**: Kontinuierliche Überwachung im Hintergrund
- **Multi-Client Support**: Mehrere Browser/Geräte gleichzeitig
- **Development Mode**: Auto-Reload bei Code-Änderungen

### Episches Dashboard
- 🎨 Futuristisches Gaming-Design mit Neon-Effekten
- 📊 Echtzeit-Visualisierung mit Fortschrittsbalken
- ⚡ Auto-Refresh alle 5 Sekunden
- 📱 Responsive Design

## 📦 Enthaltene Dateien

1. **quick_scanner.py** - Automatischer Netzwerk-Scanner
2. **gaming_dashboard.html** - Episches Monitoring-Dashboard
3. **network_data.json** - Generierte Netzwerk-Daten

## 🔧 Installation & Verwendung

### Methode 1: NPM (Empfohlen) ⚡

```bash
# Dependencies installieren
npm install

# Optional: Python-Erweiterungen
npm run install-python-deps

# Server starten
npm start
```

Dashboard verfügbar unter: **http://localhost:3000**

#### NPM Commands:
```bash
npm start          # Server starten (mit Auto-Scan)
npm run dev        # Development-Modus mit Auto-Reload
npm run scan       # Manueller Netzwerk-Scan
npm run monitor    # Scan + Server starten
```

**Siehe [NPM_GUIDE.md](NPM_GUIDE.md) für Details!**

---

### Methode 2: Standalone (ohne NPM)

```bash
# Scanner ausführen
python3 quick_scanner.py

# Dashboard öffnen
open gaming_dashboard.html
```

---

## 📊 Verwendung

### Mit NPM-Server:
1. Server läuft: `npm start`
2. Dashboard öffnen: http://localhost:3000
3. Auto-Updates erfolgen automatisch via WebSocket
4. Manueller Scan: Button im Dashboard oder `POST /api/scan`

### Standalone:
1. Scanner ausführen: `python3 quick_scanner.py`
2. Dashboard öffnen: `gaming_dashboard.html`
3. Manuelle Aktualisierung im Browser

---

## 🌐 REST API (nur mit NPM)

Wenn der Server läuft, stehen folgende Endpoints zur Verfügung:

```bash
# Alle Netzwerk-Daten
GET http://localhost:3000/api/network

# Spezifisches Gerät
GET http://localhost:3000/api/device/192.168.1.1

# Statistiken
GET http://localhost:3000/api/stats

# Scan auslösen
POST http://localhost:3000/api/scan

# Health Check
GET http://localhost:3000/api/health
```

---

### Voraussetzungen

#### Für NPM-Setup:
```bash
# Node.js 16+ (empfohlen: 18 oder 20)
node --version

# npm kommt mit Node.js
npm --version

# Python 3 für Scanner
python3 --version
```

Installation:
- **Node.js**: https://nodejs.org/ oder `brew install node` (macOS)
- **Python 3**: `sudo apt install python3` (Linux) oder `brew install python3` (macOS)

#### Für Standalone:
```bash
# Nur Python 3 benötigt
python3 --version
```

---

### Schnellstart

#### 1. Netzwerk scannen
```bash
python3 quick_scanner.py
```

Das Script wird:
- Alle Geräte im Netzwerk finden
- Gerätetypen automatisch erkennen
- Metriken sammeln
- `network_data.json` generieren

#### 2. Dashboard öffnen
Öffne `gaming_dashboard.html` in deinem Browser:
```bash
# In Chrome/Firefox
open gaming_dashboard.html
# oder
firefox gaming_dashboard.html
```

### Anpassung für dein Netzwerk

#### Netzwerkbereich ändern
In `quick_scanner.py`, Zeile 125:
```python
scanner = NetworkScanner("192.168.1.0/24")  # Dein Netzwerk hier
```

#### Eigene Geräte hinzufügen
Die Device-Erkennung basiert auf:
- **Hostname-Keywords**: z.B. "unifi", "playstation", "xbox"
- **MAC-Adress-Präfixe**: Hersteller-spezifisch
- **Offene Ports**: Typische Dienste

Editiere die `device_signatures` in `quick_scanner.py` (Zeile 17-52).

## 🎯 Erweiterte Features

### Echtzeit-Daten Sammlung

Für echtes Live-Monitoring kannst du die Scan-Funktion erweitern:

```python
# SNMP für Router/Switches
from pysnmp.hlapi import *

# SSH für UniFi APs
import paramiko

# API-Calls für spezifische Geräte
import requests
```

### Integration mit echten Systemen

#### UniFi Controller
```python
import requests

def get_unifi_clients():
    controller = "https://unifi-controller:8443"
    response = requests.post(
        f"{controller}/api/login",
        json={"username": "admin", "password": "password"}
    )
    # ... weitere API-Calls
```

#### Router (SNMP)
```python
from pysnmp.hlapi import *

def get_router_stats(host):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('IF-MIB', 'ifInOctets', 1))
    )
```

## 📊 Dashboard-Features

### Live-Updates
Das Dashboard aktualisiert sich automatisch alle 5 Sekunden. Du kannst dies anpassen in `gaming_dashboard.html`:
```javascript
setInterval(loadNetworkData, 5000);  // 5000ms = 5 Sekunden
```

### Alarm-Schwellwerte
Setze eigene Schwellwerte für Alarme:
```javascript
// Uplink > 70% = High Usage (rot)
if (percentage > 70) {
    progressBar.className = 'progress-fill high';
}
```

### Design-Anpassungen
Alle Farben sind CSS-Variablen. Ändere in `<style>`:
```css
/* Hauptfarben */
--primary-color: #00d4ff;    /* Neon-Blau */
--secondary-color: #7b2cbf;  /* Lila */
--accent-color: #ff006e;     /* Pink */
```

## 🔐 Sicherheitshinweise

⚠️ **Wichtig**: Der Scanner verwendet aktuell Demo-Daten. Für Produktion:

1. **Netzwerk-Zugriff beschränken**
   - Firewall-Regeln für Scan-Host
   - Separate VLAN für Management

2. **Authentifizierung**
   - Sichere API-Keys
   - Verschlüsselte Credentials
   - HTTPS für Dashboard

3. **Rate Limiting**
   - Scan-Frequenz begrenzen
   - Keine aggressive Port-Scans

## 🎮 Gaming Day Optimierungen

### Performance-Tipps
- **QoS-Regeln**: Gaming-Traffic priorisieren
- **DFS-Kanäle**: Nutze 5GHz DFS für weniger Interferenz
- **Dedicated AP**: Separater AP für Gaming-Zone
- **Kabel bevorzugen**: Konsolen per LAN verbinden

### Monitoring-Alerts
Füge Benachrichtigungen hinzu:
```javascript
if (latency > 50) {
    showAlert("Hohe Latenz erkannt!");
}
if (uplinkUsage > 8000) {
    showAlert("Uplink fast ausgelastet!");
}
```

## 📈 Weitere Metriken

Das System kann erweitert werden für:
- **Bandwidth-Historie**: Zeitverlauf der Nutzung
- **Top Talkers**: Geräte mit höchstem Traffic
- **Paket-Verlust**: Quality-of-Service Monitoring
- **DNS-Statistiken**: Query-Zeiten
- **DHCP-Leases**: IP-Vergabe-Übersicht

## 🛠️ Troubleshooting

### Dashboard zeigt keine Daten
```bash
# Prüfe ob JSON existiert
ls -la network_data.json

# Validiere JSON
python3 -m json.tool network_data.json
```

### Scanner findet keine Geräte
```bash
# Teste Netzwerk-Zugriff
ping 192.168.1.1

# Prüfe Netzwerk-Interface
ip addr show

# Root-Rechte für Raw-Sockets
sudo python3 quick_scanner.py
```

## 🎨 Screenshots & Demo

Das Dashboard zeigt:
- ✅ Live-Status aller Geräte
- 📊 Echtzeit-Bandbreiten-Nutzung
- 🎮 Gaming-Performance-Metriken
- 📡 WLAN-Kanal-Auslastung
- 🌐 Netzwerk-Topologie

## 📝 Lizenz

Dieses Projekt ist für deinen Gaming Day! Viel Spaß beim Zocken! 🎮🚀

## 🤝 Support

Bei Fragen oder Problemen:
- Prüfe die Console im Browser (F12)
- Validiere network_data.json
- Teste Scanner-Output

---

**Viel Erfolg beim Gaming Day! Möge dein Ping niedrig und deine FPS hoch sein!** 🎯
