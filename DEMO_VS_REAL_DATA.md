# 🚨 Troubleshooting: Demo-Daten vs. Echte Daten

## Problem: Dashboard zeigt "Fritz!Box Router" und Demo-Daten

### 🔍 Symptome
```
Dashboard zeigt:
- Fritz!Box Router (192.168.1.1)
- PlayStation 5 (192.168.1.20)
- Gaming PC Alpha (192.168.1.50)
- Alle Werte sehen "zu perfekt" aus
- /api zeigt: Cannot GET /api
```

**Diagnose: Das sind Demo-Daten vom alten `network_scanner.py`!**

---

## ✅ Lösung: Echte Daten verwenden

### Option 1: Intelligenter Startup (Empfohlen)

```bash
# Startet automatisch mit echten Daten
npm start

# Das Script fragt automatisch:
# "Demo-Daten erkannt! Echte Daten sammeln? [Ja/Nein]"
```

Das neue `start.sh` Script:
- ✅ Erkennt Demo-Daten automatisch
- ✅ Fragt ob Smart Scanner laufen soll
- ✅ Prüft Alter der Daten
- ✅ Startet dann den Server

### Option 2: Manuell Smart Scanner ausführen

```bash
# 1. Demo-Daten löschen
npm run clean

# 2. Smart Scanner ausführen
npm run scan:smart

# 3. Server starten
npm run start:server-only
```

### Option 3: Force Real Data (Ein Befehl)

```bash
# Löscht alte Daten und scannt neu
npm run start:force-scan
```

---

## 🔎 Wie erkenne ich Demo-Daten?

### Demo-Daten (Fake):
```json
{
  "devices": {
    "192.168.1.1": {
      "hostname": "Fritz!Box Router",    // ❌ Generisch
      "vendor": "AVM",                    // ❌ Hardcoded
      "metrics": {
        "uplink_usage_mbps": 4088,       // ❌ Runde Zahl
        "active_connections": 1247        // ❌ Zu perfekt
      }
    }
  },
  "scan_method": undefined                // ❌ Fehlt
}
```

### Echte Daten (Smart Scanner):
```json
{
  "devices": {
    "192.168.1.1": {
      "hostname": "router.local",        // ✅ Echter Hostname
      "sysDescr": "Cisco IOS Software...", // ✅ SNMP-Daten
      "vendor": "cisco",                 // ✅ SNMP-erkannt
      "metrics": {
        "uplink_usage_mbps": 4235.73,   // ✅ Echte Messung
        "cpu_usage": 23.4                // ✅ SNMP Real
      }
    }
  },
  "scan_method": "smart_scanner_v2",    // ✅ Vorhanden
  "auto_discovered": true                // ✅ Flag
}
```

---

## 🛠️ Schritt-für-Schritt: Demo → Real

### Aktueller Status prüfen

```bash
# Prüfe ob Demo-Daten
grep "Fritz!Box Router" network_data.json

# Wenn Output → Demo-Daten vorhanden!
```

### Clean Start

```bash
# 1. Stoppe Server (Ctrl+C)

# 2. Lösche alte Daten
rm network_data.json

# 3. Smart Scanner ausführen
python3 smart_scanner.py

# Output sollte sein:
# 🤖 SMART SCANNER V2
# 🔍 Auto-erkanntes Netzwerk: 192.168.1.0/24
# 📊 Phase 1: X Geräte discovered
# ...

# 4. Prüfe neue Daten
cat network_data.json | grep "scan_method"
# Sollte zeigen: "scan_method": "smart_scanner_v2"

# 5. Server starten
npm run start:server-only
```

---

## 📊 API Endpoints prüfen

### Nach Smart Scanner sollte funktionieren:

```bash
# Test API
curl http://localhost:3000/api/network

# Sollte echte Geräte zeigen mit:
# - "scan_method": "smart_scanner_v2"
# - "auto_discovered": true
# - Echte Hostnames
# - SNMP-Daten
```

### API Fehler beheben

Wenn `/api` zeigt `Cannot GET /api`:

```bash
# Das ist korrekt! API ist unter:
# /api/network
# /api/device/:ip
# /api/stats
# /api/scan
# /api/health

# Test:
curl http://localhost:3000/api/health
```

---

## 🚀 Automatisierung

### Immer echte Daten beim Start

```bash
# In .bashrc oder .zshrc
alias gaming-start='cd /path/to/project && npm run start:force-scan'
```

### Cron Job für Auto-Updates

```bash
# Alle 5 Minuten Scan
*/5 * * * * cd /path/to/project && python3 smart_scanner.py
```

