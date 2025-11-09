#!/bin/bash

# Calypso Visual Accuracy Check Hook (Gate 3 - AI-Based)
# Triggered when Quality Gate 3 fails (ai-visual-accuracy-check)
# AI has compared rendered HTML to original PDF and scored below 85% threshold
# Reports visual accuracy metrics and recommendations

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

# Explain what AI visual accuracy measures
echo -e "${YELLOW}What AI Visual Accuracy Measures (AI Judgment):${NC}"
echo "  • Layout match (40% weight): Overall structure, sections, spacing"
echo "  • Visual hierarchy (30% weight): Emphasis, heading distinction, relationships"
echo "  • Content positioning (20% weight): Alignment, indentation, flow"
echo "  • Typography & styling (10% weight): Font sizes, text styling, readability"
echo ""
echo -e "${YELLOW}AI Visual Accuracy Approach:${NC}"
echo "  • AI compared rendered HTML to original PDF visually"
echo "  • Not pixel-perfect matching, but contextual understanding"
echo "  • Acceptable minor differences: web rendering vs PDF constraints"
echo "  • Scoring focuses on readability and intent preservation"
echo ""

# Provide remediation guidance
echo -e "${YELLOW}Why AI Accuracy May Be Below 85% Threshold:${NC}"
echo "  1. HTML structure doesn't match PDF layout expectations"
echo "  2. Heading hierarchy incorrect or inconsistent across pages"
echo "  3. Spacing/margins differ noticeably from original"
echo "  4. Font sizes or text styling not preserved"
echo "  5. List indentation, alignment, or formatting different"
echo "  6. Visual hierarchy not sufficiently emphasized"
echo "  7. Content flow in continuous format differs from paginated PDF"
echo ""

echo -e "${YELLOW}How to Improve (AI Regeneration):${NC}"
echo "  Option 1: Re-run AI HTML generation with refined prompt"
echo "    • Provide more specific CSS class guidance"
echo "    • Reference the original PDF layout more explicitly"
echo "    • Use more detailed descriptions of visual structure"
echo ""
echo "  Option 2: Check generated semantic class usage"
echo "    ${BLUE}grep -o 'class=\"[^\"]*\"' \"chapter_XX.html\" | sort -u${NC}"
echo "    • Verify classes match skill requirements (page-container, section-heading, etc.)"
echo ""
echo "  Option 3: Manual CSS refinement"
echo "    • Fine-tune styling in main.css for better visual match"
echo "    • Adjust spacing, font sizes, line heights"
echo ""
echo "  Option 4: Accept below-threshold if content is accurate"
echo "    • If AI notes content accuracy is high but styling differs"
echo "    • Document decision and business justification"
echo ""

# Provide threshold context
echo -e "${YELLOW}Similarity Threshold Context:${NC}"
echo "  90-100%: Excellent match, approve for deployment"
echo "  85-90%:  Good match, minor cosmetic differences acceptable"
echo "  80-85%:  Acceptable, but should review differences"
echo "  <80%:    Poor match, requires investigation"
echo ""

# Show AI accuracy report details
echo -e "${YELLOW}AI Visual Accuracy Report:${NC}"
echo "  Report location:"
echo "    ${BLUE}Calypso/output/chapter_${CHAPTER_NUMBER}/chapter_artifacts/ai_visual_accuracy.json${NC}"
echo ""
echo "  Report includes:"
echo "  • AI's detailed visual comparison analysis"
echo "  • Scores for each evaluation criterion"
echo "  • Specific differences noted by AI"
echo "  • Confidence level and explanation"
echo "  • Pass/fail recommendation"
echo ""

# Suggest next steps
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Review the AI accuracy report (ai_visual_accuracy.json)"
echo "  2. Read AI's explanation of why score is below 85%"
echo "  3. Identify if issues are:"
echo "     a) HTML generation issues (re-prompt AI)"
echo "     b) CSS styling issues (update main.css)"
echo "     c) Semantic structure issues (update page HTML)"
echo "  4. Decide: Fix & re-run AI validation, or accept below-threshold"
echo ""
echo "  5. If accepting below-threshold:"
echo "     ${BLUE}Document decision in chapter_artifacts/APPROVAL_DECISION.md${NC}"
echo "     Include: Business justification and approval details"
echo ""

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo -e "${BLUE}Hook triggered at: $TIMESTAMP${NC}"
echo ""

# Note: This is a BLOCKING quality gate
# Visual accuracy must be ≥85% to proceed to deployment
# AI judgment is used to allow contextual understanding
# User can override with documented approval if justified
# Exit code 1 blocks pipeline (as designed)

exit 1
