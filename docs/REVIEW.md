# Project Review: AI-DLC Starter

**Reviewer**: Claude (as a user with a lightning idea)
**Date**: 2026-04-06
**Focus**: Usability for transforming rough ideas into development-ready projects

---

## Executive Summary

The project has a solid foundation with well-designed interactive refinement and comprehensive skill templates. However, there's a significant gap between the stated goal ("start with just a lightning idea") and the current implementation (requires structured input). The project is currently optimized for users who already know what they want to build, not for users who have a rough concept they need help developing.

---

## 1. Is This Easy to Use?

### Current User Journey

```
1. Clone repo
2. Create docs/inception.md (with structured sections)
3. Run /init-project
4. Go through interactive refinement
5. Manually run "Using AI-DLC, create inception phase documents"
6. Start development with /dev-{project}
```

### Issues Identified

| Issue | Severity | Impact |
|-------|----------|--------|
| **inception.md requires structure upfront** | High | Defeats "lightning idea" purpose |
| **Multi-step manual process** | Medium | User friction, easy to get lost |
| **AI-DLC not auto-triggered** | Medium | Extra manual step |
| **File naming conflict** | High | `docs/inception.md` used for two purposes |
| **"Using AI-DLC" magic phrase** | Low | Non-obvious, not a skill |

### The Core Problem

**Current expectation** (from README):
```markdown
# My Project

## Vision
A REST API for managing personal book collections

## Core Features
- User authentication (JWT)
- CRUD operations for books
- Search by title/author
- Export to CSV

## Tech Preferences
- Language: Go
- Database: PostgreSQL
```

**What a "lightning idea" actually looks like**:
```
"I want to build something that helps me track my reading habits"
```

or even:
```
"Book tracker app"
```

The gap between these is enormous. A user with a lightning idea doesn't have JWT, CRUD, or tech stack decisions ready.

### Verdict: ⚠️ Not Easy Enough for Lightning Ideas

The project is well-designed for **elaborating existing requirements**, not for **discovering and developing raw ideas**.

---

## 2. Is This Really Helpful to Elaborate Ideas?

### Strengths

| Aspect | Assessment |
|--------|------------|
| Interactive refinement concept | Excellent |
| Analysis categories (completeness, clarity, feasibility) | Comprehensive |
| Dialogue patterns (proceed, skip, discuss) | Well thought out |
| Requirements.md output format | Professional, complete |
| Traceability (refinement-log.md) | Valuable |

### Weaknesses

| Gap | Why It Matters |
|-----|----------------|
| **No "idea discovery" phase** | Users with vague ideas need guided questions before writing anything |
| **No problem-first approach** | Great products solve problems, but we jump straight to features |
| **No competitive context** | No prompts about existing solutions, differentiation |
| **No user persona exploration** | "Who has this problem?" is never asked |
| **Assumes technical decisions** | What if user doesn't know Go vs Python? |

### Missing: The Pre-Inception Phase

The project assumes user arrives with:
- Clear vision
- Feature list
- Tech preferences

But a "lightning idea" user needs help figuring out:
- What problem am I actually solving?
- Who would use this?
- What's the MVP vs nice-to-have?
- What tech stack makes sense for my constraints?

### Verdict: ⚠️ Helpful Once You Have Structure, Not Before

---

## 3. What Can Claude Help More to Automate?

### High-Impact Additions

#### 3.1 New Skill: `/ideate` (Zero to Inception)

**Purpose**: Start from nothing, end with inception.md

```markdown
# Ideate Skill

Start with just a rough idea and generate a complete inception.md through guided discovery.

## Arguments
- `$ARGUMENTS` - (optional) Your idea in any form, even a single sentence

## Flow

### Phase 1: Idea Capture
"Tell me your idea in whatever form you have it - could be a sentence, a paragraph, or just a few keywords."

### Phase 2: Problem Discovery
- "What problem does this solve?"
- "Who experiences this problem?"
- "How do they solve it today?"
- "What's frustrating about current solutions?"

### Phase 3: Solution Shaping
- "What would success look like?"
- "What's the simplest version that would be useful?"
- "What's definitely NOT in scope for v1?"

### Phase 4: Technical Context
- "Any technology preferences or constraints?"
- "Is this a personal project, startup, or enterprise?"
- "What's your experience level with [detected tech]?"

### Phase 5: Generate inception.md
Create structured inception.md from dialogue.
```

#### 3.2 Auto-Trigger AI-DLC

**Current** (Step 8 of /init-project):
```
To generate full AI-DLC specs, run:
> Using AI-DLC, create the inception phase documents
```

**Should be**:
```
Automatically executing AI-DLC inception phase...
[AI-DLC runs]
Done. aidlc-docs/ has been generated.
```

#### 3.3 New Skill: `/scaffold` (Project Structure)

After specs are generated, create actual project structure:

```
/scaffold

Creates:
- src/ directory structure based on tech stack
- Test directory structure
- Config files (Dockerfile, CI, etc.)
- README.md for the actual project
```

### Medium-Impact Additions

#### 3.4 Example-Driven Refinement

During interactive refinement:
```
"For the 'book search' feature, here's how it might work:
- User types in search box
- Results filter in real-time
- Can search by title, author, or ISBN

Does this match your vision, or did you have something different in mind?"
```

#### 3.5 Smart Defaults

