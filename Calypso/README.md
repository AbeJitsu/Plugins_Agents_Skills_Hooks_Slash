# Calypso - PDF to HTML Conversion Project

This project extracts and converts PDF content into well-structured HTML with semantic classes and a separate stylesheet.

## Project Structure

```
Calypso/
├── analysis/          # First page extracts for TOC analysis
├── chapters/          # Extracted chapter data organized by chapter
├── output/            # Final HTML files and styles
│   └── styles/        # CSS stylesheets
├── tools/             # Python scripts for extraction and conversion
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Libraries Used

- **pdfplumber** - Text and layout extraction with positioning data
- **PyMuPDF (fitz)** - Image extraction, fonts, and metadata
- **pdf2image** - Convert PDF pages to images for visual analysis
- **Pillow** - Image processing
- **pytesseract** - OCR fallback for difficult sections

## Workflow

1. **TOC Analysis** - Extract first pages to analyze table of contents
2. **Pattern Detection** - Identify heading styles, layouts, and structures
3. **Chapter Extraction** - Split PDF by chapters
4. **HTML Conversion** - Generate clean, semantic HTML with linked CSS

## Setup

```bash
pip install -r requirements.txt
```

## Scripts

- `tools/toc_analyzer.py` - Analyzes table of contents
- `tools/pattern_detector.py` - Detects visual patterns
- `tools/chapter_extractor.py` - Extracts chapters
- `tools/html_converter.py` - Converts to HTML with CSS
