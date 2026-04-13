# U1 Shared Foundation — NFR Design Plan

**Unit**: U1 Shared Foundation
**Stage**: NFR Design
**Created**: 2026-04-14
**AIDLC rule**: `construction/nfr-design.md`
**Inputs**: `aidlc-docs/construction/U1/nfr-requirements/` (41 NFRs + 16 tech-stack decisions)

## Scope Recap

NFR Design translates the **what** from NFR Requirements into the **how** as patterns + logical components. For U1 (a library), this means:
- Concrete retry/backoff state machines (NFR-050/052)
- Structlog processor pipeline incl. redaction (NFR-032/060–063)
- Error-class hierarchy contract for U2/U4/U6 consumers (NFR-053)
- Cost-aggregation pattern: live SUM vs. summary table (NFR-011)
- R2 multipart upload thresholds (NFR-012)
- Concurrency model — per-invocation client construction (NFR-003)
- PBT property catalog mapping (NFR-091/092/093)

Most NFR knobs are already pinned. Open questions below target the few remaining design choices.

## Planning Checklist

- [x] **P1** Answer questions below
- [x] **P2** Write `aidlc-docs/construction/U1/nfr-design/nfr-design-patterns.md` covering: retry/backoff, redaction processor pipeline, error taxonomy, cost-aggregation pattern, idempotency derivation, structured-log processor chain, validation patterns, secret-resolution gateway pattern
- [x] **P3** Write `aidlc-docs/construction/U1/nfr-design/logical-components.md` enumerating internal sub-components of U1 (`SupabaseClient`, `R2Client`, `SecretsProvider`, `ConfigLoader`, `Logger`, `CostLedger`, `RunRecorder`, `IdempotencyGuard`, `RedactionProcessor`, `RetryExecutor`) with their interfaces, dependencies, and the NFRs each one realizes
- [ ] **P4** Present completion (2-option workflow)

---

## Open Questions

Please fill in `[Answer]:`. Questions are intentionally narrow — most NFR decisions are already locked.

### Q1 — Cost-aggregation pattern (NFR-UNIT-U1-011, p95 ≤ 200ms)

**Q1.1** For `CostLedger.month_spend_all_providers(channel_id)`, choose the pattern:
- **(a) Live SUM**: `SELECT SUM(usd_cost) FROM cost_ledger WHERE channel_id=? AND month=?`. Add an index on `(channel_id, month_bucket)`. Simple, correct, but may breach 200ms once row counts grow (~10K+ entries/channel).
- **(b) Materialized view + scheduled refresh**: `cost_summary_monthly` MV refreshed every N minutes. Fast reads, but stale by up to N minutes — risk of overshooting $20 cap during refresh window.
- **(c) Trigger-maintained roll-up table**: `cost_summary_monthly` row updated by AFTER INSERT trigger on `cost_ledger`. Always-current, fast reads, +1 write per ledger insert.

[Answer]: We go to A

**Q1.2** Acceptable budget-cap overshoot tolerance: zero (option c required) or "up to one in-flight call past cap" (any option works since BudgetGovernor pre-flights)?

[Answer]: Up to one in-flight call past cap is acceptable, given that BudgetGovernor pre-flights and the $20/channel/month cap is a soft limit for MVP.

### Q2 — R2 upload pattern (NFR-UNIT-U1-012)

**Q2.1** For `R2Client.put`, use boto3's auto-multipart with default 8 MiB part size, or set a custom threshold (e.g. 16 MiB to reduce overhead for typical 10–30 MB shorts)?

[Answer]: Set a custom threshold of 16 MiB to reduce overhead for typical 10–30 MB shorts, while still benefiting from multipart uploads for larger files.

**Q2.2** Should `R2Client.put` compute and verify a content hash (MD5/SHA256) for upload integrity, or rely on R2's own ETag and S3 checksum?

[Answer]: Rely on R2's own ETag and S3 checksum for upload integrity, as it simplifies the implementation and leverages the storage provider's built-in mechanisms.

### Q3 — Retry-classification taxonomy (NFR-UNIT-U1-050/051)

**Q3.1** For Supabase errors, classification is straightforward: 5xx + network → retry; 4xx (except 408/429) → terminal. Do you want **429 (rate limit)** to use the standard backoff (200/600/1200ms), or honor `Retry-After` header if present (capped at 10s)?

[Answer]: Honor the `Retry-After` header if present (capped at 10s) for 429 errors, as it allows for more efficient retry behavior in response to rate limits.

**Q3.2** For `CostLedger.record` extended retry (5 attempts, up to 10s last delay): if a non-retryable error occurs (e.g. unique-violation 23505, RLS denial), should it short-circuit immediately (skip remaining attempts) or run the full budget? Short-circuit is standard.

[Answer]: Short-circuit immediately on non-retryable errors to avoid unnecessary attempts and reduce latency in failure cases.

### Q4 — Logger / redaction processor chain (NFR-UNIT-U1-032, 060–063)

**Q4.1** Redaction is recursive across nested dicts in `fields` and `error.cause_chain`. Should it also redact values inside **lists** (e.g. `headers: ["Authorization: Bearer abc"]` — string-pattern match) or only dict-key matches?

[Answer]: Redact values inside lists as well, using string-pattern matching, to ensure that secrets are not leaked in any part of the log structure.

**Q4.2** When a deny-listed key appears, replace value with literal `"***"` (no length info), or `"***(len=N)"` (preserves length for debugging non-secret false-positives like an `email` field)?

[Answer]: Replace the value with `"***(len=N)"` to preserve length information, which can be helpful for debugging non-secret false positives while still masking the actual content.

