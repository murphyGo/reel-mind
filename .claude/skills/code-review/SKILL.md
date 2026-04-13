# Code Review Skill - Reel-Mind

Automatically analyze code for quality issues, security vulnerabilities, and best practices compliance.

## Project Configuration

**Languages**: Python 3.12 (pipelines, bot) + TypeScript (Web UI)
**Frameworks**: Claude Agent SDK + ffmpeg/moviepy (Python); Next.js 15 App Router (TypeScript)
**Lint Commands**:
- Python: `ruff check .`
- TypeScript: `cd web && npm run lint`
**Test Commands**:
- Python: `pytest`
- TypeScript: `cd web && npm test`
**Type Check**:
- Python: `mypy src/`
- TypeScript: `cd web && tsc --noEmit`

## Project-Specific Rules (Reel-Mind)

- **Pipelines write-only to Supabase** — flag any Web-UI → pipeline HTTP call.
- **No secrets in Supabase or in code** — flag any DB row or constant that stores a credential-like string.
- **Run idempotency** — any code path that publishes externally must guard on `IdempotencyGuard.run_id_for(...)`.
- **Budget attribution** — every paid API call must write a `cost_ledger` entry with `(channel_id, pipeline, run_id, provider, units, usd_cost)`.
- **Per-channel credential resolution** — secrets accessed via `SecretsProvider.get(channel_id, key)`, never via raw `os.environ`.
- **Adapter retry lives inside the adapter** — flag retry/backoff logic written in pipeline code.
- **StyleProfile immutability** — updates to `style_profiles` rows are forbidden; only inserts (new versions).
- **Korean content path** — TTS voice and subtitle language default to `ko` unless channel config specifies otherwise.
- **Security Baseline extension enabled** — credential handling, input validation, and RLS scoping are blocking findings.
- **PBT extension enabled (full)** — pure functions, serializers, budget math, and state machines must have property tests.

---

## Arguments

- `$ARGUMENTS` - One of the following:
  - `git` - Review files changed in git (staged + unstaged)
  - `session:<path>` - Review files listed in session log's "Files Modified" section
  - `files:<path1>,<path2>` - Review specific files
  - `dir:<path>` - Review all source files in directory

## Objective

Find real issues in code by reading and understanding it deeply — not by pattern-matching against a checklist.

---

## Pre-Review: Automated Checks

Before manual review, run automated tools:

```bash
# Lint
{LINT_COMMAND}

# Type check (if applicable)
{TYPE_CHECK_COMMAND}

# Tests
{TEST_COMMAND}
```

**If any automated check fails, fix those issues before proceeding with manual review.**

---

## Execution Steps

### Step 1: Identify Files to Review

#### If `git`:
```bash
git diff --name-only HEAD
git diff --name-only --cached
```
- Combine staged and unstaged changes
- Filter to source files (exclude generated, vendor, node_modules)
- Separate test files for different handling

#### If `session:<path>`:
- Read session log file
- Parse "Files Modified" or "Files Changed" section
- Extract file paths

#### If `files:<paths>`:
- Split comma-separated paths
- Validate files exist

#### If `dir:<path>`:
- Glob source files recursively
- Detect language from extensions
- Separate test files

### Step 2: Read and Understand Code

Read each file fully. Understand:
- What the code does and why
- How it interacts with other components
- What invariants it maintains
- What happens when things go wrong

### Step 2a: Protocol Selection (Triage)

After reading the code, check for deep-analysis triggers:

1. **Read** `protocols/INDEX.md` for signal-to-protocol mapping
2. **Scan** the code under review for each signal category in the index
3. **Load** the corresponding protocol file for each match (e.g., `protocols/concurrency.md`)
4. **Apply** each loaded protocol's analysis steps during Step 3

Only load protocols whose signals are present in the code. When in doubt, include the protocol.

### Step 3: Review with Focus Areas

Analyze the code from these perspectives, in priority order:

1. **Correctness** — Logic bugs, edge cases, spec non-compliance, off-by-one errors, nil/empty handling
2. **Safety** — Resource leaks, concurrency bugs, security vulnerabilities, data loss risks
3. **Reliability** — Error handling quality, failure scenarios, graceful degradation
4. **Maintainability** — Unnecessary complexity, unclear naming, missing abstractions (or over-abstraction)

#### 3a: Apply Matched Protocols

For each protocol loaded in Step 2a, execute its full analysis steps against the code. Do NOT skip steps — each step builds on the previous one. Include protocol findings in the report (Step 6).

#### Project-Specific Rules
{PROJECT_SPECIFIC_RULES}

### Step 4: Language & Framework Reference

Consult these language and framework-specific patterns during review.

#### 4.1 Language-Specific Checks

