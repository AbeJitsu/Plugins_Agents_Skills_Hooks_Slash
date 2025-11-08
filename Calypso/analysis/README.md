# Analysis Directory Structure

## Root Level
**Active/Current**:
- `page_mapping.json` - **PRIMARY SOURCE OF TRUTH**
  - Authoritative mapping of book pages to metadata
  - Structure: `{"book_page": {"chapter": X, "pdf_index": Y}}`
  - Used by all extraction scripts

## `chapter_01/`
**Chapter 1 Analysis & Reference Files**
- `page_6_pattern_analysis.json` - Text pattern analysis for page 6
- `page_7_pattern_analysis.json` - Text pattern analysis for page 7
- `page_006_hires.png` - High-res reference image of page 6
- `page_007_hires.png` - High-res reference image of page 7
- `rich_extraction.json` - Detailed extraction data for pages 6-14

**Purpose**: Contains working analysis files and reference materials for Chapter 1 extraction and validation.

## `_archive/`
**Legacy/Historical Files** (Not actively used)
- `chapter_map.json` - Table of contents analysis
- `conversion_rules.json` - Font/style conversion rules from initial analysis
- `patterns.json` - General text and font patterns from analysis
- `fitz_output.json` - Raw PyMuPDF extraction output
- `pdfplumber_output.json` - Raw pdfplumber extraction output
- `ocr_output.json` - OCR output (empty)

**Purpose**: Reference materials from early extraction experiments. Kept for historical reference but not needed for active workflow.

## Workflow
1. **Extract new chapters** → Update `page_mapping.json` with footer scan results
2. **Organize by chapter** → Create `chapter_XX/` folders as needed
3. **Archive old work** → Move experimental/legacy files to `_archive/`

## Key Points
- Single source of truth: `page_mapping.json`
- Book page numbers only (PDF indices are internal)
- Each chapter has its own analysis folder with reference materials
