# U2 Adapter Framework — Business Rules

**Unit**: U2 Adapter Framework
**Stage**: Functional Design
**Created**: 2026-05-10

These rules define the adapter framework invariants. Violations are defects unless explicitly superseded by later AIDLC artifacts or an ADR.

---

## BR-1 · Configured adapters must resolve at startup

Every adapter name referenced by `ChannelConfig.adapters` must exist in `AdapterRegistry` before the pipeline begins provider work.

Failure mode:
- Missing adapter raises `AdapterNotFound`.
- The run fails before any external paid call.

---

## BR-2 · Source adapters are ordered lists; other kinds are singletons

- `source`: ordered list; pipeline may call several source adapters.
- `tts`: exactly one.
- `stock_media`: exactly one.
- `generative_video`: exactly one when enabled.
- `publish`: exactly one per platform.

Fallback between non-source providers is not implicit in U2. If fallback is needed, downstream pipeline logic must make it explicit.

---

## BR-3 · Adapters receive dependencies by context

Adapters must receive `AdapterContext` and must not:

- read secret-shaped environment variables directly,
- instantiate their own U1 global clients,
- bypass `CostLedger`,
- create unbound loggers without channel/run context where available.

---

## BR-4 · Paid calls record cost inside adapter wrappers

Any adapter operation that can charge money must record actual cost through U1 `CostLedger` before returning success.

If the provider call succeeds but cost recording fails, the adapter operation fails. Silent ledger drift is forbidden.

---

## BR-5 · Retry logic lives inside adapters

Pipelines call adapters and receive terminal outcomes. They do not implement provider-specific retry loops.

Adapters use U1 `RetryExecutor` through U2 retry policy wrappers.

---

## BR-6 · Provider errors use U1 retryable/terminal semantics

Provider-specific errors must subclass:

- U1 `RetryableError` for transient errors.
- U1 `TerminalError` for permanent errors.

Raw provider SDK errors must not escape adapter boundaries.

---

## BR-7 · Secrets are resolved through U1 only

Adapter factories may request logical secret keys from `SecretsProvider`. They may not read `os.environ` directly.

Missing secret behavior:
- U1 `SecretError` propagates.
- Adapter initialization fails.
- The run fails before provider calls.

---

## BR-8 · Adapters normalize outputs before returning

Adapters must return U2 domain entities, not raw provider SDK objects.

Examples:

- Source providers return `TrendCandidate`.
- TTS providers return `AudioRef`.
- Stock providers return `MediaRef`.
- Publishers return `PublishedRef` and `MetricsSnapshot`.

---

## BR-9 · Licensing metadata is mandatory for stock media

`StockMediaAdapter.search` must include license and attribution fields on every `MediaRef`.

If a provider result lacks license clarity, the adapter must drop it or raise a terminal error. Copyright-unsafe media must not enter U4.

---

## BR-10 · Publishing requires AI disclosure support

`PublishAdapter.upload` must accept an `ai_disclosure` flag and map it to provider-specific upload metadata where supported.

If a provider cannot support required disclosure semantics, the adapter must fail terminally.

---

## BR-11 · Metrics fetching belongs to publish adapters

`PublishAdapter` includes `fetch_metrics` so U5 can reuse platform auth and platform ID handling from the publisher.

U5 owns metrics interpretation; U2 only defines the adapter output contract.

---

## BR-12 · Reference mocks are deterministic

Mock adapters must:

- return stable IDs for identical inputs,
- support success, retryable-error, and terminal-error modes,
- avoid external network calls,
- avoid real secret reads unless explicitly testing secret paths.

---

## BR-13 · Registry registration is deterministic

Duplicate `(kind, name)` registrations are rejected. Registration order must not change resolution behavior for singleton kinds.

---

## BR-14 · Adapter names are config contracts

Adapter names are stable operator-facing config values. Renaming an adapter requires either:

- backward-compatible aliasing, or
- a documented config migration.

---

## Validation Matrix

| Surface | Rule | Failure |
|---------|------|---------|
| Adapter name | Lowercase slug | `AdapterConfigError` |
| Registry lookup | `(kind, name)` exists | `AdapterNotFound` |
| Duplicate registration | Not allowed | `DuplicateAdapter` |
| Paid operation | Cost recorded on success | Operation fails if ledger fails |
| Provider exception | Normalized to U1 retryable/terminal | Adapter boundary violation |
| Stock media | License/attribution present | Drop result or terminal error |
| Publish metadata | AI disclosure flag present | Validation error |

---

## Extension Compliance

### Security Baseline

- Secrets only through U1 `SecretsProvider`.
- Adapter outputs are validated before pipelines consume them.
- Provider SDK errors are normalized before crossing boundaries.
- Publish adapters must support ToS/AI-disclosure metadata.

### Property-Based Testing

Candidate PBT targets for U2 Build and Test:

- Registry lookup is deterministic for any registration order without duplicates.
- Duplicate registrations always fail.
- Mock adapter outputs are stable for identical inputs.
- Adapter name validation accepts only the documented slug domain.
