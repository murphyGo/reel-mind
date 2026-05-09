# U2 Adapter Framework — Functional Design Plan

**Unit**: U2 Adapter Framework
**Stage**: Functional Design
**Created**: 2026-05-10
**AIDLC rule**: `construction/functional-design.md`
**Depends on**: U1 Shared Foundation

## Scope Recap

U2 defines the adapter framework consumed by U3, U4, and U5. It owns:

- `AdapterRegistry`
- Source adapter interface
- Generative-video adapter interface
- TTS adapter interface
- Stock-media adapter interface
- Publish adapter interface
- Adapter retry/error contract
- Reference mocks for tests

U2 does **not** implement real YouTube/TTS/stock/provider adapters. Concrete provider adapters land in downstream units, especially U4.

## Planning Checklist

- [x] **P1** Create functional design plan and collect answers below
- [x] **P2** Write `aidlc-docs/construction/U2/functional-design/domain-entities.md`
- [x] **P3** Write `aidlc-docs/construction/U2/functional-design/business-logic-model.md`
- [x] **P4** Write `aidlc-docs/construction/U2/functional-design/business-rules.md`
- [x] **P5** Present completion (2-option workflow) — approved by autonomous `/dev-reel-mind` continuation on 2026-05-10

---

## Open Questions

Please fill in `[Answer]:` tags. The defaults are chosen to keep MVP adapter work narrow and compatible with U1.

### Q1 — Registry behavior

**Q1.1** Should adapter lookup fail at startup when a configured adapter name is missing, or fail lazily when the pipeline first requests that adapter?

A) Fail at startup during channel config/bootstrap validation
B) Fail lazily on first adapter resolution
C) Warn and continue with a mock adapter
D) Other (please describe after `[Answer]:`)

[Answer]: A — fail at startup during channel config/bootstrap validation.

**Q1.2** Should the registry permit multiple adapters per kind in priority order, or exactly one configured adapter per kind except sources?

A) Sources are ordered lists; all other kinds resolve exactly one adapter
B) Every adapter kind supports ordered fallback lists
C) Exactly one adapter for every kind, including sources
D) Other (please describe after `[Answer]:`)

[Answer]: A — sources are ordered lists; all other kinds resolve exactly one adapter.

### Q2 — Adapter context

**Q2.1** What context should every adapter receive at construction?

A) `ChannelConfig`, `SecretsProvider`, `CostLedger`, `Logger`, and optional provider-specific settings
B) Only provider-specific settings; adapters pull U1 services globally
C) Full U1 `Runtime`
D) Other (please describe after `[Answer]:`)

[Answer]: A — `ChannelConfig`, `SecretsProvider`, `CostLedger`, `Logger`, and optional provider-specific settings.

### Q3 — Cost accounting

**Q3.1** Should paid adapters record cost inside the adapter call wrapper, or return cost metadata for the pipeline to record?

A) Adapter wrapper records cost through `CostLedger`
B) Adapter returns cost metadata; pipeline records it
C) Both adapter and pipeline record for redundancy
D) Other (please describe after `[Answer]:`)

[Answer]: A — adapter wrapper records cost through `CostLedger`.

### Q4 — Retry ownership

**Q4.1** U1 already has `RetryExecutor`. Should U2 define adapter-level retry policy as a thin domain wrapper around U1 retry, or define a separate retry engine?

A) Thin wrapper around U1 `RetryExecutor`
B) Separate retry engine owned by U2
C) No adapter retry; pipelines handle retry
D) Other (please describe after `[Answer]:`)

[Answer]: A — thin wrapper around U1 `RetryExecutor`.

### Q5 — Error contract

**Q5.1** Should provider-specific adapter errors subclass U1 `RetryableError` / `TerminalError`, or use adapter-local exceptions translated at registry boundary?

A) Provider-specific errors subclass U1 retryable/terminal base classes
B) Provider-specific errors stay local and are translated by registry
C) Adapters raise raw provider SDK errors
D) Other (please describe after `[Answer]:`)

[Answer]: A — provider-specific errors subclass U1 retryable/terminal base classes.

### Q6 — Reference mocks

**Q6.1** What behavior should reference mock adapters provide?

A) Deterministic successful responses plus configurable terminal/retryable failures
B) Successful responses only
C) Full fake external-provider simulations
D) Other (please describe after `[Answer]:`)

[Answer]: A — deterministic successful responses plus configurable terminal/retryable failures.

### Q7 — Publish adapter scope

**Q7.1** Should `PublishAdapter` include metrics-fetch methods for U5, or should metrics use a separate adapter interface?

A) `PublishAdapter` includes `fetch_metrics`
B) Separate `MetricsAdapter`
C) Defer metrics methods until U5
D) Other (please describe after `[Answer]:`)

[Answer]: A — `PublishAdapter` includes `fetch_metrics`.

---

## After Questions Are Answered

I will generate:

- `aidlc-docs/construction/U2/functional-design/domain-entities.md`
- `aidlc-docs/construction/U2/functional-design/business-logic-model.md`
- `aidlc-docs/construction/U2/functional-design/business-rules.md`

Then I will present the 2-option completion workflow (Request Changes / Continue to NFR Requirements).
