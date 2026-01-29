#!/bin/bash
# Pre-Deletion Safety Check
# Testet ob die App mit nur ultra_scanner.py funktioniert

echo "╔════════════════════════════════════════════════════════╗"
echo "║  🔍 PRE-DELETION SAFETY CHECK                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

#===============================================================================
# CHECK 1: Nur ultra_scanner.py existiert
#===============================================================================
echo "📋 Check 1: Scanner Files"
echo "─────────────────────────────────────────"

SCANNER_FILES=$(ls *.py 2>/dev/null | grep -v ultra_scanner)

if [ -z "$SCANNER_FILES" ]; then
    echo -e "${GREEN}✅ Nur ultra_scanner.py vorhanden${NC}"
else
    echo -e "${YELLOW}ℹ️  Andere Scanner gefunden:${NC}"
    echo "$SCANNER_FILES"
    echo "   (werden in .removed_scanners/ verschoben)"
fi

#===============================================================================
# CHECK 2: Keine Imports anderer Scanner
#===============================================================================
echo ""
echo "📋 Check 2: Code Dependencies"
echo "─────────────────────────────────────────"

# Check Python files
PYTHON_IMPORTS=$(grep -r "from.*scanner\|import.*scanner" *.py 2>/dev/null | grep -v "ultra_scanner" | grep -v "^#")

if [ -z "$PYTHON_IMPORTS" ]; then
    echo -e "${GREEN}✅ Keine Imports anderer Scanner in Python${NC}"
else
    echo -e "${RED}❌ CRITICAL: Scanner imports gefunden:${NC}"
    echo "$PYTHON_IMPORTS"
    ERRORS=$((ERRORS + 1))
fi

# Check JavaScript files
JS_REFERENCES=$(grep -r "scanner\.py" *.js 2>/dev/null | grep -v "ultra_scanner" | grep -v "^//")

if [ -z "$JS_REFERENCES" ]; then
    echo -e "${GREEN}✅ Keine Referenzen in JavaScript${NC}"
else
    echo -e "${RED}❌ CRITICAL: Scanner references in JS:${NC}"
    echo "$JS_REFERENCES"
    ERRORS=$((ERRORS + 1))
fi

#===============================================================================
# CHECK 3: package.json Commands
#===============================================================================
echo ""
echo "📋 Check 3: NPM Scripts"
echo "─────────────────────────────────────────"

if [ -f "package.json" ]; then
    # Check for ultra_scanner references
    ULTRA_REFS=$(grep -c "ultra_scanner\.py" package.json)
    
    # Check for other scanner references
    OTHER_REFS=$(grep "scanner\.py" package.json | grep -v "ultra_scanner" | wc -l)
    
    if [ $ULTRA_REFS -gt 0 ] && [ $OTHER_REFS -eq 0 ]; then
        echo -e "${GREEN}✅ package.json verwendet ultra_scanner.py${NC}"
        echo "   Found $ULTRA_REFS references"
    else
        echo -e "${RED}❌ package.json Problem:${NC}"
        echo "   ultra_scanner refs: $ULTRA_REFS"
        echo "   other scanner refs: $OTHER_REFS"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}❌ package.json not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

#===============================================================================
# CHECK 4: server.js Configuration
#===============================================================================
echo ""
echo "📋 Check 4: Server Configuration"
echo "─────────────────────────────────────────"

if [ -f "server.js" ]; then
    # Check for ultra_scanner
    ULTRA_IN_SERVER=$(grep -c "ultra_scanner\.py" server.js)
    
    # Check for other scanners
    OTHER_IN_SERVER=$(grep "scanner\.py" server.js | grep -v "ultra_scanner" | wc -l)
    
    if [ $ULTRA_IN_SERVER -gt 0 ] && [ $OTHER_IN_SERVER -eq 0 ]; then
        echo -e "${GREEN}✅ server.js verwendet ultra_scanner.py${NC}"
        echo "   Found $ULTRA_IN_SERVER references"
    else
        echo -e "${RED}❌ server.js Problem:${NC}"
        echo "   ultra_scanner refs: $ULTRA_IN_SERVER"
        echo "   other scanner refs: $OTHER_IN_SERVER"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}❌ server.js not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

#===============================================================================
# CHECK 5: ultra_scanner.py Functional Test
#===============================================================================
echo ""
echo "📋 Check 5: Scanner Functionality Test"
echo "─────────────────────────────────────────"

if [ -f "ultra_scanner.py" ]; then
    # Test Python syntax
    python3 -m py_compile ultra_scanner.py 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ultra_scanner.py syntax valid${NC}"
        
        # Test imports
        python3 -c "import sys; sys.path.insert(0, '.'); import ultra_scanner" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ ultra_scanner.py imports work${NC}"
        else
            echo -e "${YELLOW}⚠️  Import test failed (may need dependencies)${NC}"
            echo "   Run: pip3 install scapy --break-system-packages"
        fi
    else
        echo -e "${RED}❌ ultra_scanner.py has syntax errors${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}❌ CRITICAL: ultra_scanner.py not found!${NC}"
    ERRORS=$((ERRORS + 1))
fi

#===============================================================================
# CHECK 6: Essential Files Present
#===============================================================================
echo ""
echo "📋 Check 6: Essential Files"
echo "─────────────────────────────────────────"

ESSENTIAL_FILES=(
    "ultra_scanner.py"
    "server.js"
    "package.json"
    "index.html"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file MISSING${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

#===============================================================================
# CHECK 7: .removed_scanners Directory
#===============================================================================
echo ""
echo "📋 Check 7: Backup Directory"
echo "─────────────────────────────────────────"

if [ -d ".removed_scanners" ]; then
    BACKUP_COUNT=$(ls .removed_scanners/*.py 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ .removed_scanners/ exists${NC}"
    echo "   Contains $BACKUP_COUNT scanner backups"
else
    echo -e "${YELLOW}ℹ️  .removed_scanners/ not found${NC}"
    echo "   Will be created when moving old scanners"
fi

#===============================================================================
# SUMMARY & RECOMMENDATION
#===============================================================================
echo ""
echo "════════════════════════════════════════════════════════"
echo "📊 SAFETY CHECK SUMMARY"
echo "════════════════════════════════════════════════════════"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "🎉 System is ready! Safe to remove old scanners."
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│  ✅ SAFE TO PROCEED                             │"
    echo "│                                                  │"
    echo "│  Run these commands:                             │"
    echo "│                                                  │"
    echo "│  1. Test scanner:                                │"
    echo "│     python3 ultra_scanner.py                     │"
    echo "│                                                  │"
    echo "│  2. Test full stack:                             │"
    echo "│     npm start                                    │"
    echo "│                                                  │"
    echo "│  3. If working, clean up:                        │"
    echo "│     rm -rf .removed_scanners/                    │"
    echo "│     rm ultra_scanner_old.py                      │"
    echo "└─────────────────────────────────────────────────┘"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $ERRORS ERROR(S) FOUND!${NC}"
    echo ""
    echo "🚨 NOT SAFE TO PROCEED!"
    echo ""
    echo "Please fix errors above before removing old scanners."
    echo ""
    exit 1
fi
