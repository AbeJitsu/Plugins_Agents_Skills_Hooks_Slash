# Task: Apply Supportive Communication Style

## 🎯 Overview

We're making HQB feel **inviting, focused, considerate, and supportive** throughout the system. Right now, the tone is technical and functional, but lacks warmth and guidance. This task transforms how the system communicates with users and developers — making it feel like a supportive partner, not just a tool.

**Why it matters**:
- Users interact with agents, commands, and skills daily
- The tone sets expectations and shapes the experience
- Supportive language builds confidence and clarity
- Focused communication prevents confusion
- Considerate approach shows we respect the user's time

**What it covers**:
- Agent instructions and prompts
- Command descriptions and help text
- Skill documentation and guidance
- Error messages and feedback
- Library documentation and API docs

---

## 🎯 Goals

- [ ] Document the communication style framework
- [ ] Create tone examples and guidelines
- [ ] Update all agents with new tone
- [ ] Update all commands with new tone
- [ ] Update all skills with new tone
- [ ] Update all library docs with new tone
- [ ] Verify consistency across all components

---

## 📖 Current Communication Style

### Current Examples (Technical, Functional)

**Current Project Analyzer**:
```markdown
# Project Analyzer Agent

This agent detects the project type based on user input and loads appropriate standards.
```
→ Functional but impersonal

**Current Standards Definer**:
```markdown
## Interview Process

Ask a series of questions to understand the user's development principles.
```
→ Direct but not warm

**Current Skill Description**:
```markdown
# Validate Requirements

Checks that input requirements meet the standards validation rules.
```
→ Technical but not guided

### Issues with Current Style

1. **Lacks warmth**: Feels like reading documentation, not having a conversation
2. **No guidance**: Doesn't explain WHY something matters
3. **Assumes expertise**: Doesn't help new users
4. **No reassurance**: Doesn't acknowledge emotional side of development
5. **No ownership**: Doesn't feel like it's on your team

---

## 🏗️ New Communication Style: Inviting, Focused, Considerate, Supportive

### Core Principles

#### 1. **Inviting** ✨
- Makes users WANT to engage
- Warm, welcoming opening
- Explains why we're doing this
- Removes barriers to participation

**Example**:
```markdown
# Welcome to the Standards Definition Process

Let's take a moment to capture what matters most to your development approach.
This creates a personalized quality filter that ensures every deliverable reflects
your values and standards.
```

---

#### 2. **Focused** 🎯
- Clarifies the specific goal
- Eliminates unnecessary detail
- One idea per section
- Clear next steps

**Example**:
```markdown
## Step 1: Identify Your Project Type

We need to understand what you're building so we can apply the right quality standards.

What are you working on?
- Code Features
- Documentation
- Refactoring
- Test Suite
- Content Creation
```

---

#### 3. **Considerate** 🤝
- Respects user's time and knowledge
- Acknowledges effort and decisions
- Offers help without being pushy
- Recognizes different experience levels

**Example**:
```markdown
## Your Input Matters

The more detail you provide, the better we can tailor quality checks.
But even a brief description works — we'll adapt from there.

What would you like to build?
```

---

#### 4. **Supportive** 💪
- Builds confidence
- Explains reasoning
- Celebrates progress
- Offers clear guidance
- No judgment

**Example**:
```markdown
## Building Your Quality Standards

You're creating a personalized quality filter. This is powerful because:
- **Your voice**: Standards reflect what matters to YOU
- **Consistency**: Every deliverable passes the same filter
- **Confidence**: You know exactly what "done" looks like

Let's get started.
```

---

## 📋 Style Guidelines by Component

### Agents

Agents are conversational partners. They guide the user through a process.

#### Opening
- Warm greeting
- Clear purpose
- Inviting tone

**Template**:
```markdown
# [Agent Name]

Welcome! This agent helps you [specific purpose].

[Why this matters — what value does it provide?]

Let's get started.
```

