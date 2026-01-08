<!--
  Source: https://github.com/robotdad/amplifier-collection-ddd
  License: MIT
  Auto-converted for Claude Code Plugin format
-->

# DDD Core Principles

**Understanding Document-Driven Development philosophy and approach**

---

## The Fundamental Principle

**"Documentation IS the specification. Code implements what documentation describes."**

This isn't "write docs first" - it's a systematic methodology where:
1. Documentation defines the target state
2. Human reviews and approves the design
3. Code implements exactly what docs describe
4. Tests verify code matches documentation
5. Docs and code cannot drift (by design)

---

## Why Documentation First Matters

### The Traditional Problem

**Code → Docs approach**:
- Docs written after code (if at all)
- Docs lag behind changes
- Docs and code diverge over time
- AI tools load conflicting information
- Context poisoning leads to wrong implementations
- Bugs from misunderstandings

**Result**: Documentation becomes untrustworthy. Developers stop reading docs. More bugs.

### The DDD Solution

**Docs → Approval → Code approach**:
- Design captured in docs first
- Human reviews and approves design
- Only then write code
- Code matches docs exactly
- Tests verify alignment
- Drift is impossible

**Result**: Documentation is always correct. Single source of truth. Fewer bugs.

---

## Integration with Project Philosophy

DDD builds on and enforces:

### Ruthless Simplicity

From `@skills/amplifier-philosophy/SKILL.md`:

**Principles**:
- Start minimal, grow as needed
- Avoid future-proofing
- Question every abstraction
- Clear over clever

**Applied in DDD**:
- Docs define minimal viable feature
- No speculative features documented
- Each doc has one clear purpose
- Progressive organization (simple → detailed)

### Modular Design

From `@skills/amplifier-philosophy/SKILL.md`:

**Principles**:
- Clear interfaces (studs)
- Self-contained modules (bricks)
- Regeneratable from specs
- Human architects, AI builds

**Applied in DDD**:
- Docs define interfaces before implementation
- Module boundaries documented first
- Code can be regenerated from docs
- Human reviews design, AI implements

---

## Core DDD Techniques

### 1. Retcon Writing

Write documentation **as if the feature already exists**.

**Not**:
- "We will add authentication"
- "Coming in version 2.0"
- "Migration: Update your config to..."

**Instead**:
- "The system uses JWT authentication"
- "Configure authentication in config.yaml"
- Examples show current config format

**Why**: Eliminates future tense, prevents drift, makes docs immediately useful.

Reference: `@skills/ddd-guide/references/core-concepts/retcon-writing.md`

### 2. File Crawling

Systematic processing of multiple files without context overload.

**Pattern**:
1. Generate checklist of files to update
2. Process ONE file at a time
3. Mark complete in checklist
4. Move to next file

**Why**: Token efficiency (99.5% reduction), prevents missing files, clear progress, resumable.

Reference: `@skills/ddd-guide/references/core-concepts/file-crawling.md`

### 3. Context Poisoning Prevention

Detect and eliminate inconsistencies:
- Same concept explained differently
- Contradictory statements
- Inconsistent terminology
- Duplicate documentation

**Actions**: Pause, document conflicts, ask user which is correct, fix ALL instances.

**Why**: AI tools make wrong decisions when docs conflict. Single source of truth is critical.

Reference: `@skills/ddd-guide/references/core-concepts/context-poisoning.md`

### 4. Maximum DRY

Each concept lives in ONE place only.

**Practice**:
- No copy-paste between docs
- Use links/references instead of duplication
- Consolidate when same info found elsewhere

**Why**: Reduces maintenance burden, eliminates drift, single source of truth.

### 5. Progressive Organization

Right-size content for audience and purpose.

**Structure**:
- README → High-level overview
- User docs → How to use
- Developer docs → How it works
- Architecture docs → Why designed this way

**Why**: Easy to find info, appropriate detail level, not overwhelming.

**Detailed in**: `@skills/ddd-guide/references/agents/documentation-retroner.md` (Technique 5)

---

## The DDD Workflow

### Phase 0-1: Planning & Design

**Agent**: planning-architect

**Activities**:
- Problem framing (what and why)
- Reconnaissance (understand current codebase)
- Design proposals (alternatives with trade-offs)
- Detailed plan creation

**Artifact**: `ai_working/ddd/plan.md`

Reference: `@skills/ddd-guide/references/phases/00-planning-and-alignment.md`

### Phase 2: Documentation Updates

**Agent**: documentation-retroner

