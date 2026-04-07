# {Project Name} Development Skill

Incrementally develops the {Project Name} service following the development plan.

## Arguments

- `$ARGUMENTS` - (Optional) Specific Phase or task (e.g., `phase2`, `2.1`)

## Objective

Execute one sub-task at a time from the development plan to incrementally build the {Project Name} service. Ensure quality through requirements compliance, best practices, and unit tests.

---

## AIDLC Construction Integration

This skill operates within the AIDLC Construction phase. Before executing tasks, it references the project's AI-DLC artifacts to ensure alignment:

- **Execution plan**: `aidlc-docs/inception/plans/execution-plan.md` — defines which construction stages apply
- **Application design**: `aidlc-docs/inception/application-design/` — component definitions, dependencies, services
- **Requirements reference**: `aidlc-docs/inception/requirements/requirements.md` → `docs/requirements.md`
- **Unit definitions**: `aidlc-docs/inception/application-design/unit-of-work.md` (if units were generated)

### AIDLC Construction Stages Awareness

The development plan includes an "AIDLC Construction Stages" table. When the execution plan specifies stages like Functional Design or NFR Requirements, the dev skill should:

1. **Before Code Generation tasks**: Check if the execution plan requires design stages (Functional Design, NFR Requirements, NFR Design, Infrastructure Design) for the current unit
2. **If design stages apply but haven't been completed**: Guide the user through the relevant AIDLC construction stage rules (from `aidlc-workflows/aidlc-rules/aws-aidlc-rule-details/construction/`) before writing code
3. **If design stages are marked N/A**: Proceed directly to implementation
4. **Extension enforcement**: If extensions are enabled in `aidlc-docs/aidlc-state.md`, check applicable rules at each stage

---

## Execution Steps

### Step 0: Health Check (Automatic)

Automatic status check before starting development:

1. **TECH-DEBT Escalation Check**:
   - Read `docs/TECH-DEBT.md`
   - Check items exceeding thresholds:
     - Critical: Any age → Alert
     - High: > 14 days → Alert
     - Medium: > 21 days → Warn
   - Display if escalation candidates found:
     ```
     ⚠️ TECH-DEBT Alert

     | DEBT ID | Priority | Age | Action Suggested |
     |---------|----------|-----|------------------|
     | DEBT-001 | High | 16d | Consider /tech-debt promote |

     Continue with development? (yes/no/review-debt)
     ```

2. **Phase Completion Check**:
   - Scan completed Phases in `docs/development-plan.md`
   - Check existing reviews in `docs/cross-checks/`
   - If unchecked Phase found:
     ```
     📋 Phase Review Pending

     Phase [N] is complete but has no cross-check document.
     Run cross-check now? (yes/no/later)
     ```
   - **yes**: Execute `/cross-check` for the unchecked phase before proceeding to development
   - **no**: Skip cross-check and proceed directly to next development target
   - **later**: Acknowledge and proceed, but remind again at next invocation

**Note**: Health check alerts are informational. You can proceed with "yes" or address issues first.

### Step 1: Environment Validation

1. **Verify Path Existence**:
   - `docs/development-plan.md`
   - `docs/TECH-DEBT.md`
   - `docs/requirements.md`
   - `CLAUDE.md`
   - `docs/DESIGN.md`
   - `aidlc-docs/aidlc-state.md` (AI-DLC state tracking)
   - `aidlc-docs/inception/plans/execution-plan.md` (construction stage decisions)

### Step 2: Analyze Development Plan

1. **Read**: `docs/development-plan.md`

2. **Read AIDLC context** (if exists):
   - `aidlc-docs/inception/plans/execution-plan.md` — check which construction stages apply
   - `aidlc-docs/aidlc-state.md` — current state, enabled extensions

