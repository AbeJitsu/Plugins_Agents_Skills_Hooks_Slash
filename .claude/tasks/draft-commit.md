# Task: Create Draft-a-Commit Utility

## 🎯 Overview

We're building a helpful developer utility that analyzes your staged changes and drafts a thoughtful, supportive commit message. The `/dac` command makes committing easier by capturing not just what changed, but why it matters.

**Why it matters**:
- Good commit messages are hard to write
- Most developers skip writing meaningful messages
- Our tone (inviting, supportive, focused) applies here too
- Saves time and creates better git history
- Demonstrates HQB patterns on a practical tool

**What it covers**:
- Understanding staged changes
- Drafting messages in HQB's communication style
- Making the workflow feel guided and supported

---

## 🎯 Goals

- [x] Create configurable draft-commit skill
- [x] Create /dac command
- [ ] Support multiple commit message styles
- [ ] Display message in chat for copying
- [ ] Integrate with HQB communication patterns

---

## 📖 Current State

### How It Works Now

Users manually write commit messages, often:
- Generic: "Update files"
- Incomplete: "Add feature" (which feature?)
- No context: "Fix bugs" (which bugs? why?)

### What We're Building

A utility that:
1. Reviews staged changes
2. Understands what was changed
3. Captures the intent and impact
4. Writes a message in our supportive tone
5. Displays it for easy copying

---

## 🏗️ New Design

### Command Structure

```
/dac
  ↓
Invokes draft-commit skill
  ↓
Analyzes git diff --cached
  ↓
Drafts message
  ↓
Displays in chat
```

### Message Style

**Inviting, Focused, Considerate, Supportive**:

```
[What you did]

[Why it matters / what improves]

[Details if helpful]
```

**Example**:
```
Add StandardsRepository abstraction

Centralizes standards access into a single, reliable interface.
This eliminates duplication and makes the system easier to maintain.

Files:
- lib/standards-repository.md (interface docs)
- lib/schemas/standards-schema.json (validation schema)
- Updated 7 files to use the repository pattern
```

### Configuration Options

**File**: `.claude/skills/draft-commit/config.json`

Supports:
- **style**: "supportive" (default) or "concise"
- **format**: "descriptive" (default) or "conventional" (feat:, fix:, etc.)
- **messageLength**: "concise" (default) or "detailed"
- **includeContext**: true (default) or false
- **includeFileCounts**: true (default)

---

## 📋 Implementation Steps

### Step 1: Create Configuration File

**What**: Define default style and options

**Why**: Makes the utility flexible and configurable

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/skills/draft-commit/config.json`:

```json
{
  "description": "Draft a commit message from staged changes",
  "style": "supportive",
  "format": "descriptive",
  "messageLength": "concise",
  "includeContext": true,
  "includeFileCounts": true,
  "supportedStyles": [
    {
      "id": "supportive",
      "description": "Inviting, focused, considerate, supportive tone"
    },
    {
      "id": "concise",
      "description": "Brief, factual messages"
    }
  ],
  "supportedFormats": [
    {
      "id": "descriptive",
      "description": "Free-form descriptive messages"
    },
    {
      "id": "conventional",
      "description": "Conventional commits (feat:, fix:, docs:, etc.)"
    }
  ],
  "conventionalTypes": [
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "chore"
  ]
}
```

**Validation**: ✅ Config file created

---

### Step 2: Create Draft-Commit Skill

**What**: The core logic for analyzing changes and drafting messages

**Why**: Reusable, testable, configurable

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/skills/draft-commit/SKILL.md`:

