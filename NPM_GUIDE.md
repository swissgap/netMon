# 🎮 Gaming Day Network Monitor - NPM Setup Guide

## 🚀 Schnellstart mit NPM

### Installation

```bash
# 1. Node.js Dependencies installieren
npm install

# 2. Python Dependencies installieren (optional für erweiterte Features)
npm run install-python-deps

# 3. Initialer Netzwerk-Scan
npm run scan

# 4. Server starten
npm start
```

**Dashboard öffnen:** http://localhost:3000

---

## 📦 NPM Scripts

### Hauptbefehle

```bash
# Server starten (mit Auto-Scan)
npm start

# Development-Modus mit Auto-Reload
npm run dev

# Manueller Netzwerk-Scan
npm run scan

# Scan + Server starten
npm run monitor
```

### Erweiterte Befehle

```bash
# Python Dependencies installieren
npm run install-python-deps

# Build (falls später Build-Steps hinzugefügt werden)
npm run build
```

---

## ⚙️ Konfiguration

### Umgebungsvariablen (.env)

```bash
# Server Port
PORT=3000

# Auto-Scan aktivieren/deaktivieren
AUTO_SCAN=true

# Scan-Intervall in Millisekunden (30000 = 30 Sekunden)
SCAN_INTERVAL=30000

# Netzwerk-Range für Scanner
NETWORK_RANGE=192.168.1.0/24

# Log-Level
LOG_LEVEL=info
```

### Port ändern

```bash
# Methode 1: .env-Datei bearbeiten
PORT=8080

# Methode 2: Beim Start überschreiben
PORT=8080 npm start
```

### Auto-Scan deaktivieren

```bash
# In .env:
AUTO_SCAN=false

# Oder beim Start:
AUTO_SCAN=false npm start

# Dann manuell scannen mit:
curl -X POST http://localhost:3000/api/scan
```

---

## 🌐 REST API Endpoints

Der Server bietet eine REST API:

### GET /api/network
Alle Netzwerk-Daten abrufen
```bash
curl http://localhost:3000/api/network
```

### GET /api/device/:ip
Spezifisches Gerät abrufen
```bash
curl http://localhost:3000/api/device/192.168.1.1
```

### GET /api/stats
Zusammenfassung und Statistiken
```bash
curl http://localhost:3000/api/stats
```

### POST /api/scan
Manuellen Scan auslösen
```bash
curl -X POST http://localhost:3000/api/scan
```

### GET /api/health
Server Health Check
```bash
curl http://localhost:3000/api/health
```

---

## 🔌 WebSocket Integration

Das Dashboard verbindet sich automatisch per WebSocket für **Echtzeit-Updates**.

### WebSocket URL
```
ws://localhost:3000
```

### Nachrichtenformat
```json
{
  "type": "network_update",
  "data": { ... },
  "timestamp": "2024-01-27T10:30:00.000Z"
}
```

### Features
- ✅ Automatische Verbindung beim Laden
- ✅ Auto-Reconnect bei Verbindungsabbruch
- ✅ Fallback zu HTTP-Polling
- ✅ Live-Status-Anzeige im Dashboard

---

## 🛠️ Development Setup

### Mit Auto-Reload (nodemon)

```bash
npm run dev
```

Nodemon startet den Server neu bei Änderungen an:
- server.js
- *.js Dateien

### Debugging

```bash
# Node.js Debug-Modus
node --inspect server.js

# Dann in Chrome:
chrome://inspect
```

### Logs anschauen

```bash
# Server-Logs (stdout)
npm start

# Mit mehr Details
LOG_LEVEL=debug npm start
```

---

## 📊 Features des NPM-Setups

### ✅ Vorteile gegenüber statischem HTML:

1. **WebSocket Real-time Updates**
   - Keine manuelle Aktualisierung nötig
   - Dashboard aktualisiert sich automatisch bei neuen Scans

2. **REST API**
   - Programmatischer Zugriff auf Netzwerk-Daten
   - Integration mit anderen Tools möglich

3. **Auto-Scanning**
   - Kontinuierliche Überwachung
   - Konfigurierbare Intervalle

4. **File Watching**
   - Erkennt Änderungen an network_data.json
   - Pusht Updates sofort an alle Clients

5. **Multi-Client Support**
   - Mehrere Browser können gleichzeitig verbinden
   - Alle sehen die gleichen Live-Daten

