# Init Project Skill

Bootstrap a new project from an idea to AI-DLC specs and dev skills.

## Arguments

- `$ARGUMENTS` - (optional) Path to idea file. If not provided, checks in order:
  1. `IDEA.md` (primary)
  2. `docs/PROJECT-VISION.md` (secondary)
  3. `docs/inception.md` (legacy fallback)

## Objective

Transform a rough idea in inception.md into:
1. Enhanced requirements through Claude-powered interactive refinement
2. AI-DLC specification documents (vision.md, tech-env.md, aidlc-docs/)
3. Project-specific development skills

---

## Execution Steps

### Step 0: Validate Environment

1. **Check idea file exists** (in priority order):
   - If `$ARGUMENTS` provided, use that path
   - Otherwise check: `IDEA.md` → `docs/PROJECT-VISION.md` → `docs/inception.md`
   - If none found, suggest running `/ideate` to create one

2. **Verify AI-DLC rules available**:
   - Check `aidlc-workflows/aidlc-rules/` exists
   - If missing, warn and provide setup instructions

3. **Show welcome message**:
   ```
   ## Project Initialization

   I'll help you transform your idea into a fully-specified project.

   ### Process Overview
   1. Interactive Refinement - Enhance your requirements through dialogue
   2. Spec Generation - Create AI-DLC documentation
   3. Skill Generation - Create development automation skills

   Let's begin by understanding your idea...
   ```

---

## Stage 0: Interactive Requirements Refinement

### Step 1: Read and Analyze Idea

1. **Read** the idea file completely (IDEA.md or equivalent)

2. **Extract key elements**:
   - Project name/identifier
   - Vision/purpose statement
   - Core features list
   - Tech preferences (if specified)
   - Constraints (if specified)

3. **Identify what's missing** from required sections:
   - Project Name
   - Vision
   - Core Features

### Step 2: Deep Analysis

Think like a senior architect and analyze:

**Understanding Intent:**
- What is the user really trying to achieve?
- What problem are they solving for their end users?
- What's the business context (if discernible)?

**Identifying Gaps:**
- What happens when things go wrong? (error handling)
- What about edge cases? (empty states, concurrent access, failures)
- What's not mentioned but essential? (auth, logging, monitoring, validation)

**Challenging Assumptions:**
- Is this the right technical approach?
- Are there simpler alternatives?
- What are the scaling implications?

### Step 3: Present Analysis and Suggestions

Present findings in this structured format:

```markdown
## Analysis of Your Idea

I've analyzed your idea. Here's my understanding and suggestions:

### What I Understand

[Summary of the project intent in your own words - demonstrate you understand the WHY, not just the WHAT]

### Current Strengths

[List 2-3 things that are well-defined in the inception]

### Suggestions for Improvement

#### 1. [Category]: [Specific Issue]

**Current state**: [What's written or missing]
**Why it matters**: [Impact on project success]
**Suggestion**: [Concrete recommendation]
**Questions**: [Clarifying questions if needed]

#### 2. [Category]: [Specific Issue]
...

### Categories to Consider

| Category | Status | Notes |
|----------|--------|-------|
| Core Features | ✅/⚠️/❌ | [Brief assessment] |
| Error Handling | ✅/⚠️/❌ | [Brief assessment] |
| Authentication | ✅/⚠️/❌ | [Brief assessment] |
| Data Validation | ✅/⚠️/❌ | [Brief assessment] |
| Performance | ✅/⚠️/❌ | [Brief assessment] |
| Security | ✅/⚠️/❌ | [Brief assessment] |
| Monitoring | ✅/⚠️/❌ | [Brief assessment] |

### Questions for You

1. [Specific question that affects architecture]
2. [Specific question about edge cases]
3. [Specific question about non-functional requirements]

---

How would you like to proceed?
- **proceed**: Accept suggestions and continue
- **skip [N]**: Skip suggestion N
- **discuss [N]**: Discuss suggestion N in more detail
- **add [feature]**: Add a new requirement
```