3. **Parse Plan** (supports both Unit-centric and Phase-centric layouts):

   **Unit-centric plan** (has `## Unit:` sections):
   - Unit Overview table (units, stories, construction stages, design artifacts, status)
   - Per-unit sub-tasks with checkbox status
   - Cross-Unit integration tasks

   **Phase-centric plan** (fallback, has `## Phase N:` sections):
   - Construction Stages table
   - Current status table (component status)
   - Per-phase sub-tasks with checkbox status

   For both formats:
   - Checkbox status: `[x]` = complete, `[ ]` = incomplete
   - Note **AIDLC Design** path for the current unit/phase (e.g., `aidlc-docs/construction/{unit-name}/`)
   - Note story mappings (e.g., `→ US-001`, `→ FR-003`)

4. **Find Next Development Target** (scan top to bottom):
   - Skip fully checked `[x]` units/phases/sub-tasks
   - Skip items marked "deferred" or "— *deferred*"
   - Select **first sub-task** with at least one unchecked `[ ]` item
   - For mixed-status sub-tasks, target only unchecked items
   - **AIDLC check**: If the target unit has construction design stages listed (e.g., Functional Design, NFR) and corresponding artifacts don't exist in `aidlc-docs/construction/{unit-name}/`, prompt the user:
     ```
     ⚠️ AIDLC Design Stage Pending

     Unit "{unit-name}" requires Functional Design before code generation
     (per execution-plan.md), but no design artifacts found.

     Options:
     - **design**: Run AIDLC design stages for this unit first
     - **skip**: Proceed without formal design (acknowledge in audit.md)
     ```

### Step 3: Present Development Target

Present identified sub-task in this format:

```
## Next Development Target

**Unit**: [unit-name] (or "single-unit" if phase-centric plan)
**Sub-task**: [Sub-task number and title]
**Story**: [US-XXX or FR-XXX mapping, if any]
**AIDLC Design**: [path to design artifacts, if applicable]

### Items to Develop:
- [ ] Item 1 description
- [ ] Item 2 description
...

### Related Requirements:
- FR-XXX: [Requirement description]
- NFR-XXX: [Requirement description]

### Estimated Files:
- New: [List of files to create]
- Modified: [List of files to modify]

Proceed with this development? (yes/no)
```

**Wait for user approval before proceeding.**

### Step 4: Development (Plan Mode)

After user approval:

1. **Enter Plan Mode**: Use `EnterPlanMode` tool

2. **Research Phase**:
   - Read related requirements from `docs/requirements.md`
   - Check design patterns in `docs/DESIGN.md`
   - Read AIDLC design artifacts (if they exist for this unit):
     - `aidlc-docs/construction/{unit-name}/functional-design/` — business logic, domain entities
     - `aidlc-docs/construction/{unit-name}/nfr-design/` — NFR patterns, logical components
     - `aidlc-docs/inception/application-design/` — component definitions, services, dependencies
   - Explore existing codebase for patterns and dependencies

3. **Write Implementation Plan**:
   - Files to create/modify
   - Implementation approach aligned with requirements
   - Test strategy (unit tests for all new features)
   - Integration points with existing code

4. **Exit Plan Mode** and implement:
   - Strictly follow language best practices
   - Write clean, idiomatic code
   - Include comprehensive unit tests
   - Run tests to verify

### Step 5: Self-Review & Documentation

After successful implementation:

**5.1 Code Review** (delegated to separate agent for fresh-eyes analysis):

Delegate code review to a **separate agent** using the Agent tool. This avoids confirmation bias — the reviewer reads the code without knowing the author's intent.

