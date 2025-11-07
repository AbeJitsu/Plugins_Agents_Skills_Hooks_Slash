---
description: View your saved quality standards
---

# Show Standards - View Your Quality Framework

Display all your saved standards by project type. See what quality criteria you've defined and what principles guide your work.

## Usage

`/show-standards` - View all standards
`/show-standards <project-type>` - View standards for a specific type

Examples:
- `/show-standards` - See everything you've defined
- `/show-standards react-components` - See just your React component standards
- `/show-standards documentation` - See your doc writing standards

## What You'll See

For each project type, you'll see:
- **Principles**: High-level values (maintainable, consistent, secure, etc.)
- **Validation Rules**: What makes valid input
- **Quality Criteria**: What the finished work must have
- **Common Patterns**: What you typically use
- **Anti-patterns**: What to avoid

## Example Output

```
Project Type: React Components
Principles:
  - Reusable and testable
  - Clear prop contracts
  - Follows component composition

Validation:
  - Must have PropTypes or TypeScript
  - Must include example usage
  - Should handle loading/error states

Quality Criteria:
  - Completeness: All props documented
  - Correctness: Passes eslint/prettier
  - Performance: Memoization where needed
  - Maintainability: Comments on complex logic
  - Security: No XSS vulnerabilities
```

## Managing Your Standards

You can update standards by running `/define-standards <type>` again. The new definition replaces the old one.