### Step 4: Interactive Dialogue Loop

Handle user responses:

| User Response | Action |
|---------------|--------|
| "proceed" / "looks good" / "continue" | Move to Step 5 |
| "yes to all" | Apply all suggestions, move to Step 5 |
| "skip N" | Mark suggestion N as skipped, re-prompt |
| "discuss N" | Explain suggestion N in detail, re-prompt |
| Asks question | Answer thoughtfully, re-prompt |
| Provides context | Incorporate into understanding, re-analyze if needed |
| "add [feature]" | Add to requirements, suggest related considerations |

**Loop until** user confirms readiness to proceed.

### Step 5: Generate Enhanced Requirements

Create `docs/requirements.md` with this structure:

```markdown
# Project Requirements: {Project Name}

*Generated via interactive refinement on {date}*

## 1. Overview

### Problem Statement
[What problem does this solve - from understanding, not just copying]

### Target Users
[Who will use this - inferred or specified]

### Success Metrics
[How do we measure success - explicit or suggested]

## 2. Functional Requirements

### FR-001: {Feature Name}
- **Description**: Clear description of the feature
- **User Story**: As a [user], I want to [action] so that [benefit]
- **Acceptance Criteria**:
  - [ ] Criterion 1
  - [ ] Criterion 2
- **Priority**: Must-have / Should-have / Nice-to-have
- **Notes**: Clarifications from refinement dialogue

[Repeat for each feature]

## 3. Non-Functional Requirements

### NFR-001: Performance
- [Specific requirements]

### NFR-002: Security
- [Specific requirements]

### NFR-003: Scalability
- [Specific requirements]

### NFR-004: Reliability
- [Specific requirements]

## 4. Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | {choice} | {why} |
| Framework | {choice} | {why} |
| Database | {choice} | {why} |
| Infrastructure | {choice} | {why} |

## 5. Constraints & Assumptions

### Constraints
- [Known limitations]

### Assumptions
- [Assumptions made during refinement]

## 6. Out of Scope

- [Features explicitly deferred]
- [Future considerations]

## 7. Open Questions

- [Items requiring further clarification]
```

### Step 6: Create Refinement Log

Save the dialogue to `docs/refinement-log.md`:

```markdown
# Refinement Log: {Project Name}

**Date**: {date}
**Initial idea**: [summary of original content from IDEA.md or equivalent]

## Refinement Dialogue

### Round 1
**Claude's Analysis**: [summary]
**User's Response**: [response]
**Outcome**: [what was decided]

[Continue for each round]

## Final Changes

| Original | Refined | Reason |
|----------|---------|--------|
| [original text] | [new text] | [why changed] |

## Suggestions Applied
- [x] Suggestion 1
- [ ] Suggestion 2 (skipped - reason)
- [x] Suggestion 3
```

---

## Stage 1: AI-DLC Spec Generation

### Step 7: Generate AI-DLC Input Documents

Create `docs/vision.md` (AI-DLC format):

```markdown
# Vision Document

## Project Overview
[From requirements.md Overview section]

## Goals
[Derived from requirements]

## Scope
### In Scope
[From FR requirements]

### Out of Scope
[From Out of Scope section]

## Stakeholders
[From Target Users]

## Success Criteria
[From Success Metrics]
```

Create `docs/tech-env.md` (AI-DLC format):

```markdown
# Technical Environment

## Technology Stack
[From Technical Decisions]

## Development Environment
- [Standard setup based on tech stack]

## Deployment Target
[From Infrastructure decision or inferred]

## Existing Systems
[From Constraints if any]

## Technical Constraints
[From Constraints section]
```

### Step 8: Auto-Execute AI-DLC Inception

