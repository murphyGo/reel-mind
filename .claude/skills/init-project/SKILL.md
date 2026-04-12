# Init Project Skill

Bootstrap a new project from an idea to AI-DLC specs and dev skills.

## Arguments

- `$ARGUMENTS` - (optional):
  - (empty) - Full 3-stage initialization with path fallback: `IDEA.md` → `docs/PROJECT-VISION.md` → `docs/inception.md`
  - `quick` or `--quick` - Fast-track mode for prototypes/hackathons (skips user stories, workflow planning, app design, units, NFR analysis)
  - Path to custom idea file - Use the specified file as input

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
   - Resolve rule details directory: `.aidlc-rule-details/` → `.kiro/aws-aidlc-rule-details/` → `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/`
   - If missing, warn and provide setup instructions

3. **Check for existing session** (Session Continuity):
   - If `aidlc-docs/aidlc-state.md` exists, read it and determine current stage
   - Follow `common/session-continuity.md`: load previous stage artifacts automatically
   - Present resumption options to user instead of starting fresh
   - If no state file exists, proceed as new initialization

4. **MANDATORY: Load Common Rules** (per core-workflow.md):
   - Read `common/process-overview.md` — workflow overview
   - Read `common/session-continuity.md` — session resumption guidance
   - Read `common/content-validation.md` — content validation requirements
   - Read `common/question-format-guide.md` — question formatting rules
   - Reference these throughout the entire workflow execution

5. **MANDATORY: Load Extension Opt-in Files**:
   - Scan `extensions/` directory recursively under resolved rule details path
   - Load ONLY `*.opt-in.md` files (lightweight prompts, NOT full rule files)
   - Store loaded opt-in prompts for presentation during Step 9 (Requirements Bridge)
   - Full rule files are loaded on-demand only after user opts in

6. **Show welcome message**:
   - Read and display `common/welcome-message.md` from the resolved rule details directory
   - Display ONCE only — do NOT reload in subsequent interactions
   - After the AIDLC welcome, append:
   ```
   ### Additional: aidlc-starter Process
   1. Interactive Refinement - Enhance your requirements through dialogue
   2. AI-DLC Inception - Initialize state, bridge requirements, plan workflow
   3. Skill Generation - Create development automation skills

   Let's begin by understanding your idea...
   ```

---

## Quick Mode Branch

**Trigger**: `$ARGUMENTS` contains `quick` or `--quick`.

When quick mode is triggered, execute this streamlined path **instead of** Stage 0, Stage 1, and Stage 2 below. Step 0 (validation, common rules load) still runs first.

**Target audience**: Prototypes, hackathons, personal scripts, single-session experiments.

**What is skipped**: User stories, workflow planning, application design, units generation, extension opt-in, NFR analysis, audit log, refinement-questions file, DESIGN.md, TECH-DEBT.md, code-review/tech-debt/cross-check skills.

**What is kept**: Idea analysis, lightweight requirements, minimal AI-DLC state, dev skill, CLAUDE.md, README.md.

### Quick Step 1: Read and Analyze Idea

Same as full-mode Step 1 — read IDEA.md, extract project name, vision, core features, tech preferences, constraints.

### Quick Step 2: Rapid Refinement (1 round max)

Present a condensed analysis:

```
## Quick Analysis

I've read your idea. Here's what I see:

**Core concept**: [1-2 sentence summary]

**Quick questions** (answer any, or say "skip"):
1. [Most critical missing piece — usually target user or core constraint]
2. [Second most critical — usually tech preference if not specified]

Or say **"go"** to proceed with what we have.
```

| Response | Action |
|----------|--------|
| Answers questions | Incorporate, proceed to Quick Step 3 |
| "skip" / "go" | Proceed with reasonable defaults to Quick Step 3 |

**No second round.** Accept whatever the user gives. Fill gaps with smart defaults (apply the Tech Stack Recommendation logic from Step 3 if tech unspecified).

### Quick Step 3: Generate Lightweight Requirements

Create `docs/requirements.md` with simplified structure:

