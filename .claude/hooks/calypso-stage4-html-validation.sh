#!/bin/bash

# Stage 4: HTML Validation Hook - Comprehensive 3-Part Validation
# Validates text coverage, HTML structure, and AI visual similarity
# Usage: ./calypso-stage4-html-validation.sh <chapter> <page>
# Exit codes: 0 (pass), 1 (warning), 2 (fail)

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHAPTER=$1
PAGE=$2
PROJECT_DIR="/Users/abiezerreyes/Projects/experiment/Plugins_Agents_Skills_Hooks_Slash"

if [ -z "$CHAPTER" ] || [ -z "$PAGE" ]; then
    echo -e "${RED}Usage: $0 <chapter> <page>${NC}"
    exit 1
fi

CHAPTER_PADDED=$(printf "%02d" "$CHAPTER")
PAGE_DIR="${PROJECT_DIR}/Calypso/output/chapter_${CHAPTER_PADDED}/page_artifacts/page_${PAGE}"
PAGE_HTML="${PAGE_DIR}/04_page_${PAGE}.html"
PAGE_PNG="${PAGE_DIR}/02_page_${PAGE}.png"

# Initialize state manager
STATE_MANAGER="${PROJECT_DIR}/Calypso/tools/validation_state_manager.py"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     STAGE 4 VALIDATION - Chapter ${CHAPTER} Page ${PAGE}                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verify files exist
if [ ! -f "$PAGE_HTML" ]; then
    echo -e "${RED}❌ FAIL: Page HTML not found: $PAGE_HTML${NC}"
    python3 "$STATE_MANAGER" "$CHAPTER" "$PAGE" || true
    exit 2
fi

if [ ! -f "$PAGE_PNG" ]; then
    echo -e "${RED}❌ FAIL: Page PNG not found: $PAGE_PNG${NC}"
    python3 "$STATE_MANAGER" "$CHAPTER" "$PAGE" || true
    exit 2
fi

# ============================================================================
# PART 1: TEXT COVERAGE VALIDATION
# ============================================================================
echo -e "${BLUE}[Part 1] Text Coverage Validation${NC}"

EXTRACTION_JSON="${PROJECT_DIR}/Calypso/analysis/chapter_${CHAPTER_PADDED}/rich_extraction.json"

TEXT_OUTPUT=$(python3 "${PROJECT_DIR}/Calypso/tools/verify_text_content.py" "$CHAPTER" "$PAGE" 2>&1)
TEXT_EXIT=$?

COVERAGE=$(echo "$TEXT_OUTPUT" | grep "Coverage:" | awk '{print $2}' | sed 's/%//')

if ! [[ "$COVERAGE" =~ ^[0-9]+\.?[0-9]*$ ]]; then
    echo -e "${RED}❌ FAIL: Could not determine text coverage${NC}"
    exit 2
fi

# Evaluate text coverage
if (( $(echo "$COVERAGE < 85" | bc -l) )); then
    echo -e "${RED}  ❌ Text coverage: ${COVERAGE}% (CRITICAL FAIL - need ≥95%)${NC}"
    TEXT_STATUS="fail"
    TEXT_SCORE=$COVERAGE
elif (( $(echo "$COVERAGE < 95" | bc -l) )); then
    echo -e "${YELLOW}  ⚠️  Text coverage: ${COVERAGE}% (WARNING - should be ≥95%)${NC}"
    TEXT_STATUS="warning"
    TEXT_SCORE=$COVERAGE
else
    echo -e "${GREEN}  ✓ Text coverage: ${COVERAGE}% (PASS)${NC}"
    TEXT_STATUS="pass"
    TEXT_SCORE=$COVERAGE
fi

echo ""

# ============================================================================
# PART 2: HTML STRUCTURE VALIDATION
# ============================================================================
echo -e "${BLUE}[Part 2] HTML Structure Validation${NC}"

HTML_OUTPUT=$(python3 "${PROJECT_DIR}/Calypso/tools/validate_html.py" "$PAGE_HTML" 2>&1 || true)

if echo "$HTML_OUTPUT" | grep -qE "Status:.*✓.*VALID|error_count.*0"; then
    echo -e "${GREEN}  ✓ HTML structure is valid (0 errors)${NC}"
    HTML_STATUS="pass"
    HTML_SCORE=100
else
    echo -e "${RED}  ❌ HTML structure has errors${NC}"
    HTML_STATUS="fail"
    HTML_SCORE=0
    # Show errors
    echo "$HTML_OUTPUT" | grep -E "error|Error|ERROR" || true
