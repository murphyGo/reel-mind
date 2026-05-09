# U2 Adapter Framework — Tech Stack Decisions

**Unit**: U2 Adapter Framework
**Stage**: NFR Requirements
**Created**: 2026-05-10
**Source plan**: `aidlc-docs/construction/plans/U2-nfr-requirements-plan.md`

U2 is an internal Python adapter framework. It should reuse U1 dependencies wherever possible and avoid introducing provider SDKs until concrete adapters are implemented in downstream units.

---

## Decision Index

| ID | Concern | Decision |
|----|---------|----------|
| TS-U2-01 | Interface style | Python `typing.Protocol` |
| TS-U2-02 | Data models | Pydantic v2 models from U1 style |
| TS-U2-03 | Retry | Thin wrapper around U1 `RetryExecutor` |
| TS-U2-04 | Errors | Subclass U1 `RetryableError` / `TerminalError` |
| TS-U2-05 | Registry storage | In-memory dict keyed by `(AdapterKind, AdapterName)` |
| TS-U2-06 | Provider SDKs | Not added in U2 |
| TS-U2-07 | Mock adapters | In-repo deterministic mocks |
| TS-U2-08 | Tests | `pytest` + `hypothesis` |

---

## TS-U2-01 — Python `Protocol` Interfaces

Adapter contracts use `typing.Protocol`.

Rationale:
- Concrete adapters can satisfy contracts structurally.
- Test mocks stay lightweight.
- `mypy --strict` can validate call sites.

Alternatives:
- Abstract base classes: rejected because explicit inheritance adds little value for provider adapters.
- Duck typing only: rejected because interface drift would surface too late.

Satisfies:
- NFR-UNIT-U2-070
- NFR-UNIT-U2-071

---

## TS-U2-02 — Pydantic v2 Domain Models

U2 adapter inputs/outputs use Pydantic v2 strict models, following U1 conventions.

Rationale:
- Runtime validation at provider boundaries.
- Consistent serialization with U1 artifacts.
- Clear error reporting for malformed provider outputs.

Satisfies:
- NFR-UNIT-U2-035
- NFR-UNIT-U2-090

---

## TS-U2-03 — U1 RetryExecutor

U2 adapter retry policy is a thin wrapper around U1 `RetryExecutor`.

Rationale:
- Avoid duplicate retry engines.
- Preserve one retry/error vocabulary across foundation and adapters.
- Keeps pipelines free of provider retry logic.

Satisfies:
- NFR-UNIT-U2-050
- NFR-UNIT-U2-051

---

## TS-U2-04 — U1 Error Hierarchy

Adapter errors subclass U1 `RetryableError` or `TerminalError`.

Rationale:
- Pipelines can handle adapter failures consistently.
- Raw provider SDK exceptions stay inside adapter boundaries.
- Structured logging can consume U1 `to_log_dict()` style where applicable.

Satisfies:
- NFR-UNIT-U2-031
- NFR-UNIT-U2-032

---

## TS-U2-05 — In-Memory Registry

`AdapterRegistry` uses an in-memory dictionary keyed by `(AdapterKind, AdapterName)`.

Rationale:
- Registry lookup target is p95 ≤ 5 ms.
- Adapter specs are code-level contracts in MVP.
- Dynamic plugin loading is unnecessary for the walking skeleton.

Satisfies:
- NFR-UNIT-U2-010
- NFR-UNIT-U2-053

---

## TS-U2-06 — No Provider SDKs in U2

U2 does not add YouTube, TTS, stock-media, or generative-video provider SDK dependencies.

Rationale:
- U2 owns interfaces, registry, retry/error wrappers, and mocks.
- Concrete provider implementations belong in U4/U5 or later units.
- Keeps U2 fast and stable for downstream testing.

Satisfies:
- NFR-UNIT-U2-093

---

## TS-U2-07 — Deterministic In-Repo Mocks

Reference mock adapters live in the repo and depend only on U1/U2 domain models.

Rationale:
- Downstream units need deterministic tests without network access.
- Mock behavior must support success, retryable error, and terminal error modes.

Satisfies:
- NFR-UNIT-U2-011
- NFR-UNIT-U2-054

---

## TS-U2-08 — `pytest` + `hypothesis`

U2 uses the existing project test stack:

- `pytest` for unit tests.
- `hypothesis` for adapter-name and registry determinism properties.

Rationale:
- Matches U1 and project-level PBT extension.
- No live provider tests in U2.

Satisfies:
- NFR-UNIT-U2-090
- NFR-UNIT-U2-091
- NFR-UNIT-U2-092