```markdown
# Project Requirements: {Project Name}

*Generated via quick mode on {YYYY-MM-DD}*

## Overview

[Problem + target users in 2-3 sentences]

## Features

| # | Feature | Priority | Notes |
|---|---------|----------|-------|
| 1 | [feature] | Must-have | [brief] |
| 2 | [feature] | Must-have | [brief] |
| 3 | [feature] | Should-have | [brief] |

## Technical Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | [choice or smart default] | [why] |
| Framework | [choice or smart default] | [why] |
| Database | [choice or "TBD"] | [why] |

## Constraints

- [Any mentioned constraints, or "None specified"]

## Out of Scope

- [Anything explicitly deferred]
```

### Quick Step 4: Generate Minimal AI-DLC State

Create `aidlc-docs/aidlc-state.md` with simplified tracking:

```markdown
# AI-DLC State (Quick Mode)

## Project Information
- **Project Name**: {name}
- **Project Type**: Greenfield (Quick)
- **Start Date**: {YYYY-MM-DD}
- **Mode**: Quick — simplified inception, direct to construction

## Stage Progress

| Stage | Status |
|-------|--------|
| Requirements | ✅ Complete (quick) |
| Code Generation | ⏳ Pending |
| Build and Test | ⏳ Pending |

## Notes

- Generated via `/init-project --quick`
- To upgrade to full AI-DLC (user stories, app design, units), run `/init-project` — existing requirements.md will be preserved and enhanced.
```

Do not create audit.md, refinement-questions.md, refinement-log.md, vision.md, tech-env.md, or any `aidlc-docs/inception/` subdirectories.

### Quick Step 5: Generate Dev Skill

Same as full-mode Step 14 — create `.claude/skills/dev-{project}/SKILL.md` from `docs/references/dev-skill-template.md`. Customize project name and tech stack commands.

The dev skill reads `aidlc-state.md` and handles missing units by treating the whole project as a single implicit unit.

### Quick Step 6: Generate Essential Files

Create only:
- `CLAUDE.md` — shortened version (Quick Commands table + Key Files table + Tech Stack)
- `README.md` — same as full-mode Step 16.3

**Skip**: DESIGN.md, TECH-DEBT.md, code-review skill, tech-debt skill, cross-check skill.

### Quick Step 7: Summary

```
## Quick Initialization Complete

**Project**: {name}
**Mode**: Quick (prototype/hackathon)

### Created
- docs/requirements.md (lightweight)
- aidlc-docs/aidlc-state.md (minimal tracking)
- .claude/skills/dev-{name}/SKILL.md
- CLAUDE.md
- README.md

### Skipped (available via full `/init-project`)
- Detailed NFR analysis
- User stories
- Application design artifacts
- Code review / tech-debt / cross-check skills
- Extension opt-in (security, testing)

### Next Steps
1. Run `/dev-{name}` to start building
2. Run `/scaffold` to generate directory structure and config files
3. Run `/init-project` later to upgrade to full AI-DLC (requirements.md will be preserved)

Your project is ready — go build!
```

**End of Quick Mode Branch.** Do NOT proceed to Stage 0.

---

## Stage 0: Interactive Requirements Refinement

### AIDLC Compliance Notes for Stage 0

Stage 0 uses a conversational dialogue style (proceed/skip/discuss) rather than AIDLC's strict question-file format. This is intentional — the interactive refinement is a pre-AIDLC step designed for rapid idea exploration. However, to maintain traceability:

1. **Record dialogue in AIDLC-compatible format**: After each dialogue round, save key questions and answers to `docs/refinement-questions.md` using `[Answer]:` tags for auditability
2. **Apply adaptive depth** (per `common/depth-levels.md`):
   - Assess idea complexity before starting refinement
   - **Minimal**: Simple, clear idea with obvious tech choices → fewer rounds, focus on gaps only
   - **Standard**: Normal complexity → full analysis with 3-5 categories
   - **Comprehensive**: Complex multi-service system → deep analysis across all categories, more rounds
3. **Mandatory ambiguity analysis**: After each user response, analyze for vague language ("depends", "maybe", "not sure"). If found, create targeted follow-up questions before proceeding.

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

### Tech Stack Recommendation

If `docs/requirements.md` Section 4 (Technical Decisions) is empty, marked "TBD", or IDEA.md had no tech preferences, generate a recommendation based on functional requirements.