#### Go
| Pattern | Issue | Severity |
|---------|-------|----------|
| `err` assigned but not checked | Ignored error | High |
| `return err` without wrapping | Missing context | Medium |
| `go func()` without sync | Goroutine leak | High |
| Missing `defer` for Close() | Resource leak | High |

#### Python
| Pattern | Issue | Severity |
|---------|-------|----------|
| Bare `except:` clause | Catches too much | Medium |
| Missing type hints on public funcs | Type ambiguity | Low |
| `open()` without context manager | Resource leak | Medium |
| Mutable default argument | Shared state bug | High |

#### TypeScript/JavaScript
| Pattern | Issue | Severity |
|---------|-------|----------|
| `any` type usage | Type safety loss | Medium |
| Missing null/undefined check | Runtime error risk | High |
| Unhandled promise rejection | Silent failure | High |
| `==` instead of `===` | Type coercion bug | Medium |

#### 4.2 Framework-Specific Checks

{FRAMEWORK_SECTION}

<!-- BEGIN FRAMEWORK: FastAPI -->
#### FastAPI (Python)
| Pattern | Issue | Severity |
|---------|-------|----------|
| Sync function in async endpoint | Blocking event loop | High |
| Missing `response_model` | Type safety loss | Medium |
| No dependency injection for DB | Testing difficulty | Medium |
| Pydantic model without validation | Data integrity | Medium |
| No `BackgroundTasks` for heavy ops | Slow response | Medium |
| Missing `HTTPException` handling | Poor error responses | Medium |
| No request body validation | Security risk | High |
| Hardcoded CORS origins | Security misconfiguration | Medium |
<!-- END FRAMEWORK: FastAPI -->

<!-- BEGIN FRAMEWORK: Django -->
#### Django (Python)
| Pattern | Issue | Severity |
|---------|-------|----------|
| Raw SQL without parameterization | SQL injection | Critical |
| Missing CSRF protection | Security vulnerability | Critical |
| N+1 query in loop | Performance issue | High |
| No `select_related`/`prefetch_related` | Performance issue | Medium |
| `DEBUG=True` in production settings | Security risk | Critical |
| Missing migration files | Database inconsistency | High |
| No input validation in forms | Data integrity | Medium |
| Using `objects.get()` without try/except | Unhandled exception | Medium |
<!-- END FRAMEWORK: Django -->

<!-- BEGIN FRAMEWORK: Flask -->
#### Flask (Python)
| Pattern | Issue | Severity |
|---------|-------|----------|
| `debug=True` in production | Security risk | Critical |
| Missing input validation | Security vulnerability | High |
| Global state mutation | Thread safety | High |
| No CSRF protection | Security vulnerability | High |
| Secret key in code | Credential exposure | Critical |
| No error handlers defined | Poor error responses | Medium |
<!-- END FRAMEWORK: Flask -->

<!-- BEGIN FRAMEWORK: Express -->
#### Express (Node.js)
| Pattern | Issue | Severity |
|---------|-------|----------|
| No `helmet` middleware | Security headers missing | High |
| Callback without error handling | Silent failure | High |
| Sync file operations | Blocking event loop | Medium |
| No rate limiting | DoS vulnerability | Medium |
| `trust proxy` misconfigured | IP spoofing risk | Medium |
| Missing body-parser limits | DoS via large payload | High |
| No input sanitization | XSS/Injection risk | Critical |
<!-- END FRAMEWORK: Express -->

<!-- BEGIN FRAMEWORK: NestJS -->
#### NestJS (Node.js)
| Pattern | Issue | Severity |
|---------|-------|----------|
| Missing DTO validation | Data integrity | High |
| No guards on sensitive routes | Authorization bypass | Critical |
| Circular dependency | Runtime error | High |
| Missing exception filters | Poor error handling | Medium |
| No pipe validation | Data integrity | High |
| Injectable without scope | Memory leak potential | Medium |
<!-- END FRAMEWORK: NestJS -->

<!-- BEGIN FRAMEWORK: React -->
#### React (TypeScript/JavaScript)
| Pattern | Issue | Severity |
|---------|-------|----------|
| `useEffect` missing dependencies | Stale closure | High |
| State mutation directly | React won't re-render | High |
| Missing `key` prop in lists | Reconciliation issues | Medium |
| Inline function in render | Performance issue | Low |
| No error boundary | Crash propagation | Medium |
| `dangerouslySetInnerHTML` usage | XSS vulnerability | Critical |
| State in URL not synced | UX inconsistency | Low |
| No loading/error states | Poor UX | Medium |
<!-- END FRAMEWORK: React -->