```
Agent(subagent_type="general-purpose", prompt="""
You are reviewing {PRIMARY_LANGUAGE} code for the {Project Name} project.

## Files to Review
[list changed source files from `git diff --name-only HEAD` + `git diff --name-only --cached`]

## Review Focus (priority order)
1. Correctness — logic bugs, edge cases, spec non-compliance
2. Safety — resource leaks, concurrency bugs, security, data loss risks
3. Reliability — error handling quality, failure scenarios
4. Maintainability — unnecessary complexity, unclear naming

## Project-Specific Rules
{PROJECT_SPECIFIC_RULES}

## Output Format
Generate a code review report with:
1. Summary table (Correctness/Safety/Reliability/Maintainability/Test Coverage × Pass/Warn/Fail)
2. Issues detail grouped by severity (Critical/High → Medium → Low)
   - Each issue: File:Line, Category, Issue description, Concrete fix suggestion
3. Self-review checklist with evidence
4. TECH-DEBT candidates if any

Read each file fully. Understand what the code does, then analyze.
Do NOT just pattern-match — reason about the code's behavior.
""")
```

After receiving the agent's report:
- If 🔴 Critical/High issues found, fix before proceeding or document in TECH-DEBT
- If ⚠️ Medium severity issues found, propose as improvement items:
  ```
  ### Code Review Improvement Suggestions

  The following issues were found during code review.
  Would you like to address them now or add to the development plan?

  | # | Severity | Issue | Suggested Action |
  |---|----------|-------|------------------|
  | 1 | ⚠️ Medium | [issue description] | [concrete fix suggestion] |
  | 2 | ⚠️ Medium | [issue description] | [concrete fix suggestion] |

  Options:
  - fix: Address now before proceeding
  - plan: Add as sub-task to development plan
  - skip: Acknowledge and continue
  ```
  - **fix**: Implement the fix immediately, re-run tests, update the code review results
  - **plan**: Add a new sub-task to `development-plan.md` under the current phase with the improvement description
  - **skip**: Document in session log as "Acknowledged, not addressed" with rationale

**5.2 Create Session Log** (`docs/sessions/YYYY-MM-DD-<phase>-<task>.md`):

```markdown
# Session Log: YYYY-MM-DD - Phase N.M - [Task Title]

## Overview
- **Date**: YYYY-MM-DD
- **Phase**: N - [Phase Name]
- **Sub-task**: N.M - [Sub-task Name]

## Work Summary
[Brief description of completed work]

## Files Changed
- Created: [List]
- Modified: [List]

## Key Decisions
| Decision | Rationale |
|----------|-----------|
| [What] | [Why] |

## Code Review Results
| Category | Status |
|----------|--------|
| Error Handling | ✅/⚠️/🔴 |
| Resource Management | ✅/⚠️/🔴 |
| Security | ✅/⚠️/🔴 |
| Type Safety | ✅/⚠️/🔴 |
| Tests | ✅/⚠️/🔴 |

## Potential Risks
- [Identified risks]

## TECH-DEBT Items
- [New items to track, if any]
```

**5.3 Update TECH-DEBT.md** (if applicable):
- Add new debt items discovered during implementation
- Add unfixed issues from code review
- Mark resolved debt items

**5.4 Create ADR** (if significant architectural decision was made):

ADR-worthy decisions:
- Affects system architecture or component boundaries
- Chooses between multiple valid approaches
- Has long-term implications worth documenting

If ADR needed:
1. Find highest existing number in `docs/adr/`
2. Create `docs/adr/NNNN-<short-title>.md` using ADR template
3. Reference ADR in session log


### Step 6: Update Development Plan

After documentation:

1. **Update Checkboxes**:
   - Mark completed items with `[x]`
   - When all items in a sub-task are complete, consider sub-task header complete

2. **Update Status** (Unit Overview table or Current Status table):
   - `✅ Complete` - All related sub-tasks complete
   - `🔄 In Progress` - Some sub-tasks complete
   - `❌ Not Started` - No sub-tasks started

3. **Suggest Additions** (if applicable):
   - If additional needs discovered during implementation, suggest new sub-task
   - Format: "Suggested addition to Unit {name} / Phase X: [description]"

