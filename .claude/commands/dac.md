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