fi

echo ""

# ============================================================================
# PART 3: VISUAL ACCURACY VALIDATION NOTE
# ============================================================================
echo -e "${BLUE}[Part 3] Visual Accuracy Validation${NC}"
echo -e "${YELLOW}ℹ️  Visual accuracy check requires Claude Code vision analysis${NC}"
echo ""
echo "    To validate visual accuracy for this page:"
echo "    → Invoke skill: visual-accuracy-check"
echo "    → Input: Chapter ${CHAPTER}, Page ${PAGE}"
echo ""
echo "    This will compare PNG source against HTML for:"
echo "    • Layout accuracy (0-100%)"
echo "    • Content presentation (0-100%)"
echo "    • Visual hierarchy (0-100%)"
echo "    • Formatting details (0-100%)"
echo "    • Completeness (0-100%)"
echo ""
VISUAL_STATUS="pending"
echo ""

# ============================================================================
# RESULTS SUMMARY
# ============================================================================
echo -e "${BLUE}[Summary] Validation Results${NC}"

OVERALL_STATUS="pass"
FAILURE_REASONS=()

# Check for failures
if [ "$TEXT_STATUS" = "fail" ] || [ "$HTML_STATUS" = "fail" ] || [ "$VISUAL_STATUS" = "fail" ]; then
    OVERALL_STATUS="fail"

    if [ "$TEXT_STATUS" = "fail" ]; then
        FAILURE_REASONS+=("Text coverage ${COVERAGE}% (need ≥95%)")
    fi

    if [ "$HTML_STATUS" = "fail" ]; then
        FAILURE_REASONS+=("HTML structure has errors")
    fi

    if [ "$VISUAL_STATUS" = "fail" ]; then
        FAILURE_REASONS+=("Visual similarity ${VISUAL_SCORE}% (need ≥80%)")
    fi
fi

# Check for warnings
if [ "$OVERALL_STATUS" = "pass" ] && ([ "$TEXT_STATUS" = "warning" ] || [ "$VISUAL_STATUS" = "warning" ]); then
    OVERALL_STATUS="warning"
fi

# Display summary
echo ""
echo -e "Text Coverage:      ${COVERAGE}% - ${TEXT_STATUS}"
echo -e "HTML Structure:     ${HTML_STATUS}"
echo -e "Visual Accuracy:    ${VISUAL_STATUS} (requires skill invocation)"
echo ""

# ============================================================================
# RECORD STATE
# ============================================================================
python3 "$STATE_MANAGER" "$CHAPTER" "$PAGE" >> /dev/null 2>&1 || true

echo ""

# ============================================================================
# FINAL DECISION
# ============================================================================
if [ "$OVERALL_STATUS" = "fail" ]; then
    echo -e "${RED}❌ STAGE 4 FAILED: Page $PAGE needs regeneration${NC}"
    echo ""
    echo "Issues found:"
    for reason in "${FAILURE_REASONS[@]}"; do
        echo "  • $reason"
    done
    echo ""
    echo -e "${YELLOW}→ Next steps:${NC}"
    echo "  1. Regenerate page with feedback on missing/incorrect content"
    echo "  2. Re-run text coverage check (must be ≥95%)"
    echo "  3. Re-run HTML structure check (must be 0 errors)"
    echo "  4. Invoke visual-accuracy-check skill for visual validation"
    echo ""
    exit 2

elif [ "$OVERALL_STATUS" = "warning" ]; then
    echo -e "${YELLOW}⚠️  STAGE 4 WARNING: Minor issues detected${NC}"
    echo "  Text coverage or HTML structure below ideal threshold"
    echo ""
    echo -e "${YELLOW}→ Next steps:${NC}"
    echo "  1. Consider regenerating page to reach ≥95% text coverage"
    echo "  2. After regeneration, invoke visual-accuracy-check skill"
    echo ""
    exit 1

else
    # OVERALL_STATUS = "pass" - text and structure both passed
    echo -e "${GREEN}✅ STAGE 4 PARTS 1-2 PASSED: Text and structure validated${NC}"
    echo ""
    echo -e "${YELLOW}→ Next: Complete validation with visual-accuracy-check skill${NC}"
    echo "  Run the skill to verify visual similarity ≥80%"
    echo "  Then page is ready for consolidation"
    echo ""
    exit 0
fi
