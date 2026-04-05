# Code Review Skill

Automatically analyze code for quality issues, security vulnerabilities, and best practices compliance.

## Arguments

- `$ARGUMENTS` - One of the following:
  - `git` - Review files changed in git (staged + unstaged)
  - `session:<path>` - Review files listed in session log's "Files Modified" section
  - `files:<path1>,<path2>` - Review specific files
  - `dir:<path>` - Review all source files in directory

## Objective

Proactively verify code quality by analyzing actual source code for common issues, security vulnerabilities, and best practices violations. Language-agnostic with specialized checks per language.

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

### Step 2: Detect Language and Apply Rules

| Extension | Language | Specialized Checks |
|-----------|----------|-------------------|
| `.go` | Go | Error handling, goroutines, defer |
| `.py` | Python | Type hints, exception handling |
| `.ts`, `.tsx` | TypeScript | Types, null checks, async/await |
| `.js`, `.jsx` | JavaScript | Null checks, async/await |
| `.rs` | Rust | Ownership, lifetimes, unwrap |
| `.java` | Java | Null checks, resources, exceptions |

### Step 3: Universal Checks (All Languages)

#### 3.1 Error Handling
| Pattern | Issue | Severity |
|---------|-------|----------|
| Caught error not logged/handled | Swallowed error | High |
| Generic catch-all exception | Loss of context | Medium |
| Error not propagated | Silent failure | High |

#### 3.2 Security
| Pattern | Issue | Severity |
|---------|-------|----------|
| Hardcoded password/secret/key | Credential exposure | Critical |
| SQL string concatenation | SQL injection risk | Critical |
| User input in shell command | Command injection | Critical |
| Weak random (non-crypto) | Predictable values | High |
| Disabled SSL verification | MITM vulnerability | Critical |

#### 3.3 Resource Management
| Pattern | Issue | Severity |
|---------|-------|----------|
| File opened without close | Resource leak | High |
| Connection without cleanup | Resource leak | High |
| Lock without unlock | Deadlock risk | Critical |

#### 3.4 Code Quality
| Pattern | Issue | Severity |
|---------|-------|----------|
| TODO/FIXME without tracking | Untracked work | Low |
| Debug print statements | Debug code left in | Low |
| Magic numbers | Unexplained literals | Low |
| Commented-out code blocks | Dead code | Low |

### Step 4: Language-Specific Checks

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
| Error Handling | X | Y | Z |
| Security | X | Y | Z |
| Resource Management | X | Y | Z |
| Code Quality | X | Y | Z |
| Test Coverage | X | Y | Z |
| **Total** | **X** | **Y** | **Z** |

**Status**: ✅ All Clear / ⚠️ Warnings Found / 🔴 Issues Found

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
| All errors handled appropriately | ⚠️ | 2 unhandled errors found |
| No hardcoded secrets | ✅ | None detected |
| Resources properly cleaned up | ✅ | All files use context managers |
| No obvious security issues | ✅ | No injection risks found |
| Test coverage adequate | ⚠️ | 1 function untested |

---

### TECH-DEBT Candidates

Issues that should be tracked:

```markdown
### DEBT-XXX: Generic exception handling in db.py

**Category**: Reliability
**Priority**: Medium
**Location**: `src/db.py:78,92`

**Description**:
2 bare except clauses catching all exceptions.

**Remediation**:
Catch specific exceptions (ConnectionError, TimeoutError).

**Estimated Effort**: 30 minutes
```

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