```
## AI-DLC Spec Generation

The following documents have been created:
- docs/requirements.md (enhanced requirements)
- docs/vision.md (AI-DLC vision document)
- docs/tech-env.md (AI-DLC technical environment)

Now generating full AI-DLC specs...
```

**Auto-trigger AI-DLC by outputting**:

> Using AI-DLC, create the inception phase documents for this project.

This will generate:
- aidlc-docs/inception/requirements/
- aidlc-docs/inception/application-design/
- aidlc-docs/inception/plans/

Wait for AI-DLC to complete before proceeding to Stage 2.

---

## Stage 2: Skill Generation

### Step 9: Generate Project-Specific Dev Skill

Create `.claude/skills/dev-{project}/SKILL.md`:

- Use `docs/references/dev-skill-template.md` as template
- Customize for:
  - Project name (replace `{Project Name}` and `{project}`)
  - Tech stack specific commands (test, build, lint)
  - Language-specific best practices section
  - Project-specific file paths

### Step 10: Generate Common Skills from Templates

Copy skill templates from `docs/references/` to `.claude/skills/`:

| Template | Destination |
|----------|-------------|
| `docs/references/code-review-template.md` | `.claude/skills/code-review/SKILL.md` |
| `docs/references/tech-debt-template.md` | `.claude/skills/tech-debt/SKILL.md` |
| `docs/references/cross-check-template.md` | `.claude/skills/cross-check/SKILL.md` |

These skills are generic and work with any project that follows the AI-DLC structure.

### Step 11: Create CLAUDE.md

Generate project root `CLAUDE.md`:

```markdown
# {Project Name}

## Overview
[From requirements overview]

## Quick Commands

| Skill | Purpose |
|-------|---------|
| `/dev-{name}` | Main development driver |
| `/code-review git` | Review changed files |
| `/tech-debt` | View tech debt dashboard |
| `/cross-check` | Verify implementation vs requirements |

## Project Structure

```
[Generated structure based on tech stack]
```

## Development Workflow

1. Run `/dev-{name}` to get next task
2. Implement the task
3. Run `/code-review git` before committing
4. Track issues in `/tech-debt`

## Key Documents

- `docs/requirements.md` - Project requirements
- `docs/development-plan.md` - Development roadmap
- `docs/TECH-DEBT.md` - Technical debt tracker
```

---

## Step 12: Summary Report

```
## Project Initialization Complete

**Project**: {name}
**Date**: {date}

### Stage 0: Interactive Refinement ✅
- Refinement rounds: {N}
- Suggestions applied: {N} of {M}
- Requirements generated: docs/requirements.md

### Stage 1: AI-DLC Inputs ✅
- Vision document: docs/vision.md
- Tech environment: docs/tech-env.md

### Stage 2: Skills Generated ✅
- /dev-{name}: Main development skill
- /code-review: Code quality checks
- /tech-debt: Debt management
- /cross-check: Requirements compliance

### Files Created
- docs/requirements.md
- docs/refinement-log.md
- docs/vision.md
- docs/tech-env.md
- docs/development-plan.md (template)
- docs/TECH-DEBT.md (template)
- .claude/skills/dev-{name}/SKILL.md
- CLAUDE.md

### Next Steps

1. Review generated requirements in `docs/requirements.md`
2. Review AI-DLC specs in `aidlc-docs/`
3. Start development: `/dev-{name}`

Your project is ready for development!
```

---

## Error Handling

| Error | Recovery |
|-------|----------|
| No idea file found | Suggest running `/ideate` to capture idea first |
| Idea file empty/minimal | Start with more questions, build up |
| User doesn't respond | Re-prompt with options |
| AI-DLC rules missing | Provide setup instructions |

---

## Example Invocation

Default (auto-detects IDEA.md):
```
/init-project
```

Custom path:
```
/init-project /path/to/my-idea.md
```

If no idea file found:
```
No idea file found. Run /ideate first to capture your idea,
or create IDEA.md at the project root.
```
