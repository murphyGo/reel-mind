# Design Document: AI-DLC Starter

## Overview

AI-DLC Starter is a meta-template that transforms rough ideas into fully-specified, development-ready projects through Claude-powered interactive refinement and AWS AI-DLC methodology.

---

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      ENTRY POINT                                 │
│              /start → auto-detects state and routes              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PRE-INCEPTION: IDEA CAPTURE                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   /ideate   │───▶│  Dialogue   │───▶│     IDEA.md         │  │
│  │   skill     │    │   Loop      │    │    (created)        │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STAGE 0: INTERACTIVE REFINEMENT                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Analyze   │───▶│   Suggest   │───▶│  Dialogue Loop      │  │
│  │   Intent    │    │Improvements │    │  (until confirmed)  │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                  │               │
│                              ┌───────────────────┘               │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │ requirements.md │                          │
│                    │ refinement-log  │                          │
│                    └─────────────────┘                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STAGE 1: SPEC GENERATION                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │ vision.md   │    │ tech-env.md │    │    AI-DLC Rules     │  │
│  │ (AI-DLC)    │    │  (AI-DLC)   │    │    Execution        │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                  │               │
│                              ┌───────────────────┘               │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │   aidlc-docs/   │                          │
│                    │   (full specs)  │                          │
│                    └─────────────────┘                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STAGE 2: SKILL GENERATION                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │/dev-{name}  │    │/code-review │    │  /tech-debt         │  │
│  │  (custom)   │    │  (generic)  │    │  /cross-check       │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                                  │               │
│                              ┌───────────────────┘               │
│                              ▼                                   │
│                    ┌─────────────────┐                          │
│                    │   CLAUDE.md     │                          │
│                    │ (project ready) │                          │
│                    └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Interactive Refinement Engine

**Purpose**: Transform rough ideas into structured requirements through dialogue.

**Design Decisions**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Refinement approach | Iterative dialogue | Users often don't know what they need until they see suggestions |
| Suggestion format | Structured with categories | Makes it easy to accept/reject individual items |
| Confirmation model | Explicit "proceed" | Prevents premature advancement |

**Analysis Categories**:
- Completeness (missing features, edge cases)
- Clarity (ambiguous requirements)
- Feasibility (technical complexity)
- Architecture (component structure)
- Non-Functional (performance, security, scalability)

### 2. AI-DLC Integration

**Purpose**: Generate comprehensive specifications using proven methodology.

**Design Decisions**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Rule storage | Local copy in repo | Self-contained, version controlled |
| Input format | vision.md + tech-env.md | Standard AI-DLC format |
| Output location | aidlc-docs/ | Follows AI-DLC convention |

**AI-DLC Phases Used**:
- Inception: Requirements, user stories, application design
- Construction: Functional design, NFRs, build plans

### 3. Skill System

**Purpose**: Provide executable automation for development workflow.

**Design Decisions**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skill format | Markdown with structured sections | Human-readable, Claude-parseable |
| Skill location | .claude/skills/{name}/SKILL.md | Standard Claude Code convention |
| Common vs custom | Templates + generated | Reuse patterns, customize per project |

**Skill Categories**:

| Category | Skills | Customization |
|----------|--------|---------------|
| Entry | /start | None (template) |
| Ideation | /ideate | None (template) |
| Bootstrap | /init-project | None (template) |
| Development | /dev-{name} | Generated per project |
| Quality | /code-review | Template (language detection) |
| Tracking | /tech-debt, /cross-check | Template (path customization) |

---

## Data Flow

### Input Documents

```
IDEA.md (user creates via /ideate or manually)
    │
    ├── One-Liner
    ├── The Problem
    ├── Core Features
    ├── Tech Preferences (optional)
    └── Notes (optional)
```

### Generated Documents