6. **Development Mode**
   - Auto-Reload bei Code-Änderungen
   - Einfaches Debugging

---

## 🎮 Production Deployment

### Mit PM2 (Process Manager)

```bash
# PM2 installieren
npm install -g pm2

# App starten
pm2 start server.js --name gaming-monitor

# Auto-Start bei System-Reboot
pm2 startup
pm2 save

# Status prüfen
pm2 status

# Logs anschauen
pm2 logs gaming-monitor

# Neu starten
pm2 restart gaming-monitor
```

### Als Systemd Service (Linux)

```bash
# Service-Datei erstellen: /etc/systemd/system/gaming-monitor.service
[Unit]
Description=Gaming Day Network Monitor
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/gaming-monitor
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target

# Service aktivieren
sudo systemctl enable gaming-monitor
sudo systemctl start gaming-monitor
```

### Mit Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

```bash
# Build
docker build -t gaming-monitor .

# Run
docker run -d -p 3000:3000 --name gaming-monitor gaming-monitor
```

---

## 🔐 Sicherheit

### Für Production:

1. **Umgebungsvariablen schützen**
   ```bash
   # .env sollte NICHT in Git committet werden
   # Ist bereits in .gitignore
   ```

2. **CORS konfigurieren** (falls nötig)
   ```javascript
   // In server.js
   app.use(cors({
     origin: 'https://your-domain.com'
   }));
   ```

3. **HTTPS verwenden**
   ```bash
   # Nginx Reverse Proxy empfohlen
   # Let's Encrypt für SSL
   ```

4. **Authentifizierung hinzufügen** (optional)
   ```javascript
   // Beispiel: Basic Auth Middleware
   const auth = require('express-basic-auth');
   ```

---

## 📱 Mobile Access

### Lokales Netzwerk

Server ist im lokalen Netzwerk erreichbar:
```
http://192.168.1.x:3000
```

### Externe Access (optional)

```bash
# Mit ngrok für Testing
npx ngrok http 3000

# Oder Port-Forwarding im Router konfigurieren
```

---

## 🐛 Troubleshooting

### Server startet nicht

```bash
# Port bereits belegt?
lsof -i :3000
# Oder anderen Port verwenden:
PORT=8080 npm start
```

### WebSocket verbindet nicht

```bash
# Firewall prüfen
sudo ufw allow 3000

# Port-Forwarding testen
curl http://localhost:3000/api/health
```

### Python-Scanner funktioniert nicht

```bash
# Python-Version prüfen
python3 --version

# Dependencies installieren
pip3 install --break-system-packages python-nmap scapy

# Manuell testen
python3 network_scanner.py
```

### Keine Geräte gefunden

```bash
# Netzwerk-Range in .env prüfen
NETWORK_RANGE=192.168.1.0/24

# Oder direkt in network_scanner.py anpassen
```

---

## 📈 Performance-Optimierung

### Scan-Intervall anpassen

```bash
# Für Gaming Day: Häufige Updates
SCAN_INTERVAL=10000  # 10 Sekunden

# Für normalen Betrieb: Weniger Last
SCAN_INTERVAL=60000  # 60 Sekunden
```

### Memory Usage reduzieren

```javascript
// Node.js Memory Limit setzen
node --max-old-space-size=512 server.js
```

---

## 🎯 Nächste Schritte

1. ✅ Installiere Dependencies: `npm install`
2. ✅ Konfiguriere .env mit deinem Netzwerk
3. ✅ Starte den Server: `npm start`
4. ✅ Öffne http://localhost:3000
5. 🎮 Genieße den Gaming Day!

---

## 💡 Tipps & Tricks

### Multi-Monitor Setup
```bash
# Terminal 1: Server mit Auto-Scan
npm start

# Terminal 2: Scanner-Logs folgen
tail -f scanner.log

# Browser: Dashboard auf zweitem Monitor
```

### Custom Scanner-Integration
```javascript
// In server.js kannst du andere Scanner integrieren:
// - SNMP (advanced_scanner.py)
// - UniFi Controller API
// - Dein eigenes Monitoring-Script
```

### API in eigenen Apps nutzen
```javascript
// Fetch network data in deiner App
fetch('http://localhost:3000/api/network')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

**Viel Erfolg beim Gaming Day! 🎮🚀**
