#!/bin/bash
# Gaming Day Network Monitor - Setup Script
# Automatische Installation und Konfiguration

echo "============================================================"
echo "🎮 GAMING DAY NETWORK MONITOR - Setup"
echo "============================================================"
echo ""

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion für Status-Meldungen
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# System-Check
print_status "Prüfe System-Voraussetzungen..."

# Python Version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python 3 gefunden: $PYTHON_VERSION"
else
    print_error "Python 3 nicht gefunden!"
    echo "Bitte installiere Python 3:"
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  macOS: brew install python3"
    exit 1
fi

# Netzwerk-Konfiguration
print_status "Netzwerk-Konfiguration..."
echo ""
echo "Welches Netzwerk soll gescannt werden?"
echo "Beispiele:"
echo "  - 192.168.1.0/24 (typisches Heimnetzwerk)"
echo "  - 10.0.0.0/24"
echo "  - 172.16.0.0/24"
echo ""
read -p "Netzwerk-Range [192.168.1.0/24]: " NETWORK_RANGE
NETWORK_RANGE=${NETWORK_RANGE:-192.168.1.0/24}

# Update Scanner mit Netzwerk-Range
print_status "Konfiguriere Scanner für $NETWORK_RANGE..."
sed -i.bak "s|NetworkScanner(.*)|NetworkScanner(\"$NETWORK_RANGE\")|" network_scanner.py
print_success "Scanner konfiguriert"

# Optional: Dependencies installieren
echo ""
read -p "Erweiterte Netzwerk-Scanning-Tools installieren? (y/N): " INSTALL_DEPS

if [[ $INSTALL_DEPS =~ ^[Yy]$ ]]; then
    print_status "Installiere zusätzliche Pakete..."
    
    if command -v apt &> /dev/null; then
        # Debian/Ubuntu
        sudo apt update
        sudo apt install -y nmap python3-pip
    elif command -v brew &> /dev/null; then
        # macOS
        brew install nmap
    fi
    
    # Python-Pakete (optional für erweiterte Funktionen)
    print_status "Installiere Python-Pakete..."
    pip3 install --break-system-packages python-nmap scapy 2>/dev/null || \
    pip3 install python-nmap scapy
    
    print_success "Pakete installiert"
fi

# Initialer Scan
echo ""
print_status "Führe initialen Netzwerk-Scan durch..."
python3 network_scanner.py

if [ $? -eq 0 ]; then
    print_success "Scan erfolgreich abgeschlossen"
    print_success "Daten exportiert nach: network_data.json"
else
    print_error "Scan fehlgeschlagen"
    exit 1
fi

# Dashboard öffnen
echo ""
echo "============================================================"
print_success "Setup abgeschlossen!"
echo "============================================================"
echo ""
echo "📊 Dashboard öffnen:"
echo "   Browser: Öffne gaming_dashboard.html"
echo ""
echo "🔄 Daten aktualisieren:"
echo "   python3 network_scanner.py"
echo ""
echo "⚙️  Automatisches Update (alle 30 Sekunden):"
echo "   ./start_monitoring.sh"
echo ""

# Optional: Browser öffnen
if command -v xdg-open &> /dev/null; then
    read -p "Dashboard jetzt im Browser öffnen? (y/N): " OPEN_BROWSER
    if [[ $OPEN_BROWSER =~ ^[Yy]$ ]]; then
        xdg-open gaming_dashboard.html &
    fi
elif command -v open &> /dev/null; then
    read -p "Dashboard jetzt im Browser öffnen? (y/N): " OPEN_BROWSER
    if [[ $OPEN_BROWSER =~ ^[Yy]$ ]]; then
        open gaming_dashboard.html &
    fi
fi

print_success "Viel Spaß beim Gaming Day! 🎮"
