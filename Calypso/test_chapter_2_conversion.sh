#!/bin/bash

# Test Calypso Skill System on Chapter 2
# Full end-to-end test of PDF → HTML conversion pipeline
#
# This script demonstrates the complete workflow:
# 1. Extract data from Chapter 2 pages
# 2. Generate ASCII preview (AI)
# 3. Generate HTML (AI)
# 4. Validate structure (Python)
# 5. Compare visually (AI)

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  CALYPSO CHAPTER 2 CONVERSION TEST                             ║"
echo "║  Testing complete skill-based PDF-to-HTML pipeline             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
PDF_PATH="PREP-AL 4th Ed 9-26-25.pdf"
CHAPTER=2
PAGES_START=15
PAGES_END=28
OUTPUT_BASE="output"
ANALYSIS_BASE="analysis"
TOOLS_DIR="tools"

echo "📋 CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PDF: $PDF_PATH"
echo "Chapter: $CHAPTER"
echo "Pages: $PAGES_START-$PAGES_END"
echo "Output: $OUTPUT_BASE/chapter_${CHAPTER:=02}"
echo ""

# Step 1: Extract data from Chapter 2
echo "🔧 STEP 1: Extract PDF Data (Skill 1: pdf-page-extract)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create directories
mkdir -p "$OUTPUT_BASE/chapter_02/page_artifacts"
mkdir -p "$ANALYSIS_BASE/chapter_02"

# Extract rich data for Chapter 2
echo "⏳ Extracting rich text data from pages $PAGES_START-$PAGES_END..."
python3 "$TOOLS_DIR/rich_extractor.py" \
  --pdf "$PDF_PATH" \
  --start $PAGES_START \
  --end $PAGES_END \
  --output "$ANALYSIS_BASE/chapter_02/rich_extraction.json" 2>/dev/null

if [ -f "$ANALYSIS_BASE/chapter_02/rich_extraction.json" ]; then
  echo "✅ Rich extraction complete: $ANALYSIS_BASE/chapter_02/rich_extraction.json"
  EXTRACTED_PAGES=$(grep -o '"page_number"' "$ANALYSIS_BASE/chapter_02/rich_extraction.json" | wc -l)
  echo "   $EXTRACTED_PAGES pages extracted"
else
  echo "❌ Rich extraction failed"
  exit 1
fi

# Extract images for Chapter 2
echo "⏳ Extracting images from Chapter 2 pages..."
mkdir -p "$OUTPUT_BASE/chapter_02/images/chapter_02"
python3 "$TOOLS_DIR/extract_images.py" \
  --chapter 2 \
  --pages $PAGES_START-$PAGES_END \
  --pdf "$PDF_PATH" \
  --output "$OUTPUT_BASE" \
  --mapping "$ANALYSIS_BASE/page_mapping.json" 2>/dev/null

echo "✅ Image extraction complete"
echo ""

# Step 2: Show what we have
echo "📊 DATA EXTRACTED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Rich text extraction: $ANALYSIS_BASE/chapter_02/rich_extraction.json"
echo "✅ Images: $OUTPUT_BASE/chapter_02/images/chapter_02/"
echo ""

# Step 3: Manual AI Generation Instructions
echo "🤖 NEXT STEPS: AI Generation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "The following steps require AI generation (Claude API):"
echo ""
echo "1️⃣  SKILL 2: Generate ASCII Preview"
echo "   Input: "
echo "     • PNG image: Render pages 15-28 from PDF"
echo "     • Rich extraction: $ANALYSIS_BASE/chapter_02/rich_extraction.json"
echo "   Output:"
echo "     • ASCII text preview: $OUTPUT_BASE/chapter_02/page_artifacts/page_XX/03_page_XX_ascii.txt"
echo ""
echo "2️⃣  SKILL 3: Generate HTML"
echo "   Input:"
echo "     • PNG image: $OUTPUT_BASE/chapter_02/page_artifacts/page_XX/02_page_XX.png"
echo "     • Rich extraction: $ANALYSIS_BASE/chapter_02/rich_extraction.json"
echo "     • ASCII preview: (generated in step 1)"
echo "   Output:"
echo "     • HTML: $OUTPUT_BASE/chapter_02/page_artifacts/page_XX/04_page_XX.html"
echo ""
echo "3️⃣  SKILL 4: Consolidate Pages"
echo "   Input: All page_XX.html files (pages 15-28)"
echo "   Output:"
echo "     • Consolidated: $OUTPUT_BASE/chapter_02/chapter_02.html"
echo ""
echo "Commands to render PDF pages to PNG:"
echo ""
echo "  python3 << 'PYEOF'"
echo "  import fitz"
echo "  pdf = fitz.open('$PDF_PATH')"
echo "  for idx in range($PAGES_START, $PAGES_END + 1):"
echo "    page = pdf[idx]"
echo "    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))"
echo "    pix.save('$OUTPUT_BASE/chapter_02/page_artifacts/page_{:02d}/02_page_{:02d}.png'.format(idx, idx))"
echo "  pdf.close()"
echo "  PYEOF"
echo ""

# Step 4: Validation instructions
echo "✔️  VALIDATION GATES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Gate 1: HTML Structure Validation (Python)"
echo "  Command: python3 $TOOLS_DIR/validate_html.py $OUTPUT_BASE/chapter_02/chapter_02.html"
echo ""
echo "Gate 2: Semantic Validation (Python)"
echo "  Command: python3 $TOOLS_DIR/validate_html.py $OUTPUT_BASE/chapter_02/chapter_02.html"
echo ""
echo "Gate 3: Visual Accuracy Check (AI)"
echo "  Compare: Original PDF PNG + Rendered HTML PNG"
echo "  AI scores on: Layout (40%), Hierarchy (30%), Positioning (20%), Typography (10%)"
echo ""

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  READY FOR AI GENERATION TEST                                  ║"
echo "║  All extraction complete. Data ready for Skills 2-4.           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "To manually test the full pipeline:"
echo ""
echo "1. Use Claude to generate ASCII preview (Skill 2)"
echo "2. Use Claude to generate HTML (Skill 3)"
echo "3. Run: python3 $TOOLS_DIR/validate_html.py <html_file>"
echo "4. Use Claude to compare visually (Gate 3)"
echo ""
