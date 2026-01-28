# 🚀 QUICK START GUIDE

## Sofort loslegen in 3 Schritten!

### 1️⃣ Basis-Setup (Demo-Modus)
```bash
# Dashboard öffnen
open gaming_dashboard.html
# oder
firefox gaming_dashboard.html
```

Das war's! Das Dashboard läuft mit Demo-Daten. 🎉

---

### 2️⃣ Mit echten Netzwerk-Daten

```bash
# 1. Setup ausführen
chmod +x setup.sh
./setup.sh

# 2. Scanner starten
python3 quick_scanner.py

# 3. Dashboard öffnen
open gaming_dashboard.html
```

---

### 3️⃣ Kontinuierliches Monitoring

```bash
# Startet automatische Scans alle 30 Sekunden
./start_monitoring.sh
```

Öffne in einem anderen Terminal/Tab das Dashboard!

---

## 📊 Was du siehst

### Im Dashboard:
- ✅ **10 Gbit/s Uplink**: Live-Bandbreiten-Nutzung
- ✅ **WLAN APs**: Client-Anzahl und Kanal-Auslastung  
- ✅ **Gaming Consoles**: Latenz und Geschwindigkeit
- ✅ **Alle Geräte**: Status und IP-Adressen

### Auto-Refresh:
- Dashboard aktualisiert sich automatisch alle 5 Sekunden
- Zeigt immer die neuesten Daten aus `network_data.json`

---

## 🎮 Für den Gaming Day optimiert

### Empfohlenes Setup:

1. **Großer Monitor / TV**: Dashboard im Fullscreen-Modus (F11)
2. **Auto-Scan aktiv**: `./start_monitoring.sh` im Hintergrund
3. **Beamer-Modus**: Sieht episch aus auf großen Screens!

### Performance-Tipps:

```bash
# Scan-Intervall anpassen (in start_monitoring.sh)
SCAN_INTERVAL=10  # 10 Sekunden für Gaming Day
SCAN_INTERVAL=60  # 60 Sekunden für normalen Betrieb
```

---

## 🔧 Anpassung an dein Netzwerk

### Netzwerk-Range ändern:

In `quick_scanner.py`, Zeile 125:
```python
scanner = NetworkScanner("192.168.1.0/24")  # ← Hier anpassen
```

Oder automatisch mit:
```bash
./setup.sh  # Fragt nach deinem Netzwerk
```

---

## 🆘 Probleme?

### Dashboard zeigt "Lädt..."
```bash
# Prüfe ob JSON-Datei existiert
ls -la network_data.json

# Scanner manuell ausführen
python3 quick_scanner.py
```

### Keine Geräte gefunden
```bash
# Teste Ping zu einem Gerät
ping 192.168.1.1

# Netzwerk-Interface prüfen
ip addr show  # Linux
ifconfig      # macOS
```

### Permission Denied
```bash
# Skripte ausführbar machen
chmod +x setup.sh start_monitoring.sh
```

---

## 🎯 Erweiterte Features (Optional)

### Mit echtem SNMP/UniFi API:

1. Editiere `monitor_config.json`
2. Aktiviere gewünschte Integrations
3. Nutze: `python3 advanced_scanner.py`

Siehe `README.md` für Details!

---

## 🎊 Das war's!

**Viel Spaß beim Gaming Day!** 🎮

Bei Fragen: Check die README.md oder Console (F12 im Browser)