```markdown
# Draft a Commit

Create a thoughtful, supportive commit message from your staged changes.

## Welcome

Writing good commit messages is an art. This skill helps you capture the essence
of your changes in a clear, inviting way that your future self (and teammates)
will appreciate.

Your staged changes tell a story. Let's write that story together.

---

## What You're Doing

You're about to:
1. Review what you've staged
2. Understand the nature of your changes
3. Create a commit message that captures both what AND why
4. Copy that message and use it when you commit

---

## How It Works

### Step 1: Analyzing Staged Changes

First, we'll look at your staged changes using `git diff --cached`.

This shows us:
- **What files changed**: Which files did you touch?
- **What changed in them**: Added lines? Deleted? Refactored?
- **Patterns**: Can we detect what you were working on?

### Step 2: Understanding Intent

From the changes, we infer:
- **Type of work**: Feature? Bug fix? Refactoring? Documentation?
- **Scope**: Which part of the system?
- **Impact**: What improves? What does this enable?

### Step 3: Drafting the Message

We craft a message that:
- **Is specific**: Not "Update files" but "Add StandardsRepository abstraction"
- **Explains why**: Not just what changed, but why it matters
- **Shows confidence**: Your changes are worth celebrating
- **Invites understanding**: Future readers will understand your intent

### Step 4: Sharing with You

We display the drafted message so you can:
- Review it
- Copy it
- Use it in your git commit command

---

## Configuration

### Loading Configuration

The skill reads from `.claude/skills/draft-commit/config.json`:

- **style**: How the message sounds ("supportive" or "concise")
- **format**: Message structure ("descriptive" or "conventional")
- **messageLength**: How much detail ("concise" or "detailed")
- **includeContext**: Add explanatory context (true/false)
- **includeFileCounts**: Show file/line counts (true/false)

### Customizing Behavior

Edit `config.json` to change defaults:

```json
{
  "style": "supportive",         // or "concise"
  "format": "descriptive",       // or "conventional"
  "messageLength": "concise",    // or "detailed"
  "includeContext": true,
  "includeFileCounts": true
}
```

---

## Process

### Get Staged Changes

```
Run: git diff --cached
Returns: All staged changes in unified diff format
```

### Categorize Changes

Analyze the diff to understand:
- Added files, deleted files, modified files
- Lines added, lines deleted
- Change patterns (new feature, bug fix, refactoring, docs, etc.)

### Infer Work Type

From patterns, detect:
- `feat` — New functionality
- `fix` — Bug fixes
- `docs` — Documentation changes
- `refactor` — Code structure improvements
- `test` — Test additions/changes
- `chore` — Dependency updates, config changes
- `style` — Formatting, cleanup
- `perf` — Performance improvements

### Determine Scope

Identify what part of the system:
- Components affected
- Modules changed
- Features impacted

### Draft the Message

#### For Supportive Style + Descriptive Format

**Template**:
```
[Brief description of what you did]

[Why this matters — what improves or what it enables]

[Optional: More context if helpful]

[Optional: File counts if configured]
```

**Example**:
```
Add StandardsRepository abstraction

Centralizes standards access into a single, reliable interface.
This eliminates duplication and makes the system easier to maintain.

Files changed:
- Added: lib/standards-repository.md, lib/schemas/standards-schema.json
- Modified: 7 agent/skill files updated to use new pattern

Why: Standards were scattered across multiple files, creating duplication
and coupling. Now there's one clear way to access standards with validation.
```

#### For Concise Style

**Template**:
```
[Concise description]

[Brief context if needed]
```

**Example**:
```
Centralize standards access

Standards scattered across 7 files now use single repository pattern.
```

#### For Conventional Format

**Template**:
```
[type]: [description]

[Why this matters / additional context]
```

**Example**:
```
refactor: Centralize standards access with repository pattern

Consolidates standards loading into single interface.
Eliminates duplication and improves testability.
```

---

## Output Format

The skill displays the drafted message like this:

```markdown
## 📝 Drafted Commit Message

[The actual message, ready to copy]

---

## How to Use It

1. Copy the message above
2. Stage your changes: `git add .` (or select specific files)
3. Create the commit: `git commit -m "your message"`

Or paste into your editor's commit message prompt.

---