4. **Unit/Phase Completion Auto-Actions** (if all sub-tasks in a Unit or Phase just completed):
   - Detect: All sub-tasks in current Unit/Phase are now `[x]`
   - Prompt user for cross-check:
     ```
     🎉 Unit "{unit-name}" / Phase [N] Complete!

     All sub-tasks are now complete.
     Run cross-check against specs now? (yes/no/later)
     ```
   - **yes**: Execute `/cross-check` for the completed unit/phase:
     - Verify implementation vs specs and AIDLC design artifacts
     - Generate compliance matrix
     - Create `docs/cross-checks/{unit-name or phase-N}-[name].md`
     - Report any gaps found:
       ```
       Cross-Check Results:
       - ✅ Complete: X requirements
       - ⚠️ Partial: Y requirements
       - ❌ Gap: Z requirements

       [If gaps] Add gap items to next phase? (yes/no)
       ```
   - **no**: Skip cross-check, proceed to summary
   - **later**: Skip for now, but flag in Step 0 health check on next invocation

### Step 7: Summary Report

Provide completion summary:

```
## Development Complete

**Sub-task**: [Sub-task number and title]
**Status**: Complete

### Changes Made:
- Created: [List of new files]
- Modified: [List of modified files]

### Tests:
- Added: [count] new tests
- All tests passing: Yes/No

### Documentation:
- Session Log: [filename]
- TECH-DEBT: [Added/resolved items, if any]

### Feedback Loop Actions:
- TECH-DEBT: [Added/resolved items]
- Cross-Check: [Generated on Phase completion / Not needed]

### Phase Completion: (if applicable)
- Phase [N] complete: Yes/No
- Cross-check generated: [filename]
- Compliance rate: [X]% complete
- Gaps added to next Phase: [count]

### Development Plan Updated:
- [List of checkbox changes]
- Current status: [Component] → [New status]

### Next Sub-task Preview:
[Brief description of next incomplete sub-task, if any]
```

---

## Guidelines

### Commit Policy

**No Auto-Commit**: Do not automatically commit changes. Always show changes to the user and get explicit approval before committing.

### Sub-task Selection Rules

1. **One sub-task per execution** - Don't develop multiple sub-tasks in a single run
2. **Skip deferred items** - Items marked "deferred" or "— *deferred to Phase X*" are not development targets
3. **Partial completion** - For sub-tasks with some completed items, only develop remaining incomplete items
4. **Sequential order** - Always process Phases and sub-tasks in document order (top to bottom)

### Development Standards

1. **Requirements Compliance**:
   - All implementations must match `docs/requirements.md`
   - Reference requirement IDs in code comments (e.g., FR-001, NFR-001)

2. **Language Best Practices**:
   - Follow language-specific style guides
   - Use type annotations where applicable
   - Error handling with context
   - Comprehensive testing

3. **Test Requirements**:
   - Unit tests required for all new functions/methods
   - Test both success and error paths
   - Use appropriate test fixtures
   - Mock external dependencies

4. **Code Structure**:
   - New code goes in appropriate source directory
   - Follow existing project structure patterns

### Development Plan Update Rules

1. **Checkbox Updates**:
   ```markdown
   - [x] Completed item    # Check when complete
   - [ ] Pending item      # Unchecked when incomplete
   ```

2. **Status Mapping**:
   | Condition | Status |
   |-----------|--------|
   | All sub-tasks complete | `✅ Complete` |
   | At least one sub-task complete | `🔄 In Progress` |
   | No sub-tasks started | `❌ Missing` |

3. **Adding New Sub-tasks**:
   - Suggest only, don't add without user approval
   - Format suggestions clearly with rationale

---

## Error Handling

- **No incomplete sub-tasks**: Report "All sub-tasks in development plan are complete!"
- **Test failures**: Don't mark sub-task as complete; report failures and suggest fixes
- **Build errors**: Fix before proceeding; don't update development plan until resolved

---

## Example Invocations

Develop next pending task:
```
/dev-{project}
```

Work on specific Phase:
```
/dev-{project} phase2
```

Work on specific sub-task:
```
/dev-{project} 2.1
```