<!-- BEGIN FRAMEWORK: Vue -->
#### Vue (TypeScript/JavaScript)
| Pattern | Issue | Severity |
|---------|-------|----------|
| Mutating props directly | Unexpected behavior | High |
| `v-if` and `v-for` on same element | Performance issue | Medium |
| Missing `key` in `v-for` | Reconciliation issues | Medium |
| No error handling in async | Silent failure | High |
| Computed property with side effects | Unexpected behavior | High |
<!-- END FRAMEWORK: Vue -->

<!-- BEGIN FRAMEWORK: Gin -->
#### Gin (Go)
| Pattern | Issue | Severity |
|---------|-------|----------|
| `c.JSON()` without return | Handler continues | High |
| Missing middleware for auth | Security bypass | Critical |
| No request validation | Data integrity | Medium |
| `c.Abort()` without return | Handler continues | High |
| No panic recovery | Server crash | High |
| Missing CORS configuration | Security issue | Medium |
<!-- END FRAMEWORK: Gin -->

<!-- BEGIN FRAMEWORK: Echo -->
#### Echo (Go)
| Pattern | Issue | Severity |
|---------|-------|----------|
| Context not passed to DB calls | Timeout not respected | Medium |
| Missing error handler | Poor error responses | Medium |
| No request binding validation | Data integrity | Medium |
| Missing middleware | Security/logging gaps | Medium |
<!-- END FRAMEWORK: Echo -->

<!-- BEGIN FRAMEWORK: Spring Boot -->
#### Spring Boot (Java)
| Pattern | Issue | Severity |
|---------|-------|----------|
| Missing `@Transactional` | Data inconsistency | High |
| No input validation (`@Valid`) | Data integrity | Medium |
| Hardcoded credentials | Security risk | Critical |
| Missing exception handler | Poor error responses | Medium |
| N+1 query in JPA | Performance issue | High |
| No connection pool limits | Resource exhaustion | High |
<!-- END FRAMEWORK: Spring Boot -->

<!-- BEGIN FRAMEWORK: Actix -->
#### Actix (Rust)
| Pattern | Issue | Severity |
|---------|-------|----------|
| Blocking in async handler | Performance issue | High |
| Missing error handling | Silent failure | High |
| No request validation | Data integrity | Medium |
| Unwrap without context | Poor error messages | Medium |
<!-- END FRAMEWORK: Actix -->

### Step 5: Test Coverage Check

For each new/modified function:

| Check | Method | Severity |
|-------|--------|----------|
| Test file exists | Find corresponding test file | Medium |
| Function has test | Find test for function name | Medium |
| Error paths tested | Find test with error assertions | Medium |

### Step 6: Generate Report

```markdown
## Code Review Report

**Scope**: [N files reviewed]
**Languages**: [detected languages]
**Date**: YYYY-MM-DD HH:MM

---

### Summary

| Category | ✅ Pass | ⚠️ Warn | 🔴 Fail |
|----------|---------|---------|---------|
| Correctness | X | Y | Z |
| Safety | X | Y | Z |
| Reliability | X | Y | Z |
| Maintainability | X | Y | Z |
| Test Coverage | X | Y | Z |
| **Total** | **X** | **Y** | **Z** |

**Status**: ✅ All Clear / ⚠️ Warnings Found / 🔴 Issues Found

---

### Protocols Applied

| Protocol | Triggered By | Key Findings |
|----------|-------------|--------------|
| {protocol name} | {signal that triggered it} | {summary of findings or "No issues"} |

_If no protocols were triggered, write: "No deep-analysis protocols triggered."_

---

### Issues Detail

#### 🔴 Critical/High Severity

| # | File:Line | Category | Issue | Suggestion |
|---|-----------|----------|-------|------------|
| 1 | src/auth.py:45 | Security | Hardcoded secret | Use environment variable |

#### 🟡 Medium Severity

| # | File:Line | Category | Issue | Suggestion |
|---|-----------|----------|-------|------------|
| 2 | src/db.py:78 | Error | Generic except | Catch specific exceptions |

#### 🟢 Low Severity

| # | File:Line | Category | Issue | Suggestion |
|---|-----------|----------|-------|------------|
| 3 | src/utils.py:12 | Quality | TODO without ID | Add TECH-DEBT reference |

---

### Self-Review Checklist

| Item | Status | Evidence |
|------|--------|----------|
| No logic bugs or edge case gaps | ✅/⚠️/🔴 | [brief evidence] |
| Resources properly cleaned up | ✅/⚠️/🔴 | [brief evidence] |
| Concurrency is safe | ✅/⚠️/🔴 | [brief evidence] |
| No hardcoded secrets | ✅/⚠️/🔴 | [brief evidence] |
| Errors handled with context | ✅/⚠️/🔴 | [brief evidence] |
| Failure scenarios covered | ✅/⚠️/🔴 | [brief evidence] |
| Unit tests cover key paths | ✅/⚠️/🔴 | [brief evidence] |

---

### TECH-DEBT Candidates

Issues that should be tracked as technical debt:

| DEBT ID | Priority | Location | Description | Effort |
|---------|----------|----------|-------------|--------|
| DEBT-XXX | Medium | `file.py:78` | [description] | 15 min |

Add to TECH-DEBT.md? (yes/no)
```