**Changes analyzed**:
- [X files] changed
- [+Y lines] added
- [-Z lines] deleted
```

---

## Important Notes

### What This Does

- Analyzes your **staged** changes only
- Drafts a message for you to review
- Shows the message in chat for easy copying
- Does NOT commit automatically

### What This Doesn't Do

- Does NOT make the commit (you do that)
- Does NOT stage changes (you do that)
- Does NOT modify your repository

### Why This Matters

This keeps you in control. You:
1. Stage your changes carefully
2. See what we're proposing
3. Decide if it's right
4. Make the commit yourself

---

## Error Handling

If we encounter issues:

- **No staged changes**: We'll let you know and suggest staging first
- **Unclear intent**: We'll ask for clarification or offer suggestions
- **Config issues**: We'll use defaults and let you know

---

## Tips for Great Commit Messages

1. **Stage intentionally**: Group related changes together
2. **Small commits**: Easier to understand and review
3. **Specific**: "Add validation" not "Update files"
4. **Why matters**: Explain the reasoning, not just the changes
5. **Present tense**: "Add feature" not "Added feature"

---

## Examples

### Example 1: Feature Addition

**Staged changes**: New function + tests + docs

**Drafted message**:
```
Add user authentication module

Implements JWT-based authentication for API.
Includes token generation, validation, and refresh logic.

Files:
- auth/jwt-handler.ts (main implementation)
- auth/__tests__/jwt-handler.test.ts (comprehensive tests)
- docs/AUTHENTICATION.md (usage guide)

Why: Enables secure API access. Provides foundation for role-based access control.
```

### Example 2: Bug Fix

**Staged changes**: Fixed bug in error handler

**Drafted message**:
```
Fix error handling in API response middleware

Error messages weren't being properly serialized, causing 500 errors
to appear as malformed JSON. Now returns clean error objects.

Files:
- middleware/error-handler.ts (fixed serialization)
- __tests__/error-handler.test.ts (added test case)

This fixes issue #245.
```

### Example 3: Documentation

**Staged changes**: Added README and guides

**Drafted message**:
```
Document setup and deployment process

Adds comprehensive guides for:
- Local development setup
- Running tests
- Building for production
- Deployment procedures

Files:
- SETUP.md (new)
- DEPLOYMENT.md (new)
- README.md (updated with links)

Why: New contributors need clear guidance. This reduces time to productivity.
```

---

## Configuration Examples

### For Conventional Commits

```json
{
  "style": "concise",
  "format": "conventional",
  "messageLength": "concise",
  "includeContext": true,
  "includeFileCounts": false
}
```

Output: `feat: Add authentication module`

### For Detailed Messages

```json
{
  "style": "supportive",
  "format": "descriptive",
  "messageLength": "detailed",
  "includeContext": true,
  "includeFileCounts": true
}
```

Output: Long, detailed message with full context

### For Concise Updates

```json
{
  "style": "concise",
  "format": "descriptive",
  "messageLength": "concise",
  "includeContext": false,
  "includeFileCounts": false
}
```

Output: Brief, to-the-point message

---

## Troubleshooting

**Q: What if I staged wrong changes?**
A: Unstage them with `git reset HEAD <file>` and run `/dac` again.

**Q: Can I edit the drafted message?**
A: Absolutely! Copy it, edit it, and use your version. It's a draft!

**Q: Does this work with conventional commits?**
A: Yes! Set `format: "conventional"` in config.json.

**Q: Can I configure it differently per project?**
A: Yes! Each project's config.json is independent. Just edit the file.

---

## Integration with HQB

This skill demonstrates HQB patterns:
- **Supportive tone**: Guides without judgment
- **Focused clarity**: One clear purpose
- **Considerate approach**: Respects your autonomy
- **Skill architecture**: Reusable, configurable logic

---

## Next Steps After Using This

1. Copy the drafted message
2. Review your changes one more time
3. Make your commit with `git commit -m "your message"`
4. Continue building awesome things!

---
```

**Validation**: ✅ Comprehensive skill documentation created

---

### Step 3: Create the /dac Command

**What**: Entry point for the utility

**Why**: Makes it discoverable and accessible

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/commands/dac.md`:

```markdown
---
description: Draft a thoughtful commit message from your staged changes
---

# Draft a Commit (/dac)

Create a clear, supportive commit message that captures what you've changed and why it matters.

## Welcome

