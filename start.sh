#!/bin/bash
# Gaming Day Monitor - Intelligent Startup
# Stellt sicher dass echte Daten verwendet werden

echo "╔════════════════════════════════════════════════════════╗"
echo "║   🎮 GAMING DAY MONITOR - Intelligent Startup         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check für network_data.json
if [ -f "network_data.json" ]; then
    echo -e "${BLUE}[INFO]${NC} Found network_data.json"
    
    # Prüfe ob Demo-Daten (mehrere Indikatoren)
    is_demo=false
    
    if grep -q "Fritz!Box Router\|PlayStation 5\|Gaming PC Alpha" network_data.json 2>/dev/null; then
        echo -e "${RED}[CRITICAL]${NC} DEMO DATA detected (hardcoded device names)!"
        is_demo=true
    fi
    
    if grep -q '"has_demo_data": true' network_data.json 2>/dev/null; then
        echo -e "${RED}[CRITICAL]${NC} DEMO DATA flag set!"
        is_demo=true
    fi
    
    if ! grep -q '"scan_method"' network_data.json 2>/dev/null; then
        echo -e "${YELLOW}[WARNING]${NC} No scan_method field - possibly old demo data"
        is_demo=true
    fi
    
    if [ "$is_demo" = true ]; then
        echo -e "${RED}[ACTION REQUIRED]${NC} Demo data must be replaced!"
        echo ""
        echo "Options:"
        echo "  1) Delete and run Smart Scanner (RECOMMENDED)"
        echo "  2) Delete and run Basic Scanner"
        echo "  3) Exit (cannot start with demo data)"
        echo ""
        read -p "Choice [1]: " choice
        choice=${choice:-1}
        
        if [ "$choice" = "1" ]; then
            echo -e "${GREEN}[✓]${NC} Deleting demo data..."
            rm -f network_data.json
            
            echo -e "${GREEN}[✓]${NC} Running Smart Scanner..."
            python3 smart_scanner.py
            
            if [ $? -ne 0 ]; then
                echo -e "${RED}[✗]${NC} Smart Scanner failed!"
                echo "Try: sudo python3 smart_scanner.py"
                exit 1
            fi
        elif [ "$choice" = "2" ]; then
            echo -e "${GREEN}[✓]${NC} Deleting demo data..."
            rm -f network_data.json
            
            echo -e "${GREEN}[✓]${NC} Running Basic Scanner..."
            python3 network_scanner_v3.py
            
            if [ $? -ne 0 ]; then
                echo -e "${RED}[✗]${NC} Scanner failed - no devices found"
                exit 1
            fi
        else
            echo -e "${RED}[✗]${NC} Cannot start server with demo data!"
            exit 1
        fi
    else
        echo -e "${GREEN}[✓]${NC} Echte Daten vorhanden"
        
        # Prüfe Alter der Daten
        file_age=$((($(date +%s) - $(stat -f%m network_data.json 2>/dev/null || stat -c%Y network_data.json)) / 60))
        
        if [ $file_age -gt 30 ]; then
            echo -e "${YELLOW}[!]${NC} Daten sind ${file_age} Minuten alt"
            echo ""
            read -p "Neuen Scan durchführen? (y/N): " update_scan
            
            if [[ $update_scan =~ ^[Yy]$ ]]; then
                echo -e "${GREEN}[✓]${NC} Aktualisiere Daten..."
                python3 smart_scanner.py
            fi
        else
            echo -e "${GREEN}[✓]${NC} Daten sind aktuell (${file_age} Min alt)"
        fi
    fi
else
    echo -e "${YELLOW}[!]${NC} Keine network_data.json gefunden"
    echo ""
    echo "Möchtest du einen initialen Scan durchführen?"
    echo "  1) Smart Scanner (empfohlen - findet echte Geräte)"
    echo "  2) Basic Scanner (Demo-Daten für Testing)"
    echo ""
    read -p "Auswahl [1]: " scanner_choice
    scanner_choice=${scanner_choice:-1}
    
    if [ "$scanner_choice" = "1" ]; then
        echo -e "${GREEN}[✓]${NC} Starte Smart Scanner..."
        python3 smart_scanner.py
    else
        echo -e "${BLUE}[i]${NC} Generiere Demo-Daten..."
        python3 quick_scanner.py
    fi
fi

echo ""
echo -e "${GREEN}[✓]${NC} Daten bereit!"
echo ""

# Zeige Zusammenfassung
if [ -f "network_data.json" ]; then
    echo "📊 Netzwerk-Zusammenfassung:"
    
    # Extrahiere Statistiken (funktioniert mit/ohne jq)
    if command -v jq &> /dev/null; then
        total=$(jq '.total_devices' network_data.json)
        scan_method=$(jq -r '.scan_method // "unknown"' network_data.json)
        
        echo "   Geräte: ${total}"
        echo "   Scanner: ${scan_method}"
        
        # Device Types
        echo "   Typen:"
        jq -r '.summary.by_type | to_entries[] | "     - \(.key): \(.value)"' network_data.json 2>/dev/null
    else
        device_count=$(grep -o '"192.168' network_data.json | wc -l)
        echo "   Geräte: ~${device_count}"
    fi
fi

echo ""
echo "─────────────────────────────────────────────────────────"
echo ""

# Starte Server
echo -e "${GREEN}[✓]${NC} Starte Dashboard Server..."
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}[✗]${NC} Node.js nicht gefunden!"
    echo "   Installiere Node.js: https://nodejs.org/"
    exit 1
fi

# Check Dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}[!]${NC} Node.js Dependencies nicht installiert"
    echo -e "${BLUE}[i]${NC} Installiere Dependencies..."
    npm install
fi

# Start Server
exec node server.js
