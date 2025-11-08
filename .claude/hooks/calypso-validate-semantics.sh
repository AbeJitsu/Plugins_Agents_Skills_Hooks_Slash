#!/bin/bash

# Calypso Semantic Validation Hook
# Triggered when Quality Gate 2 fails (html-semantic-validate)
# Reports semantic structure issues and provides remediation guidance

set -e

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${RED}❌ QUALITY GATE 2 FAILED: SEMANTIC VALIDATION${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Extract parameters
CHAPTER_NUMBER=${1:-"unknown"}
HTML_FILE=${2:-"unknown"}
VALIDATION_REPORT=${3:-"unknown"}

echo -e "${YELLOW}Issue Location:${NC}"
echo "  Chapter: $CHAPTER_NUMBER"
echo "  HTML File: $HTML_FILE"
echo "  Validation Report: $VALIDATION_REPORT"
echo ""

# Display validation errors from report
if [ -f "$VALIDATION_REPORT" ]; then
    echo -e "${YELLOW}Semantic Validation Errors:${NC}"
    echo ""

    # Extract error count
    ERROR_COUNT=$(grep -o '"error_count":[0-9]*' "$VALIDATION_REPORT" | grep -o '[0-9]*' || echo "0")

    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo -e "${RED}Found $ERROR_COUNT semantic errors:${NC}"
        echo ""

        # Parse and display errors
        grep -o '"check"[^}]*"message":"[^"]*' "$VALIDATION_REPORT" | \
            sed 's/.*"check":"\([^"]*\)".*"message":"\([^"]*\)"/  • [\1] \2/' || true
        echo ""
    else
        echo -e "${BLUE}No errors, but warnings detected - see below${NC}"
        echo ""
    fi

    # Display warnings if any
    WARNING_COUNT=$(grep -o '"severity":"[^"]*"' "$VALIDATION_REPORT" | wc -l || echo "0")
    if [ "$WARNING_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}Warnings Found ($WARNING_COUNT):${NC}"
        grep -o '"message":"[^"]*"' "$VALIDATION_REPORT" | sed 's/"message":"\(.*\)"/  ⚠️  \1/' || true
        echo ""
    fi
else
    echo -e "${RED}ERROR: Validation report not found at: $VALIDATION_REPORT${NC}"
    echo ""
fi

# Provide guidance on common semantic issues
echo -e "${YELLOW}Common Semantic Issues:${NC}"
echo "  1. Missing required CSS classes (page-container, page-content)"
echo "  2. Incorrect heading hierarchy (h1 → h3 jump, h4 as first heading)"
echo "  3. Headings with no text content"
echo "  4. Lists without proper structure (empty <ul> or unmatched <li>)"
echo "  5. Paragraphs without semantic class"
echo "  6. Missing or inconsistent semantic classes throughout"
echo "  7. Document not in continuous format (contains page breaks)"
echo ""

echo -e "${YELLOW}How to Fix:${NC}"
echo "  1. Review the semantic issues listed above"
echo "  2. Check your CSS class usage:"
echo "     ${BLUE}grep -o 'class=\"[^\"]*\"' \"$HTML_FILE\" | sort -u${NC}"
echo ""
echo "  3. Verify heading hierarchy:"
echo "     ${BLUE}grep -o '<h[1-6]' \"$HTML_FILE\" | sort | uniq -c${NC}"
echo ""
echo "  4. Ensure all major elements have semantic classes"
echo "  5. Re-validate:"
echo "     ${BLUE}python3 Calypso/tools/validate_html.py --semantic \"$HTML_FILE\"${NC}"
echo ""

# Show requirement checklist
echo -e "${YELLOW}Semantic Requirements Checklist:${NC}"
echo "  ☐ Page has <div class=\"page-container\">"
echo "  ☐ Page has <main class=\"page-content\">"
echo "  ☐ Sections use .section-heading (h2)"
echo "  ☐ Subsections use .subsection-heading (h3-h4)"
echo "  ☐ Body text uses .paragraph"
echo "  ☐ Lists use .bullet-list and .bullet-item"
echo "  ☐ Heading hierarchy has no jumps (h1 → h2 → h3)"
echo "  ☐ All elements with text have appropriate semantics"
echo ""

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo -e "${BLUE}Hook triggered at: $TIMESTAMP${NC}"
echo ""

exit 1