If user doesn't specify tech stack:
```
"Based on your requirements (REST API, simple CRUD, PostgreSQL preference),
I'd suggest:
- Language: Go (good for APIs, your team knows it)
- Framework: Chi or Gin (lightweight, fast)
- ORM: sqlc (type-safe, performant)

Would you like to go with these, or discuss alternatives?"
```

### Automation Summary

| What to Automate | Current State | Proposed State |
|------------------|---------------|----------------|
| Idea → inception.md | Manual | `/ideate` skill |
| inception.md → requirements.md | `/init-project` | Keep (works well) |
| requirements.md → AI-DLC | Manual trigger | Auto-execute |
| AI-DLC → Project structure | Not supported | `/scaffold` skill |
| Tech stack decisions | User must specify | Smart defaults with dialogue |

---

## 4. Other Issues

### 4.1 File Naming Conflict (Critical)

**Problem**: `docs/inception.md` is used for TWO things:
1. Meta-description of aidlc-starter itself (current content)
2. User's project idea (per README instructions)

**Solution**:
- Rename current `docs/inception.md` → `docs/PROJECT-VISION.md` (describes aidlc-starter)
- User's idea goes in `IDEA.md` at project root (simple, obvious)
- Or use a `workspace/` directory for user's project

### 4.2 Template vs Workspace Confusion

**Problem**: After cloning, user is in a mixed state:
- Some files are "template infrastructure" (skills, aidlc-workflows)
- Some files describe the template itself (docs/inception.md, DESIGN.md)
- User needs to add their own content (where?)

**Solution**: Clear separation:
```
aidlc-starter/
├── IDEA.md                    ← USER WRITES HERE (clear, obvious)
├── .claude/skills/            ← Template infrastructure
├── aidlc-workflows/           ← Template infrastructure
├── docs/
│   ├── PROJECT-VISION.md      ← About aidlc-starter (renamed)
│   └── DESIGN.md              ← About aidlc-starter
└── workspace/                 ← All user's generated content goes here
    ├── requirements.md
    ├── vision.md
    ├── tech-env.md
    └── aidlc-docs/
```

### 4.3 No End-to-End Example

**Problem**: User can't see what "success" looks like.

**Solution**: Add `examples/` directory:
```
examples/
├── book-tracker/
│   ├── 1-initial-idea.md      (3 sentences)
│   ├── 2-refined-requirements.md
│   ├── 3-aidlc-docs/
│   └── 4-final-project-structure/
```

### 4.4 Missing "Quick Win" Path

**Problem**: Full process is comprehensive but lengthy for small projects.

**Solution**: Add quick mode:
```
/init-project --quick

Skips:
- Detailed NFR analysis
- Full AI-DLC generation
- Cross-check setup

Generates:
- Basic requirements.md
- Simple development-plan.md
- /dev-{project} skill

Good for: Personal projects, prototypes, hackathons
```

---

## 5. Recommendations Summary

### Must Do (Critical for "lightning idea" use case)

| # | Recommendation | Effort |
|---|----------------|--------|
| 1 | **Create `/ideate` skill** - Zero to inception through dialogue | Medium |
| 2 | **Rename `docs/inception.md`** - Resolve naming conflict | Low |
| 3 | **Create `IDEA.md` template** - Obvious place for user's idea | Low |
| 4 | **Auto-trigger AI-DLC** - Remove manual step | Low |

### Should Do (Significant improvement)

| # | Recommendation | Effort |
|---|----------------|--------|
| 5 | Create `/scaffold` skill for project structure | Medium |
| 6 | Add `examples/` directory with complete flow | Medium |
| 7 | Add quick mode for small projects | Low |
| 8 | Smart defaults for tech stack | Low |

### Nice to Have

| # | Recommendation | Effort |
|---|----------------|--------|
| 9 | Example-driven refinement prompts | Medium |
| 10 | Diagram generation (architecture, data model) | High |
| 11 | Market/competitive analysis prompts | Medium |

---

## 6. Proposed New User Journey

### Before (Current)

```
Clone → Write structured inception.md → /init-project → Manual AI-DLC → ???
```

### After (Proposed)

```
Clone → /ideate → (dialogue) → /init-project → (auto AI-DLC) → /scaffold → /dev-{project}
```

Or even simpler:

```
Clone → /start "I want to build a book tracker"
        ↓
    (Claude asks questions, guides entire process)
        ↓
    Project ready to develop
```

### The Dream: Single Entry Point

```markdown
# /start Skill

The ultimate entry point. Handles everything based on what user provides:

- No input? Start with /ideate
- Has rough idea? Run /ideate with it
- Has inception.md? Run /init-project
- Has requirements.md? Run AI-DLC
- Has aidlc-docs? Run /scaffold
- Has code? Run /dev-{project}

Automatically detects state and continues from there.
```

---

## 7. Conclusion

**Current State**: Well-architected system for structured requirements refinement.

**Gap**: Not optimized for truly rough "lightning ideas" - requires too much upfront structure.

**Path Forward**: Add pre-inception tooling (`/ideate`) and streamline the flow to achieve the stated goal of "start with just an idea."

The bones are good. The interactive refinement engine is valuable. The skill system works. We just need to extend the beginning of the funnel to catch users at an earlier stage of idea development.

---

*This review was conducted from a user perspective, focusing on the stated goal of helping users "start with just a lightning idea."*
