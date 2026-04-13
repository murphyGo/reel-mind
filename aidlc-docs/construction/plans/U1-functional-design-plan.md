# U1 Shared Foundation — Functional Design Plan

**Unit**: U1 Shared Foundation
**Stage**: Functional Design
**Created**: 2026-04-13
**AIDLC rule**: `construction/functional-design.md`

## Scope Recap

U1 delivers the foundational library that every pipeline + the Web UI sit on top of. Technology-agnostic design focus here — no schema DDL, no boto3 calls, no concrete SDK usage. Those land in NFR Design / Infrastructure Design / Code Generation.

Components in scope:

- `ConfigLoader` — merges repo `config/defaults.yaml` with per-channel config rows into a validated `ChannelConfig`
- `SecretsProvider` — per-channel secret resolution from the environment
- `SupabaseClient` — schema-validated DB wrapper (write-only from pipelines; read+write for Web UI)
- `R2Client` — artifact storage (put / get / presigned URL)
- `Logger` — structured logger bound to `(channel_id, pipeline, run_id, stage)`
- `CostLedger` — paid-API-call accounting, monthly spend queries, remaining-budget queries
- `RunRecorder` — pipeline run + stage lifecycle
- `IdempotencyGuard` — deterministic `run_id` + "already ran" check

## Planning Checklist

- [x] **P1** Clarify open questions (section below) — block until answered
- [x] **P2** Define domain entities in `domain-entities.md`
- [x] **P3** Specify business logic / algorithms in `business-logic-model.md`
- [x] **P4** Enumerate business rules + invariants in `business-rules.md`
- [x] **P5** Error taxonomy captured in `domain-entities.md` §9 + `business-rules.md` BR-15
- [x] **P6** Present completion (Review Required + 2-option workflow)

---

## Open Questions

Please fill in `[Answer]:` tags. When in doubt, say so — I will add follow-up questions rather than assume.

### Q1 — Config precedence and override surface

Config resolution for `ChannelConfig` has three potential sources: repo `config/defaults.yaml`, per-channel `channels` row in Supabase, and runtime overrides (e.g. a CLI flag or env var during one-off reruns).

**Q1.1** Should runtime overrides exist at all in MVP, or is the merged `defaults.yaml + channels row` the whole story?

[Answer]: defaults.yaml + channels row

**Q1.2** For fields present in both `defaults.yaml` and a channel row — does the channel row always win, or are there fields where defaults are "locked" (operator cannot override)? If locked fields exist, list them.

[Answer]: channel row always win

### Q2 — Secret naming convention

Application Design hints at `{KIND}_{PROVIDER}_CHANNEL_{id}` (e.g. `YT_REFRESH_TOKEN_CHANNEL_1`). A few edge cases:

**Q2.1** Is `channel_id` a numeric int (`1`, `2`, ...) or a slug (`ko-shorts-tech`)? Env var names historically prefer `[A-Z0-9_]`.

[Answer]: slug

**Q2.2** For shared (non-per-channel) secrets like `SUPABASE_SERVICE_KEY` or `R2_ACCESS_KEY`, should `SecretsProvider.get(channel_id, key)` accept a `channel_id=None` / "global" scope, or should those be accessed via a separate method / separate class?

[Answer]: "global" scope

**Q2.3** `get_with_refresh` is declared for OAuth tokens. Who owns the refreshed value — does `SecretsProvider` persist the refreshed token somewhere (not DB per invariants), or is the refresh ephemeral per-process and the GHA secret is updated out-of-band?

[Answer]: Secrets only in GHA encrypted secrets, I will update it manually.

### Q3 — Cost ledger: month boundary + attribution

**Q3.1** The $20/channel monthly cap is stated. What timezone defines "month"? `Asia/Seoul` (KST) makes sense given the MVP channel locale, but UTC is simpler for SQL. Pick one.

[Answer]: UTC

**Q3.2** Are there cost buckets besides `generative_video` (e.g. TTS, stock media, Claude API calls)? If yes, is the $20 cap **per provider**, **per bucket**, or **aggregate**?

[Answer]: $20 cap Aggregate

