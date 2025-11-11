#!/bin/bash

# Calypso Gate 1: Per-Page Text Verification Hook
# MANDATORY: Verifies all individual pages pass text content validation BEFORE consolidation
# Blocks consolidation if any page has <85% text coverage or wrong content detected
#
# This fail-safe prevents incorrect content from being consolidated into chapters
# Exit codes: 0 = all pages pass, 1 = consolidation blocked

set -e

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get chapter number from parameter
CHAPTER_NUM=${1:-""}

if [ -z "$CHAPTER_NUM" ]; then
    echo -e "${RED}❌ Usage: calypso-gate1-per-page-verification.sh <chapter_num>${NC}"
    echo "Example: calypso-gate1-per-page-verification.sh 1"
    exit 1
fi

# Pad chapter number to 2 digits
CHAPTER_NUM=$(printf "%02d" "$CHAPTER_NUM")
CHAPTER_DISPLAY=$(echo "$CHAPTER_NUM" | sed 's/^0//')

# Set paths
PROJECT_DIR="/Users/abiezerreyes/Projects/experiment/Plugins_Agents_Skills_Hooks_Slash"
CHAPTER_DIR="${PROJECT_DIR}/Calypso/output/chapter_${CHAPTER_NUM}"
ANALYSIS_DIR="${PROJECT_DIR}/Calypso/analysis/chapter_${CHAPTER_NUM}"
EXTRACTION_JSON="${ANALYSIS_DIR}/rich_extraction.json"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}GATE 1: Per-Page Text Verification (Chapter ${CHAPTER_DISPLAY})${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Verify extraction JSON exists
if [ ! -f "$EXTRACTION_JSON" ]; then
    echo -e "${RED}❌ Extraction JSON not found: $EXTRACTION_JSON${NC}"
    exit 1
fi

# Extract page range from JSON
if command -v jq &> /dev/null; then
    PAGE_RANGE=$(jq -r '.metadata.page_range' "$EXTRACTION_JSON")
    TOTAL_PAGES=$(jq -r '.metadata.total_pages_extracted' "$EXTRACTION_JSON")
else
    # Fallback parsing
    PAGE_RANGE=$(grep -A 2 '"page_range"' "$EXTRACTION_JSON" | head -1 | grep -o '[0-9-]*' | tail -1)
    TOTAL_PAGES=$(grep '"total_pages_extracted' "$EXTRACTION_JSON" | grep -o '[0-9]*' | head -1)
fi

if [ -z "$PAGE_RANGE" ]; then
    echo -e "${RED}❌ Could not extract page range from JSON${NC}"
    exit 1
fi

echo -e "${BLUE}Verifying pages: $PAGE_RANGE ($TOTAL_PAGES pages total)${NC}"
echo ""

# Parse page range
FIRST_PAGE=$(echo "$PAGE_RANGE" | cut -d'-' -f1)
LAST_PAGE=$(echo "$PAGE_RANGE" | cut -d'-' -f2)

# Track results
all_passed=true
failed_pages=()
warning_pages=()
passed_pages=()

# Verify each page
for page_num in $(seq "$FIRST_PAGE" "$LAST_PAGE"); do
    # Pad to 2 digits or use as-is depending on convention
    page_display="$page_num"

    echo -n "Page $page_display: "

    # Run verification (suppress stderr, capture output)
    verify_output=$(python3 "${PROJECT_DIR}/Calypso/tools/verify_text_content.py" "$CHAPTER_DISPLAY" "$page_display" 2>&1 || true)

    # Extract coverage percentage
    coverage=$(echo "$verify_output" | grep -oE "Coverage:[[:space:]]*[0-9]+(\.[0-9]+)?" | grep -oE "[0-9]+(\.[0-9]+)?" || echo "0")

    if [ -z "$coverage" ]; then
        # Try alternate format
        coverage=$(echo "$verify_output" | grep -oE "[0-9]+(\.[0-9]+)?%" | grep -oE "[0-9]+(\.[0-9]+)?" | head -1 || echo "0")
    fi

    # Determine status based on coverage
    # Validation ranges (strict - >99% to 100% acceptable window):
    # - >100% = FAIL (extra content, not allowed)
    # - >99% to 100% = PASS (acceptable, accounting for headers/footers being filtered)
    # - ≤99% to 85% = FAIL (missing or boundary content)
    # - <85% = FAIL (missing critical content)

    if (( $(echo "$coverage > 100" | bc -l) )); then
        # Over 100% = extra content (not allowed)
        echo -e "${RED}❌ FAIL - EXTRA CONTENT ($coverage% coverage = content added that wasn't in original)${NC}"
        all_passed=false
        failed_pages+=("$page_display")
    elif (( $(echo "$coverage > 99" | bc -l) )); then
        # >99% to 100% = PASS (acceptable range)
        if (( $(echo "$coverage >= 99.5" | bc -l) )); then
            # Near perfect
            echo -e "${GREEN}✓ PASS - EXCELLENT ($coverage% coverage)${NC}"
        else
            # Acceptable with minor differences
            echo -e "${GREEN}✓ PASS ($coverage% coverage)${NC}"
        fi
        passed_pages+=("$page_display")
    else
        # Coverage ≤ 99% = FAIL (per user requirement)
        echo -e "${RED}❌ FAIL - MISSING/BOUNDARY CONTENT ($coverage% coverage - must be >99%)${NC}"
        all_passed=false
        failed_pages+=("$page_display")
    fi
done

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Verification Summary${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Summary counts
passed_count=${#passed_pages[@]}
warning_count=${#warning_pages[@]}
failed_count=${#failed_pages[@]}

echo -e "${GREEN}✓ Passed:${NC} $passed_count pages"
echo -e "${YELLOW}⚠️  Warnings:${NC} $warning_count pages"
echo -e "${RED}❌ Failed:${NC} $failed_count pages"
echo ""

# Show which pages failed
if [ ${#failed_pages[@]} -gt 0 ]; then
    echo -e "${RED}Failed pages (>100% or <85% coverage):${NC}"
    for page in "${failed_pages[@]}"; do
        echo "  ❌ Page $page"
    done
    echo ""
fi

# Show which pages have warnings
if [ ${#warning_pages[@]} -gt 0 ]; then
    echo -e "${YELLOW}Pages needing review (85-95% coverage):${NC}"
    for page in "${warning_pages[@]}"; do
        echo "  ⚠️  Page $page"
    done
    echo ""
fi

# Final decision
echo -e "${CYAN}CONSOLIDATION DECISION:${NC}"
echo ""

if [ "$all_passed" = true ]; then
    if [ ${#warning_pages[@]} -eq 0 ]; then
        # Perfect - all passed
        echo -e "${GREEN}✅ ALL PAGES PASS GATE 1${NC}"
        echo -e "Ready to consolidate chapter ${CHAPTER_DISPLAY}${NC}"
        echo ""
        echo "Next step:"
        echo "  1. Run Skill 4 to consolidate pages into chapter_${CHAPTER_DISPLAY}.html"
        echo "  2. Run final validation: ./Calypso/tools/verify_chapter_complete.sh ${CHAPTER_DISPLAY}"
        echo "  3. Commit with proof of validation"
        echo ""
        exit 0
    else
        # All passed but some have warnings
        echo -e "${YELLOW}✓ ALL PAGES PASS (with warnings)${NC}"
        echo -e "Pages ${warning_pages[@]} have coverage 85-95% - review recommended"
        echo ""
        echo "You may consolidate, but review these pages first:"
        for page in "${warning_pages[@]}"; do
            echo "  - Page $page (check for missing content)"
        done
        echo ""
        exit 0
    fi
else
    # Critical failures - block consolidation
    echo -e "${RED}❌ GATE 1 FAILED - CONSOLIDATION BLOCKED${NC}"
    echo ""
    echo "Reason: ${failed_count} page(s) have content issues"
    echo ""
    echo "DO NOT CONSOLIDATE. Instead:"
    echo "  1. Review failed pages in detail"
    echo "  2. Check if wrong page content is present (coverage >105%)"
    echo "  3. Regenerate failed pages with AI Skill 3"
    echo "  4. Re-run this verification after regeneration"
    echo ""
    echo "Failed pages that need regeneration:"
    for page in "${failed_pages[@]}"; do
        echo "  - Page $page"
    done
    echo ""
    exit 1
fi
