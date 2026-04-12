# Scaffold Skill

Generate project directory structure, config files, and boilerplate based on AI-DLC specs.

## Arguments

- `$ARGUMENTS` - (optional):
  - (empty) - Auto-detect from `docs/requirements.md` and `docs/tech-env.md`, then scaffold
  - `preview` - Show what would be created without creating anything
  - `minimal` - Only directory structure, no config files
  - `"tech stack override"` - e.g., `go chi postgres` to override detected stack

## Objective

Bridge the gap between "AI-DLC specs ready" and "code ready to write." Create a language/framework-appropriate project structure with boilerplate config files so the user can run `/dev-{project}` against a proper skeleton.

**Scope boundary**: Scaffold creates **directories and config files only**. It does NOT generate application code — that is AI-DLC construction's job via the dev skill. Generating code here would conflict with the code-generation stage.

---

## Execution Steps

### Step 1: Validate Prerequisites

1. **Check requirements.md exists**:
   - Required: `docs/requirements.md`
   - If missing, suggest running `/init-project` first and stop.

2. **Check recommended inputs**:
   - `docs/tech-env.md` (optional — adds infrastructure detail)
   - `aidlc-docs/aidlc-state.md` (optional — enables state tracking update)

3. **Check if already scaffolded**:
   - If ANY of `src/`, `cmd/`, `lib/`, `app/`, or `pkg/` directories exist with content, warn:
     ```
     ⚠️  Project appears to be already scaffolded.
     Found: [list of existing source directories]

     Continue anyway? Options:
     - **merge** — Add missing directories/files, skip existing
     - **cancel** — Stop scaffold
     ```
   - Wait for user choice before proceeding.

### Step 2: Detect Tech Stack

1. **Read** `docs/requirements.md` Section 4 (Technical Decisions table) — extract language, framework, database, infrastructure.

2. **Read** `docs/tech-env.md` Technology Stack section (if exists) — fill in any gaps.

3. **Parse `$ARGUMENTS` override** (if provided) — user-specified stack overrides detected values.

4. **Present detection** and wait for confirmation:

```
## Tech Stack Detected

| Component | Value | Source |
|-----------|-------|--------|
| Language | [detected] | requirements.md §4 |
| Framework | [detected] | requirements.md §4 |
| Database | [detected or "None"] | tech-env.md |
| Infrastructure | [detected or "Not specified"] | tech-env.md |
| Test framework | [inferred from language] | inferred |

Is this correct?
- **yes** — Proceed to scaffold plan
- **override [component] [value]** — Correct a detection
- **cancel** — Stop
```

### Step 3: Present Scaffold Plan

Based on detected stack, generate a tree preview and config file list.

**Stack-to-structure mapping** (guidance — adapt to actual stack):

| Stack | Directories |
|-------|-------------|
| Go + Chi/Gin (API) | `cmd/{name}/`, `internal/`, `internal/handlers/`, `internal/models/`, `pkg/`, `api/`, `migrations/`, `tests/` |
| Go + library | `pkg/`, `internal/`, `examples/`, `testdata/` |
| Python + FastAPI | `src/{name}/`, `src/{name}/api/`, `src/{name}/models/`, `src/{name}/services/`, `tests/`, `alembic/` |
| Python + Django | `{name}/`, `{name}/apps/`, `{name}/templates/`, `{name}/static/`, `tests/` |
| Python + CLI/script | `src/{name}/`, `tests/` |
| TypeScript + React/Next.js | `src/`, `src/components/`, `src/pages/` (or `app/`), `src/hooks/`, `src/lib/`, `public/`, `tests/` |
| TypeScript + NestJS | `src/`, `src/modules/`, `src/common/`, `src/config/`, `test/` |
| Rust + Actix/Axum | `src/`, `src/handlers/`, `src/models/`, `src/routes/`, `tests/`, `migrations/` |
| Java + Spring | `src/main/java/{pkg}/`, `src/main/resources/`, `src/test/java/{pkg}/` |

**Config file table**:

| File | When | Purpose |
|------|------|---------|
| `.gitignore` | Always (append language patterns if exists) | Ignore build artifacts, env files |
| `Makefile` or `justfile` | Always | `build`, `test`, `lint`, `run` targets |
| Package manifest (`go.mod`, `package.json`, `pyproject.toml`, `Cargo.toml`) | Always | Dependency declaration |
| `Dockerfile` | If Docker/containers in tech decisions | Multi-stage build for detected language |
| `docker-compose.yml` | If database specified | App + database service |
| `.github/workflows/ci.yml` | If GitHub remote detected in `.git/config` | Language-appropriate CI |
| `.env.example` | If database or external services referenced | Template environment variables |
| `README.md` (update) | If README exists | Add Getting Started / Development sections |

**Present as**:

```
## Scaffold Plan

Based on: [Language] + [Framework] + [Database]

### Directory Structure
[ASCII tree view using aidlc ASCII rules: only + - | ^ v < > — no Unicode]

### Config Files
[Table of files to create]

### Options
- **create** — Generate this structure
- **adjust** — Modify before creating (ask which dirs/files to skip or add)
- **preview [file]** — See contents of a specific config file
- **minimal** — Directories only, no config files
- **cancel** — Stop
```

Wait for user choice before proceeding.

### Step 4: Generate Structure

1. **Create directories** in order (parent before child). Each directory gets a `.gitkeep` file so git tracks the empty dir.

2. **Generate config files** from templates:
   - **`.gitignore`**: If exists, append missing language-specific patterns. If not, create with language defaults + common patterns (`.env`, `.DS_Store`, IDE dirs).
   - **`Makefile`**: `build`, `test`, `lint`, `run`, `clean`, `help` targets. Adapt commands to detected language (e.g., `go build ./...` vs `npm run build`).
   - **Package manifest**: Initialize with project name from requirements.md and minimal dependencies (e.g., `go mod init {module-path}`, `npm init -y`, `poetry init --no-interaction`).
   - **`Dockerfile`**: Multi-stage build for the detected language (e.g., `golang:alpine` → `scratch` or `distroless`).
   - **`docker-compose.yml`**: App service + database service (PostgreSQL, MySQL, etc.) with named volumes.
   - **`.github/workflows/ci.yml`**: Checkout + language setup + install + lint + test.
   - **`.env.example`**: `DATABASE_URL=...`, `PORT=...`, other env vars referenced in requirements.
   - **README.md update**: Insert Getting Started section if not present.

3. **Do NOT generate application code** (no `main.go`, no `app.py`, no `index.ts`). The dev skill handles code generation through AI-DLC construction stages.

4. **Show each file's content before writing** when it's the first of its kind (so the user can spot errors early).

### Step 5: Verify and Report

1. **List all created files/directories** in a tree view.

2. **Run basic validation** where possible:
   - Go: `go mod tidy` (if go.mod created)
   - Node: mention `npm install` needed (don't auto-run)
   - Python: mention `pip install -e .` or `poetry install` needed

3. **Present summary**:

```
## Scaffold Complete

### Created
[tree of directories and files]

### Next Steps
1. [Install dependencies command for detected stack]
2. Run `/dev-{name}` to start AI-DLC construction (code generation)
3. Or write code manually — structure is ready
```

### Step 6: Update State

If `aidlc-docs/aidlc-state.md` exists, append a row to the Stage Progress table:

```markdown
| Scaffold | ✅ Complete ({YYYY-MM-DD}) |
```

If `aidlc-docs/audit.md` exists, append an entry with timestamp and list of scaffolded items.

---

## Error Handling

| Situation | Response |
|-----------|----------|
| No `docs/requirements.md` | Suggest `/init-project` (or `/init-project --quick`) first |
| Tech stack not specified in requirements | Use smart defaults based on project type, confirm with user |
| Source directory already exists with content | Ask: merge / cancel |
| Package manifest exists | Ask: update (merge deps) / skip / replace |
| Unknown tech stack | Ask user to specify, offer 3-4 common options |
| No write permission | Report error, suggest user check filesystem permissions |
| `.gitignore` conflicts | Append missing patterns only, preserve user additions |

---

## Example Invocations

Auto-detect and scaffold:
```
/scaffold
```

Preview without writing:
```
/scaffold preview
```

Directories only (no config files):
```
/scaffold minimal
```

Override detected stack:
```
/scaffold go chi postgres
```
