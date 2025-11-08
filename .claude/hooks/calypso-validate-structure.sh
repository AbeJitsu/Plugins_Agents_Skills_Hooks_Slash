#!/bin/bash

# Calypso HTML Structure Validation Hook
# Triggered when Quality Gate 1 fails (html-structure-validate)
# Provides detailed error reporting and guidance for user

set -e

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${RED}❌ QUALITY GATE 1 FAILED: HTML STRUCTURE VALIDATION${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Extract parameters passed to hook
PAGE_NUMBER=${1:-"unknown"}
HTML_FILE=${2:-"unknown"}
VALIDATION_REPORT=${3:-"unknown"}

echo -e "${YELLOW}Issue Location:${NC}"
echo "  Page: $PAGE_NUMBER"
echo "  HTML File: $HTML_FILE"
echo "  Validation Report: $VALIDATION_REPORT"
echo ""

# Check if validation report exists and display errors
if [ -f "$VALIDATION_REPORT" ]; then
    echo -e "${YELLOW}Validation Errors Found:${NC}"
    echo ""

    # Extract error count from JSON report
    ERROR_COUNT=$(grep -o '"error_count":[0-9]*' "$VALIDATION_REPORT" | grep -o '[0-9]*' || echo "0")

    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo -e "${RED}Found $ERROR_COUNT structural errors:${NC}"
        echo ""

        # Display each error (parse from JSON)
        grep -o '"message":"[^"]*"' "$VALIDATION_REPORT" | sed 's/"message":"\(.*\)"/  • \1/' || true
        echo ""
    fi
else
    echo -e "${RED}ERROR: Validation report not found at: $VALIDATION_REPORT${NC}"
    echo ""
fi

# Provide guidance based on common issues
echo -e "${YELLOW}Common Causes:${NC}"
echo "  1. Missing DOCTYPE declaration (<!DOCTYPE html>)"
echo "  2. Unclosed HTML tags (<p>, <div>, <li>, etc.)"
echo "  3. Missing required meta tags (charset, viewport)"
echo "  4. Missing <title> tag"
echo "  5. Missing CSS stylesheet link"
echo "  6. Missing page-container or page-content divs"
echo "  7. Improperly nested tags (e.g., <p><h2>text</h2></p>)"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Review the generated HTML file:"
echo "     ${BLUE}cat \"$HTML_FILE\"${NC}"
echo ""
echo "  2. Review the full validation report:"
echo "     ${BLUE}cat \"$VALIDATION_REPORT\"${NC}"
echo ""
echo "  3. Fix the HTML manually, OR"
echo "  4. Re-run AI generation with improved prompt"
echo ""
echo "  5. After fixing, re-validate:"
echo "     ${BLUE}python3 Calypso/tools/validate_html.py \"$HTML_FILE\"${NC}"
echo ""

# Log timestamp for debugging
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo -e "${BLUE}Hook triggered at: $TIMESTAMP${NC}"
echo ""

# Exit with failure code to stop pipeline
exit 1
