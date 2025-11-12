#!/usr/bin/env python3
"""
Transform ch24_mathml_table.html to apply professional inline styling
"""

import re
from pathlib import Path

def style_html_file(file_path):
    """Apply professional inline styles to chapter 24 HTML"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace old table tags with new styled ones
    # Pattern: <table border="1" cellpadding="10">
    content = re.sub(
        r'<table border="1" cellpadding="10">',
        '<table class="-table-basic" style="border-collapse: collapse; text-align: left; margin: 0 auto 25px auto; border: 1px solid #ccc;"><colgroup><col style="width: 50%;"><col style="width: 50%;"></colgroup>\n<tbody>',
        content
    )

    # 2. Replace closing tbody with </tbody> if needed (remove old closing)
    # First, let's handle the case where tables don't have tbody yet

    # 3. Add tbody closing tags
    # Find </table> and ensure </tbody> is before it
    content = re.sub(
        r'</table>',
        '</tbody>\n</table>',
        content
    )

    # Remove duplicate tbody closing tags
    content = re.sub(
        r'</tbody>\n</tbody>',
        '</tbody>',
        content
    )

    # 4. Style tr elements
    # Pattern: <tr> with optional attributes
    # Find tr at start of line and style them, but preserve existing styles
    def style_tr(match):
        tr_tag = match.group(0)
        if 'style=' in tr_tag:
            return tr_tag  # Already styled
        return '<tr style="border-bottom: 1px solid #ddd;">'

    content = re.sub(r'<tr(?![^>]*style=)>', '<tr style="border-bottom: 1px solid #ddd;">', content)

    # 5. Style td elements within tables
    # Replace <td width="40%"> and <td width="60%"> with styled versions
    content = re.sub(
        r'<td width="40%">',
        '<td style="padding: 12px 15px; border-right: 1px solid #ddd;">',
        content
    )

    content = re.sub(
        r'<td width="60%">',
        '<td style="padding: 12px 15px; text-align: left;">',
        content
    )

    # Replace plain <td> tags (in formulas section)
    # But be careful not to replace ones that already have styles
    content = re.sub(
        r'<td>(?!.*style=)',
        '<td style="padding: 12px 15px; border-right: 1px solid #ddd;">',
        content,
        flags=re.DOTALL
    )

    # Actually, let's use a more sophisticated approach
    # Replace <td> that's not preceded by style= on same tag
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        # If this line has a td tag without style
        if '<td>' in line and 'style=' not in line:
            line = line.replace('<td>', '<td style="padding: 12px 15px; border-right: 1px solid #ddd;">')
        new_lines.append(line)

    content = '\n'.join(new_lines)

    # Now handle the second td in each row (should not have border-right)
    # This is trickier - let's identify rows and update them
    content = re.sub(
        r'(<tr[^>]*>.*?)<td style="padding: 12px 15px; border-right: 1px solid #ddd;">(<.*?)<td style="padding: 12px 15px; border-right: 1px solid #ddd;">',
        r'\1<td style="padding: 12px 15px; border-right: 1px solid #ddd;">\2<td style="padding: 12px 15px; text-align: left;">',
        content,
        flags=re.DOTALL
    )

    return content

def main():
    file_path = Path('/Users/abereyes/Projects/Work/PDF_to-HTML_Converter/Calypso/output/chapter_24/ch24_mathml_table.html')

    print(f"Processing {file_path}")
    content = style_html_file(str(file_path))

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Styling applied successfully")

if __name__ == '__main__':
    main()
