#!/bin/bash
# Gaming Day Network Monitor - Continuous Monitoring
# Führt automatisch regelmäßige Scans durch

echo "🎮 GAMING DAY - Continuous Network Monitoring"
echo "=============================================="
echo ""
echo "Monitoring läuft... (Strg+C zum Beenden)"
echo ""

# Scan-Intervall in Sekunden
SCAN_INTERVAL=30

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counter für Scans
SCAN_COUNT=0

# Infinite Loop
while true; do
    SCAN_COUNT=$((SCAN_COUNT + 1))
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${BLUE}[${TIMESTAMP}]${NC} Scan #${SCAN_COUNT} wird gestartet..."
    
    # Führe Scanner aus
    python3 quick_scanner.py > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        # Zähle Geräte
        DEVICE_COUNT=$(grep -o '"type"' network_data.json | wc -l)
        echo -e "${GREEN}[✓]${NC} Scan abgeschlossen - ${DEVICE_COUNT} Geräte gefunden"
        
        # Extrahiere wichtige Metriken
        if command -v jq &> /dev/null; then
            UPLINK=$(jq -r '.devices | to_entries[] | select(.value.type == "router") | .value.metrics.uplink_usage_mbps' network_data.json 2>/dev/null)
            CLIENTS=$(jq -r '.summary.total_wlan_clients' network_data.json 2>/dev/null)
            
            if [ ! -z "$UPLINK" ] && [ "$UPLINK" != "null" ]; then
                echo "    └─ Uplink: ${UPLINK} Mbps"
            fi
            if [ ! -z "$CLIENTS" ] && [ "$CLIENTS" != "null" ]; then
                echo "    └─ WLAN Clients: ${CLIENTS}"
            fi
        fi
    else
        echo -e "${RED}[✗]${NC} Scan fehlgeschlagen"
    fi
    
    echo ""
    
    # Warte bis zum nächsten Scan
    sleep $SCAN_INTERVAL
done
