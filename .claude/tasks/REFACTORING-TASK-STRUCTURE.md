# Refactoring Task Structure Guide

Each task in the Priority 1 refactoring follows a consistent, approachable format designed to guide you through implementation with clarity and support.

## Task File Format

Every task markdown file contains:

### 1. **Overview Section**
- Clear, inviting description of what we're doing
- Why it matters (business/technical impact)
- What problems it solves

### 2. **Goals Section**
- Specific, measurable outcomes
- What "done" looks like

### 3. **Current State**
- How things work now
- Problems with current approach
- Code examples from real files

### 4. **New Design**
- How things will work after refactoring
- Architecture diagrams or structure
- Key abstractions and interfaces

### 5. **Implementation Steps**
- Numbered, sequential steps
- Each step includes:
  - **What**: What we're doing
  - **Why**: Purpose and reasoning
  - **How**: Specific code/commands
  - **Validation**: How to verify it worked

### 6. **Files to Create**
- List of new files to create
- File templates or examples included
- Directory placement

### 7. **Files to Modify**
- Each file with:
  - Current problematic section
  - What needs to change
  - Replacement code/pattern

### 8. **Testing & Validation**
- How to verify the refactoring is successful
- Commands to run
- Expected outcomes

### 9. **Rollback Plan** (if breaking changes)
- How to undo if something goes wrong
- Recovery commands

## Task Naming Convention

Tasks are named descriptively:
- `standards-repository.md` - Implementation of StandardsRepository abstraction
- `project-type-registry.md` - Implementation of ProjectTypeRegistry
- `structured-pipeline-state.md` - Replacement of text-based hook validation
- `communication-style.md` - Application of supportive tone throughout

## Using This Structure

Each task is **self-contained**: You can read and understand one task independently.

Tasks are **sequential but not dependent**: While we do them in priority order, most can be understood without reading others first.

Tasks are **detailed and supportive**: They explain the reasoning, not just the mechanics.

---

## Current Tasks in Priority 1

1. **StandardsRepository** — Centralized standards access pattern
2. **ProjectTypeRegistry** — Single source of truth for project types
3. **StructuredPipelineState** — Replacing fragile text-parsing with structured state
4. **CommunicationStyle** — Applying inviting, supportive tone everywhere

---

**Note**: When implementing, reference these task files frequently. They're your guide through the refactoring journey.