**Example - Project Analyzer**:
```markdown
# Project Type Analyzer

Welcome! This agent helps you identify your project type and load the right quality standards.

Understanding your project type ensures we apply standards that actually matter to what you're building. It's like giving our quality checklist the context it needs to be useful.

Let's start by understanding what you're working on.
```

#### Questions
- Clear and specific
- Explain WHY you're asking
- Offer examples if helpful

**Template**:
```markdown
## [Question Topic]

[Why we're asking this — what will we do with the answer?]

[The actual question or options]

[Optional: Example or clarification]
```

**Example**:
```markdown
## What's Your Project Type?

The project type helps us understand your context so we can apply standards that are relevant to your work.

Which of these best describes what you're building?

1. **Code Features** — New functions, components, APIs, or modules
2. **Documentation** — Guides, tutorials, specifications, or README files
3. **Refactoring** — Improving existing code structure or performance
4. **Test Suite** — Automated tests or testing infrastructure
5. **Content Creation** — Articles, blog posts, or educational content

(You can also describe your project in your own words if these don't fit!)
```

#### Closing
- Celebration of progress
- Clear next step
- Supportive tone

**Template**:
```markdown
Great! You've [accomplished something].

Next, we'll [next step] so that [benefit].
```

---

### Commands

Commands are entry points. They should feel like helpful invitations.

#### Description
- One clear sentence
- No jargon
- Tells what you'll accomplish

**Current example** (bad):
```markdown
Run the quality pipeline for your project
```

**Improved example**:
```markdown
Launch the high-quality builder — your guided path to a polished, standards-aligned deliverable
```

#### Help Text
- Warm introduction
- Clear purpose
- What you'll accomplish
- Next steps

**Template**:
```markdown
## [Command Description]

This command guides you through our quality pipeline. By the end, you'll have:
- ✓ Validated requirements
- ✓ Generated your deliverable
- ✓ Formatted to your standards
- ✓ Verified quality

## How It Works

[Brief explanation of the process]

## Next Steps

1. Run the command
2. Answer a few questions about your project
3. Get your polished deliverable

Ready? Let's build something great!
```

**Example - /hqb command**:
```markdown
# High-Quality Builder — Main Pipeline

Guided path to a polished, standards-aligned deliverable.

## What This Does

This command runs our adaptive quality pipeline — your personal quality checklist in action.

By the end, you'll have:
- ✓ Validated that your requirements are clear
- ✓ Generated your deliverable
- ✓ Formatted it to your standards
- ✓ Verified it meets quality criteria

## How It Works

1. You tell us your project type
2. We load your quality standards
3. The pipeline runs 4 verification steps
4. Your deliverable emerges, polished and ready

## Ready?

The pipeline adapts based on your project. Let's build something great!
```

---

### Skills

Skills execute work. They should be clear, guided, and celebrate progress.

#### Introduction
- What we're doing now
- Why it matters
- What you'll get

**Template**:
```markdown
# [Skill Name]

We're now [what we're doing]. This is important because [why].

By the end, you'll have [what they get].
```

**Example - Validate Requirements**:
```markdown
# Validate Requirements

We're now reviewing your requirements to ensure they're clear and complete.
This matters because well-understood requirements lead to better outcomes.

By the end, you'll know exactly what we're building and why.
```

#### Process Steps
- Clear action
- Explanation
- What to expect

**Template**:
```markdown
## Step [N]: [Action]

We'll [specific action] to [goal].

This helps us [benefit].

[Any guidance or examples]
```

#### Progress & Results
- Show what we found
- Celebrate completeness
- Clear next step

**Template**:
```markdown
## Results

✓ [Achievement 1]
✓ [Achievement 2]
✓ [Achievement 3]

Everything looks great! Moving to the next step.
```

---

### Library Documentation

Library docs explain how to USE something. Keep it supportive and clear.

#### Overview Section
- What it is
- Why it exists
- What problems it solves

