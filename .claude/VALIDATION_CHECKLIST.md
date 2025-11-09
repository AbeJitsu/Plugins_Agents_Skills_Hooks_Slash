# Calypso Chapter Validation Checklist

**Purpose:** Standardized process for validating chapters against established quality standards
**Last Updated:** 2025-11-08
**Status:** Proven on Chapters 2-3; Validated with hook

---

## Quick Validation (30 seconds)

Run the automated validation hook:

```bash
./.claude/hooks/calypso-chapter-boundary-validation.sh <chapter_number>
```

Example: `./.claude/hooks/calypso-chapter-boundary-validation.sh 2`

**Expected Output:** Chapter passes all validation standards (exit code 0) or fails with specific issues (exit code 1)

---

## Complete Manual Validation (5-10 minutes)

Use this checklist when manual validation is needed or hook results require investigation.

### 1. EXTRACTION METADATA ✓

**Purpose:** Ensure extraction JSON contains correct page boundaries

**Steps:**
1. Open `Calypso/analysis/chapter_XX/rich_extraction.json`
2. Check metadata section:
   ```json
   "metadata": {
     "source": "PREP-AL 4th Ed 9-26-25.pdf",
     "total_pages_extracted": [N pages],
     "page_range": "[first]-[last]"
   }
   ```
3. Verify:
   - ✓ `page_range` matches expected chapter boundaries
   - ✓ `total_pages_extracted` equals (last - first + 1)
   - ✓ Pages object contains all pages from first to last

**Example - Chapter 2:**
```json
"page_range": "15-27"      // 13 pages
"total_pages_extracted": 13
"pages": { "15": {...}, "16": {...}, ..., "27": {...} }
```

**Common Issues:**
- Extraction includes next chapter opening (e.g., Ch2 had page 28 = Ch3 opening)
- Extraction starts at wrong page (e.g., Ch3 started at 29 instead of 28)
- Extraction includes extra pages (e.g., Ch3 had pages 38-42 = Ch4)

---

### 2. CHAPTER OPENING ✓

**Purpose:** Verify first page contains chapter header and navigation

**Steps:**
1. Open `Calypso/output/chapter_XX/page_artifacts/page_[first_page]/03_page_[first_page]_ascii.txt`
2. Review ASCII preview for:
   - ✓ `[CHAPTER HEADER - LARGE]` or similar section marker
   - ✓ Large chapter number (70-80pt)
   - ✓ Chapter title (26-28pt)
   - ✓ `[SUBSECTION NAVIGATION HEADINGS]` or navigation list
   - ✓ Navigation items (3+ items typical)

**Example - Chapter 2 Page 15:**
```
[CHAPTER HEADER - LARGE]
2  Rights in Real Estate
[SUBSECTION NAVIGATION HEADINGS]
• Real Estate as Property
• Real Versus Personal Property
• Regulation of Real Property Interests
```

**Check HTML file:**
```bash
grep -A 5 'class="chapter-header"' Calypso/output/chapter_XX/page_artifacts/page_[first]/04_page_[first].html
```

**Common Issues:**
- Missing chapter number or title
- Missing navigation menu
- Wrong chapter number shown
- Navigation items incomplete

---

### 3. CHAPTER CLOSING ✓

**Purpose:** Verify last page contains summary and no next chapter content

**Steps:**
1. Open `Calypso/output/chapter_XX/page_artifacts/page_[last_page]/03_page_[last_page]_ascii.txt`
2. Scan full file for:
   - ✓ `Snapshot Review` keyword (appears on closing page)
   - ✓ Summary sections with h2/h4 headings
   - ✓ Bullet lists summarizing chapter content
   - ✗ NO next chapter opening (no "Chapter [N+1]" header, no new chapter number)

**Example - Chapter 2 Page 27:**
```
Snapshot Review

[H2 Major Section - Bold, All Caps]
REAL ESTATE AS PROPERTY

[H4 Subsection - 11pt Bold]
Land

[Bullet List - 11pt Regular]
• Constitution guarantees private ownership...
```

**Book Page Continuity Check:**
- Last line should show: `Book Page: [N] | Chapter: X | PDF Index: [N]`
- Next chapter first page should show: `Book Page: [N+1] | Chapter: [X+1]`
- Example: Page 27 → Page 28 boundary marks Ch2→Ch3 transition

