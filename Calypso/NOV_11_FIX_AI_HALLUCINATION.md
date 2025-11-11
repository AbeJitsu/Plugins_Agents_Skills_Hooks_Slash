# Nov 11 Fix: AI Hallucination in Page Boundary Generation

**Date:** November 11, 2025
**Status:** DOCUMENTED - Root cause identified, fix pending
**Impact:** All failing pages with >100% coverage (Pages 15, 16, 19, 23, 26 in Chapter 2)

---

## Executive Summary

HTML pages are failing the >100% coverage validation because the AI generation process is **creating text that does not exist in the PDF**. This is not an extraction problem—it's an AI hallucination problem during HTML generation.

### Key Finding
The PDF extraction is **working correctly**. Multiple extraction libraries (PyMuPDF, pdfplumber) extract the same content. The problem is that the AI is **inventing bridge sentences and connecting words** to smooth page transitions, adding content that wasn't in the source material.

---

## Investigation Details

### Tests Performed

**1. Library Comparison Test**
- Tested 4 PDF extraction libraries on Page 16 (PDF index 15)
- Libraries: PyMuPDF (current), pdfplumber, pypdfium2, pdfminer.six
- Result: PyMuPDF and pdfplumber extracted identical text (297-298 words)
- Both libraries missed the same "extra" words (also, heterogeneity, functionality)
- **Conclusion:** All libraries extract the same content from the PDF

**2. PDF Content Verification**
- Direct extraction from PDF shows:
  - Page 16 (PDF index 15) ends with: "In addition, land includes all" (incomplete sentence)
  - Page 17 (PDF index 16) starts with: "Chapter 2: Rights in Real Estate 17 plants attached to the ground..."
  - The word "also" does NOT appear in the PDF at this location

**3. JSON Extraction Verification**
- Confirmed that rich_extraction.json matches PDF content
- JSON page 15 ends with: "In addition, land includes all"
- JSON page 16 starts with: "Chapter 2: Rights in Real Estate 17 plants attached..."
- No "also" in the JSON

**4. HTML Generation Analysis**
- HTML page 16 starts with: "All land also includes all plants attached to the ground..."
- The phrase "All land also includes" was completely invented
- This does not appear in:
  - ✗ The PDF
  - ✗ The extraction JSON
  - ✗ Any extraction library test

---

## Root Cause: AI Hallucination

The AI (Claude) is generating **bridging text** when creating HTML from the page artifacts. When a page starts mid-sentence (like "plants attached..."), the AI is:

1. Recognizing there's an incomplete opening
2. Attempting to create a complete sentence by synthesizing a beginning
3. Adding words that sound natural but don't exist in the source: "All land also includes"

### Why This Happens

The HTML generation process (Skill 3) receives:
- PNG image of the page
- JSON extraction data
- ASCII preview showing structure

But when the page starts with incomplete text (due to page boundaries), the AI tries to "fix" it rather than preserving the exact boundary from the source.

### Example: Page 16

**PDF/JSON Content:**
```
[Page 15 ends:] "In addition, land includes all"
[Page 16 starts:] "Chapter 2: Rights in Real Estate 17 plants attached to the ground or in the ground..."
```

**Expected HTML:**
```html
<p class="paragraph">
    plants attached to the ground or in the ground, such as trees and grass...
</p>
```

**Actual HTML Generated:**
```html
<p class="paragraph">
    All land also includes all plants attached to the ground or in the ground...
</p>
```

The AI invented: "All land also includes all" to bridge from the previous page concept.

---

## Failing Pages Analysis

### Pages with >100% Coverage (AI Hallucination)

| Page | Coverage | Issue | Extra Words |
|------|----------|-------|------------|
| 15 | 100.7% | Bridging text | "also", "includes" synthesized |
| 16 | 101.2% | Opening sentence invented | "All land also includes" (4 words) |
| 19 | 100.6% | Transition words added | "earth." |
| 23 | 100.2% | Connecting phrase | "functionality" in context |
| 26 | 102.0% | Table synthesis issue | "description", "level", "type" |

### Pages with <99% Coverage (Different Issue)

| Page | Coverage | Issue | Resolution |
|------|----------|-------|-----------|
| 21 | 98.5% | Missing bullet chars | Add ● handling |
| 24 | 97.1% | Wrong content? | Regenerate - may have wrong page |
| 27 | 94.6% | Footer + bullets | Filter footers properly |

---

## What Changed

### Previous Understanding
- Assumed: "Extra content" might be in JSON extraction
- Tested: Multiple PDF libraries
- Result: All libraries confirm JSON is accurate

### New Understanding
- Root cause: **AI generation adds non-existent content**
- Pages with incomplete boundaries trigger hallucination
- Need strict boundary enforcement in HTML generation

---

## Solution Approach