**Q4.3** structlog processor order — confirm the chain:
`merge_contextvars → add_log_level → TimeStamper(UTC, ISO-8601) → add_caller → bind static (service, git_sha, python_version, gha_run_id) → RedactionProcessor → JSONRenderer`. Anything missing or out of order?

[Answer]: The proposed processor order looks good. The `RedactionProcessor` is correctly placed after all context and static information is added, ensuring that any sensitive data introduced at any stage will be redacted before rendering.

### Q5 — Concurrency / client lifecycle (NFR-UNIT-U1-003, 002)

**Q5.1** Client construction model — confirm: `SupabaseClient` and `R2Client` are constructed **once per process invocation** (not per-call), passed by dependency injection to `CostLedger`, `RunRecorder`, etc. They share a single underlying `httpx`/`urllib3` connection pool. No per-channel multiplexing. OK?

[Answer]: Yes, constructing `SupabaseClient` and `R2Client` once per process invocation and sharing a single underlying connection pool is a good approach for efficiency and simplicity. This model allows for efficient reuse of connections while avoiding the complexity of per-channel multiplexing.

**Q5.2** Burst case (NFR-002, 5 parallel Pipeline A runs against one channel): in MVP, GHA matrix runs them as 5 separate processes, each with its own clients. There is **no** in-process parallelism. Confirm we do **not** need a thread-safe internal connection pool?

[Answer]: Correct, if each GHA matrix run is a separate process with its own clients, there is no in-process parallelism and therefore no need for a thread-safe internal connection pool. Each process will manage its own connections independently.

### Q6 — Error taxonomy contract (NFR-UNIT-U1-053)

**Q6.1** Should U1's exception classes carry **structured fields** (e.g. `BudgetExceeded.cap_usd`, `BudgetExceeded.attempted_usd`, `IdempotencyConflict.existing_run_id`) or just a `message` string? Structured fields make `error.fields` log emission deterministic; messages are looser.

[Answer]: Structured fields are preferable as they allow for deterministic log emission and easier programmatic access to error details. This approach enhances the ability to analyze and respond to errors effectively.

**Q6.2** For `RetryableStorageError` raised after retry exhaustion, should it preserve the **last underlying exception** as `__cause__` (Python's `raise ... from ...`), or flatten all attempt errors into a `cause_chain` list?

[Answer]: Preserving the last underlying exception as `__cause__` is more in line with Python's standard error handling and allows for better integration with existing tooling and practices. A `cause_chain` list could be useful for debugging but may add unnecessary complexity to the error structure.

### Q7 — `IdempotencyGuard.run_id_for` derivation (NFR-UNIT-U1-054)

**Q7.1** Algorithm — confirm: `run_id = sha256(f"{channel_id}|{pipeline}|{canonical_slot or 'noslot'}").hexdigest()[:24]`. 24 hex chars (96 bits) — collision-safe within problem domain. OK, or do you want the full digest / a different prefix length?

[Answer]: The proposed algorithm for `run_id` derivation is sound. Using the first 24 hex characters (96 bits) of the SHA-256 hash should provide sufficient uniqueness for the problem domain while keeping the `run_id` manageable in length. This approach balances collision safety with practicality.

**Q7.2** For pipelines without scheduled slots (Pipeline A backfill, manual ops): how do we derive `run_id`? Options:
- (a) Pass an explicit `idempotency_key` argument from the caller.
- (b) Synthesize from `timestamp` (allows duplicates) — disables idempotency for these runs.
- (c) Reject — caller must supply a slot or explicit key.

Option (a) is most flexible.

[Answer]: Option (a) is the most flexible and robust approach. It allows callers to provide a specific `idempotency_key` when there is no natural slot, ensuring that idempotency can still be maintained for backfill and manual operations. This method also avoids the risk of collisions that could arise from using timestamps.

### Q8 — PBT property mapping (NFR-UNIT-U1-091..093)

**Q8.1** Should the PBT property catalog live in `nfr-design-patterns.md` (design-time spec) or be deferred to Build & Test (test-implementation-time spec)? AIDLC convention varies; I lean toward including it here as **specifications** (what the property is), with **implementations** in Build & Test.

[Answer]: Including the PBT property catalog in `nfr-design-patterns.md` as specifications is a good approach. It allows for a clear design-time reference for what each property is and how it should behave, while leaving the implementation details to be fleshed out during the Build & Test phase. This separation of concerns helps maintain clarity and focus during each phase of development.

### Q9 — Logical-components decomposition

**Q9.1** Beyond the 8 components named in functional design (`ConfigLoader`, `SecretsProvider`, `R2Client`, `Logger`, `CostLedger`, `RunRecorder`, `IdempotencyGuard`, `SupabaseClient`), I will also extract two cross-cutting helpers:
- `RetryExecutor` — generic exponential-backoff with classification callback (used by SupabaseClient, R2Client, CostLedger.record).
- `RedactionProcessor` — structlog processor implementing NFR-032.

OK to introduce these as named components, or keep them inlined inside their callers?

[Answer]: Introducing `RetryExecutor` and `RedactionProcessor` as named components is a good idea. It promotes separation of concerns, makes the codebase more modular, and allows for easier testing and maintenance of these cross-cutting functionalities. This approach also enhances readability by clearly delineating the responsibilities of each component.

---

## After Questions Are Answered

I will generate:
- `aidlc-docs/construction/U1/nfr-design/nfr-design-patterns.md`
- `aidlc-docs/construction/U1/nfr-design/logical-components.md`

Then present the 2-option completion (Request Changes / Continue to Infrastructure Design).
