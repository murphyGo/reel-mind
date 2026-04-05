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

#### 10.1 Generate Customized Code Review Skill

Create `.claude/skills/code-review/SKILL.md` from `docs/references/code-review-template.md`:

1. **Read project's Technical Decisions** from `docs/requirements.md`
2. **Customize template** by replacing placeholders:

| Placeholder | Replace With |
|-------------|--------------|
| `{Project Name}` | Project name |
| `{PRIMARY_LANGUAGE}` | Python / TypeScript / Go / etc. |
| `{FRAMEWORK}` | FastAPI / React / Gin / etc. |
| `{LINT_COMMAND}` | `ruff check .` / `npm run lint` / `golangci-lint run` |
| `{TEST_COMMAND}` | `pytest` / `npm test` / `go test ./...` |
| `{TYPE_CHECK_COMMAND}` | `mypy src/` / `tsc --noEmit` / `N/A` |

3. **Include only relevant sections**:
   - Remove language checks for unused languages
   - Keep only the framework section matching project (e.g., FastAPI for Python+FastAPI)
   - Keep only the style guide for project's language

4. **Framework selection guide**:

| Tech Stack | Include Framework Section |
|------------|--------------------------|
| Python + FastAPI | FastAPI |
| Python + Django | Django |
| Python + Flask | Flask |
| Node.js + Express | Express |
| Node.js + NestJS | NestJS |
| TypeScript + React | React |
| TypeScript + Vue | Vue |
| Go + Gin | Gin |
| Go + Echo | Echo |
| Java + Spring | Spring Boot |
| Rust + Actix | Actix |

5. **Add project-specific patterns** based on `docs/DESIGN.md`:
   - Component naming conventions
   - File organization rules
   - Project-specific anti-patterns to avoid

#### 10.2 Copy Other Skills

Copy remaining templates (no customization needed):

| Template | Destination |
|----------|-------------|
| `docs/references/tech-debt-template.md` | `.claude/skills/tech-debt/SKILL.md` |
| `docs/references/cross-check-template.md` | `.claude/skills/cross-check/SKILL.md` |

### Step 11: Create CLAUDE.md

Generate project root `CLAUDE.md`:

```markdown
# {Project Name}

## Overview
{Brief description from requirements}

---

## Important: Before Development

**Always check `docs/development-plan.md` before starting any work.**

Run `/dev-{name}` to:
1. See current development status
2. Get the next task to work on
3. Follow the established development workflow

---

## Quick Commands

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/dev-{name}` | Main development driver | Start here for any development work |
| `/code-review git` | Review code changes | Before committing |
| `/tech-debt` | Manage technical debt | Track and prioritize issues |
| `/cross-check` | Verify requirements | After completing a phase |

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `docs/development-plan.md` | **Start here** - Development roadmap and task tracking |
| `docs/requirements.md` | Project requirements and acceptance criteria |
| `docs/DESIGN.md` | Architecture decisions and rationale |
| `docs/TECH-DEBT.md` | Technical debt registry |
| `aidlc-docs/` | AI-DLC generated specifications |

---

## Development Workflow

```
1. /dev-{name}          → Get next task from development-plan.md
2. Implement            → Write code following requirements
3. /code-review git     → Review before committing
4. Commit               → Save your work
5. /dev-{name}          → Mark complete, get next task
```

---

## Project Structure

```
{Generated structure based on tech stack}
```

---

## Tech Stack

{From technical decisions - language, framework, database, etc.}
```

### Step 11.1: Create DESIGN.md

Generate `docs/DESIGN.md`:

```markdown
# Design Document: {Project Name}

*Generated on {date}*

## Overview

{Brief description of the system architecture based on requirements}

## Architecture

### High-Level Design

```
{ASCII diagram showing main components and their relationships}
```

### Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| {component} | {what it does} | {tech choice} |

## Technical Decisions

### TD-001: {Decision Topic}

**Choice**: {What was chosen}
**Rationale**: {Why this choice was made}
**Alternatives Considered**: {What else was evaluated}

## Data Model

{Entity descriptions and relationships based on requirements}

## API Design (if applicable)

{Endpoint patterns, authentication approach, etc.}

## Non-Functional Considerations

### Performance
{How performance requirements will be met}

### Security
{Security measures and approach}

### Scalability
{Scaling strategy}

---

*Update this document as architectural decisions evolve during development.*
```

### Step 11.2: Create development-plan.md

Generate `docs/development-plan.md`:

```markdown
# Development Plan: {Project Name}

*Generated on {date}*

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| {component from DESIGN} | ❌ Not Started | |

---

## Phase 1: Foundation

### 1.1 - {First task based on requirements}
- [ ] {Implementation item}
- [ ] {Implementation item}
- [ ] Add unit tests

### 1.2 - {Second task}
- [ ] {Implementation item}
- [ ] {Implementation item}
- [ ] Add unit tests

---

## Phase 2: Core Features

### 2.1 - {Feature from FR requirements}
- [ ] {Implementation item}
- [ ] {Implementation item}
- [ ] Add integration tests

### 2.2 - {Another feature}
- [ ] {Implementation item}
- [ ] {Implementation item}