**Activities**:
- File crawling through all docs
- Retcon writing applied
- Maximum DRY enforcement
- Context poisoning elimination
- Progressive organization

**Artifacts**: Updated docs, `ai_working/ddd/docs_status.md`

**Gate**: User reviews and commits when satisfied

Reference: `@skills/ddd-guide/references/phases/01-documentation-retcon.md`, `02-approval-gate.md`

### Phase 3: Code Planning

**Agent**: code-planner

**Activities**:
- Gap analysis (current code vs new docs)
- Implementation chunking
- Dependency sequencing
- Risk assessment

**Artifact**: `ai_working/ddd/code_plan.md`

**Gate**: User approves implementation approach

Reference: `@skills/ddd-guide/references/phases/03-implementation-planning.md`

### Phase 4-5: Implementation & Testing

**Agent**: implementation-verifier

**Activities**:
- Chunk-by-chunk implementation
- Test as user would (integration focus)
- Verification against docs
- Philosophy compliance checks

**Artifacts**: Code changes, `ai_working/ddd/impl_status.md`, `test_report.md`

**Gates**: User authorizes each commit

Reference: `@skills/ddd-guide/references/phases/04-code-implementation.md`, `05-testing-and-verification.md`

### Phase 6: Finalization

**Agent**: finalization-specialist

**Activities**:
- Final integration testing
- Cleanup temporary artifacts
- Prepare for delivery

**Gates**: User authorizes push/PR

Reference: `@skills/ddd-guide/references/phases/06-cleanup-and-push.md`

---

## Why DDD Works

### 1. Prevents Expensive Mistakes

- Design flaws caught before implementation
- Review is cheap, rework is expensive
- Philosophy compliance checked early
- Human judgment applied at right time

### 2. Eliminates Context Poisoning

- Single source of truth
- No duplicate documentation
- No stale information
- Clear, unambiguous specs

### 3. Optimizes AI Collaboration

- AI has clear specifications
- No guessing from unclear docs
- Can regenerate from spec
- Systematic file processing

### 4. Maintains Quality

- Documentation always correct
- Code matches documentation
- Examples always work
- New developers understand from docs alone

### 5. Reduces Bugs

- Fewer misunderstandings
- Clear requirements
- Tested against spec
- Integration verified early

---

## Success Criteria

You're doing DDD well when:

**Documentation Quality**:
- ✅ Docs and code never diverge
- ✅ Zero context poisoning incidents
- ✅ Examples work when copy-pasted
- ✅ New developers understand from docs alone

**Process Quality**:
- ✅ Changes require minimal rework
- ✅ Design flaws caught at approval gate
- ✅ Philosophy principles naturally followed
- ✅ Git history is clean (no thrashing)

**AI Collaboration**:
- ✅ AI tools make correct decisions
- ✅ No "wrong approach implemented confidently"
- ✅ Can regenerate modules from docs

**Team Impact**:
- ✅ Implementation time decreases
- ✅ Bug rate decreases
- ✅ Questions about features, not "which docs are right?"

---

## When Not to Use DDD

DDD has overhead that's not justified for:

- Simple typo fixes
- Single-file bug fixes
- Emergency hotfixes
- Trivial updates
- Documentation-only changes (no code impact)

**Rule of thumb**: If the change touches fewer than 3 files and is straightforward, skip DDD.

---

## Comparison to Other Methodologies

### vs Traditional "Docs First"

**Traditional**: Write docs, write code, docs drift over time
**DDD**: Systematic process with approval gates preventing drift

### vs Spec-Driven Development (Spec-Kit)

**Spec-Kit**: Formal specifications for greenfield development
**DDD**: Documentation-first for existing codebase evolution

**Both work together**: Use spec-kit for formal specs, DDD for documentation updates

### vs Agile Stories

**Agile**: User stories define requirements
**DDD**: Documentation defines complete behavior

**Can combine**: Stories inform docs, docs are the detailed spec

---

## Related Documentation

**This Collection**:
- Core Concepts: `@skills/ddd-guide/references/core-concepts/`
- Phase Guides: `@skills/ddd-guide/references/phases/`
- Agent Definitions: `@skills/ddd-guide/references/agents/`

**Foundation**:
- `@skills/amplifier-philosophy/SKILL.md`
- `@skills/amplifier-philosophy/SKILL.md`

**Amplifier**:
- Collections Guide
- Profile Authoring Guide
- Agent Delegation Guide

---

**Document Version**: 1.0
**Last Updated**: 2025-10-27