**Common Issues:**
- Missing "Snapshot Review" marker
- Incomplete summary sections
- Next chapter content leaked into last page
- Summary content cuts off

---

### 4. HTML VALIDATION ✓

**Purpose:** Ensure HTML file has valid structure with 0 errors

**Steps:**
1. Run validation:
   ```bash
   python3 Calypso/tools/validate_html.py Calypso/output/chapter_XX/chapter_XX.html
   ```

2. Check report for:
   - ✓ `Status: ✓ VALID`
   - ✓ `error_count: 0`
   - ✓ Warnings are acceptable (heading hierarchy jumps are intentional)

**Expected Output:**
```
Status: ✓ VALID

⚠️  WARNINGS (7):
   • Heading hierarchy jump: h1 → h3
   • Heading hierarchy jump: h2 → h4
   ... (these are acceptable)

ℹ️  INFO:
   • Page title: 'Chapter X: [Title]'
   • Document format: Continuous
```

**Common Issues:**
- Missing DOCTYPE, meta tags, or title
- Unclosed tags
- Invalid semantic structure
- Missing CSS stylesheet link

---

### 4b. TEXT CONTENT VERIFICATION ✓ (MANDATORY Gate 3)

**Purpose:** Ensure all extracted text from PDF made it into final HTML (no content loss)

**Steps:**
1. Run text content verification:
   ```bash
   python3 Calypso/tools/verify_text_content.py <chapter_num>
   ```

2. Check report for:
   - ✓ `Coverage: ≥95%` (required minimum)
   - ✓ Exit code 0 (success)
   - ✓ All major sections present
   - ⚠️ Exit code 1: Warning (85-95% coverage) - investigate before accepting
   - ❌ Exit code 2: Failure (<85% coverage) - MUST FIX before considering complete

**Expected Output (PASSING):**
```
================================================================================
TEXT CONTENT VERIFICATION
================================================================================
Extracting text from JSON... ✓ (XXX text spans, YYYY words)
Extracting text from HTML... ✓ (ZZZZ words)

Comparison:
  JSON word count:  YYYY
  HTML word count:  ZZZZ
  Coverage:         ≥95.0%

✅ VERIFICATION PASSED: Text content is comprehensive
```

**Common Issues:**
- **Low coverage (<85%)**: Individual pages have content gaps during AI generation
  - Run page-by-page analysis to identify which pages are incomplete
  - Regenerate incomplete pages with revised prompts
  - Re-consolidate and re-verify

- **Minor gaps (85-95%)**: Minor content loss acceptable but investigate
  - Usually page numbers, punctuation variations, or formatting artifacts
  - Check if critical content is present
  - Proceed with caution and note in progress.md

- **Missing words are just page numbers**: Acceptable variance
  - Extraction JSON includes footer page numbers
  - HTML may strip these during formatting
  - Not a real content gap if semantic content is complete

---

### 5. PAGE BOUNDARIES ✓

**Purpose:** Confirm all expected pages are present with no gaps

**Steps:**
1. Count pages in extraction JSON:
   ```bash
   grep -c '"[0-9]*":' Calypso/analysis/chapter_XX/rich_extraction.json
   ```

2. Compare to expected:
   ```
   Expected = (last_page - first_page + 1)
   Actual = (count from above)
   Should match!
   ```

3. Verify sequential page numbers:
   ```bash
   grep '"[0-9]*":' Calypso/analysis/chapter_XX/rich_extraction.json | \
     grep -o '"[0-9]*"' | sort -n
   ```

**Example - Chapter 2:**
```
Page count: 13
Range: 15-27
Expected: 27 - 15 + 1 = 13 ✓
Sequence: 15, 16, 17, ..., 26, 27 (no gaps) ✓
```

---

### 6. PROGRESS TRACKING ✓

**Purpose:** Ensure progress.md is updated with validation status

**Steps:**
1. Open `Calypso/progress.md`
2. Find chapter row in status table
3. Verify:
   - ✓ Status is `✅ Complete` if all checks pass
   - ✓ Validation column shows `✓ 0 errors`
   - ✓ Notes column explains any issues

**Example:**
```markdown
| 2 (Rights in Real Estate) | 15-27 | ✅ Complete | ✓ 0 errors | Fixed: extracted 15-27 only |
```

---

## Automation Integration

### Running Validation Automatically

The validation hook can be integrated into:

