# 🎮 Setup-Vergleich: NPM vs. Standalone

## 📊 Vergleichstabelle

| Feature | NPM-Setup ⚡ | Standalone |
|---------|-------------|-----------|
| **Installation** | `npm install` | Keine |
| **Auto-Updates** | ✅ WebSocket | ❌ Manuell |
| **REST API** | ✅ Ja | ❌ Nein |
| **Multi-Client** | ✅ Ja | ⚠️ Eingeschränkt |
| **Auto-Scan** | ✅ Konfigurierbar | ❌ Manuell |
| **Dev-Mode** | ✅ Hot-Reload | ❌ Nein |
| **Production-Ready** | ✅ PM2/Docker | ⚠️ Basic |
| **Mobile Access** | ✅ Server-basiert | ⚠️ File-basiert |
| **Komplexität** | Mittel | Einfach |

**Empfehlung**: NPM für Gaming Day und Production, Standalone für Quick-Tests

---

## 🚀 Setup-Flussdiagramm

### NPM-Setup (Empfohlen)

```
┌─────────────────────────────────────────────────┐
│  1. Repository clonen/herunterladen             │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  2. npm install                                  │
│     → Installiert: express, ws, chokidar, cors  │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  3. Optional: npm run install-python-deps        │
│     → Für erweiterte Scanner-Features            │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  4. .env anpassen (optional)                     │
│     → NETWORK_RANGE, PORT, SCAN_INTERVAL        │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  5. npm start                                    │
│     → Server startet auf Port 3000               │
│     → Auto-Scan läuft alle 30s                  │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  6. Browser öffnen: http://localhost:3000       │
│     → Dashboard mit Live-Updates! 🎉            │
└─────────────────────────────────────────────────┘
```

### Standalone-Setup (Quick & Simple)

```
┌─────────────────────────────────────────────────┐
│  1. Repository clonen/herunterladen             │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  2. python3 network_scanner.py                   │
│     → Generiert network_data.json                │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  3. gaming_dashboard.html öffnen                 │
│     → Im Browser (Doppelklick oder open)         │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  4. Dashboard lädt JSON und zeigt Daten         │
│     → Keine Auto-Updates                         │
│     → F5 für Refresh                             │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Entscheidungshilfe

### Nutze NPM-Setup wenn:
- ✅ Du ein Gaming-Event veranstaltest
- ✅ Live-Updates wichtig sind
- ✅ Mehrere Personen gleichzeitig schauen
- ✅ Du einen zentralen Monitor/Beamer hast
- ✅ Du kontinuierliches Monitoring brauchst
- ✅ Du die API nutzen willst
- ✅ Production-Deployment geplant ist

### Nutze Standalone wenn:
- ✅ Du nur schnell testen willst
- ✅ Keine Node.js-Installation möglich
- ✅ Einmalige Verwendung
- ✅ Sehr einfaches Setup bevorzugt
- ✅ Offline-Nutzung (nach Scan)

---

## 💡 Pro-Tipps

### NPM-Setup optimieren:

```bash
# 1. Schnelleren Scan-Intervall für Gaming Day
SCAN_INTERVAL=10000 npm start

# 2. Development mit Auto-Reload
npm run dev

# 3. Production mit PM2
pm2 start server.js --name gaming-monitor

# 4. Multi-Terminal Setup
# Terminal 1: npm start
# Terminal 2: tail -f scanner.log
# Browser: Dashboard auf großem Screen
```

### Standalone optimieren:

```bash
# 1. Auto-Scan mit Cron
*/1 * * * * cd /path/to/project && python3 network_scanner.py

# 2. Browser Auto-Refresh (Browser-Extension)
# z.B. "Auto Refresh Plus" für Chrome

# 3. Schnelles Testen ohne Installation
python3 network_scanner.py && open gaming_dashboard.html
```

---

## 🔄 Migration: Standalone → NPM

Falls du von Standalone zu NPM wechseln willst:

```bash
# 1. Node.js installieren
# macOS: brew install node
# Ubuntu: sudo apt install nodejs npm

# 2. Im Projekt-Ordner
npm install

# 3. Bestehende network_data.json bleibt erhalten!
npm start

# 4. Fertig! Dashboard jetzt mit Live-Updates
```

Keine Daten gehen verloren - `network_data.json` wird weiterverwendet!

---

## 📈 Performance-Vergleich

| Metrik | NPM | Standalone |
|--------|-----|-----------|
| **Setup-Zeit** | ~2 min | ~10 sek |
| **Update-Latenz** | <1 sek | Manuell |
| **CPU-Last** | ~30 MB | ~0 MB |
| **Gleichzeitige Clients** | Unbegrenzt | 1 |
| **Netzwerk-Traffic** | WebSocket | Keine |
| **Skalierbarkeit** | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## ❓ FAQ

### Kann ich NPM und Standalone mischen?

**Ja!** Du kannst:
- Scanner standalone laufen lassen: `python3 network_scanner.py`
- Server trotzdem nutzen: `npm start`
- Server liest das gleiche `network_data.json`

### Brauche ich für NPM Internet?

**Nur für Installation:**
- `npm install` braucht Internet für Packages
- Danach läuft alles lokal im Netzwerk
- Keine Cloud-Abhängigkeiten

### Kann ich den Port ändern?

**Ja, sehr einfach:**
```bash
# In .env
PORT=8080

# Oder beim Start
PORT=8080 npm start
```

### Funktioniert es auf Raspberry Pi?

**Ja!** Beide Varianten:
```bash
# Node.js installieren
sudo apt install nodejs npm

# Dann wie gewohnt
npm install && npm start
```

---

**Fazit**: NPM-Setup ist aufwändiger beim ersten Mal, aber viel mächtiger für echtes Monitoring! 🚀