**Q3.3** When a paid call happens outside a pipeline run (e.g. a cron health check or manual CLI), what does the ledger entry look like? Null `run_id`? A synthetic `run_id="manual-<ts>"`? Reject / disallow?

[Answer]: synthetic

### Q4 — Idempotency guard: hash inputs

`IdempotencyGuard.run_id_for(channel_id, pipeline, scheduled_slot)` must produce the same `run_id` for the same slot so retries don't double-publish.

**Q4.1** What is `scheduled_slot` — a `datetime` (which timezone? truncated to minute?), or a string like `2026-04-13T09:00+09:00`? The representation must be canonical.

[Answer]: datetime string like 2026-04-13T09:00+09:00, timezone in KST

**Q4.2** Pipeline A (Style Study) runs daily and Pipeline C (Measure) runs daily — do they also use `scheduled_slot`, or does idempotency only matter for Pipeline B (publish)? Is it OK if A/C get a new run_id on retry?

[Answer]: if A/C get a new run_id on retry

**Q4.3** If the same slot is manually retried after a terminal failure (operator intent: "try again, really"), is there a force-new-run-id escape hatch, and who is authorized to use it?

[Answer]: generate a new run id

### Q5 — Run lifecycle state machine

**Q5.1** Proposed states: `started → (stage records) → succeeded | failed | skipped | canceled`. Is `canceled` needed in MVP (e.g. approval rejected = canceled, or approval rejected = succeeded-with-outcome=rejected)?

[Answer]: approval rejected = canceled

**Q5.2** Stage-level status enum — `ok | error | skipped` sufficient, or do you want `retrying` as a first-class state visible in the Web UI timeline?

[Answer]: Yes. Add retrying

### Q6 — Logger context

**Q6.1** Required bound fields per the design are `(channel_id, pipeline, run_id, stage)`. Should `operator_id` / `trigger` (`cron` vs. `manual` vs. `retry`) also be bound? The Web UI timeline may want them.

[Answer]: Add trigger, operator_id

**Q6.2** Log sink for MVP — stdout only (captured by GHA logs + Vercel logs), or also mirrored to a Supabase `logs` table for the Web UI to query? The latter adds cost and a write-path for pipelines.

[Answer]: stdout only

### Q7 — Supabase client: RLS posture

**Q7.1** The invariant is "pipelines write-only, Web UI reads + writes config/approval". Concretely, do pipelines authenticate to Supabase with a **service-role key** (bypasses RLS) or with an **anon/JWT** that has RLS policies allowing inserts only? Service-role is simpler for MVP but widens the blast radius of a leaked secret.

[Answer]: Service-role

**Q7.2** For the Web UI, does the single operator auth mean one Supabase user row, with RLS `auth.uid() = '<fixed>'` policies? Or an allow-list approach?

[Answer]: one Supabase user row

### Q8 — R2 object layout

**Q8.1** Proposed key convention: `channels/{channel_id}/runs/{run_id}/{artifact_kind}/{filename}`. Acceptable?

[Answer]: Yes

**Q8.2** Presigned URL TTL for the Web UI approval preview — minutes or hours? (Longer = fewer regenerations but wider exposure window.)

[Answer]: 1 hour

### Q9 — Error taxonomy

**Q9.1** Do we want a shared exception hierarchy in U1 (e.g. `ReelMindError` → `RetryableError` / `TerminalError` / `ConfigError` / `BudgetExceeded`), or let each component raise provider-native errors and classify at pipeline boundaries?

[Answer]: shared exception hierarchy

### Q10 — What's out of scope for U1?

**Q10.1** Confirm that the following are NOT in U1 and will live elsewhere: schema DDL (Infrastructure Design), retry policy implementation (U2 `RetryPolicy`), approval/RLS policies specific to Web UI (U7), GHA workflow wiring (U8). Any you want pulled into U1?

[Answer]: OK

---

## After Questions Are Answered

I will generate:

- `aidlc-docs/construction/U1/functional-design/domain-entities.md`
- `aidlc-docs/construction/U1/functional-design/business-logic-model.md`
- `aidlc-docs/construction/U1/functional-design/business-rules.md`

Then present the 2-option completion (Request Changes / Continue to NFR Requirements).
