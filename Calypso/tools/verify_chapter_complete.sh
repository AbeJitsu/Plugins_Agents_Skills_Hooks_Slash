#!/bin/bash

# Comprehensive Chapter Validation Script - FIXED VERSION
# Validates all 4 gates in sequence and fails fast
# Usage: ./verify_chapter_complete.sh <chapter_num>

set -e  # Exit on any error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHAPTER_NUM=${1:-""}

if [ -z "$CHAPTER_NUM" ]; then
    echo -e "${RED}Usage: $0 <chapter_num>${NC}"
    exit 1
fi

CHAPTER_PADDED=$(printf "%02d" "$CHAPTER_NUM")
PROJECT_DIR="/Users/abiezerreyes/Projects/experiment/Plugins_Agents_Skills_Hooks_Slash"
EXTRACTION_JSON="${PROJECT_DIR}/Calypso/analysis/chapter_${CHAPTER_PADDED}/rich_extraction.json"
OUTPUT_DIR="${PROJECT_DIR}/Calypso/output/chapter_${CHAPTER_PADDED}"
CHAPTER_HTML="${OUTPUT_DIR}/chapter_${CHAPTER_PADDED}.html"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     COMPREHENSIVE CHAPTER ${CHAPTER_NUM} VALIDATION                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# GATE 0: Extraction Validation
# ============================================================================
echo -e "${BLUE}[Gate 0] Extraction Validation${NC}"

[ ! -f "$EXTRACTION_JSON" ] && echo -e "${RED}❌ FAIL: Extraction JSON not found${NC}" && exit 1

PAGE_RANGE=$(python3 -c "import json; data=json.load(open('$EXTRACTION_JSON')); print(data['metadata']['page_range'])" 2>/dev/null || echo "")
[ -z "$PAGE_RANGE" ] && echo -e "${RED}❌ FAIL: Could not extract page range${NC}" && exit 1

START_PAGE=$(echo "$PAGE_RANGE" | cut -d'-' -f1)
END_PAGE=$(echo "$PAGE_RANGE" | cut -d'-' -f2)
TOTAL_PAGES=$((END_PAGE - START_PAGE + 1))

echo -e "${GREEN}✓ Extraction JSON found${NC}"
echo "  Page Range: $PAGE_RANGE ($TOTAL_PAGES pages)"
echo ""

# ============================================================================
# GATE 1: Per-Page Text Verification (CRITICAL)
# ============================================================================
echo -e "${BLUE}[Gate 1] Per-Page Text Verification${NC}"

failed_pages=()
warning_pages=()

for page in $(seq $START_PAGE $END_PAGE); do
    PAGE_HTML="$OUTPUT_DIR/page_artifacts/page_$page/04_page_${page}.html"

    [ ! -f "$PAGE_HTML" ] && echo -e "${RED}❌ FAIL: Page $page HTML not found${NC}" && exit 1

    # Use updated verify_text_content.py with page number
    VERIFY_EXIT=0
    VERIFY_OUTPUT=$(python3 "${PROJECT_DIR}/Calypso/tools/verify_text_content.py" "$CHAPTER_NUM" "$page" 2>&1) || VERIFY_EXIT=$?

    COVERAGE=$(echo "$VERIFY_OUTPUT" | grep "Coverage:" | awk '{print $2}' | sed 's/%//')

    # Check if coverage is numeric
    if ! [[ "$COVERAGE" =~ ^[0-9]+\.?[0-9]*$ ]]; then
        echo -e "${RED}❌ FAIL: Page $page - Could not determine coverage${NC}"
        exit 1
    fi

    # Determine status based on coverage
    if (( $(echo "$COVERAGE < 85" | bc -l) )); then
        echo -e "${RED}  ❌ Page $page: ${COVERAGE}% coverage (CRITICAL FAIL)${NC}"
        failed_pages+=($page)
    elif (( $(echo "$COVERAGE < 95" | bc -l) )); then
        echo -e "${YELLOW}  ⚠️  Page $page: ${COVERAGE}% coverage (WARNING)${NC}"
        warning_pages+=($page)
    else
        echo -e "${GREEN}  ✓ Page $page: ${COVERAGE}% coverage${NC}"
    fi
done