### Option A: Strict Page Boundary Constraints (Recommended)
When generating HTML, the AI must:
1. Start page content EXACTLY where JSON starts it
2. End page content EXACTLY where JSON ends it
3. Never add bridging text, connectors, or completing phrases
4. Preserve incomplete sentences at page boundaries
5. Add a directive: "Do not synthesize, bridge, or invent connecting text"

### Option B: Pre-Processing the JSON
Mark in JSON where page boundaries occur and enforce them:
```json
{
  "text_spans": [
    {"text": "...", "is_page_boundary_start": true},
    {"text": "...", "is_page_boundary_end": true}
  ]
}
```

### Option C: Post-Process Generated HTML
Run a cleanup step that:
1. Compares HTML against JSON
2. Identifies and removes synthesized text
3. Restores page boundaries
4. May be fragile and error-prone

---

## Immediate Next Steps

1. **Document the Issue** ✅ (This file)
2. **Choose Solution Approach** (Recommend: Option A - Strict Constraints)
3. **Update HTML Generation Instructions**
   - Add explicit constraint: "Do not synthesize bridging text"
   - Add instruction: "Preserve exact page boundaries"
   - Add validation: "Every sentence must come from source JSON"
4. **Regenerate Failing Pages**
   - Pages 15, 16, 19, 23, 26 (Chapter 2)
   - Use strict boundary constraints
5. **Verify Coverage**
   - Re-run validation
   - Should show 100% coverage (not >100%)

---

## Files to Update

### Skill 3 Instructions (HTML Generation)
- Location: `.claude/skills/` or prompt template for page generation
- Add constraint: No synthesizing content, preserve boundaries exactly
- Add validation rule: Every word in HTML must exist in JSON

### Validation Script Consideration
- Current: `verify_text_content.py` correctly identifies >100% as failure
- No changes needed - it's working as designed
- The issue is in the generation step, not validation

---

## Prevention for Future Chapters

### When Generating Pages for New Chapters
1. Use strict boundary constraints
2. Accept that pages may start/end mid-sentence
3. Never synthesize bridging text
4. Validate immediately after generation
5. If coverage >100%, STOP and regenerate with corrections

### Chapter Generation Template
Add to all page generation prompts:
```
CRITICAL CONSTRAINT:
- Do not create bridging text between pages
- Do not invent transitional phrases
- Do not complete incomplete sentences with invented content
- Start exactly where PDF starts, end exactly where PDF ends
- Every single word must come from the extraction JSON
```

---

## Testing Results Summary

### PDF Extraction Libraries Tested
```
Library           Words Extracted    Found Target Words
PyMuPDF           298                earth, includes
pdfplumber        297                earth, includes
pypdfium2         0 (failed)         n/a
pdfminer.six      0 (failed)         n/a
```

**Conclusion:** Extraction is accurate. "Extra" words (also, heterogeneity, functionality) are NOT in the PDF or JSON.

### PDF Content vs HTML Content
```
Location          Content
PDF page 15 end   "In addition, land includes all"
PDF page 16 start "Chapter 2: Rights in Real Estate 17 plants attached..."
JSON page 15 end  "In addition, land includes all"
JSON page 16 start "Chapter 2: Rights in Real Estate 17 plants attached..."
HTML page 16 start "All land also includes all plants attached..."
```

The phrase "All land also includes all" appears **ONLY** in the HTML. It was synthesized by the AI.

---

## Resources Created

### Diagnostic Tools
- `compare_extractors.py` - Tests multiple PDF libraries on a page
- `detailed_extraction_diff.py` - Shows exact word differences between JSON and HTML

### Usage
```bash
# Compare extraction libraries
python3 Calypso/tools/compare_extractors.py "Calypso/PREP-AL 4th Ed 9-26-25.pdf" 15 --target-words "also" "includes" "heterogeneity"

# Detailed diff analysis
python3 Calypso/tools/detailed_extraction_diff.py 2 16
```

---

## Status Tracking

**Investigation:** ✅ COMPLETE
- ✅ Verified PDF extraction is working
- ✅ Confirmed AI hallucination is the issue
- ✅ Identified specific pages affected
- ✅ Root cause documented

**Fix Implementation:** ⏳ PENDING
- ⏳ Choose solution approach
- ⏳ Update HTML generation constraints
- ⏳ Regenerate failing pages
- ⏳ Re-validate all pages

**Consolidation:** ⏳ PENDING
- ⏳ Once all pages pass (≤100%)
- ⏳ Consolidate Chapter 2
- ⏳ Apply learning to remaining chapters

---

## Questions/Notes for Future Sessions

1. Should we implement Option A (strict constraints) or use a different approach?
2. Do we need to regenerate ALL previous pages, or just the failing ones?
3. Should we add page boundary metadata to JSON to make this clearer?
4. Can we add a validation step that checks "Is every word in HTML found in JSON?"

---

**Created:** Nov 11, 2025
**Last Updated:** Nov 11, 2025
**Status:** PENDING IMPLEMENTATION
