#!/bin/bash
# Verify No Demo Data - Comprehensive Check

echo "╔════════════════════════════════════════════════════════╗"
echo "║     🔍 DEMO DATA VERIFICATION                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0
warnings=0

# Check 1: network_data.json existence
echo "📋 Check 1: network_data.json existence"
if [ ! -f "network_data.json" ]; then
    echo -e "${YELLOW}⚠️  network_data.json missing${NC}"
    echo "   Run: python3 smart_scanner.py"
    warnings=$((warnings + 1))
else
    echo -e "${GREEN}✅ network_data.json exists${NC}"
fi

# Check 2: Hardcoded demo device names
echo ""
echo "📋 Check 2: Hardcoded demo device names"
if [ -f "network_data.json" ]; then
    demo_names=$(grep -o "Fritz!Box Router\|PlayStation 5\|Gaming PC Alpha\|Xbox Series X" network_data.json 2>/dev/null | wc -l)
    
    if [ $demo_names -gt 0 ]; then
        echo -e "${RED}❌ DEMO DATA FOUND: $demo_names hardcoded devices!${NC}"
        echo "   Found:"
        grep -o "Fritz!Box Router\|PlayStation 5\|Gaming PC Alpha\|Xbox Series X" network_data.json | sort -u | sed 's/^/     - /'
        errors=$((errors + 1))
    else
        echo -e "${GREEN}✅ No hardcoded demo devices${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipped (file missing)${NC}"
fi

# Check 3: Simulated metrics (hash function)
echo ""
echo "📋 Check 3: Simulated metrics in scanner"
if grep -q "hash(ip)" network_scanner.py 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Old network_scanner.py has simulated metrics${NC}"
    echo "   Don't use network_scanner.py - use network_scanner_v3.py or smart_scanner.py"
    warnings=$((warnings + 1))
else
    echo -e "${GREEN}✅ No hash-based simulation found${NC}"
fi

# Check 4: scan_method field
echo ""
echo "📋 Check 4: scan_method field"
if [ -f "network_data.json" ]; then
    if grep -q '"scan_method"' network_data.json 2>/dev/null; then
        method=$(grep '"scan_method"' network_data.json | cut -d'"' -f4)
        
        if [ "$method" = "network_scanner_v3_real_only" ] || [ "$method" = "smart_scanner_v2" ]; then
            echo -e "${GREEN}✅ Valid scan method: $method${NC}"
        else
            echo -e "${RED}❌ Invalid/old scan method: $method${NC}"
            errors=$((errors + 1))
        fi
    else
        echo -e "${RED}❌ No scan_method field (old demo data?)${NC}"
        errors=$((errors + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Skipped (file missing)${NC}"
fi

# Check 5: has_demo_data flag
echo ""
echo "📋 Check 5: has_demo_data flag"
if [ -f "network_data.json" ]; then
    if grep -q '"has_demo_data": true' network_data.json 2>/dev/null; then
        echo -e "${RED}❌ Demo data flag is TRUE!${NC}"
        errors=$((errors + 1))
    else
        echo -e "${GREEN}✅ Demo data flag is false or absent${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipped (file missing)${NC}"
fi

# Check 6: Dashboard demo fallback
echo ""
echo "📋 Check 6: Dashboard demo fallback"
if grep -q "generateDemoData" gaming_dashboard.html 2>/dev/null; then
    echo -e "${RED}❌ Dashboard still has generateDemoData() function!${NC}"
    errors=$((errors + 1))
else
    echo -e "${GREEN}✅ Dashboard clean (no demo fallback)${NC}"
fi

if grep -q "generateDemoData" index.html 2>/dev/null; then
    echo -e "${RED}❌ index.html has generateDemoData() function!${NC}"
    errors=$((errors + 1))
else
    echo -e "${GREEN}✅ index.html clean${NC}"
fi

# Check 7: Config files
echo ""
echo "📋 Check 7: Config files for demo data"
if grep -q "Fritz!Box\|PlayStation" monitor_config.json 2>/dev/null; then
    echo -e "${YELLOW}⚠️  monitor_config.json has demo device names (example only)${NC}"
    echo "   This is OK if it's just example config"
    warnings=$((warnings + 1))
else
    echo -e "${GREEN}✅ Config files clean${NC}"
fi

# Check 8: Git protection
echo ""
echo "📋 Check 8: Git protection (.gitignore)"
if grep -q "network_data.json" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅ network_data.json in .gitignore${NC}"
else
    echo -e "${RED}❌ network_data.json NOT in .gitignore!${NC}"
    errors=$((errors + 1))
fi

# Summary
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED - NO DEMO DATA!${NC}"
    echo ""
    echo "✅ System is clean and ready for production"
    exit 0
elif [ $errors -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $warnings WARNING(S) - System OK but check warnings${NC}"
    echo ""
    echo "System is functional but review warnings above"
    exit 0
else
    echo -e "${RED}❌ $errors ERROR(S) FOUND!${NC}"
    if [ $warnings -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $warnings WARNING(S)${NC}"
    fi
    echo ""
    echo "DEMO DATA DETECTED - Must fix before production!"
    echo ""
    echo "Quick fix:"
    echo "  rm network_data.json"
    echo "  python3 smart_scanner.py"
    exit 1
fi
