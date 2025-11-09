#!/bin/bash

# Calypso Chapter Boundary Validation Hook
# Validates that chapters meet established standards:
# 1. ASCII preview files show proper opening/closing markers
# 2. HTML files validate with 0 errors
# 3. Chapter boundaries are correct (no orphaned content)
# 4. Progress.md is updated

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
    echo -e "${RED}❌ Usage: calypso-chapter-boundary-validation.sh <chapter_num>${NC}"
    echo "Example: calypso-chapter-boundary-validation.sh 2"
    exit 1
fi

# Pad chapter number to 2 digits
CHAPTER_NUM=$(printf "%02d" "$CHAPTER_NUM")

# Set paths
PROJECT_DIR="/Users/abiezerreyes/Projects/experiment/Plugins_Agents_Skills_Hooks_Slash"
CHAPTER_DIR="${PROJECT_DIR}/Calypso/output/chapter_${CHAPTER_NUM}"
ANALYSIS_DIR="${PROJECT_DIR}/Calypso/analysis/chapter_${CHAPTER_NUM}"
EXTRACTION_JSON="${ANALYSIS_DIR}/rich_extraction.json"
CHAPTER_HTML="${CHAPTER_DIR}/chapter_${CHAPTER_NUM}.html"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Chapter ${CHAPTER_NUM} Boundary Validation${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Track validation results
all_passed=true
validation_results=()

# STEP 1: Verify extraction JSON exists and get page range
echo -e "${BLUE}Step 1: Verifying extraction metadata${NC}"
if [ ! -f "$EXTRACTION_JSON" ]; then
    echo -e "${RED}  ❌ Extraction JSON not found: $EXTRACTION_JSON${NC}"
    all_passed=false
else
    # Extract page range from JSON using jq if available, otherwise use grep
    if command -v jq &> /dev/null; then
        PAGE_RANGE=$(jq -r '.metadata.page_range' "$EXTRACTION_JSON")
        TOTAL_PAGES=$(jq -r '.metadata.total_pages_extracted' "$EXTRACTION_JSON")
    else
        # Fallback to grep-based parsing
        PAGE_RANGE=$(grep -A 2 '"page_range"' "$EXTRACTION_JSON" | head -1 | grep -o '[0-9-]*' | tail -1)
        TOTAL_PAGES=$(grep '"total_pages_extracted"' "$EXTRACTION_JSON" | grep -o '[0-9]*')
    fi

    if [ -z "$PAGE_RANGE" ] || [ "$PAGE_RANGE" = "null" ]; then
        echo -e "${RED}  ❌ Could not extract page range from JSON${NC}"
        all_passed=false
    else
        echo -e "${GREEN}  ✓ Extraction found${NC}"
        echo "    Page Range: $PAGE_RANGE"
        echo "    Total Pages: $TOTAL_PAGES"
        validation_results+=("Extraction Metadata: VALID")
    fi
fi

echo ""

# STEP 2: Check ASCII preview for chapter opening
echo -e "${BLUE}Step 2: Verifying chapter opening markers${NC}"

# Get first page number from page range
FIRST_PAGE=$(echo "$PAGE_RANGE" | cut -d'-' -f1)
FIRST_PAGE_ASCII="${CHAPTER_DIR}/page_artifacts/page_${FIRST_PAGE}/03_page_${FIRST_PAGE}_ascii.txt"

if [ ! -f "$FIRST_PAGE_ASCII" ]; then
    echo -e "${RED}  ❌ ASCII preview not found for first page: $FIRST_PAGE_ASCII${NC}"
    all_passed=false
else
    # Check for opening markers in ASCII file
    # ASCII files have [CHAPTER HEADER - LARGE], [SUBSECTION NAVIGATION HEADINGS], or similar markers
    HAS_CHAPTER_HEADER=$(grep -qE "CHAPTER HEADER|LARGE|Chapter Title" "$FIRST_PAGE_ASCII" 2>/dev/null && echo "yes" || echo "no")
    HAS_NAV=$(grep -qE "NAVIGATION|Navigation|nav-item" "$FIRST_PAGE_ASCII" 2>/dev/null && echo "yes" || echo "no")

    if [ "$HAS_CHAPTER_HEADER" = "yes" ] && [ "$HAS_NAV" = "yes" ]; then
        echo -e "${GREEN}  ✓ Chapter opening markers found on page ${FIRST_PAGE}${NC}"
        echo "    - Chapter header present"
        echo "    - Navigation menu present"
        validation_results+=("Opening Markers: VALID")
    else
        if [ "$HAS_CHAPTER_HEADER" = "yes" ] || [ "$HAS_NAV" = "yes" ]; then
            echo -e "${YELLOW}  ⚠️  Partial opening markers on page ${FIRST_PAGE}${NC}"
            [ "$HAS_CHAPTER_HEADER" = "yes" ] && echo "    ✓ Chapter header found"
            [ "$HAS_NAV" = "yes" ] && echo "    ✓ Navigation found"
            [ "$HAS_CHAPTER_HEADER" = "no" ] && echo "    - Missing chapter header"
            [ "$HAS_NAV" = "no" ] && echo "    - Missing navigation"
        else
            echo -e "${RED}  ❌ No opening markers found on page ${FIRST_PAGE}${NC}"
            all_passed=false
        fi
    fi
fi

echo ""

# STEP 3: Check ASCII preview for chapter closing
echo -e "${BLUE}Step 3: Verifying chapter closing markers${NC}"

LAST_PAGE=$(echo "$PAGE_RANGE" | cut -d'-' -f2)
LAST_PAGE_ASCII="${CHAPTER_DIR}/page_artifacts/page_${LAST_PAGE}/03_page_${LAST_PAGE}_ascii.txt"

if [ ! -f "$LAST_PAGE_ASCII" ]; then
    echo -e "${RED}  ❌ ASCII preview not found for last page: $LAST_PAGE_ASCII${NC}"
    all_passed=false
else
    # Check for closing markers in ASCII file
    HAS_SNAPSHOT=$(grep -q "Snapshot Review\|CLOSING" "$LAST_PAGE_ASCII" 2>/dev/null && echo "yes" || echo "no")
    # Calculate next chapter number for boundary check
    NEXT_CHAPTER_NUM=$(($(echo "$CHAPTER_NUM" | sed 's/^0//') + 1))
    HAS_NEXT_CHAPTER=$(grep -qE "OPENING.*Chapter|Chapter $(printf "%d" "$NEXT_CHAPTER_NUM")" "$LAST_PAGE_ASCII" 2>/dev/null && echo "yes" || echo "no")

    if [ "$HAS_SNAPSHOT" = "yes" ] && [ "$HAS_NEXT_CHAPTER" = "no" ]; then
        echo -e "${GREEN}  ✓ Chapter closing markers found on page ${LAST_PAGE}${NC}"
        echo "    - 'Snapshot Review' section present"
        echo "    - No next chapter content detected"
        validation_results+=("Closing Markers: VALID")
    else
        if [ "$HAS_SNAPSHOT" = "no" ]; then
            echo -e "${YELLOW}  ⚠️  Warning: 'Snapshot Review' not found on page ${LAST_PAGE}${NC}"
        fi
        if [ "$HAS_NEXT_CHAPTER" = "yes" ]; then
            echo -e "${RED}  ❌ ERROR: Next chapter content detected on page ${LAST_PAGE}${NC}"
            all_passed=false
        fi
    fi
fi

echo ""

# STEP 4: Validate HTML structure
echo -e "${BLUE}Step 4: Running HTML validation${NC}"

if [ ! -f "$CHAPTER_HTML" ]; then
    echo -e "${RED}  ❌ Chapter HTML not found: $CHAPTER_HTML${NC}"
    all_passed=false
else
    # Run Python validation
    VALIDATION_OUTPUT=$(python3 "${PROJECT_DIR}/Calypso/tools/validate_html.py" "$CHAPTER_HTML" 2>&1 || true)

    # Check if validation passed (look for "Status: ✓ VALID" or error_count: 0)
    if echo "$VALIDATION_OUTPUT" | grep -qE "Status:.*✓.*VALID|\"error_count\":\s*0"; then
        echo -e "${GREEN}  ✓ HTML validation passed${NC}"

        # Extract error and warning counts
        ERROR_COUNT=$(echo "$VALIDATION_OUTPUT" | grep -o '"error_count":[[:space:]]*[0-9]*' | grep -o '[0-9]*' || echo "0")
        WARNING_COUNT=$(echo "$VALIDATION_OUTPUT" | grep -E "WARNINGS|warnings" | head -1 | grep -o '[0-9]*' || echo "0")

        if [ "$ERROR_COUNT" = "0" ]; then
            echo "    - No structural errors detected"
            [ -n "$WARNING_COUNT" ] && echo "    - $WARNING_COUNT warning(s) (non-blocking)"
        fi
        validation_results+=("HTML Validation: VALID")
    else
        ERROR_COUNT=$(echo "$VALIDATION_OUTPUT" | grep -o '"error_count":[[:space:]]*[0-9]*' | grep -o '[0-9]*' || echo "unknown")
        echo -e "${RED}  ❌ HTML validation found error(s)${NC}"
        echo "$VALIDATION_OUTPUT" | head -30
        all_passed=false
    fi
fi

echo ""

# STEP 5: Verify progress.md is updated
echo -e "${BLUE}Step 5: Checking progress.md status${NC}"

PROGRESS_FILE="${PROJECT_DIR}/Calypso/progress.md"
# Remove leading zero for comparison with progress.md format (uses "2" not "02")
CHAPTER_DISPLAY=$(echo "$CHAPTER_NUM" | sed 's/^0//')

if grep -qE "^\| ${CHAPTER_DISPLAY}[^0-9]" "$PROGRESS_FILE" 2>/dev/null; then
    STATUS=$(grep -E "^\| ${CHAPTER_DISPLAY}[^0-9]" "$PROGRESS_FILE" | grep -o "✅\|⭕" | head -1)
    if [ "$STATUS" = "✅" ]; then
        echo -e "${GREEN}  ✓ Progress.md marked as complete for chapter ${CHAPTER_DISPLAY}${NC}"
        validation_results+=("Progress Tracking: VALID")
    else
        echo -e "${YELLOW}  ⚠️  Progress.md not marked as complete for chapter ${CHAPTER_DISPLAY}${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠️  Chapter ${CHAPTER_DISPLAY} not found in progress.md${NC}"
fi

echo ""

# STEP 6: Summary
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Validation Summary${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Display validation results
for result in "${validation_results[@]}"; do
    echo -e "${GREEN}  ✓${NC} $result"
done

echo ""

if [ "$all_passed" = true ]; then
    echo -e "${GREEN}✅ Chapter ${CHAPTER_NUM} PASSED all validation standards${NC}"
    echo ""
    echo -e "${YELLOW}Ready for:${NC}"
    echo "  • Chapter consolidation"
    echo "  • Git commit with full validation proof"
    echo "  • Moving to next chapter"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Chapter ${CHAPTER_NUM} FAILED validation standards${NC}"
    echo ""
    echo -e "${YELLOW}Issues to fix:${NC}"
    echo "  1. Review ASCII preview files for missing markers"
    echo "  2. Fix HTML validation errors: python3 Calypso/tools/validate_html.py \"$CHAPTER_HTML\""
    echo "  3. Ensure page boundaries are correct in extraction JSON"
    echo "  4. Update progress.md with validation status"
    echo ""
    exit 1
fi
