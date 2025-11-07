# High-Quality Builder Plugin Project

An adaptive quality pipeline system that learns your standards and ensures high-quality deliverables for any project type.

## Quick Start

When you open this project in Claude Code, install the plugin to enable the quality pipeline:

```bash
/plugin install ./high-quality-builder
```

## Available Commands

Once the plugin is installed, you can use these slash commands:

### `/hqb`
Launch the adaptive quality pipeline. The system will:
1. Ask what type of project you're working on
2. Load your saved standards (or suggest defaults)
3. Run you through validation → generation → formatting → quality verification
4. Deliver the finished deliverable

### `/define-standards <project-type>`
Define quality standards for a specific project type through a conversational interview. Examples:
- `/define-standards react-components`
- `/define-standards documentation`
- `/define-standards refactoring`

### `/show-standards [project-type]`
View your saved standards by project type, or see all standards if no type specified.

## Project Types Supported

1. **code-features** - Writing new functions, components, modules
2. **documentation** - Writing docs, guides, tutorials, specs
3. **refactoring** - Improving existing code structure
4. **test-suite** - Writing automated tests
5. **content-creation** - Writing articles, tutorials, blog posts

## How It Works

The quality pipeline adapts based on your project type and runs everything through a 4-step process:

1. **Validate Requirements** - Checks if your input is clear and complete
2. **Generate Output** - Creates the actual deliverable
3. **Format & Standardize** - Applies consistent formatting
4. **Quality Verification** - Final quality check against 6 dimensions

## Your Standards

Your personal quality standards are saved in `.claude/standards/standards.json` (per-machine). This file:
- Starts empty when you first install the plugin
- Grows as you define standards for different project types
- Is not version controlled (use `.gitignore`)
- Can be updated by running `/define-standards <type>` again

## For Multiple Machines

This plugin is designed to be portable across your home laptop, workstation, and work setup:

1. Clone the project repo
2. Navigate to the project directory
3. Run `/plugin install ./high-quality-builder`
4. Start using the quality pipeline!

Each machine will have its own `.claude/standards/` directory with learned standards.

## Tips for Best Results

1. **Start with one project type** - Define standards for React components, then documentation, etc.
2. **Be specific in standards** - "Readable code" is vague; "clear variable names, max 3 levels of nesting" is better
3. **Share your anti-patterns** - Tell the system what NOT to do
4. **Update standards as needed** - Run `/define-standards` again to refine
5. **Trust the process** - Let the 4-step pipeline work

## Troubleshooting

**Command not found?**
- Make sure you've run `/plugin install ./high-quality-builder` in this session

**Plugin list:**
```bash
/plugin list
```

**Validate plugin structure:**
```bash
/plugin validate ./high-quality-builder
```

---

**For more information:** See `high-quality-builder/README.md`
