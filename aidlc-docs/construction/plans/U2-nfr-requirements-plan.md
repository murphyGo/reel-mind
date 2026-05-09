# U2 Adapter Framework — NFR Requirements Plan

**Unit**: U2 Adapter Framework
**Stage**: NFR Requirements
**Created**: 2026-05-10
**AIDLC rule**: `construction/nfr-requirements.md`
**Inputs**: `aidlc-docs/construction/U2/functional-design/`

## Scope Recap

U2 is an internal Python adapter framework, not a network service. NFR focus:

- Adapter resolution must be deterministic and fail fast.
- Adapter boundaries must protect secrets and normalize provider errors.
- Paid adapter calls must preserve cost-ledger integrity.
- Reference mocks must support deterministic tests for downstream units.
- Interfaces must remain easy for U3/U4/U5 to implement and test.

## Planning Checklist

- [x] **P1** Create NFR requirements plan and collect answers below
- [x] **P2** Write `aidlc-docs/construction/U2/nfr-requirements/nfr-requirements.md`
- [ ] **P3** Write `aidlc-docs/construction/U2/nfr-requirements/tech-stack-decisions.md`
- [ ] **P4** Present completion (2-option workflow)

---

## Open Questions

### Q1 — Scalability

**Q1.1** At 10 channels, how many adapter instances should the framework comfortably construct in one pipeline process?

A) Up to 20 adapter instances per process
B) Up to 100 adapter instances per process
C) Construct adapters lazily only, no startup validation
D) Other (please describe after `[Answer]:`)

[Answer]: A — up to 20 adapter instances per process.

### Q2 — Performance

**Q2.1** Adapter registry resolution should be effectively local and fast. What p95 threshold should apply?

A) 5 ms per lookup
B) 50 ms per lookup
C) 200 ms per lookup
D) Other (please describe after `[Answer]:`)

[Answer]: A — 5 ms per lookup.

### Q3 — Availability

**Q3.1** If one source adapter fails terminally, should Pipeline B still use other source adapters for that slot?

A) Yes, source adapters are independently degradable
B) No, any source adapter failure fails the scout stage
C) Only retryable failures are degradable
D) Other (please describe after `[Answer]:`)

[Answer]: A — source adapters are independently degradable.

### Q4 — Security

**Q4.1** Should U2 add a CI/static guard against direct `os.environ` secret reads in adapter modules?

A) Yes, enforce no direct secret env reads outside U1 `SecretsProvider`
B) No, rely on code review
C) Defer to U8 CI
D) Other (please describe after `[Answer]:`)

[Answer]: A — enforce no direct secret env reads outside U1 `SecretsProvider`.

### Q5 — Reliability

**Q5.1** Adapter retry policy defaults should follow which budget?

A) U1 `STORAGE_DEFAULT` style: 3 attempts with short exponential backoff and jitter
B) Longer provider retry budget: 5 attempts up to 10 seconds
C) No default; every adapter must define its own
D) Other (please describe after `[Answer]:`)

[Answer]: A — U1 `STORAGE_DEFAULT` style: 3 attempts with short exponential backoff and jitter.

### Q6 — Maintainability and typing

**Q6.1** Should adapter interfaces be Python `Protocol`s or abstract base classes?

A) `Protocol`s for structural typing
B) Abstract base classes for explicit inheritance
C) Plain duck typing with tests only
D) Other (please describe after `[Answer]:`)

[Answer]: A — `Protocol`s for structural typing.

### Q7 — Testing

**Q7.1** What is the minimum test bar for U2?

A) Unit tests for registry/interfaces/mocks plus PBT for registry determinism
B) Unit tests only
C) Live provider contract tests in U2
D) Other (please describe after `[Answer]:`)

[Answer]: A — unit tests for registry/interfaces/mocks plus PBT for registry determinism.

---

## After Questions Are Answered

I will generate:

- `aidlc-docs/construction/U2/nfr-requirements/nfr-requirements.md`
- `aidlc-docs/construction/U2/nfr-requirements/tech-stack-decisions.md`

Then I will present the 2-option completion workflow (Request Changes / Continue to NFR Design).