```
docs/
├── requirements.md      ← Stage 0 output (enhanced requirements)
├── refinement-log.md    ← Stage 0 output (dialogue record)
├── vision.md            ← Stage 1 input (AI-DLC format)
├── tech-env.md          ← Stage 1 input (AI-DLC format)
├── development-plan.md  ← Stage 1 output (from AI-DLC)
└── TECH-DEBT.md         ← Initialized template

aidlc-docs/              ← Stage 1 output (AI-DLC generates)
├── inception/
│   ├── requirements/
│   ├── user-stories/
│   └── application-design/
└── construction/
    ├── functional-design/
    └── nfr-requirements/

.claude/skills/          ← Stage 2 output
├── dev-{name}/SKILL.md  ← Project-specific
├── code-review/SKILL.md ← Template
├── tech-debt/SKILL.md   ← Template
└── cross-check/SKILL.md ← Template
```

---

## Feedback Loop Design

### Continuous Improvement Mechanisms

```
┌─────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT CYCLE                        │
│                                                              │
│  /dev-{name}  ──────▶  Implementation  ──────▶  /code-review│
│       │                      │                       │       │
│       │                      ▼                       │       │
│       │              Session Log Created             │       │
│       │                      │                       │       │
│       ▼                      ▼                       ▼       │
│  ┌─────────┐         ┌─────────────┐         ┌──────────┐   │
│  │ Plan    │◀────────│ TECH-DEBT   │◀────────│ Issues   │   │
│  │ Update  │         │ Tracking    │         │ Found    │   │
│  └─────────┘         └─────────────┘         └──────────┘   │
│       │                      │                              │
│       │                      ▼                              │
│       │              Phase Complete?                        │
│       │                      │                              │
│       │                     YES                             │
│       │                      │                              │
│       │                      ▼                              │
│       │              /cross-check                           │
│       │                      │                              │
│       │                      ▼                              │
│       └──────────────  Gap Analysis  ───────────────────────│
│                              │                              │
│                              ▼                              │
│                    New Tasks Added                          │
└─────────────────────────────────────────────────────────────┘
```

### Traceability

| Artifact | Purpose | Created By |
|----------|---------|------------|
| Session logs | Record of each dev session | /dev-{name} |
| Refinement log | Dialogue during refinement | /init-project |
| Cross-check reports | Compliance verification | /cross-check |
| TECH-DEBT entries | Issue tracking | /code-review, manual |

---

## Design Principles

### 1. Human in the Loop

- No automatic commits without approval
- Interactive refinement requires explicit confirmation
- Suggestions presented, not imposed

### 2. Progressive Enhancement

- Start with rough idea
- Incrementally add structure
- Each stage builds on previous

### 3. Traceability

- Every decision logged
- Requirements linked to implementation
- Gaps tracked and actioned

### 4. Language Agnostic

- Skills detect language automatically
- Templates work for any tech stack
- AI-DLC rules are framework-independent

### 5. Self-Contained

- All rules included in repo
- No external dependencies beyond Claude
- Version controlled alongside code

---

## Extension Points

### Adding New Skills

1. Create `.claude/skills/{name}/SKILL.md`
2. Follow standard structure (Arguments, Objective, Steps)
3. Document in CLAUDE.md

### Customizing Refinement

Modify analysis categories in `/init-project`:
- Add domain-specific checks
- Adjust suggestion format
- Change dialogue patterns

### Integrating Additional AI-DLC Extensions

Add to `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/extensions/`:
- Security rules
- Testing rules
- Compliance rules

---

## Limitations

| Limitation | Mitigation |
|------------|------------|
| Skills are text-based, not executable | Claude interprets and executes |
| No IDE integration | Works in any terminal with Claude |

---

## Future Considerations

- [x] Automated AI-DLC execution integration (implemented)
- [x] Pre-inception idea capture (/ideate skill)
- [x] Unified entry point (/start skill)
- [ ] IDE-specific skill variants
- [ ] Multi-language skill templates
- [ ] Team collaboration patterns
- [ ] /scaffold skill for project structure generation
