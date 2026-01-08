<!--
  Source: https://github.com/robotdad/amplifier-collection-ddd
  License: MIT
  Auto-converted for Claude Code Plugin format
-->

# Foundation Philosophy Integration

**How DDD applies Amplifier's core philosophies**

---

## Ruthless Simplicity in DDD

Reference: `@skills/amplifier-philosophy/SKILL.md`

### How Each Phase Applies Simplicity

**Phase 0-1: Planning**
- Propose 2-3 alternatives, choose simplest that works
- Question every abstraction in design
- Avoid future-proofing in plan
- Document minimal viable implementation

**Phase 2: Documentation**
- Each concept in ONE place (Maximum DRY)
- Progressive organization (simple → detailed)
- Clear over comprehensive
- Remove cruft and outdated content

**Phase 3: Code Planning**
- Minimal implementation chunks
- Avoid over-engineering
- Direct solutions over complex patterns

**Phase 4: Implementation**
- Write simplest code that matches docs
- No speculative features
- Clear error messages over clever handling
- One working feature > multiple partial features

**Phase 5-6: Finalization**
- Remove temporary artifacts
- Eliminate unnecessary complexity
- Clean git history

---

## Modular Design in DDD

Reference: `@skills/amplifier-philosophy/SKILL.md`

### Bricks and Studs Applied

**Documentation Defines Studs First**:
- Phase 1: Document interfaces (studs) before implementation
- Clear contracts between modules
- Stable connection points
- Implementation can be regenerated

**Code Implements Bricks**:
- Phase 4: Build self-contained modules
- Each module implements documented interface
- Modules can be rebuilt from docs
- AI builds, human reviews behavior

**Key Insight**: Docs ARE the blueprint. Code implements the blueprint.

### AI as Builder, Human as Architect

**Human Role** (DDD):
- Design the feature (planning phase)
- Review the documentation (approval gate)
- Approve implementation approach (code planning)
- Verify behavior matches docs (testing)

**AI Role** (DDD):
- Systematic documentation updates (file crawling)
- Retcon writing application
- Code generation from docs
- Testing and verification

**Never**: Human reads all code. They verify BEHAVIOR matches DOCS.

---

## How DDD Enforces Philosophy

### Simplicity Enforcement

**At Each Phase**:
- Planning: "Is this the simplest approach?"
- Documentation: "Can this be explained more simply?"
- Code Planning: "Do we need this complexity?"
- Implementation: "Is there a simpler way?"

**Agents Check**:
- planning-architect validates against simplicity principles
- documentation-retroner removes cruft
- code-planner questions abstractions
- implementation-verifier implements minimally

### Modularity Enforcement

**At Each Phase**:
- Planning: "Are module boundaries clear?"
- Documentation: "Are interfaces documented?"
- Code Planning: "Are modules self-contained?"
- Implementation: "Does code follow documented structure?"

**Agents Check**:
- planning-architect defines clear module boundaries
- documentation-retroner documents interfaces (studs)
- code-planner validates separation of concerns
- implementation-verifier implements modular structure

---

## Philosophy as Quality Gate

### Planning Gate

Before moving to documentation:
- [ ] Ruthless Simplicity: Simplest approach chosen?
- [ ] Modular Design: Clear boundaries defined?
- [ ] No future-proofing: Building only what's needed?

### Documentation Gate

Before moving to implementation:
- [ ] Maximum DRY: Each concept in one place?
- [ ] Progressive organization: Right-sized for audience?
- [ ] Clear interfaces: Studs documented before bricks?

### Implementation Gate

Before finalizing:
- [ ] Code matches docs: Perfect alignment?
- [ ] No over-engineering: Minimal implementation?
- [ ] Modular structure: Self-contained modules?

---

## Why This Integration Matters

**DDD without philosophy** → Process without principle (mechanical)

**DDD with philosophy** → Principled evolution (thoughtful)

Every DDD decision traces back to:
- Ruthless Simplicity (keep it minimal)
- Modular Design (clear boundaries)
- Trust in emergence (simple parts → complex systems)

---

**The philosophies aren't separate from DDD - they ARE DDD's foundation.**

**Document Version**: 1.0
**Last Updated**: 2025-10-27
