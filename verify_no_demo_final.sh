#!/bin/bash
# verify_no_demo_final.sh - Comprehensive Demo Data Check
# Ensures NO demo/fake data in production

echo "╔════════════════════════════════════════════════════════╗"
echo "║     🔍 COMPREHENSIVE DEMO DATA VERIFICATION            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0
WARNINGS=0
CHECKS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

#===============================================================================
# CHECK 1: network_scanner.py (Demo Scanner)
#===============================================================================
echo "📋 Check 1: network_scanner.py (Demo Scanner)"
CHECKS=$((CHECKS + 1))

if [ -f "network_scanner.py" ]; then
    if grep -q "Fritz.*Box\|PlayStation.*5\|Gaming PC Alpha" network_scanner.py 2>/dev/null; then
        echo -e "${RED}❌ CRITICAL: network_scanner.py contains hardcoded demo devices!${NC}"
        echo "   Found: Fritz!Box, PlayStation 5, or Gaming PC Alpha"
        echo "   Action: Rename/delete network_scanner.py"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ network_scanner.py exists but appears clean${NC}"
    fi
else
    echo -e "${GREEN}✅ network_scanner.py not found (good)${NC}"
fi

#===============================================================================
# CHECK 2: Hardcoded Demo Device Names
#===============================================================================
echo ""
echo "📋 Check 2: Hardcoded demo device names in Python files"
CHECKS=$((CHECKS + 1))

DEMO_PATTERNS="Fritz.*Box|PlayStation.*5|Gaming PC Alpha|Xbox.*Series.*X"
DEMO_FILES=$(grep -l -E "$DEMO_PATTERNS" *.py 2>/dev/null | grep -v ".bak\|.old\|DEMO\|_old")

if [ ! -z "$DEMO_FILES" ]; then
    echo -e "${RED}❌ CRITICAL: Demo device names found in:${NC}"
    echo "$DEMO_FILES" | while read file; do
        echo "   - $file"
        grep -n -E "$DEMO_PATTERNS" "$file" | head -3 | sed 's/^/     Line /'
    done
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No hardcoded demo device names${NC}"
fi

#===============================================================================
# CHECK 3: Simulated/Fake Metrics (ACTUAL CODE, NOT COMMENTS)
#===============================================================================
echo ""
echo "📋 Check 3: Simulated metrics in scanner code"
CHECKS=$((CHECKS + 1))

# Look for ACTUAL fake data patterns (hash calculations, hardcoded values)
# NOT comments that say "NO fake data" (those are good!)
ACTUAL_FAKE_PATTERNS="uplink.*=.*3847|uplink.*=.*hash\(ip\)|clients.*=.*8.*\+.*hash|active_connections.*=.*1247"
FAKE_FILES=$(grep -l -E "$ACTUAL_FAKE_PATTERNS" *.py 2>/dev/null | grep -v ".bak\|.old\|DEMO")

if [ ! -z "$FAKE_FILES" ]; then
    echo -e "${RED}❌ CRITICAL: Actual simulated metrics found in:${NC}"
    echo "$FAKE_FILES" | while read file; do
        echo "   - $file"
        grep -n -E "$ACTUAL_FAKE_PATTERNS" "$file" | head -3 | sed 's/^/     Line /'
    done
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ No simulated metrics found${NC}"
    echo "   (Comments about avoiding fake data are OK)"
fi

#===============================================================================
# CHECK 4: server.js Scanner Configuration
#===============================================================================
echo ""
echo "📋 Check 4: server.js scanner configuration"
CHECKS=$((CHECKS + 1))

if [ -f "server.js" ]; then
    # Check if server calls demo scanner
    if grep -q "network_scanner\.py\|network_scanner_v3\.py" server.js; then
        echo -e "${YELLOW}⚠️  WARNING: server.js references network_scanner*.py${NC}"
        echo "   Verify it's commented out or uses approved scanner"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✅ server.js does not call demo scanners${NC}"
    fi
    
    # Check what scanner is actually used
    SCANNER=$(grep -o "spawn.*scanner\.py" server.js | head -1)
    if [ ! -z "$SCANNER" ]; then
        echo "   Current scanner: $SCANNER"
    fi
else
    echo -e "${YELLOW}⚠️  server.js not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

#===============================================================================
# CHECK 5: network_data.json
#===============================================================================
echo ""
echo "📋 Check 5: network_data.json"
CHECKS=$((CHECKS + 1))

if [ -f "network_data.json" ]; then
    echo -e "${GREEN}✅ network_data.json exists${NC}"
    
    # Check for demo devices
    if grep -q "Fritz.*Box\|PlayStation.*5\|Gaming PC Alpha" network_data.json; then
        echo -e "${RED}❌ CRITICAL: Demo devices found in network_data.json!${NC}"
        echo "   Action: Delete network_data.json and run real scan"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ No demo devices in network_data.json${NC}"
    fi
    
    # Check for scan_method
    if grep -q "scan_method" network_data.json; then
        SCAN_METHOD=$(grep -o '"scan_method"[^,}]*' network_data.json | cut -d':' -f2 | tr -d ' ",')
        echo "   Scan method: $SCAN_METHOD"
        
        # Verify it's not a demo method
        case $SCAN_METHOD in
            "quick_scanner"|"ultra_scanner"|"kali_tools_scanner"|"smart_scanner_v2")
                echo -e "${GREEN}✅ Valid scan method${NC}"
                ;;
            *)
                echo -e "${YELLOW}⚠️  Unknown scan method${NC}"
                WARNINGS=$((WARNINGS + 1))
                ;;
        esac
    else
        echo -e "${YELLOW}⚠️  No scan_method field (may be old format)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Check for auto_discovered flag
    if grep -q "auto_discovered.*true" network_data.json; then
        echo -e "${GREEN}✅ auto_discovered flag is true${NC}"
    else
        echo -e "${YELLOW}⚠️  auto_discovered flag missing or false${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  network_data.json not found${NC}"
    echo "   Run: python3 kali_scanner.py or quick_scanner.py"
    WARNINGS=$((WARNINGS + 1))
