# AI-DLC Starter

A meta-template for transforming ideas into fully-specified, development-ready projects.

## Project Purpose

This project provides:
1. **Interactive Requirements Refinement** - Claude analyzes rough ideas and enhances them through dialogue
2. **AI-DLC Integration** - Generates specification documents using AWS AI-DLC methodology
3. **Development Automation** - Creates project-specific skills for ongoing development

## Quick Commands

| Skill | Purpose | Example |
|-------|---------|---------|
| `/start` | Unified entry point - auto-detects and routes | `/start` |
| `/ideate` | Capture lightning idea through dialogue | `/ideate` |
| `/init-project` | Bootstrap new project from IDEA.md | `/init-project` |
| `/code-review` | Analyze code for issues | `/code-review git` |
| `/tech-debt` | View/manage technical debt | `/tech-debt` |
| `/cross-check` | Verify implementation vs requirements | `/cross-check` |

## Key Files

| File | Purpose |
|------|---------|
| `IDEA.md` | User's project idea (entry point) |
| `docs/PROJECT-VISION.md` | About the aidlc-starter template itself |
| `docs/DESIGN.md` | Architecture and design decisions |
| `.claude/skills/` | Skill definitions for automation |
| `aidlc-workflows/` | AWS AI-DLC rules and templates |

## Development Workflow

### For This Project (aidlc-starter itself)

1. Read `docs/PROJECT-VISION.md` to understand the template's purpose
2. Read `docs/DESIGN.md` for architecture decisions
3. Skills are in `.claude/skills/*/SKILL.md`

### For Projects Using This Template

1. User runs `/start` or `/ideate` to begin
2. `/ideate` captures rough idea through dialogue → creates `IDEA.md`
3. Run `/init-project` to start interactive refinement
4. Claude enhances requirements through dialogue
5. AI-DLC specs are auto-generated
6. Project-specific skills are created
7. User runs `/dev-{project}` for ongoing development

## Skill Format

Skills follow this structure:

```markdown
# Skill Name

Brief description.

## Arguments
- `$ARGUMENTS` - What the skill accepts

## Objective
What the skill accomplishes.

## Execution Steps
### Step 1: ...
### Step 2: ...

## Guidelines
Best practices and rules.

## Example Invocations
```

## AI-DLC Rules Location

- Core workflow: `aidlc-workflows/aidlc-rules/aws-aidlc-rules/core-workflow.md`
- Stage details: `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/`
  - `inception/` - Requirements, user stories, application design
  - `construction/` - Functional design, NFRs, code generation
  - `common/` - Shared guidelines and standards

## Code Style

- Skills are written in Markdown with structured sections
- Use tables for status tracking and option presentation
- Use code blocks for examples and templates
- Keep instructions actionable and specific

## Important Conventions

1. **Skills don't auto-commit** - Always show changes and wait for user approval
2. **Interactive dialogue** - Use structured prompts with clear response options
3. **Traceability** - Log decisions, create session logs, track debt
4. **Incremental progress** - One task at a time, update status as you go