**Analysis inputs**:
- Project type (API, web app, CLI, library, etc.) from FR analysis
- Scale indicators (single user, team, enterprise) from NFR analysis
- Data complexity (simple CRUD, relationships, time-series, etc.)
- Real-time requirements (WebSocket, streaming, polling)
- Team/user preference signals from IDEA.md

**Present as**:

```
### Tech Stack Suggestion

Based on your requirements:
- [Signal 1 from requirements]
- [Signal 2 from requirements]

| Component | Recommendation | Alternative | Trade-off |
|-----------|---------------|-------------|-----------|
| Language | [choice] | [alt] | [brief comparison] |
| Framework | [choice] | [alt] | [brief comparison] |
| Database | [choice] | [alt] | [brief comparison] |
| Infrastructure | [choice] | [alt] | [brief comparison] |

Options:
- **accept** — Use these recommendations
- **discuss [component]** — Explore alternatives for a specific choice
- **specify** — Provide your own tech stack
```

If tech decisions are already present in requirements.md and reasonable, skip this block and reference the existing choices.

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

**AIDLC-Compatible Format**: Generate `docs/requirements.md` as the **single source of truth** for requirements. This file uses AIDLC-compatible structure so that Step 9's bridging becomes a lightweight reference rather than a full duplicate.

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

### Step 6: Create Refinement Log and Question Record

**6.1** Save the dialogue to `docs/refinement-log.md`:

```markdown
# Refinement Log: {Project Name}

**Date**: {date}
**Depth Level**: [Minimal/Standard/Comprehensive]
**Initial idea**: [summary of original content from IDEA.md or equivalent]

## Refinement Dialogue

### Round 1
**Claude's Analysis**: [summary]
**User's Response**: [response]
**Ambiguity Check**: [Any vague language detected? Follow-up needed?]
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

**6.2** Save key questions and answers to `docs/refinement-questions.md` (AIDLC-compatible format for traceability):

```markdown
# Refinement Questions: {Project Name}

**Date**: {date}

