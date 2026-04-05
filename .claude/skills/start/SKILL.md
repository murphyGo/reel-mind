# Start Skill

Single entry point that detects project state and routes to the appropriate skill.

## Arguments

- `$ARGUMENTS` - (optional) Force specific mode:
  - (empty) - Auto-detect state and route
  - `ideate` - Force ideation mode
  - `init` - Force initialization mode
  - `dev` - Force development mode
  - `status` - Show current state without routing

## Objective

Provide a unified entry point for new users. Automatically detect where the project is in its lifecycle and invoke the appropriate skill, eliminating the need to know which command to run.

---

## Execution Steps

### Step 1: Check for Override Mode

If `$ARGUMENTS` is provided:

| Argument | Action |
|----------|--------|
| `ideate` | Go to `/ideate` |
| `init` | Go to `/init-project` |
| `dev` | Go to Development Options |
| `status` | Go to Step 3 (show status only) |

If no argument, proceed to Step 2.

### Step 2: Detect Project State

Check for indicators in this order:

```
Check 1: Development Ready?
├── Look for: .claude/skills/dev-*/SKILL.md
├── If found: State = "development"
└── If not: Continue

Check 2: Initialized?
├── Look for: aidlc-docs/ directory with content
├── If found: State = "initialized"
└── If not: Continue

Check 3: Has Idea?
├── Look for: IDEA.md OR docs/PROJECT-VISION.md OR docs/inception.md
├── If found: State = "has-idea"
└── If not: Continue

Check 4: Has AI-DLC Rules?
├── Look for: aidlc-workflows/aidlc-rules/
├── If found: State = "fresh"
└── If not: State = "needs-setup"
```

### Step 3: Route Based on State

#### State: `development`

```
## Project Ready for Development

Your project is initialized and ready for development.

### Available Skills

| Skill | Purpose |
|-------|---------|
| `/dev-{name}` | Continue development (follow development plan) |
| `/code-review git` | Review recent code changes |
| `/tech-debt` | View/manage technical debt |
| `/cross-check` | Verify requirements compliance |

### Quick Actions

- **continue** - Run the main development skill
- **review** - Run code review on recent changes
- **status** - Show project status

What would you like to do?
```

Handle responses:
| Response | Action |
|----------|--------|
| "continue" / "dev" | Find and invoke `/dev-*` skill |
| "review" | Invoke `/code-review git` |
| "status" | Show development plan status |

#### State: `initialized`

```
## Project Initialized

AI-DLC specs have been generated, but development skills aren't set up yet.

### Current Status
- aidlc-docs/: Generated
- Development skills: Not yet created

### Next Step
Run `/init-project` to complete setup and generate development skills.

Shall I run `/init-project` now? (yes/no)
```

If yes, invoke `/init-project`.

#### State: `has-idea`

```
## Ready to Initialize

I found your idea file. Ready to transform it into a full project.

### Found
- [filename]: [first line or one-liner if present]

### Next Step
Run `/init-project` to:
1. Analyze and enhance your requirements through dialogue
2. Generate AI-DLC specification documents
3. Create project-specific development skills

Shall I run `/init-project` now? (yes/no)
```

If yes, invoke `/init-project`.

#### State: `fresh`

```
## New Project - Let's Start!

This looks like a fresh workspace. I'll help you capture your idea.

### Two Ways to Start

**Option 1: Guided (Recommended)**
Run `/ideate` - I'll ask questions to help shape your idea

**Option 2: Manual**
Create `IDEA.md` at the project root with your idea

### Quick Start

Shall I run `/ideate` now? (yes/no)

Or tell me your idea right here and I'll start capturing it.
```

Handle responses:
| Response | Action |
|----------|--------|
| "yes" / "ideate" | Invoke `/ideate` |
| "no" / "manual" | Show IDEA.md template location |
| [idea text] | Invoke `/ideate [idea text]` |

#### State: `needs-setup`

```
## Setup Required

This workspace doesn't have AI-DLC rules installed.

### Setup Options

**Option 1: Clone aidlc-starter**
```bash
git clone https://github.com/murphyGo/aidlc-starter.git
```

**Option 2: Copy from existing project**
Copy the `aidlc-workflows/` directory from another aidlc-starter project.

### After Setup
Run `/start` again to begin.
```

---

## Status Mode

When `$ARGUMENTS` is `status`:

```
## Project Status

| Aspect | Status |
|--------|--------|
| AI-DLC Rules | ✅ Present / ❌ Missing |
| Idea File | ✅ IDEA.md / ✅ docs/inception.md / ❌ None |
| AI-DLC Specs | ✅ Generated / ❌ Not yet |
| Dev Skills | ✅ Created / ❌ Not yet |
| Tech Debt | [N] items |

### Current State: [state name]

### Recommended Next Step
[Based on state]
```

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Multiple dev skills found | List them and ask which to use |
| Partial initialization | Explain what's missing, suggest fix |
| Corrupted state | Offer to diagnose or reset |

---

## Example Invocations

Auto-detect and route:
```
/start
```

Force specific mode:
```
/start ideate
/start init
/start dev
```

Check status only:
```
/start status
```