1. **Pre-commit hook:** Run before git commit
   ```bash
   # In .git/hooks/pre-commit
   ./.claude/hooks/calypso-chapter-boundary-validation.sh ${CHAPTER} || exit 1
   ```

2. **CI/CD pipeline:** Run on every push
   ```bash
   for chapter in {1..29}; do
     ./.claude/hooks/calypso-chapter-boundary-validation.sh $chapter || exit 1
   done
   ```

3. **Manual validation workflow:**
   ```bash
   # After generating chapter
   ./.claude/hooks/calypso-chapter-boundary-validation.sh 4

   # Check output
   # If PASS: proceed to next chapter
   # If FAIL: fix issues, re-run validation
   ```

---

## Standards Reference

### Required Structure (All Chapters)

| Element | Chapter Opening | Content Pages | Chapter Closing |
|---------|-----------------|-------------------|---|
| Chapter Header | ✓ Required | - | - |
| Navigation Menu | ✓ Required | - | - |
| Section Headings | First h2 | h2/h4/h5 hierarchy | h2 (summary sections) |
| Content | Intro paragraph | Full sections | Bullet summary |
| Snapshot Review | - | - | ✓ Required |
| Next Chapter Content | ✗ None | - | ✗ None |

### Quality Gates (Required)

1. **Gate 1 - Structure:** 0 errors from `validate_html.py`
2. **Gate 2 - Semantics:** Proper h1/h2/h3/h4/h5 hierarchy with CSS classes
3. **Gate 3 - Boundaries:** First page has opening markers, last page has closing markers
4. **Gate 4 - Completeness:** All expected pages present, no gaps, no next chapter content

---

## Troubleshooting

### "ASCII preview not found"

**Cause:** Page artifacts haven't been generated by AI skills
**Solution:**
1. Re-run AI generation skills for those pages
2. Generate both 03_page_XX_ascii.txt and 04_page_XX.html files
3. Re-run validation

### "Chapter opening markers missing"

**Cause:** First page HTML doesn't show chapter number/title/navigation
**Solution:**
1. Check if page_artifacts exist
2. Review 03_page_XX_ascii.txt for actual markers present
3. Regenerate HTML if markers exist but not showing
4. Check CSS styling isn't hiding markers

### "Next chapter content detected"

**Cause:** Last page includes opening of next chapter
**Solution:**
1. Verify extraction JSON page_range is correct
2. Check ASCII file if it actually shows next chapter
3. Adjust page boundaries in extraction JSON
4. Regenerate HTML page

### "HTML validation error"

**Cause:** Generated HTML has structural issues
**Solution:**
1. Review error details from validate_html.py
2. Manual review of HTML file structure
3. Regenerate HTML page with improved prompt
4. Verify all tags are properly closed

---

## Validation Workflow Summary

```
1. Extract PDF pages
   ↓
2. Generate PNG renders
   ↓
3. Generate ASCII previews (boundary validation)
   ↓
4. Generate HTML pages (semantic structure)
   ↓
5. Consolidate chapter HTML
   ↓
6. Validate HTML (0 errors required)
   ↓
7. Run chapter boundary validation hook
   ↓
8. Update progress.md
   ↓
9. Commit with validation proof
   ↓
10. Move to next chapter
```

**Exit criteria at each step:**
- ASCII: Confirms opening/closing boundaries
- HTML: 0 errors from validate_html.py
- Hook: All 5 checks pass
- Progress: Status updated to ✅ Complete

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `Calypso/analysis/chapter_XX/rich_extraction.json` | Source extraction metadata and page content |
| `Calypso/output/chapter_XX/page_artifacts/page_YY/03_page_YY_ascii.txt` | ASCII preview with boundary markers |
| `Calypso/output/chapter_XX/page_artifacts/page_YY/04_page_YY.html` | Individual page HTML |
| `Calypso/output/chapter_XX/chapter_XX.html` | Consolidated chapter HTML |
| `Calypso/tools/validate_html.py` | Python validation tool (Gate 1-2) |
| `.claude/hooks/calypso-chapter-boundary-validation.sh` | Automated validation hook |
| `Calypso/progress.md` | Single source of truth for project status |

---

## Questions?

Refer to:
- **Full process documentation:** `CLAUDE.md`
- **Project status:** `Calypso/progress.md`
- **Standards definition:** `Calypso/progress.md` - Standards Established section
- **Hook implementation:** `.claude/hooks/calypso-chapter-boundary-validation.sh`