---

## Ignore Directives

Code can be excluded from review with comments:

```python
# code-review:ignore-next-line
password = os.getenv("PASSWORD")  # This is OK, reads from env

# code-review:ignore-block-start
# Legacy code, will be refactored
def old_function():
    pass
# code-review:ignore-block-end
```

---

## Severity Definitions

| Severity | Meaning | Action |
|----------|---------|--------|
| 🔴 Critical | Security vulnerability or data loss risk | Must fix before commit |
| 🔴 High | Likely bug or resource leak | Should fix before commit |
| 🟡 Medium | Code quality issue | Fix or document as TECH-DEBT |
| 🟢 Low | Style/convention issue | Fix if easy, else ignore |

---

## Example Invocations

Review git changes:
```
/code-review git
```

Review from session log:
```
/code-review session:docs/sessions/2026-04-05-phase1.md
```

Review specific files:
```
/code-review files:src/auth.py,src/db.py
```

Review directory:
```
/code-review dir:src/services
```

---

## Language Style Guide

{STYLE_GUIDE_SECTION}

<!-- BEGIN STYLE: Python -->
### Python Style Guide

#### Naming Conventions
- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_CASE` for constants
- `_private` prefix for internal use
- `__dunder__` for magic methods only

#### Code Organization
- Imports at top: stdlib → third-party → local
- One class per file (usually)
- Keep functions under 20 lines when possible
- Use `__all__` for public API

#### Error Handling
```python
# Good
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise OperationError("Context message") from e

# Bad
try:
    result = risky_operation()
except:
    pass
```

#### Type Hints
- Required on all public functions
- Use `Optional[]` for nullable types
- Use `TypeVar` for generics
<!-- END STYLE: Python -->

<!-- BEGIN STYLE: TypeScript -->
### TypeScript Style Guide

#### Naming Conventions
- `camelCase` for variables, functions
- `PascalCase` for classes, interfaces, types
- `UPPER_CASE` for constants
- `I` prefix for interfaces (optional, team preference)

#### Code Organization
- Imports: types → external → internal
- Export at declaration, not bottom
- One component per file (React)
- Co-locate tests with source

#### Error Handling
```typescript
// Good
try {
  const result = await riskyOperation();
} catch (error) {
  if (error instanceof SpecificError) {
    logger.error('Operation failed', { error });
    throw new AppError('Context message', { cause: error });
  }
  throw error;
}

// Bad
try {
  const result = await riskyOperation();
} catch (e: any) {
  console.log(e);
}
```

#### Type Safety
- Avoid `any` - use `unknown` if type is truly unknown
- Use strict mode: `"strict": true`
- Prefer `interface` for object shapes
- Use `type` for unions/intersections
<!-- END STYLE: TypeScript -->

<!-- BEGIN STYLE: Go -->
### Go Style Guide

#### Naming Conventions
- `camelCase` for unexported
- `PascalCase` for exported
- Short names for local scope: `i`, `ctx`, `err`
- Descriptive names for package scope
- No `Get` prefix for getters

#### Code Organization
- Group imports: stdlib → external → internal
- Constants and types at top
- Constructor functions: `New{Type}()`
- Keep packages focused and small

#### Error Handling
```go
// Good
result, err := riskyOperation()
if err != nil {
    return fmt.Errorf("operation failed: %w", err)
}

// Bad
result, _ := riskyOperation()
```

#### Best Practices
- Accept interfaces, return structs
- Use `context.Context` for cancellation
- `defer` for cleanup immediately after resource acquisition
- Handle all errors or explicitly ignore with `_`
<!-- END STYLE: Go -->

<!-- BEGIN STYLE: JavaScript -->
### JavaScript Style Guide

#### Naming Conventions
- `camelCase` for variables, functions
- `PascalCase` for classes, components
- `UPPER_CASE` for constants
- `_private` convention for internal (no enforcement)

#### Code Organization
- Imports at top, organized by type
- Prefer named exports
- One component/class per file
- Keep files under 300 lines

#### Error Handling
```javascript
// Good
try {
  const result = await riskyOperation();
} catch (error) {
  logger.error('Operation failed', { error });
  throw new AppError('Context message', { cause: error });
}

// Bad
try {
  const result = await riskyOperation();
} catch (e) {
  console.log(e);
}
```
<!-- END STYLE: JavaScript -->

---

## Project-Specific Patterns

{PROJECT_PATTERNS_SECTION}

<!-- This section should include project-specific patterns based on DESIGN.md -->