## Architecture & Tech Stack
Q1: [Question asked during refinement]
[Answer]: [User's response]

## Scope & Features
Q2: [Question]
[Answer]: [Response]

## Non-Functional Requirements
Q3: [Question]
[Answer]: [Response]

## Ambiguity Resolutions
[If any follow-up questions were asked due to vague responses, document them here]
```

---

## Stage 1: AI-DLC Inception

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

### Step 8: Initialize AI-DLC State (Workspace Detection)

**Reference**: `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/inception/workspace-detection.md`

Key adaptations for init-project:
- Project is always greenfield (created from template)
- No reverse engineering needed
- Auto-proceed (no user approval required)

1. Create `aidlc-docs/aidlc-state.md`:

```markdown
# AI-DLC State

## Project Information
- **Project Name**: {Project Name}
- **Project Type**: Greenfield
- **Start Date**: {ISO 8601 timestamp}
- **Workspace Root**: {absolute path}

## Code Location Rules
- Application code: Workspace root (NEVER in aidlc-docs/)
- Documentation: aidlc-docs/ only

## Stage Progress

### INCEPTION PHASE
| Stage | Status | Date |
|-------|--------|------|
| Workspace Detection | ✅ Complete | {date} |
| Reverse Engineering | ⏭️ Skipped (Greenfield) | {date} |
| Requirements Analysis | ✅ Complete (via interactive refinement) | {date} |
| User Stories | ⏳ Pending | |
| Workflow Planning | ⏳ Pending | |
| Application Design | ⏳ Pending | |
| Units Generation | ⏳ Pending | |

### CONSTRUCTION PHASE
| Stage | Status | Date |
|-------|--------|------|
| Determined by Workflow Planning | ⏳ Pending | |

## Extension Configuration
| Extension | Enabled | Opted In |
|-----------|---------|----------|
| (none configured) | | |
```

2. Create `aidlc-docs/audit.md` with initial entry:

```markdown
# AI-DLC Audit Log

## Project Initialization
**Timestamp**: {ISO 8601}
**User Input**: "{original idea from IDEA.md — first line or summary}"
**AI Response**: "Project initialized via /init-project. Interactive refinement completed."
**Context**: Stage 1 — AI-DLC State Initialization

---
```

3. Present brief status:
```
AI-DLC state initialized.
- Project type: Greenfield
- State file: aidlc-docs/aidlc-state.md
- Audit log: aidlc-docs/audit.md

Proceeding to bridge requirements...
```

### Step 9: Bridge Requirements to AI-DLC Format + Extension Opt-in

**Reference**: `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/inception/requirements-analysis.md` (output format only)

Key adaptations for init-project:
- Skip verification questions (Stage 0's interactive dialogue already handled clarification)
- `docs/requirements.md` is the **single source of truth** — the AIDLC bridge creates a lightweight reference, NOT a full duplicate
- Add intent analysis summary
- Present extension opt-in prompts (per core-workflow.md Extensions Loading)

1. Read `docs/requirements.md` and `docs/refinement-log.md`

2. Perform intent analysis:
   - Request clarity (Clear / Mostly Clear / Vague)
   - Request type (New Project)
   - Scope estimate (Small / Medium / Large)
   - Complexity estimate (Low / Medium / High)

3. **MANDATORY: Extension Opt-in** (per core-workflow.md):
   - Present opt-in prompts from all loaded `*.opt-in.md` files (e.g., security-baseline, property-based-testing)
   - For each extension, ask user whether to enable it
   - If user opts IN: load the corresponding full rule file (e.g., `security-baseline.opt-in.md` → `security-baseline.md`)
   - If user opts OUT: do NOT load full rules (saves context)
   - Record decisions in `aidlc-docs/aidlc-state.md` under `## Extension Configuration`

4. Create `aidlc-docs/inception/requirements/requirements.md` as a **reference document**:
   ```markdown
   # Requirements Reference

   ## Intent Analysis
   - Request Clarity: [Clear/Mostly Clear/Vague]
   - Request Type: New Project
   - Scope: [Small/Medium/Large]
   - Complexity: [Low/Medium/High]

   ## Source
   Primary requirements document: `docs/requirements.md`
   Refinement questions: `docs/refinement-questions.md`
   Refinement log: `docs/refinement-log.md`

   ## Extension Configuration
   [List enabled extensions and their impact on requirements]

   ## Traceability Summary
   - Functional Requirements: FR-001 through FR-{N}
   - Non-Functional Requirements: NFR-001 through NFR-{N}
   - All requirement IDs are defined in docs/requirements.md
   ```

5. Update `aidlc-docs/aidlc-state.md`: confirm Requirements Analysis complete, update Extension Configuration

6. **MANDATORY: Log in `aidlc-docs/audit.md`** — append (NEVER overwrite) with ISO 8601 timestamp, complete raw user input for approval, and extension opt-in decisions

7. Present summary:
```
## Requirements Bridged to AI-DLC Format

Source: docs/requirements.md (single source of truth)
Reference: aidlc-docs/inception/requirements/requirements.md

Intent Analysis:
- Request Type: New Project
- Scope: [estimated]
- Complexity: [estimated]

Extensions:
- [Extension Name]: [Enabled/Disabled]

Options:
- **approve**: Continue to next stage
- **changes**: Request modifications
```

**Wait for user approval before proceeding.**

### Step 10: User Stories (CONDITIONAL)

**Reference**: `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/inception/user-stories.md`

1. Perform intelligent assessment using criteria from the rule file:

   **Execute IF** (any of):
   - New user-facing features or functionality
   - Multiple user types or personas involved
   - Complex business requirements with acceptance criteria needs
   - Customer-facing API or service

   **Skip IF** (all of):
   - Pure utility/infrastructure project
   - Simple single-user tool
   - No complex user workflows

2. Present assessment:
```
## User Stories Assessment

- User Impact: [Direct/Indirect/None]
- Complexity: [Simple/Medium/Complex]
- Recommendation: [Execute/Skip]
- Reasoning: [brief justification]

Options:
- **generate**: Proceed with user story creation
- **skip**: Move directly to Workflow Planning
```

3. **If user chooses "generate"**:
   - Follow `inception/user-stories.md` fully:
     - Part 1: Create story generation plan with questions → get user answers → analyze for ambiguities → get plan approval
     - Part 2: Execute approved plan → generate stories and personas → get approval
   - Outputs:
     - `aidlc-docs/inception/plans/story-generation-plan.md`
     - `aidlc-docs/inception/user-stories/stories.md`
     - `aidlc-docs/inception/user-stories/personas.md`

4. **If user chooses "skip"**:
   - Log skip decision in `aidlc-docs/audit.md`
   - Update `aidlc-docs/aidlc-state.md`: User Stories = ⏭️ Skipped

### Step 11: Workflow Planning (ALWAYS)

**Reference**: `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/inception/workflow-planning.md`

**This is the critical stage** — it determines what Construction phases the generated dev skill will need.

1. Load all prior context:
   - `aidlc-docs/inception/requirements/requirements.md`
   - `aidlc-docs/inception/user-stories/stories.md` (if generated)
   - `docs/requirements.md` (technical decisions)

2. Follow `inception/workflow-planning.md`:
   - Analyze scope, impact, risk, and component relationships
   - Determine which remaining inception stages to execute:
     - **Application Design**: EXECUTE if new components/services needed
     - **Units Generation**: EXECUTE if multiple units, complex decomposition needed
   - Determine which Construction stages the project needs:
     - Functional Design (per-unit): EXECUTE if complex business logic
     - NFR Requirements: EXECUTE if performance/security/scalability concerns
     - NFR Design: EXECUTE if NFR Requirements executed
     - Infrastructure Design: EXECUTE if infrastructure mapping needed
     - Code Generation: ALWAYS
     - Build and Test: ALWAYS
   - Generate workflow visualization (Mermaid diagram)
   - **MANDATORY: Content Validation** (per `common/content-validation.md`): Validate Mermaid diagram syntax before writing. Use only basic ASCII for any text diagrams (`+` `-` `|` `^` `v` `<` `>`). Escape special characters.
   - **Extension compliance**: If extensions are enabled, check applicable extension rules and include compliance status in the execution plan

3. Create `aidlc-docs/inception/plans/execution-plan.md`

4. Update `aidlc-docs/aidlc-state.md` with execution decisions

5. Present plan to user:
```
## Workflow Planning Complete

Based on project analysis:

### Remaining Inception Stages
| Stage | Decision | Reasoning |
|-------|----------|-----------|
| Application Design | [EXECUTE/SKIP] | [reasoning] |
| Units Generation | [EXECUTE/SKIP] | [reasoning] |

### Construction Phase Plan
| Stage | Decision | Reasoning |
|-------|----------|-----------|
| Functional Design | [EXECUTE/SKIP] | [reasoning] |
| NFR Requirements | [EXECUTE/SKIP] | [reasoning] |
| NFR Design | [EXECUTE/SKIP] | [reasoning] |
| Infrastructure Design | [EXECUTE/SKIP] | [reasoning] |
| Code Generation | EXECUTE | Always required |
| Build and Test | EXECUTE | Always required |

Execution plan: aidlc-docs/inception/plans/execution-plan.md

Options:
- **approve**: Accept plan and continue
- **changes**: Modify stage decisions
- **add [stage]**: Include a skipped stage
```

**Wait for explicit user approval before proceeding.**

### Step 12: Application Design (CONDITIONAL)

**Reference**: `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/inception/application-design.md`

**Execute only if** Step 11's execution-plan.md recommends EXECUTE for Application Design.

If SKIP:
- Log in `aidlc-docs/audit.md`
- Update `aidlc-docs/aidlc-state.md`: Application Design = ⏭️ Skipped
- Proceed to Step 13

If EXECUTE:
1. Follow `inception/application-design.md` fully:
   - Ask design questions (components, methods, services, dependencies)
   - Analyze answers for ambiguities
   - Get plan approval
   - Generate design artifacts
   - Get artifact approval

2. Outputs:
   - `aidlc-docs/inception/application-design/components.md`
   - `aidlc-docs/inception/application-design/component-methods.md`
   - `aidlc-docs/inception/application-design/services.md`
   - `aidlc-docs/inception/application-design/component-dependency.md`
   - `aidlc-docs/inception/application-design/application-design.md`

3. Update `aidlc-docs/aidlc-state.md`: Application Design = ✅ Complete

### Step 13: Units Generation (CONDITIONAL)

**Reference**: `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/inception/units-generation.md`

**Execute only if** Step 11's execution-plan.md recommends EXECUTE for Units Generation.
**Prerequisite**: Application Design (Step 12) must have been executed.

If SKIP:
- Log in `aidlc-docs/audit.md`
- Update `aidlc-docs/aidlc-state.md`: Units Generation = ⏭️ Skipped
- Mark INCEPTION phase complete
- Proceed to Stage 2

If EXECUTE:
1. Follow `inception/units-generation.md` fully:
   - Part 1: Create unit decomposition plan with questions → get answers → analyze ambiguities → get plan approval
   - Part 2: Execute approved plan → generate unit artifacts → get approval

2. Outputs:
   - `aidlc-docs/inception/application-design/unit-of-work.md`
   - `aidlc-docs/inception/application-design/unit-of-work-dependency.md`
   - `aidlc-docs/inception/application-design/unit-of-work-story-map.md`

3. Update `aidlc-docs/aidlc-state.md`: Units Generation = ✅ Complete
4. Mark INCEPTION phase complete in `aidlc-docs/aidlc-state.md`

---

## Stage 2: Skill Generation

### Step 14: Generate Project-Specific Dev Skill

Create `.claude/skills/dev-{project}/SKILL.md`:

- Use `docs/references/dev-skill-template.md` as template
- Customize for:
  - Project name (replace `{Project Name}` and `{project}`)
  - Tech stack specific commands (test, build, lint)
  - Language-specific best practices section
  - Project-specific file paths

### Step 15: Generate Common Skills from Templates

#### 15.1 Generate Customized Code Review Skill

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

6. **Copy protocol files**:
   - Copy `docs/references/code-review-protocols/` directory to `.claude/skills/code-review/protocols/`
   - Protocol files are language-agnostic deep-analysis frameworks — no customization needed
   - Files: `INDEX.md`, `concurrency.md`, `data-integrity.md`, `error-contract.md`, `memory.md`, `performance.md`, `resource-lifecycle.md`, `security-boundary.md`

#### 15.2 Copy Other Skills

Copy remaining templates (no customization needed):

| Template | Destination |
|----------|-------------|
| `docs/references/tech-debt-template.md` | `.claude/skills/tech-debt/SKILL.md` |
| `docs/references/cross-check-template.md` | `.claude/skills/cross-check/SKILL.md` |

### Step 16: Create CLAUDE.md

Generate project root `CLAUDE.md`:

```markdown
# {Project Name}

## Overview
{Brief description from requirements}

---

## Important: Before Development

Run `/dev-{name}` to:
1. See current construction stage and unit progress
2. Get the next task to work on (from AIDLC per-stage plan files)
3. Follow the AIDLC Construction workflow

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
| `aidlc-docs/aidlc-state.md` | **Start here** - AIDLC state and construction progress |
| `docs/requirements.md` | Project requirements and acceptance criteria |
| `docs/DESIGN.md` | Architecture decisions and rationale |
| `docs/TECH-DEBT.md` | Technical debt registry |
| `aidlc-docs/` | AI-DLC generated specifications |

---

## Development Workflow

```
1. /dev-{name}          → Get next task from AIDLC construction stage
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

### Step 16.1: Create DESIGN.md

**Document Relationship**: `docs/DESIGN.md` is a developer-facing summary derived from AI-DLC application design artifacts. The source of truth for detailed design is `aidlc-docs/inception/application-design/`.

**Enhanced with AI-DLC outputs**:
- If `aidlc-docs/inception/application-design/application-design.md` exists, use it as the primary source for architecture, components, and dependencies
- If `aidlc-docs/inception/application-design/component-dependency.md` exists, use it for component relationship diagrams
- **MANDATORY: Content Validation** — validate any ASCII diagrams per `common/content-validation.md` (basic ASCII only, no Unicode box-drawing)

Generate `docs/DESIGN.md`:

```markdown
# Design Document: {Project Name}

*Generated on {date}*
*Source: aidlc-docs/inception/application-design/ (see AI-DLC artifacts for detailed design)*

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

### Step 16.2: Create TECH-DEBT.md

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

### Step 16.3: Create README.md

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
| `aidlc-docs/aidlc-state.md` | AIDLC state and progress |
| `docs/requirements.md` | Detailed requirements |
| `docs/DESIGN.md` | Architecture decisions |

## License

{License - default to MIT or ask user}
```

---

## Step 17: Summary Report

```
## Project Initialization Complete

**Project**: {name}
**Date**: {date}

### Stage 0: Interactive Refinement ✅
- Refinement rounds: {N}
- Suggestions applied: {N} of {M}
- Requirements generated: docs/requirements.md

### Stage 1: AI-DLC Inception ✅
- State initialized: aidlc-docs/aidlc-state.md
- Requirements bridged: aidlc-docs/inception/requirements/requirements.md
- User Stories: [Generated/Skipped]
- Workflow Planning: aidlc-docs/inception/plans/execution-plan.md
- Application Design: [Generated/Skipped]
- Units Generation: [Generated/Skipped]
- Vision document: docs/vision.md
- Tech environment: docs/tech-env.md

### Stage 2: Project Setup ✅
- Skills generated: /dev-{name}, /code-review, /tech-debt, /cross-check
- Documentation: CLAUDE.md, README.md, DESIGN.md
- Development tracking: TECH-DEBT.md

### Files Created
- README.md (project readme)
- CLAUDE.md (Claude context)
- docs/requirements.md
- docs/refinement-log.md
- docs/vision.md
- docs/tech-env.md
- docs/DESIGN.md
- docs/TECH-DEBT.md
- .claude/skills/dev-{name}/SKILL.md
- .claude/skills/code-review/SKILL.md
- .claude/skills/tech-debt/SKILL.md
- .claude/skills/cross-check/SKILL.md
- aidlc-docs/aidlc-state.md
- aidlc-docs/audit.md
- aidlc-docs/inception/requirements/requirements.md
- aidlc-docs/inception/plans/execution-plan.md
- aidlc-docs/inception/user-stories/ (if generated)
- aidlc-docs/inception/application-design/ (if generated)

### Next Steps

1. Review `aidlc-docs/aidlc-state.md` for construction stage overview
2. Run `/dev-{name}` to start development
3. Use `/code-review git` before committing

Your project is ready for development!
```

---

## Step 18: Cleanup Starter Files

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
| Session interrupted mid-stage | Resume from aidlc-state.md (Step 0.3) |
| Extension rule non-compliance | Block stage completion until resolved (per core-workflow.md) |

---

## AIDLC Compliance Rules (applied throughout all steps)

### Audit Logging (MANDATORY)
- **ALWAYS append** to `aidlc-docs/audit.md` — NEVER overwrite entire contents
- Log EVERY user input with **complete raw text** (never summarize)
- Log EVERY approval prompt before asking the user
- Log EVERY user response after receiving it
- Use ISO 8601 format for timestamps
- Include stage context for each entry
- Format:
  ```markdown
  ## [Stage Name]
  **Timestamp**: [ISO 8601]
  **User Input**: "[Complete raw input]"
  **AI Response**: "[Response or action taken]"
  **Context**: [Stage, action, decision]
  ---
  ```

### Content Validation (MANDATORY before file creation)
- Validate Mermaid diagram syntax
- Validate ASCII diagrams: basic ASCII only (`+` `-` `|` `^` `v` `<` `>`), NO Unicode box-drawing
- ALL lines in a box must have EXACTLY the same character count
- Escape special characters properly
- Reference: `common/content-validation.md`

### Extension Enforcement (if any extensions enabled)
- Before completing ANY stage, check enabled extensions in `aidlc-docs/aidlc-state.md`
- Evaluate which extension rules apply to the current stage
- Non-compliance with applicable rules = **blocking finding** — do NOT present stage completion
- Include extension compliance summary in stage completion messages
- Reference: `core-workflow.md` Extensions Loading section

### Document Hierarchy (avoid duplication)
- `docs/requirements.md` = **single source of truth** for requirements
- `aidlc-docs/inception/requirements/requirements.md` = reference/pointer + intent analysis only
- `docs/DESIGN.md` = developer summary derived from `aidlc-docs/inception/application-design/`
- `aidlc-docs/inception/plans/execution-plan.md` = construction stage strategy (which stages apply per unit)
- `aidlc-docs/construction/plans/` = per-stage plan files with task checkboxes (created just-in-time during construction)

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

Resume interrupted session:
```
/init-project
# Automatically detects aidlc-state.md and resumes from last completed stage
```

If no idea file found:
```
No idea file found. Run /ideate first to capture your idea,
or create IDEA.md at the project root.
```
