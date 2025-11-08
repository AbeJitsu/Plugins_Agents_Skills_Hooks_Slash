# PDF Index Mapping - Off-by-One Fix

## The Problem

Throughout the codebase, there was confusion between **PDF page indices** (0-based) and **book page numbers** (1-based, displayed in footers).

**Example: PDF Index 6 = Book Page 7**
- Footer text in the PDF says: "Chapter 1: The Real Estate Business 7"
- But the file was being called "page_6_reference.html"
- This created constant confusion: "Am I looking at page 6 or page 7?"

## The Solution

All code now consistently uses this mapping:

### PDF Index (0-based)
- Used internally in code: `pdf_index`, `page_num`, `start_idx`, `end_idx`
- Example: `page_6_reference.html` extracts PDF index 6
- Ranges: 0, 1, 2, ... 592

### Book Page Number (1-based)
- Displayed in PDF footers and titles
- Example: PDF index 6 → book page 7 (footer shows "7")
- Ranges: 1, 2, 3, ... 593

### Mapping Rule

```python
# PDF index 0-5 = Front matter (no book page)
# PDF index 6+ = Book page = PDF index + 1

def pdf_index_to_book_page(pdf_index):
    if pdf_index < 6:
        return None  # Front matter, no book page
    return pdf_index + 1  # Book page = PDF index + 1

# Examples:
pdf_index_to_book_page(0)  # → None (front matter)
pdf_index_to_book_page(5)  # → None (front matter)
pdf_index_to_book_page(6)  # → 7   (first content page)
pdf_index_to_book_page(7)  # → 8
pdf_index_to_book_page(14) # → 15
```

## Chapter 1 Example

Chapter 1 covers **PDF indices 6-14**, which are **book pages 7-15**:

| PDF Index | Book Page | Content |
|-----------|-----------|---------|
| 6 | 7 | Start of Chapter 1 ("Real Estate Professions") |
| 7 | 8 | Continues with subsections |
| ... | ... | |
| 14 | 15 | End of Chapter 1 summary |

## How This Fixes the Naming

### Before (Confusing)
```
page_6_reference.html        # But footer says "Page 7" - confusing!
chapter_1.html               # Supposed to be pages 6-14 (but is that PDF indices or book pages?)
--chapter 1 --pages 6-14     # Ambiguous: which indexing system?
```

### After (Clear)
```
page_6_reference.html        # Clearly: PDF index 6 (book page 7)
chapter_1.html               # Clearly: PDF indices 6-14 (book pages 7-15)
--chapter 1 --pages 6-14     # Clear: These are PDF indices (help text explains mapping)
```

## Files Updated

1. **semantic_html_generator.py**
   - Updated `pdf_index_to_book_page()` documentation with examples
   - Updated `CHAPTER_BOUNDARIES` comment to clarify it uses PDF indices
   - Updated `generate_html()` to use `pdf_index_to_book_page()` consistently
   - Updated argument help text to clarify PDF index vs book page

2. **rich_extractor.py**
   - Updated module docstring with PDF index mapping
   - Updated `extract_rich_page_data()` to clarify `page_num` is PDF index
   - Added comments clarifying `page_number` vs `book_page` in output

3. **PAGE_6_CHECKLIST.md**
   - Added header: "PDF Index 6 (Book Page 7) Implementation Checklist"
   - Added note about the mapping

4. **CALYPSO_STRUCTURE.md**
   - Added "PDF Index Mapping" section with clear table
   - Updated section heading to "PDF Index 6 (Book Page 7) Reference Structure"

## Usage Examples

### Generate Chapter 1 (PDF indices 6-14, book pages 7-15)
```bash
python3 semantic_html_generator.py --chapter 1
# Output: output/chapter_01.html
# Title will show: "Pages 7-15"
```

### Generate single page (PDF index 6 = book page 7)
```bash
python3 semantic_html_generator.py --page 6
# Output: output/page_6.html
# Title will show: "Page 7"
```

### Generate page range (PDF indices 10-12 = book pages 11-13)
```bash
python3 semantic_html_generator.py --pages 10-12
# Output: output/pages_10_12.html
# Title will show: "Pages 11-13"
```

## What Changed in the Code

The logic was already correct - we just made it explicit:

```python
# The rule (same as before, just clearer now):
book_page = pdf_index + 1  (for pdf_index >= 6)

# Applied consistently in:
# - Title generation
# - Page footer display
# - Documentation and help text
# - Comments throughout codebase
```

## No Functional Change

This is a documentation and clarity fix, not a logic change. The actual page mapping logic was always correct; we just:
1. Made it explicit throughout the codebase
2. Updated all comments and help text
3. Created this reference document
4. Renamed files to be clearer when possible