### SystemD Service (Linux)

```ini
[Unit]
Description=Gaming Day Monitor
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/project
ExecStartPre=/usr/bin/python3 smart_scanner.py
ExecStart=/usr/bin/node server.js
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🎮 Für Gaming Day

### Setup Checklist

- [ ] Smart Scanner getestet
- [ ] Demo-Daten gelöscht
- [ ] Echte Daten generiert
- [ ] Server läuft mit echten Daten
- [ ] Dashboard zeigt echte Geräte
- [ ] API funktioniert

```bash
# Quick Check Script
#!/bin/bash

echo "🔍 Gaming Day Monitor - Health Check"
echo ""

# 1. Prüfe network_data.json
if grep -q "Fritz!Box Router" network_data.json 2>/dev/null; then
    echo "❌ WARNUNG: Demo-Daten aktiv!"
    echo "   Lösung: npm run start:force-scan"
else
    echo "✅ Echte Daten aktiv"
fi

# 2. Prüfe Scan-Method
if grep -q "smart_scanner_v2" network_data.json 2>/dev/null; then
    echo "✅ Smart Scanner verwendet"
else
    echo "⚠️  Alter Scanner oder Demo-Daten"
fi

# 3. Prüfe Server
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Server läuft"
else
    echo "❌ Server nicht erreichbar"
fi

# 4. Prüfe Geräte-Count
device_count=$(grep -o '"192.168' network_data.json 2>/dev/null | wc -l)
echo "📊 Geräte gefunden: ${device_count}"

echo ""
echo "Status: $([ -f network_data.json ] && echo 'Ready' || echo 'Setup nötig')"
```

---

## 💡 Warum passiert das?

### Problem-Ursache

```
network_scanner.py (Alt)
  └─> Generiert Demo-Daten
  └─> Schreibt network_data.json

Dashboard/Server
  └─> Liest network_data.json
  └─> Kennt Quelle nicht
  └─> Zeigt Daten (egal ob Demo oder echt)
```

### Lösung

```
smart_scanner.py (Neu)
  └─> Auto-Discovery
  └─> SNMP Walk
  └─> Echte Metriken
  └─> Schreibt network_data.json mit "scan_method" Flag

start.sh (Intelligent)
  └─> Prüft auf Demo-Daten
  └─> Fragt Benutzer
  └─> Führt Smart Scanner aus
  └─> Startet Server

Dashboard
  └─> Zeigt jetzt echte Daten!
```

---

## 🔄 Quick Fixes

### "Ich will jetzt sofort echte Daten!"

```bash
rm network_data.json && python3 smart_scanner.py && npm run start:server-only
```

### "Ich will Demo-Daten behalten (Testing)"

```bash
# Server starten ohne Scan
npm run start:server-only

# Oder in start.sh auf Frage "Nein" antworten
```

### "Server zeigt alte Daten"

```bash
# Server neustarten (lädt network_data.json neu)
# Ctrl+C
npm start
```

### "Smart Scanner findet keine Geräte"

```bash
# 1. Prüfe Netzwerk
ip addr show

# 2. Prüfe pysnmp
python3 -c "import pysnmp" && echo "OK" || echo "FEHLT"

# 3. Als root ausführen (für ARP)
sudo python3 smart_scanner.py

# 4. Fallback: Basic Discovery (ohne SNMP)
python3 smart_scanner.py  # Funktioniert auch ohne SNMP
```

---

## ✅ Verifikation

### Dashboard sollte zeigen:

- ✅ Echte Hostnames (nicht "Fritz!Box")
- ✅ Dynamische Werte (ändern sich bei Refresh)
- ✅ SNMP-Vendor (cisco, ubiquiti, etc.)
- ✅ Realistische Metriken

### API `/api/network` sollte zeigen:

```json
{
  "scan_method": "smart_scanner_v2",
  "auto_discovered": true,
  "devices": {
    "192.168.1.1": {
      "sysDescr": "Cisco IOS...",
      "vendor": "cisco",
      ...
    }
  }
}
```

---

## 🎯 Zusammenfassung

**Problem:** Dashboard zeigt Demo-Daten (Fritz!Box, PlayStation)

**Ursache:** `network_data.json` wurde von `network_scanner.py` generiert

**Lösung:**
1. Lösche `network_data.json`
2. Führe `smart_scanner.py` aus
3. Starte Server

**Einfachster Weg:**
```bash
npm run start:force-scan
```

**Für Zukunft:**
```bash
npm start  # Verwendet intelligentes start.sh
```

---

**Jetzt sollten echte Daten im Dashboard sein! 🎉**
