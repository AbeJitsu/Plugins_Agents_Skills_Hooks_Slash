#!/bin/bash

# Calypso Visual Accuracy Check Hook
# Triggered when Quality Gate 3 fails (visual-accuracy-check)
# Reports visual differences and comparison metrics

set -e

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${RED}⚠️  QUALITY GATE 3 FAILED: VISUAL ACCURACY CHECK${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Extract parameters
CHAPTER_NUMBER=${1:-"unknown"}
QUALITY_REPORT=${2:-"unknown"}
THRESHOLD=${3:-"85"}

echo -e "${YELLOW}Issue Location:${NC}"
echo "  Chapter: $CHAPTER_NUMBER"
echo "  Quality Report: $QUALITY_REPORT"
echo "  Threshold: $THRESHOLD%"
echo ""

# Read and display accuracy metrics from report
if [ -f "$QUALITY_REPORT" ]; then
    echo -e "${YELLOW}Visual Accuracy Results:${NC}"
    echo ""

    # Extract overall similarity
    OVERALL_SIM=$(grep -o '"overall_similarity":[0-9.]*' "$QUALITY_REPORT" | grep -o '[0-9.]*' || echo "0")
    PERCENT=$(echo "$OVERALL_SIM * 100" | bc -l 2>/dev/null | xargs printf "%.1f" || echo "$OVERALL_SIM")

    if (( $(echo "$OVERALL_SIM < 0.85" | bc -l) )); then
        echo -e "${RED}Overall Similarity: ${PERCENT}% (below ${THRESHOLD}% threshold)${NC}"
    else
        echo -e "${YELLOW}Overall Similarity: ${PERCENT}% (near threshold)${NC}"
    fi
    echo ""

    # Show per-page results
    echo -e "${YELLOW}Per-Page Breakdown:${NC}"
    echo ""

    # Parse page results (this is a simplified version - adjust based on actual JSON structure)
    grep -o '"page":[0-9]*.*"similarity":[0-9.]*' "$QUALITY_REPORT" 2>/dev/null | \
        sed 's/"page":\([0-9]*\).*"similarity":\([0-9.]*\)/  Page \1: \2/' || \
        echo "  (Unable to parse per-page results)"
    echo ""

else
    echo -e "${RED}ERROR: Quality report not found at: $QUALITY_REPORT${NC}"
    echo ""
fi

# Explain what visual accuracy means
echo -e "${YELLOW}What Visual Accuracy Measures:${NC}"
echo "  • Layout matching: How well the generated HTML matches PDF layout"
echo "  • Element positioning: Correct placement of headings, paragraphs, lists"
echo "  • Content formatting: Text sizes, spacing, alignment"
echo "  • Visual hierarchy: Proper visual distinction of sections"
echo ""

# Provide remediation guidance
echo -e "${YELLOW}Why Accuracy May Be Below Threshold:${NC}"
echo "  1. CSS styling not applied correctly"
echo "  2. Heading hierarchy incorrect (affects visual hierarchy)"
echo "  3. Spacing/margins differ from original"
echo "  4. Font sizes or styles not matching"
echo "  5. List indentation or bullets different"
echo "  6. Page structure doesn't match continuous format"
echo ""

echo -e "${YELLOW}How to Improve:${NC}"
echo "  Option 1: Review and adjust CSS styling"
echo "    ${BLUE}cat Calypso/output/styles/main.css${NC}"
echo ""
echo "  Option 2: Check semantic class usage"
echo "    ${BLUE}grep -o 'class=\"[^\"]*\"' \"chapter_XX.html\" | sort -u${NC}"
echo ""
echo "  Option 3: Re-generate with improved AI prompt"
echo "    • Provide more specific layout guidance in prompt"
echo "    • Include visual reference (PNG) in AI prompt"
echo ""
echo "  Option 4: Manual adjustment of styling"
echo "    • Override CSS for specific elements"
echo "    • Fine-tune spacing and formatting"
echo ""
echo "  Option 5: Lower acceptance threshold (if acceptable)"
echo "    • If content is accurate but styling differs"
echo "    • Document decision and reasoning"
echo ""

# Provide threshold context
echo -e "${YELLOW}Similarity Threshold Context:${NC}"
echo "  90-100%: Excellent match, approve for deployment"
echo "  85-90%:  Good match, minor cosmetic differences acceptable"
echo "  80-85%:  Acceptable, but should review differences"
echo "  <80%:    Poor match, requires investigation"
echo ""

# Show command to review diff images
echo -e "${YELLOW}Review Visual Differences:${NC}"
echo "  Difference images saved to:"
echo "    ${BLUE}Calypso/output/chapter_${CHAPTER_NUMBER}/chapter_artifacts/diff_images/${NC}"
echo ""
echo "  These images highlight areas where generated HTML differs from PDF"
echo "  Red/highlighted areas show mismatches"
echo ""

# Suggest next steps
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Review the diff_images/ directory to see specific differences"
echo "  2. Determine root cause (CSS, layout, semantic structure)"
echo "  3. Make corrections as needed"
echo "  4. Re-validate:"
echo "     ${BLUE}python3 Calypso/tools/visual_diff_checker.py\"${NC}"
echo ""
echo "  5. Option to accept below-threshold if content is accurate"
echo "     (Document decision: why visual difference is acceptable)"
echo ""

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo -e "${BLUE}Hook triggered at: $TIMESTAMP${NC}"
echo ""

# Note: This is a non-blocking warning by design
# Visual accuracy failures may be acceptable if content is correct
# This allows user to override if justified

exit 1
