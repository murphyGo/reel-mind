# AI-DLC Starter

Transform ideas into fully-specified, development-ready projects using AI-DLC methodology and Claude-powered automation.

## What is This?

AI-DLC Starter is a template project that bridges:
- **AI-DLC** (AWS's AI-Driven Development Life Cycle methodology)
- **Claude Code Skills** (executable automation commands)

**Result**: Idea → Enhanced Requirements → AI-DLC Specs → Working Project

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/murphyGo/aidlc-starter.git my-project
cd my-project
```

### 2. Start with Claude

```bash
claude
```

Then run:
```
/start
```

**Option A: Guided (Recommended for rough ideas)**
```
/ideate
```
Claude will ask questions and help you shape your idea into a structured `IDEA.md`.

**Option B: Write directly**
Edit `IDEA.md` at the project root:

```markdown
# My Project Idea

## One-Liner
A REST API for managing personal book collections

## The Problem
Book lovers struggle to track their reading lists across devices

## Core Features
- User authentication
- CRUD operations for books
- Search by title/author
- Export to CSV

## Tech Preferences
- Language: Go
- Database: PostgreSQL
```

### Applying to an Existing Project

Already have a codebase? Use `/adopt` instead of `/ideate`:

```
/adopt
```

Claude will:
1. **Scan** your existing codebase (languages, frameworks, structure)
2. **Guide** you through describing what to add and what to preserve
3. **Generate** a brownfield-formatted `IDEA.md` with Current State / What We Are Adding / What Must Not Change

Then run `/init-project` as usual — AI-DLC will auto-detect the existing code and run a reverse engineering stage before generating specs.

**Quick setup**: Copy these into your existing project, then run `/start`:
- `.claude/skills/` directory
- `aidlc-workflows/` directory
- `docs/references/` directory

### 3. Initialize Project

```
/init-project
```

Claude will:
1. **Analyze** your idea and suggest improvements
2. **Refine** requirements through interactive dialogue
3. **Generate** AI-DLC specification documents
4. **Create** project-specific development skills

## Three-Stage Automation

### Stage 0: Interactive Requirements Refinement

Claude analyzes your `IDEA.md` and:
- Identifies gaps (error handling, edge cases, security)
- Suggests improvements with clear rationale
- Engages in dialogue until requirements are solid
- Generates enhanced `docs/requirements.md`

### Stage 1: AI-DLC Spec Generation

Creates AI-DLC input documents:
- `docs/vision.md` - Project vision and goals
- `docs/tech-env.md` - Technical environment spec

Then guides AI-DLC workflow to produce:
- `aidlc-docs/inception/` - Requirements, user stories, application design
- `aidlc-docs/construction/` - Functional design, NFRs, build plans

### Stage 2: Skill Generation

Creates project-specific automation:
- `/dev-{project}` - Main development driver
- `/code-review` - Code quality checks
- `/tech-debt` - Debt management
- `/cross-check` - Requirements compliance

## Available Skills

| Skill | Purpose |
|-------|---------|
| `/start` | Unified entry point - auto-detects state and routes |
| `/ideate` | Capture lightning idea through guided dialogue |
| `/adopt` | Onboard existing codebase into AI-DLC workflow |
| `/init-project` | Bootstrap new project from idea (add `--quick` for fast-track) |
| `/scaffold` | Generate project structure from specs |
| `/code-review git` | Review changed files for issues |
| `/tech-debt` | View/manage technical debt |
| `/cross-check` | Verify implementation vs requirements |

## Example

See [`examples/book-tracker/`](examples/book-tracker/README.md) for a complete walkthrough from rough idea to project-ready state:

1. **Raw idea**: "I want to build something that helps me track my reading habits"
2. **After `/ideate`**: Structured IDEA.md with problem, features, suggested tech
3. **After `/init-project`**: 6 functional requirements, Go + Chi + PostgreSQL decisions, AI-DLC inception artifacts
4. **After `/scaffold`**: Directories and config files ready for development

## Project Structure

```
aidlc-starter/
├── README.md
├── CLAUDE.md                    # Claude Code context
├── IDEA.md                      # Your idea (input) ← START HERE
├── docs/
│   ├── PROJECT-VISION.md        # About aidlc-starter template
│   ├── DESIGN.md                # Architecture decisions
│   └── references/              # Skill templates (copied during init)
│       ├── dev-skill-template.md
│       ├── code-review-template.md
│       ├── tech-debt-template.md
│       └── cross-check-template.md
├── .claude/
│   └── skills/
│       ├── start/               # Unified entry point
│       ├── ideate/              # Idea capture skill
│       ├── adopt/               # Brownfield adoption skill
│       └── init-project/        # Bootstrap skill
└── aidlc-workflows/             # AWS AI-DLC rules
    └── aidlc-rules/
        ├── aws-aidlc-rules/     # Core workflow
        └── aws-aidlc-rule-details/  # Stage details
```

After running `/init-project`, your project will have:
- `.claude/skills/dev-{project}/` - Project-specific development skill
- `.claude/skills/code-review/` - Code quality checks
- `.claude/skills/tech-debt/` - Debt management
- `.claude/skills/cross-check/` - Requirements compliance

## Feedback Loop

The system supports continuous improvement:

1. **Session Logs** - Every dev session creates traceability
2. **TECH-DEBT Tracking** - Issues captured and prioritized
3. **Cross-Check Reports** - Phase completion triggers compliance verification
4. **Plan Evolution** - Development plan updates as work progresses

## Requirements

- [Claude Code CLI](https://github.com/anthropics/claude-code)
- Git

## How It Works

```
┌─────────────────┐
│     /start      │  Unified entry point
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│/ideate │ │/adopt  │  New idea vs. existing codebase
└───┬────┘ └───┬────┘
    │          │
    └────┬─────┘
         ▼
┌─────────────────┐
│    IDEA.md      │  Your structured idea
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /init-project  │  Claude-powered refinement
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ requirements.md │  Enhanced, structured requirements
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    AI-DLC       │  Spec generation workflow (auto)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  aidlc-docs/    │  Complete specifications
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   /scaffold     │  Directories + config files
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /dev-{name}    │  Project automation
└─────────────────┘
```

## License

MIT