echo ""

# Report failures
if [ ${#failed_pages[@]} -gt 0 ]; then
    echo -e "${RED}❌ GATE 1 FAILED: ${#failed_pages[@]} pages have <85% coverage${NC}"
    echo -e "${RED}   Failed pages: ${failed_pages[*]}${NC}"
    echo ""
    exit 1
fi

if [ ${#warning_pages[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  GATE 1 WARNING: ${#warning_pages[@]} pages have 85-95% coverage${NC}"
    echo -e "${YELLOW}   Warning pages: ${warning_pages[*]}${NC}"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
else
    echo -e "${GREEN}✅ GATE 1 PASSED: All pages have ≥95% text coverage${NC}"
fi

echo ""

# ============================================================================
# GATE 2: Boundary Markers
# ============================================================================
echo -e "${BLUE}[Gate 2] Boundary Markers Validation${NC}"

FIRST_PAGE_HTML="$OUTPUT_DIR/page_artifacts/page_$START_PAGE/04_page_${START_PAGE}.html"
LAST_PAGE_HTML="$OUTPUT_DIR/page_artifacts/page_$END_PAGE/04_page_${END_PAGE}.html"

grep -q "chapter-header\|chapter-number\|chapter-title" "$FIRST_PAGE_HTML" && \
    echo -e "${GREEN}✓ First page ($START_PAGE) has chapter opening markers${NC}" || \
    { echo -e "${RED}❌ FAIL: First page missing opening markers${NC}"; exit 1; }

grep -qi "snapshot review" "$LAST_PAGE_HTML" && \
    echo -e "${GREEN}✓ Last page ($END_PAGE) has 'Snapshot Review' closing marker${NC}" || \
    { echo -e "${RED}❌ FAIL: Last page missing 'Snapshot Review' marker${NC}"; exit 1; }

echo -e "${GREEN}✅ GATE 2 PASSED: Boundary markers present${NC}"
echo ""

# ============================================================================
# GATE 3: HTML Structure
# ============================================================================
echo -e "${BLUE}[Gate 3] HTML Structure Validation${NC}"

[ ! -f "$CHAPTER_HTML" ] && echo -e "${RED}❌ FAIL: Consolidated HTML not found${NC}" && exit 1

VALIDATION_OUTPUT=$(python3 "${PROJECT_DIR}/Calypso/tools/validate_html.py" "$CHAPTER_HTML" 2>&1 || true)

if echo "$VALIDATION_OUTPUT" | grep -qE "Status:.*✓.*VALID|\"error_count\":\s*0"; then
    echo -e "${GREEN}✓ HTML validation passed (0 errors)${NC}"
    echo -e "${GREEN}✅ GATE 3 PASSED: HTML structure valid${NC}"
else
    echo -e "${RED}❌ FAIL: HTML validation errors detected${NC}"
    exit 1
fi

echo ""

# ============================================================================
# GATE 4: Chapter-Level Text
# ============================================================================
echo -e "${BLUE}[Gate 4] Chapter-Level Text Verification${NC}"

CHAPTER_VERIFY_OUTPUT=$(python3 "${PROJECT_DIR}/Calypso/tools/verify_text_content.py" "$CHAPTER_NUM" 2>&1)
CHAPTER_VERIFY_EXIT=$?

CHAPTER_COVERAGE=$(echo "$CHAPTER_VERIFY_OUTPUT" | grep "Coverage:" | awk '{print $2}' | sed 's/%//')

if [ $CHAPTER_VERIFY_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Chapter coverage: ${CHAPTER_COVERAGE}%${NC}"
    echo -e "${GREEN}✅ GATE 4 PASSED: Chapter text coverage ≥95%${NC}"
elif [ $CHAPTER_VERIFY_EXIT -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Chapter coverage: ${CHAPTER_COVERAGE}% (85-95% range)${NC}"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
else
    echo -e "${RED}❌ FAIL: Chapter coverage ${CHAPTER_COVERAGE}% (<85%)${NC}"
    exit 1
fi

echo ""

# ============================================================================
# SUCCESS
# ============================================================================
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ ALL GATES PASSED                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Chapter $CHAPTER_NUM is verified complete and ready for release${NC}"
echo ""

exit 0
