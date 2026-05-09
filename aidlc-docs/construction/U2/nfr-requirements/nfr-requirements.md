# U2 Adapter Framework — NFR Requirements

**Unit**: U2 Adapter Framework
**Stage**: NFR Requirements
**Created**: 2026-05-10
**Source plan**: `aidlc-docs/construction/plans/U2-nfr-requirements-plan.md`

U2 is an internal Python library layer. It has no network listener and no persistence of its own; its NFRs focus on deterministic adapter resolution, security at provider boundaries, cost-ledger correctness, testability, and maintainable interface contracts.

---

## NFR Index

| Category | IDs |
|----------|-----|
| Scalability | NFR-UNIT-U2-001..002 |
| Performance | NFR-UNIT-U2-010..011 |
| Availability | NFR-UNIT-U2-020..021 |
| Security | NFR-UNIT-U2-030..035 |
| Reliability | NFR-UNIT-U2-050..054 |
| Maintainability | NFR-UNIT-U2-070..073 |
| Testing / PBT | NFR-UNIT-U2-090..093 |

---

## Scalability

### NFR-UNIT-U2-001 — Adapter construction capacity

U2 must support construction of up to 20 adapter instances in a single pipeline process without architectural redesign.

Acceptance:
- Registry validation and adapter construction complete without shared mutable state conflicts.
- No adapter singleton may retain channel-specific state globally.

### NFR-UNIT-U2-002 — Multi-channel process isolation

Adapter instances are scoped to a channel config/runtime context. No channel-specific secret, logger binding, or cost attribution may leak across adapter instances.

---

## Performance

### NFR-UNIT-U2-010 — Registry lookup p95 ≤ 5 ms

Adapter lookup is in-memory and must complete with p95 ≤ 5 ms under the 20-instance target.

### NFR-UNIT-U2-011 — Mock adapter calls p95 ≤ 10 ms

Reference mock adapters must return deterministic responses with p95 ≤ 10 ms for unit tests. Mocks must not perform network or disk I/O.

---

## Availability

### NFR-UNIT-U2-020 — Independent source adapter degradation

Source adapters are independently degradable. If one source adapter fails terminally, Pipeline B may continue with candidates from other configured source adapters.

Constraint:
- The failure must be logged and represented in stage output.
- If all source adapters fail or return no usable candidates, Pipeline B may skip the slot.

### NFR-UNIT-U2-021 — Non-source adapter failures are terminal for current stage

TTS, stock, generative-video, and publish adapter terminal failures fail the current pipeline stage. Fallback is not implicit in U2.

---

## Security

### NFR-UNIT-U2-030 — No direct secret environment reads

Adapter modules must not read secret-shaped environment variables directly. All secret access goes through U1 `SecretsProvider`.

Verification:
- CI/static grep or Ruff-compatible guard rejects direct `os.environ`/`os.getenv` secret reads outside U1.

### NFR-UNIT-U2-031 — Provider SDK errors are normalized

Raw provider SDK exceptions must not cross adapter boundaries. Adapters normalize to U1 `RetryableError` or `TerminalError` subclasses.

### NFR-UNIT-U2-032 — No secret values in adapter errors/logs

Adapter errors may include logical provider names and env-var names, but never secret values, OAuth tokens, API keys, request authorization headers, or refresh tokens.

### NFR-UNIT-U2-033 — Stock media licensing metadata required

Every `MediaRef` returned by a stock-media adapter must include license and attribution metadata. Ambiguous-license results are dropped or fail terminally.

### NFR-UNIT-U2-034 — Publish AI disclosure support

Publish adapters must accept and map an AI disclosure flag. Providers unable to satisfy required disclosure semantics must fail terminally.

### NFR-UNIT-U2-035 — Adapter input validation

Adapter public methods must validate domain inputs before provider calls. Invalid scene specs, text, media queries, or publish metadata must fail terminally before external API access.

---

## Reliability

### NFR-UNIT-U2-050 — Default adapter retry budget

Adapter retry defaults follow U1 `STORAGE_DEFAULT`: 3 attempts with short exponential backoff and jitter.

### NFR-UNIT-U2-051 — Retry ownership

Provider-specific retry loops live inside adapter wrappers. Pipelines see terminal outcomes and do not implement provider-specific retry logic.

### NFR-UNIT-U2-052 — Cost-ledger integrity on paid calls

Paid adapter calls must record actual cost through U1 `CostLedger` before returning success. If ledger recording fails, the adapter call fails.

### NFR-UNIT-U2-053 — Registry duplicate protection

Duplicate `(kind, name)` registrations fail deterministically. Registration order must not affect singleton adapter resolution.

### NFR-UNIT-U2-054 — Deterministic reference mocks

Reference mocks return stable IDs and stable payloads for identical inputs and configured mode.

---

## Maintainability

### NFR-UNIT-U2-070 — Interfaces use Python `Protocol`

Adapter contracts use `Protocol`s for structural typing. Concrete adapters do not need to inherit a shared base class.

### NFR-UNIT-U2-071 — Strict typing

U2 source must pass `mypy --strict` with the rest of the project.

### NFR-UNIT-U2-072 — Lint compatibility

U2 source must pass the project Ruff configuration.

### NFR-UNIT-U2-073 — Adapter names are stable config contracts

Renaming a config-facing adapter name requires aliasing or config migration documentation.

---

## Testing / PBT

### NFR-UNIT-U2-090 — Unit test coverage

U2 must include unit tests for:

- adapter name validation,
- registry registration and lookup,
- duplicate handling,
- missing adapter handling,
- mock adapter success/retryable/terminal behavior.

### NFR-UNIT-U2-091 — PBT for registry determinism

Property tests must verify registry lookup determinism for valid unique registration sets.

### NFR-UNIT-U2-092 — PBT for adapter name domain

Property tests must verify accepted and rejected adapter-name strings against the documented slug domain.

### NFR-UNIT-U2-093 — No live provider tests in U2

U2 does not require live provider contract tests. Real provider integration tests belong with concrete adapter implementations in downstream units.
