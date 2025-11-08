# Calypso PDF to HTML - Page Structure & CSS Classes

## PDF Index Mapping

**PDF indices are 0-based, book page numbers start at 1:**
- PDF index 0-5 = Front matter (no book page numbers)
- PDF index 6 = Book page 7 (first content page of Chapter 1)
- PDF index 7 = Book page 8
- PDF index 14 = Book page 15

**Footer Rule:** Book page = PDF index + 1 (for indices >= 6)

## PDF Index 6 (Book Page 7) Reference Structure

Based on visual analysis of the actual PDF, here's the semantic HTML structure needed:

### Elements & Classes:

```
.page-container              - Main wrapper, white bg, max-width, shadow

  .chapter-header           - Flex container for number + title
    .chapter-number         - Large italic "1" (74pt bold)
    .chapter-title          - Main title "The Real Estate Business" (27pt bold)

  .section-navigation       - Nav items list (not bullets)
    .nav-item              - Each topic (12pt bold)
                             - Real Estate Professions
                             - Real Estate Brokerage
                             - Professional Organizations
                             - Regulation and Licensing

  .section-divider          - <hr> horizontal line

  .section-heading          - "REAL ESTATE PROFESSIONS" (11pt bold, all-caps)

  .subsection-labels        - Container for label items
    .subsection-label       - Each label (11pt bold)
                             - Real estate activities
                             - Professional specialties
                             - Property type specialization

  .section-divider          - <hr>

  .paragraph                - Main body text (11pt regular)

  .sidebar-label            - Left sidebar item (bold)

  .bullet-list              - <ul> with arrow bullets
    <li>                    - Each bullet item

  .page-footer              - Right-aligned page number
```

### Heading Hierarchy:
- **H1** (.chapter-title): "The Real Estate Business"
- **H2** (.section-heading): "REAL ESTATE PROFESSIONS" (all-caps sections)
- **H3** (.subsection-label): Sub-labels under sections
- **H4**: Not used on this page

### Key CSS Classes to Style:
- `.chapter-header` - flex layout, gap, margin-bottom
- `.section-navigation` - flex wrap, gap, padding, light bg, border-left
- `.section-divider` - margin, color, height
- `.subsection-labels` - flex column, gap, padding, light bg
- `.bullet-list` - list-style set to arrow bullets (▶)
- `.page-footer` - right-aligned, small font, border-top
- `.sidebar-label` - bold, margin
- `.paragraph` - line-height, margin-bottom, font-family (Times)
- `.paragraph-italic` - italic styling for <em> or specific spans

### Missing/Issues to Handle:

1. **Tables**: Exhibit 1.1, 1.2, 1.3, 1.4 currently rendered as text blocks
   - Need to identify and structure as proper `<table>` elements
   - May require manual markup or smarter extraction

2. **Bullet List Items**: Currently being rendered as text
   - Need to detect multi-line lists and wrap in `<ul><li>` elements

3. **Bold/Italic Spans**: Currently applied at paragraph level
   - May need `<strong>` and `<em>` tags within paragraphs

4. **Page Breaks**: Handled by page number footer
   - Each page 6-14 should be separate or properly sectioned

### Extraction Strategy:

**Phase 1** (Current): Get single page (page 6) structure perfect
- Manually verify HTML matches visual layout
- Establish CSS classes and styling

**Phase 2**: Apply pattern to other pages
- Identify page type (intro, content, summary)
- Use similar structure with appropriate modifications

**Phase 3**: Handle special elements
- Tables and Exhibits
- Sidebars and callouts
- Multi-column layouts
