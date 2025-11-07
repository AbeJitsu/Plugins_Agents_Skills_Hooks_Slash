# High-Quality Builder Plugin

An adaptive quality pipeline system that learns your standards and ensures high-quality deliverables for any project type.

## What It Does

High-Quality Builder is your personal quality coach. It helps you:

1. **Define Standards Conversationally** - Tell me what matters for each type of work you do
2. **Remember Your Preferences** - It learns and applies your standards automatically
3. **Ensure Quality** - Runs every project through a 4-step quality pipeline
4. **Adapt to Your Needs** - Works for code, documentation, refactoring, tests, or content

## Installation

```bash
/plugin install ./high-quality-builder
```

## Quick Start

### Run the Quality Pipeline

```bash
/hqb
```

The system will ask what you're building, then guide you through:
1. **Validate** - Ensure your requirements are clear
2. **Generate** - Create the deliverable
3. **Format** - Apply consistent formatting
4. **Verify Quality** - Final quality check

### Define Your Standards

```bash
/define-standards react-components
```

Have a conversation about what "good work" means for that type. The system remembers for next time.

### View Your Standards

```bash
/show-standards
```

See all standards you've defined, or check a specific type:

```bash
/show-standards documentation
```

## Project Types Supported

1. **Code Features** - New components, functions, modules
2. **Documentation** - API docs, guides, specifications, tutorials
3. **Refactoring** - Improving existing code
4. **Test Suite** - Unit tests, integration tests, test coverage
5. **Content Creation** - Blog posts, articles, technical writing

## How It Works

### The 4-Step Quality Pipeline

Every project goes through the same 4 steps, adapted to your standards:

**1. Validate Requirements**
- Checks if your input is clear and complete
- Uses your saved standards to validate
- Asks for clarification if needed

**2. Generate Output**
- Creates the actual deliverable
- Follows your principles and patterns
- Includes everything you care about

**3. Format & Standardize**
- Applies consistent formatting
- Uses your coding/writing style
- Makes it look professional

**4. Quality Verify**
- Final quality check against 6 dimensions:
  - Completeness (all parts present)
  - Correctness (works as intended)
  - Consistency (uniform style)
  - Performance (efficient)
  - Security (safe/protected)
  - Maintainability (easy to understand/modify)

### Learning Over Time

Each time you define standards:
- Your preferences are saved to `standards/standards.json`
- The system adapts the pipeline to your values
- Future work automatically applies what you've learned

## Architecture

### Commands
- `/hqb` - Run the quality pipeline
- `/define-standards <type>` - Define new standards
- `/show-standards [type]` - View your standards

### Agents
- **quality-orchestrator** - Main pipeline runner
- **standards-definer** - Conversational standards setup
- **project-analyzer** - Detects project type and loads standards

### Skills
- **validate-requirements** - Check prerequisites
- **generate-output** - Create the deliverable
- **format-standardize** - Apply formatting
- **quality-verify** - Final quality gate

### Standards System
- `standards/standards.json` - Your learned standards (grows over time)
- `standards/templates/` - Default templates for each project type:
  - `code-features.json`
  - `documentation.json`
  - `refactoring.json`
  - `test-suite.json`
  - `content-creation.json`

### Validation Hooks
- **Stop Hook** - Runs at end of each agent turn
- Validates pipeline steps completed
- Provides progress feedback

## Examples

### Example 1: Creating a React Component

```
You: /hqb
System: What are you building?
You: A reusable dropdown component with search
System: I'll use your React component standards
System: [Validates requirements] ✓
System: [Generates component] ✓
System: [Formats to your style] ✓
System: [Verifies quality: 92/100] ✓
System: Here's your component, ready to use!
```

### Example 2: Writing Documentation

```
You: /hqb
System: What are you building?
You: API documentation for our payment endpoints
System: I don't have documentation standards defined yet
System: Would you like to define them now?
You: Yes
System: [Runs standards-definer agent]
System: [Asks about your documentation priorities]
You: [Answer conversational questions]
System: Great! I've saved your standards.
System: Ready to write your documentation!
```

### Example 3: Defining Standards

```
You: /define-standards react-components
System: Let's define your React component standards
System: What's most important when you create components?
You: They need to be reusable and testable
System: [Asks follow-up questions about your values]
You: [Share what matters most]
System: [Saves your standards]
System: Your React component standards are now defined!
```

## Configuration

### Understanding Quality Scores

The system rates deliverables on a scale:

- **85-100**: Excellent, ready to deliver immediately
- **70-84**: Good, minor issues to fix
- **<70**: Needs significant revision

Each dimension is scored independently, then averaged.

### Customizing Templates

You can edit the default templates in `standards/templates/` to match your preferences:

```json
{
  "projectType": "code-features",
  "principles": [...],
  "validationRules": {...},
  "qualityCriteria": {...},
  "commonPatterns": [...],
  "antiPatterns": [...]
}
```

### Standards Storage

Your learned standards are stored in `standards/standards.json`:

```json
{
  "standards": {
    "react-components": {
      "principles": [...],
      "validationRules": {...},
      ...
    }
  }
}
```

## Key Features

✅ **Conversational** - Learn what matters to you through dialogue
✅ **Adaptive** - Customizes to your specific project types
✅ **Memorable** - Saves your standards for reuse
✅ **Comprehensive** - 6 quality dimensions evaluated
✅ **Practical** - Works with actual code, docs, and content
✅ **Extensible** - Add new project types and standards as needed

## Tips for Best Results

1. **Start with one project type** - Define standards for React components, then documentation, etc.
2. **Be specific in standards** - "Readable code" is vague; "clear variable names, max 3 levels of nesting" is better
3. **Share your anti-patterns** - Tell the system what NOT to do
4. **Update standards as needed** - Run `/define-standards` again to refine
5. **Trust the process** - Let the 4-step pipeline work

## Troubleshooting

**Q: The system asks too many questions**
A: That's the standards-definer doing its job. Answer what you can; it learns from your responses.

**Q: My standards don't match what gets generated**
A: Check `/show-standards` to see what's saved. You can redefine with `/define-standards` anytime.

**Q: Can I use this for different programming languages?**
A: Yes! Define standards for Python functions, JavaScript modules, etc. separately if they differ.

**Q: What if I want the default behavior without custom standards?**
A: The system uses default templates if no custom standards exist. These are solid starting points.

## Next Steps

1. **Try the pipeline**: `/hqb` and walk through an example
2. **Define standards**: `/define-standards` for your first project type
3. **See your standards**: `/show-standards` to review what you defined
4. **Iterate**: Use the system on real projects and refine over time

## Support

For issues or feedback with Claude Code, visit: https://github.com/anthropics/claude-code/issues

---

**Your quality standards, continuously refined. One project at a time.**
