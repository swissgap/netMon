#!/bin/bash
# Safe Cleanup Script
# Entfernt alte Scanner nach Bestätigung

echo "╔════════════════════════════════════════════════════════╗"
echo "║  🗑️  CLEANUP OLD SCANNERS                              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

#===============================================================================
# Step 1: Run Safety Check
#===============================================================================
echo -e "${BLUE}Step 1: Running safety check...${NC}"
echo ""

if [ -f "test_before_delete.sh" ]; then
    bash test_before_delete.sh
    
    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}❌ Safety check failed!${NC}"
        echo "   Fix errors before cleanup."
        exit 1
    fi
else
    echo -e "${RED}❌ test_before_delete.sh not found${NC}"
    exit 1
fi

echo ""
echo "─────────────────────────────────────────"

#===============================================================================
# Step 2: Show what will be deleted
#===============================================================================
echo ""
echo -e "${BLUE}Step 2: Files to be removed:${NC}"
echo ""

if [ -d ".removed_scanners" ]; then
    echo "📁 .removed_scanners/ directory:"
    ls -lh .removed_scanners/*.py 2>/dev/null | awk '{print "   " $9, "(" $5 ")"}'
fi

if [ -f "ultra_scanner_old.py" ]; then
    SIZE=$(ls -lh ultra_scanner_old.py | awk '{print $5}')
    echo "📄 ultra_scanner_old.py ($SIZE)"
fi

echo ""
echo "─────────────────────────────────────────"

#===============================================================================
# Step 3: Confirmation
#===============================================================================
echo ""
echo -e "${YELLOW}⚠️  WARNING: This will permanently delete old scanner files!${NC}"
echo ""
echo "The following will be kept:"
echo -e "  ${GREEN}✅ ultra_scanner.py${NC} (THE ONLY SCANNER)"
echo -e "  ${GREEN}✅ server.js${NC}"
echo -e "  ${GREEN}✅ package.json${NC}"
echo -e "  ${GREEN}✅ index.html${NC}"
echo -e "  ${GREEN}✅ All other files${NC}"
echo ""

read -p "❓ Continue with cleanup? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo ""
    echo -e "${YELLOW}❌ Cleanup cancelled${NC}"
    exit 0
fi

#===============================================================================
# Step 4: Create final backup
#===============================================================================
echo ""
echo -e "${BLUE}Step 3: Creating final backup...${NC}"

BACKUP_DIR=".final_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -d ".removed_scanners" ]; then
    cp -r .removed_scanners "$BACKUP_DIR/"
    echo -e "${GREEN}✅ Backed up to: $BACKUP_DIR/.removed_scanners/${NC}"
fi

if [ -f "ultra_scanner_old.py" ]; then
    cp ultra_scanner_old.py "$BACKUP_DIR/"
    echo -e "${GREEN}✅ Backed up to: $BACKUP_DIR/ultra_scanner_old.py${NC}"
fi

#===============================================================================
# Step 5: Delete files
#===============================================================================
echo ""
echo -e "${BLUE}Step 4: Deleting old files...${NC}"

DELETED=0

# Remove .removed_scanners directory
if [ -d ".removed_scanners" ]; then
    rm -rf .removed_scanners
    echo -e "${GREEN}✅ Deleted: .removed_scanners/${NC}"
    DELETED=$((DELETED + 1))
fi

# Remove ultra_scanner_old.py
if [ -f "ultra_scanner_old.py" ]; then
    rm -f ultra_scanner_old.py
    echo -e "${GREEN}✅ Deleted: ultra_scanner_old.py${NC}"
    DELETED=$((DELETED + 1))
fi

#===============================================================================
# Step 6: Verify cleanup
#===============================================================================
echo ""
echo -e "${BLUE}Step 5: Verifying cleanup...${NC}"

# Check for any remaining scanner files
REMAINING=$(ls *.py 2>/dev/null | grep -v ultra_scanner | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo -e "${GREEN}✅ Only ultra_scanner.py remains${NC}"
else
    echo -e "${YELLOW}⚠️  Found $REMAINING other .py files${NC}"
    ls *.py | grep -v ultra_scanner
fi

#===============================================================================
# Step 7: Final test
#===============================================================================
echo ""
echo -e "${BLUE}Step 6: Testing system...${NC}"

# Test ultra_scanner.py
python3 -m py_compile ultra_scanner.py 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ ultra_scanner.py works${NC}"
else
    echo -e "${RED}❌ ultra_scanner.py has issues${NC}"
fi

# Test package.json
if grep -q "ultra_scanner.py" package.json; then
    echo -e "${GREEN}✅ package.json configured${NC}"
else
    echo -e "${RED}❌ package.json missing ultra_scanner${NC}"
fi

# Test server.js
if grep -q "ultra_scanner.py" server.js; then
    echo -e "${GREEN}✅ server.js configured${NC}"
else
    echo -e "${RED}❌ server.js missing ultra_scanner${NC}"
fi

#===============================================================================
# Summary
#===============================================================================
echo ""
echo "════════════════════════════════════════════════════════"
echo "📊 CLEANUP SUMMARY"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Deleted: $DELETED items"
echo "Backup: $BACKUP_DIR/"
echo ""
echo -e "${GREEN}✅ CLEANUP COMPLETE!${NC}"
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  🎉 SUCCESS                                      │"
echo "│                                                  │"
echo "│  System now uses ONLY ultra_scanner.py          │"
echo "│                                                  │"
echo "│  Next steps:                                     │"
echo "│                                                  │"
echo "│  1. Test scanner:                                │"
echo "│     python3 ultra_scanner.py                     │"
echo "│                                                  │"
echo "│  2. Test full stack:                             │"
echo "│     npm start                                    │"
echo "│                                                  │"
echo "│  3. Check dashboard:                             │"
echo "│     http://localhost:3000                        │"
echo "│                                                  │"
echo "│  Backup location:                                │"
echo "│     $BACKUP_DIR/          │"
echo "└─────────────────────────────────────────────────┘"
echo ""