**Example - StandardsRepository**:
```markdown
# StandardsRepository

A centralized, friendly interface for all standards access in HQB.

## Why It Exists

Standards are core to quality, but they were scattered across the system —
different files accessing them in different ways. This created fragility and duplication.

StandardsRepository brings them together into one clean interface that everyone uses.

## What It Solves

- **Consistency**: One way to access standards everywhere
- **Reliability**: Validation ensures standards are always valid
- **Clarity**: Clear methods with clear purposes
- **Future-Proof**: We can improve storage later without changing anything else
```

#### Method Documentation
- Simple explanation
- What it does
- When to use it
- Example

**Template**:
```markdown
### methodName(param1, param2)

[One clear sentence about what this does]

**Use this when**: [Specific scenario]

**Parameters**:
- `param1` (type): [What it is]
- `param2` (type): [What it is]

**Returns**: [What comes back]

**Example**:
```
[Real code example]
```
```

---

## 📋 Implementation Steps

### Step 1: Create Communication Style Guide

**What**: Document the framework and principles

**Why**: Ensures consistency across all components

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/lib/communication-style.md`:

Use the principles and examples from this task document to create a comprehensive guide. Include:
- Core principles (Inviting, Focused, Considerate, Supportive)
- Style guidelines by component type
- Tone examples and anti-examples
- Checklist for applying the style

**Validation**: ✅ Guide created and serves as reference

---

### Step 2: Update All Agents

**Target agents**:
1. `project-analyzer.md`
2. `standards-definer.md`
3. `quality-orchestrator.md`

**For each agent**:
- [ ] Make opening warmer and more inviting
- [ ] Add "why" context to questions
- [ ] Celebrate progress at key points
- [ ] Make closing supportive and forward-looking

**Example change**:

**Current**:
```markdown
# Project Analyzer Agent

This agent detects the project type based on user input and loads appropriate standards.
```

**Updated**:
```markdown
# Project Type Analyzer

Welcome! This agent helps you identify your project type and load the right quality standards.

Understanding your project type is the first step in our quality journey. It ensures we apply standards that matter to YOUR work, not some generic checklist.

Let's get started.
```

**Validation**: ✅ All agents use welcoming, guided tone

---

### Step 3: Update All Commands

**Target commands**:
1. `/define-standards` (define-standards.md)
2. `/hqb` (hqb.md)
3. `/show-standards` (show-standards.md)

**For each command**:
- [ ] Write inviting one-liner description
- [ ] Add warm introduction
- [ ] Explain what you'll accomplish
- [ ] Make help text feel like an invitation

**Example change**:

**Current**:
```markdown
/hqb - Run the quality pipeline for your project
```

**Updated**:
```markdown
/hqb - Launch the high-quality builder — your guided path to a polished, standards-aligned deliverable
```

**Validation**: ✅ All commands feel inviting and clear

---

### Step 4: Update All Skills

**Target skills**:
1. `validate-requirements/SKILL.md`
2. `generate-output/SKILL.md`
3. `format-standardize/SKILL.md`
4. `quality-verify/SKILL.md`

**For each skill**:
- [ ] Warm, clear introduction explaining what we're doing
- [ ] "Why this matters" section
- [ ] Progress celebration
- [ ] Supportive tone throughout

**Example change**:

**Current**:
```markdown
# Validate Requirements Skill

Validates that input requirements meet standards validation rules.
```

**Updated**:
```markdown
# Validate Requirements

We're now reviewing your requirements to ensure they're clear and complete.

This matters because well-understood requirements lead to better deliverables.
Let's make sure we're building the right thing.