---

## Phase 3: Polish & Integration

### 3.1 - Error Handling & Edge Cases
- [ ] Implement error handling patterns
- [ ] Handle edge cases
- [ ] Add error recovery tests

### 3.2 - Documentation & Cleanup
- [ ] Update API documentation
- [ ] Code cleanup and refactoring
- [ ] Final testing

---

## Progress Tracking

| Phase | Tasks | Complete | Progress |
|-------|-------|----------|----------|
| Phase 1 | X | 0 | 0% |
| Phase 2 | Y | 0 | 0% |
| Phase 3 | Z | 0 | 0% |

---

*This plan is updated automatically by `/dev-{name}` as tasks are completed.*
```

### Step 11.3: Create TECH-DEBT.md

Generate `docs/TECH-DEBT.md`:

```markdown
# Technical Debt Registry

## Summary

| Priority | Count | Oldest |
|----------|-------|--------|
| Critical | 0 | - |
| High | 0 | - |
| Medium | 0 | - |
| Low | 0 | - |

---

## Active Items

### Critical Priority

_No critical items._

### High Priority

_No high priority items._

### Medium Priority

_No medium priority items._

### Low Priority

_No low priority items._

---

## Resolved Items

_No resolved items yet._

---

*Managed by `/tech-debt` skill. Run `/tech-debt add` to add new items.*
```

### Step 11.4: Create README.md

Generate project `README.md` (replace aidlc-starter README):

```markdown
# {Project Name}

{One-liner from IDEA.md}

## Overview

{Problem statement from requirements}

## Features

- {Feature 1 from requirements}
- {Feature 2 from requirements}
- {Feature 3 from requirements}

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | {choice} |
| Framework | {choice} |
| Database | {choice} |

## Getting Started

### Prerequisites

- {Based on tech stack}

### Installation

```bash
# Clone the repository
git clone {repo-url}
cd {project-name}

# Install dependencies
{install command based on tech stack}

# Run the application
{run command based on tech stack}
```

## Development

This project uses AI-DLC methodology with Claude Code skills.

### Quick Start

```bash
claude
/dev-{name}
```

### Development Workflow

1. Run `/dev-{name}` to get the next development task
2. Implement following `docs/requirements.md`
3. Run `/code-review git` before committing
4. Track technical debt with `/tech-debt`

### Key Documents

| Document | Description |
|----------|-------------|
| `docs/development-plan.md` | Development roadmap |
| `docs/requirements.md` | Detailed requirements |
| `docs/DESIGN.md` | Architecture decisions |

## License

{License - default to MIT or ask user}
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

### Stage 1: AI-DLC Specs ✅
- Vision document: docs/vision.md
- Tech environment: docs/tech-env.md
- AI-DLC docs: aidlc-docs/

### Stage 2: Project Setup ✅
- Skills generated: /dev-{name}, /code-review, /tech-debt, /cross-check
- Documentation: CLAUDE.md, README.md, DESIGN.md
- Development tracking: development-plan.md, TECH-DEBT.md

### Files Created
- README.md (project readme)
- CLAUDE.md (Claude context)
- docs/requirements.md
- docs/refinement-log.md
- docs/vision.md
- docs/tech-env.md
- docs/DESIGN.md
- docs/development-plan.md
- docs/TECH-DEBT.md
- .claude/skills/dev-{name}/SKILL.md
- .claude/skills/code-review/SKILL.md
- .claude/skills/tech-debt/SKILL.md
- .claude/skills/cross-check/SKILL.md
- aidlc-docs/ (AI-DLC generated)

### Next Steps

1. Review `docs/development-plan.md` for task overview
2. Run `/dev-{name}` to start development
3. Use `/code-review git` before committing

Your project is ready for development!
```

---

## Step 13: Cleanup Starter Files

After project initialization, remove aidlc-starter specific files:

### 13.1 Remove Starter Documentation

Delete files that describe aidlc-starter (not user's project):

```
Removing aidlc-starter specific files...
- docs/PROJECT-VISION.md (aidlc-starter meta-documentation)
- docs/REVIEW.md (aidlc-starter analysis)
```

### 13.2 Remove Template References (Optional)

Ask user about template files:

```
The skill templates in docs/references/ have been copied to .claude/skills/.

Keep templates for reference? (yes/no)
- yes: Keep docs/references/ for future reference
- no: Remove docs/references/
```

### 13.3 Remove Bootstrap Skills

Remove skills that are only needed during initialization:

```
Removing bootstrap skills (no longer needed)...
- .claude/skills/start/
- .claude/skills/ideate/
- .claude/skills/init-project/
```

### 13.4 Present Cleanup Summary

```
## Cleanup Complete

### Removed (aidlc-starter specific):
- docs/PROJECT-VISION.md
- docs/REVIEW.md
- .claude/skills/start/
- .claude/skills/ideate/
- .claude/skills/init-project/
- docs/references/ (if user chose to remove)

### Kept:
- IDEA.md (your original idea)
- aidlc-workflows/ (needed for AI-DLC operations)

Your project is now clean and ready for development!

Run `/dev-{name}` to begin.
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