Writing good commit messages takes time and thought. This command helps you do it faster,
with messages that actually tell the story of your changes.

## What It Does

1. Reviews your staged changes (`git diff --cached`)
2. Understands what you've been working on
3. Drafts a message in a supportive, clear tone
4. Displays it in chat for you to copy

## How to Use It

```
/dac
```

That's it! The command will:
- Analyze what you've staged
- Draft a message
- Show it to you in chat
- Let you copy and use it

## What Happens Next

1. Review the drafted message
2. Copy it if you like it (or edit it)
3. Run `git commit -m "your message"`
4. Done!

## Important

- **Only works with staged changes**: Stage your files first with `git add`
- **Doesn't auto-commit**: You remain in control
- **Draft for review**: Edit it if needed
- **No Claude signature**: Just your message

## Configuration

You can customize how messages are drafted by editing:

```
.claude/skills/draft-commit/config.json
```

Options:
- `style`: "supportive" or "concise"
- `format`: "descriptive" or "conventional"
- `messageLength`: "concise" or "detailed"
- `includeContext`: true or false
- `includeFileCounts`: true or false

## Skill Invoked

This command invokes the `draft-commit` skill.
See `.claude/skills/draft-commit/SKILL.md` for full details.

## Examples

### Before (manual)
"Update files"

### After (drafted)
"Add StandardsRepository abstraction

Centralizes standards access into a single, reliable interface.
This eliminates duplication and makes the system easier to maintain."

---

Ready? Run `/dac` whenever you have staged changes and want help writing the message!
```

**Validation**: ✅ Command created and ready

---

### Step 4: Create Draft-Commit Skill Metadata File

**What**: Skill registration and basic info

**Why**: Helps Claude Code discover and organize skills

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/skills/draft-commit/draft-commit.json`:

```json
{
  "name": "draft-commit",
  "description": "Draft a thoughtful commit message from staged changes",
  "version": "1.0.0",
  "invocableBy": ["commands", "agents"],
  "commands": ["dac"],
  "inputs": {
    "projectRoot": {
      "description": "Root directory of git repository",
      "type": "string",
      "optional": true
    },
    "config": {
      "description": "Override default configuration",
      "type": "object",
      "optional": true
    }
  },
  "outputs": {
    "commitMessage": {
      "description": "Drafted commit message",
      "type": "string"
    },
    "analysis": {
      "description": "Analysis of staged changes",
      "type": "object"
    }
  },
  "configuration": {
    "file": "config.json",
    "editable": true,
    "description": "Customize tone, format, and detail level"
  }
}
```

**Validation**: ✅ Metadata file created

---

## 📁 Files to Create

```
.claude/
├── commands/
│   └── dac.md                        [NEW]
└── skills/
    └── draft-commit/
        ├── SKILL.md                  [NEW]
        ├── config.json               [NEW]
        └── draft-commit.json         [NEW]

.claude/tasks/
└── draft-commit.md                   [NEW - this file]
```

---

## ✏️ Files to Modify

```
REFACTORING-TODO.md                   [ADD reference to Task 5]
```

---

## 🧪 Testing & Validation

### Manual Testing

1. Stage some changes: `git add file.ts`
2. Run: `/dac`
3. Expected: Commit message displayed in chat
4. Copy the message
5. Run: `git commit -m "your copied message"`
6. Verify: Commit created with your message

### Configuration Testing

1. Edit `config.json` to change style
2. Stage new changes
3. Run: `/dac`
4. Expected: Message in new style

### Edge Cases

- No staged changes: Should handle gracefully
- Large diff: Should summarize appropriately
- Mixed change types: Should categorize correctly

---

## 🔄 Next Steps

After draft-commit is implemented:

1. Continue with Priority 1 abstractions
2. Apply communication style across system
3. Integrate draft-commit with other HQB features
4. Test full pipeline

---

**Status**: Ready for implementation
**Estimated Time**: 30-40 minutes
**Complexity**: Low-Medium
**Integration**: Fits naturally into HQB patterns

Created: 2025-11-07
Branch: dev