By the end, you'll know exactly what we're creating and why.
```

**Validation**: ✅ All skills guide and support the user

---

### Step 5: Update All Library Documentation

**Target files**:
1. `lib/standards-repository.md`
2. `lib/project-type-registry.md`
3. `lib/pipeline-state-utilities.md`
4. Any other lib files

**For each file**:
- [ ] Warm introduction (why this exists)
- [ ] Clear method documentation
- [ ] Supportive examples
- [ ] Helpful guidance

**Example**:

Make sure each library doc has:
- "Why It Exists" section (personal, not technical)
- "What It Solves" section (benefits-focused)
- Clear, friendly method docs
- Real examples

**Validation**: ✅ Library docs feel supportive and clear

---

### Step 6: Create Tone Checklist

**What**: Simple checklist for verifying tone in any file

**Why**: Makes it easy to catch tone issues

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/lib/tone-checklist.md`:

```markdown
# Tone Checklist

Use this when writing or reviewing any content for HQB.

## Inviting ✨

- [ ] Does it feel warm and welcoming?
- [ ] Would a new user feel excited to engage?
- [ ] Is there a clear invitation or call to action?
- [ ] No jargon without explanation?

## Focused 🎯

- [ ] Is there one clear idea per section?
- [ ] Can you state the purpose in one sentence?
- [ ] Are next steps clear?
- [ ] Is there any unnecessary detail?

## Considerate 🤝

- [ ] Respects the user's time and knowledge?
- [ ] Acknowledges different skill levels?
- [ ] Offers help without being pushy?
- [ ] No assumptions about background?

## Supportive 💪

- [ ] Builds confidence rather than doubt?
- [ ] Explains the reasoning?
- [ ] Free of judgment?
- [ ] Celebrates progress?
- [ ] Provides clear guidance?

## If All Boxes Are Checked ✓

The content is ready to ship!
```

**Validation**: ✅ Checklist created and available

---

## 📁 Files to Create

```
.claude/lib/
├── communication-style.md             [NEW]
└── tone-checklist.md                  [NEW]
```

---

## ✏️ Files to Modify

```
.claude/agents/
├── project-analyzer.md                [MODIFY - Step 2]
├── standards-definer.md               [MODIFY - Step 2]
└── quality-orchestrator.md            [MODIFY - Step 2]

.claude/commands/
├── define-standards.md                [MODIFY - Step 3]
├── hqb.md                             [MODIFY - Step 3]
└── show-standards.md                  [MODIFY - Step 3]

.claude/skills/
├── validate-requirements/SKILL.md     [MODIFY - Step 4]
├── generate-output/SKILL.md           [MODIFY - Step 4]
├── format-standardize/SKILL.md        [MODIFY - Step 4]
└── quality-verify/SKILL.md            [MODIFY - Step 4]

.claude/lib/
├── standards-repository.md            [MODIFY - Step 5]
├── project-type-registry.md           [MODIFY - Step 5]
└── pipeline-state-utilities.md        [MODIFY - Step 5]
```

---

## 🧪 Testing & Validation

### Read-Through Test

For each modified file:
1. Read opening paragraph
2. Does it feel warm and inviting?
3. Is the purpose clear?
4. Would a new user feel encouraged?

**Expected**: Warm, clear, encouraging tone throughout

---

### Tone Checklist Review

For each modified file:
1. Use the tone-checklist.md
2. Check all four dimensions
3. Fix any failing checks

**Expected**: All checkboxes pass

---

### Consistency Review

1. Read agent descriptions back-to-back
2. Read all command descriptions
3. Read all skill introductions

**Expected**: Consistent, warm, supportive tone throughout

---

### User Perspective Test

Ask yourself: "Would a new developer feel welcomed and supported using this system?"

**Expected**: Yes

---

## 🔄 What's Next

After Communication Style is implemented:

1. **StandardsRepository** ✓
2. **ProjectTypeRegistry** ✓
3. **StructuredPipelineState** ✓
4. **CommunicationStyle** ✓
5. **Testing & Validation** (final step)

All Priority 1 tasks will be complete, ready to merge and move to Priority 2.

---

**Status**: Ready for implementation
**Estimated Time**: 90-120 minutes
**Complexity**: High (affects 15+ files, requires careful tone work)

Created: 2025-11-07
Branch: dev