fi

#===============================================================================
# CHECK 6: Dashboard Files (index.html)
#===============================================================================
echo ""
echo "📋 Check 6: Dashboard demo fallback"
CHECKS=$((CHECKS + 1))

if [ -f "index.html" ]; then
    # Check for demo fallback code
    if grep -q "demo.*fallback\|Fritz.*Box.*fallback" index.html; then
        echo -e "${RED}❌ Dashboard has demo fallback code${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ Dashboard clean (no demo fallback)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  index.html not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

#===============================================================================
# CHECK 7: Config Files
#===============================================================================
echo ""
echo "📋 Check 7: Config files for demo data"
CHECKS=$((CHECKS + 1))

CONFIG_CLEAN=true

# Check monitor_config.json
if [ -f "monitor_config.json" ]; then
    # Only warn if there's NO _comment field indicating it's example
    if grep -q "Fritz.*Box\|PlayStation" monitor_config.json; then
        if grep -q "_comment.*EXAMPLE" monitor_config.json; then
            echo -e "${GREEN}✅ monitor_config.json (example config - OK)${NC}"
        else
            echo -e "${YELLOW}⚠️  monitor_config.json has device names without example marker${NC}"
            WARNINGS=$((WARNINGS + 1))
            CONFIG_CLEAN=false
        fi
    fi
fi

# Check snmp_config.json
if [ -f "snmp_config.json" ]; then
    if grep -q "Fritz.*Box\|PlayStation" snmp_config.json; then
        if grep -q "example\|Example\|EXAMPLE" snmp_config.json; then
            echo -e "${GREEN}✅ snmp_config.json (example config - OK)${NC}"
        else
            echo -e "${YELLOW}⚠️  snmp_config.json has device names${NC}"
            WARNINGS=$((WARNINGS + 1))
            CONFIG_CLEAN=false
        fi
    fi
fi

if $CONFIG_CLEAN && [ ! -f "monitor_config.json" ] && [ ! -f "snmp_config.json" ]; then
    echo -e "${GREEN}✅ No config files with example data${NC}"
fi

#===============================================================================
# CHECK 8: .gitignore Protection
#===============================================================================
echo ""
echo "📋 Check 8: Git protection (.gitignore)"
CHECKS=$((CHECKS + 1))

if [ -f ".gitignore" ]; then
    if grep -q "network_data.json" .gitignore; then
        echo -e "${GREEN}✅ network_data.json in .gitignore${NC}"
    else
        echo -e "${RED}❌ network_data.json NOT in .gitignore!${NC}"
        echo "   Action: Add to .gitignore to prevent committing runtime data"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  .gitignore not found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

#===============================================================================
# CHECK 9: Approved Scanners Present
#===============================================================================
echo ""
echo "📋 Check 9: Approved scanners present"
CHECKS=$((CHECKS + 1))

APPROVED_SCANNERS=("quick_scanner.py" "ultra_scanner.py" "kali_scanner.py" "smart_scanner.py")
FOUND_SCANNERS=0

for scanner in "${APPROVED_SCANNERS[@]}"; do
    if [ -f "$scanner" ]; then
        FOUND_SCANNERS=$((FOUND_SCANNERS + 1))
        echo -e "${GREEN}✅ $scanner${NC}"
    fi
done

if [ $FOUND_SCANNERS -eq 0 ]; then
    echo -e "${RED}❌ CRITICAL: No approved scanners found!${NC}"
    ERRORS=$((ERRORS + 1))
elif [ $FOUND_SCANNERS -lt 2 ]; then
    echo -e "${YELLOW}⚠️  Only $FOUND_SCANNERS approved scanner(s) found${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ $FOUND_SCANNERS approved scanners available${NC}"
fi

#===============================================================================
# CHECK 10: Package.json Scripts
#===============================================================================
echo ""
echo "📋 Check 10: NPM scripts configuration"
CHECKS=$((CHECKS + 1))

if [ -f "package.json" ]; then
    # Check if demo scanner is in scripts
    if grep -q "network_scanner\.py" package.json; then
        echo -e "${YELLOW}⚠️  package.json contains network_scanner.py reference${NC}"
        echo "   Verify it's not the default scanner"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✅ package.json clean${NC}"
    fi
fi

#===============================================================================
# SUMMARY
#===============================================================================
echo ""
echo "════════════════════════════════════════════════════════"
echo "📊 VERIFICATION SUMMARY"
echo "════════════════════════════════════════════════════════"
echo "Total Checks: $CHECKS"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "🎉 System is CLEAN - NO DEMO DATA!"
    echo "   Ready for production use"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS WARNING(S)${NC}"
    echo ""
    echo "System appears clean but has minor warnings"
    echo "Review warnings above"
    exit 0
else
    echo -e "${RED}❌ $ERRORS ERROR(S) FOUND!${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS WARNING(S)${NC}"
    fi
    echo ""
    echo "🚨 DEMO DATA DETECTED - Must fix before production!"
    echo ""
    echo "Quick fix:"
    echo "  1. rm network_scanner.py (or rename to .bak)"
    echo "  2. rm network_data.json"
    echo "  3. python3 kali_scanner.py  (or quick_scanner.py)"
    echo "  4. ./verify_no_demo_final.sh (run again)"
    exit 1
fi
