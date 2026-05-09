# U1 Shared Foundation — Infrastructure Design Plan

**Unit**: U1 Shared Foundation
**Stage**: Infrastructure Design
**Created**: 2026-05-10
**AIDLC rule**: `construction/infrastructure-design.md`
**Inputs**:
- `aidlc-docs/construction/U1/functional-design/`
- `aidlc-docs/construction/U1/nfr-requirements/`
- `aidlc-docs/construction/U1/nfr-design/`

## Scope Recap

U1 is the shared Python foundation used by pipelines, the Telegram bot, and ops scripts. It does not expose an HTTP service of its own. Infrastructure Design maps the U1 logical components to concrete infrastructure:

- Supabase schema, constraints, indexes, roles, and RLS boundaries for `channels`, `pipeline_runs`, `stage_records`, and `cost_ledger`
- Cloudflare R2 bucket and object-prefix layout for U1 artifacts
- GitHub Actions and bot-host secret layout consumed by `SecretsProvider`
- Runtime environment assumptions for GHA jobs, the Telegram bot host, and ops scripts
- Observability routing for stdout JSON logs and logs-as-metrics
- Shared-infrastructure boundaries that later units must reuse rather than redefine

## Planning Checklist

- [x] **P1** Create infrastructure design plan and collect answers below
- [x] **P2** Write `aidlc-docs/construction/U1/infrastructure-design/infrastructure-design.md` covering service mappings, Supabase schema contract, R2 bucket contract, secrets layout, runtime environment, monitoring, and security controls
- [x] **P3** Write `aidlc-docs/construction/U1/infrastructure-design/deployment-architecture.md` covering how GHA jobs, bot host, ops scripts, Supabase, and R2 interact for U1
- [x] **P4** Write or update `aidlc-docs/construction/shared-infrastructure.md` with infrastructure decisions reused by U2-U8
- [x] **P5** Present completion (2-option workflow) — approved by autonomous `/dev-reel-mind` continuation on 2026-05-10

---

## Open Questions

Please fill in `[Answer]:` tags. Questions focus only on infrastructure details that affect U1's implementation and later unit contracts.

### Q1 — Deployment environments

**Q1.1** Which named environments should U1 infrastructure support from the start?

A) `local`, `staging`, and `production`
B) `local` and `production` only
C) `production` only for MVP, with local using mocked services
D) Other (please describe after `[Answer]:`)

[Answer]: A — local, staging, and production. Local may use mocks for fast tests, but the infrastructure contract names all three environments from the start.

**Q1.2** Should `staging` use a separate Supabase project and R2 bucket, or share production infrastructure with prefixed test channel IDs?

A) Separate Supabase project and separate R2 bucket
B) Shared projects with `staging-*` channel IDs and R2 prefixes
C) No staging infrastructure for MVP
D) Other (please describe after `[Answer]:`)

[Answer]: A — separate Supabase project and separate R2 bucket. This avoids accidental production writes while testing migrations, RLS, and object paths.

### Q2 — Compute infrastructure

**Q2.1** Pipeline consumers of U1 run in GitHub Actions. Should U1 assume all pipeline jobs run on standard GitHub-hosted runners, or do you want self-hosted runners in scope?

A) GitHub-hosted runners only for MVP
B) Support both GitHub-hosted and self-hosted runners from day one
C) Self-hosted runners only
D) Other (please describe after `[Answer]:`)

[Answer]: A — GitHub-hosted runners only for MVP. Self-hosted runner assumptions are out of scope until a workload exceeds the GitHub-hosted limits.

**Q2.2** Telegram bot hosting is outside U1 code, but U1 must document secret/runtime assumptions. What bot host should the infrastructure design target?

A) Fly.io long-running worker
B) Render/Railway-style managed worker
C) A single VPS/manual host
D) Defer exact bot host to U6; U1 documents only required env vars
E) Other (please describe after `[Answer]:`)

[Answer]: D — defer exact bot host to U6. U1 documents only required env vars, process assumptions, and logging expectations.

### Q3 — Supabase storage infrastructure

**Q3.1** Should U1 create the Supabase schema as plain SQL migrations under `supabase/migrations/`, or keep schema as documentation until Code Generation?

A) Plain SQL migrations under `supabase/migrations/`
B) Documentation-only in Infrastructure Design; migration generation in Code Generation
C) Supabase dashboard/manual setup for MVP
D) Other (please describe after `[Answer]:`)

[Answer]: B — documentation-only in Infrastructure Design; migration generation in Code Generation. P2 defines the schema contract, and Code Generation creates SQL migrations.

**Q3.2** For U1 tables, should `channel_id` reference `channels.id` with foreign keys everywhere, including `cost_ledger`, `pipeline_runs`, and artifact metadata?

A) Yes, strict foreign keys everywhere
B) Foreign keys for run/config tables, but `cost_ledger` remains append-only even if channel rows change
C) No foreign keys in MVP; rely on application validation
D) Other (please describe after `[Answer]:`)

[Answer]: B — foreign keys for run/config tables, but `cost_ledger` keeps append-only accounting semantics even if channel metadata changes.

**Q3.3** For append-only tables (`cost_ledger`, run/stage history), should the infrastructure include soft-retention/archive policies now?

A) Permanent retention for MVP; no archive policy
B) Keep 24 months hot, then archive later
C) Keep 12 months hot, then archive later
D) Other (please describe after `[Answer]:`)

[Answer]: A — permanent retention for MVP; no archive policy.

### Q4 — R2 artifact storage

**Q4.1** Should U1 use one R2 bucket for all environments/channels, or separate buckets per environment?

A) Separate bucket per environment
B) One bucket with environment prefixes
C) One production bucket only for MVP
D) Other (please describe after `[Answer]:`)

[Answer]: A — separate bucket per environment.

**Q4.2** Should R2 object versioning/lifecycle rules be part of MVP infrastructure?

A) No lifecycle deletion; permanent retention for MVP
B) Delete intermediate artifacts after N days, retain published artifacts permanently
C) Enable object versioning for all artifacts
D) Other (please describe after `[Answer]:`)

[Answer]: A — no lifecycle deletion; permanent retention for MVP.

### Q5 — Messaging and async infrastructure

**Q5.1** U1 currently has no queue/buffer by design. Should Infrastructure Design explicitly prohibit queues for U1 and leave async orchestration to GHA/bot workflows?

A) Yes, no queue for U1 MVP
B) Add a lightweight queue table in Supabase for future retry/reconciliation
C) Use external queue infrastructure from day one
D) Other (please describe after `[Answer]:`)

[Answer]: A — no queue for U1 MVP. Async orchestration remains in GitHub Actions and bot workflows.

**Q5.2** If `CostLedger.record` fails after all retries, should there be any infrastructure-level reconciliation path?

A) No; fail the run and rely on operator investigation
B) Add a manual SQL reconciliation procedure documented for ops
C) Add a Supabase `pending_ledger_reconciliation` table now
D) Other (please describe after `[Answer]:`)

[Answer]: A — no infrastructure-level reconciliation path in MVP. The run fails and the operator investigates using logs and Supabase state.

### Q6 — Networking and access boundaries

**Q6.1** Should Supabase network controls such as IP allow-listing be considered in MVP infrastructure?

A) No IP allow-listing for MVP
B) Allow-list GitHub Actions and bot host egress where practical
C) Allow-list only the bot host; GHA remains unrestricted
D) Other (please describe after `[Answer]:`)

[Answer]: A — no IP allow-listing for MVP.

**Q6.2** Should R2 access be private-only with presigned URLs for previews, or should any public bucket/path exist?

A) Private-only bucket; previews use presigned URLs
B) Public read for published artifacts only
C) Public read for all non-secret media artifacts
D) Other (please describe after `[Answer]:`)

[Answer]: A — private-only bucket; previews use presigned URLs.

### Q7 — Monitoring and alerting infrastructure

**Q7.1** Where should stdout JSON logs be considered authoritative for MVP debugging?

A) GitHub Actions logs for pipelines, bot-host logs for bot, Vercel logs for Web UI
B) Mirror U1 logs into Supabase for central querying
C) Send U1 logs to an external log backend
D) Other (please describe after `[Answer]:`)

[Answer]: A — GitHub Actions logs for pipelines, bot-host logs for bot, Vercel logs for Web UI.

**Q7.2** Should Infrastructure Design include any automated alerting for U1 failures before U6 exists?

A) No; rely on failed GHA runs until U6
B) GitHub Actions email/notification only
C) Minimal Telegram webhook alert from GHA before U6
D) Other (please describe after `[Answer]:`)

[Answer]: A — no automated U1 alerting before U6; rely on failed GitHub Actions runs.

### Q8 — Shared infrastructure and ownership

**Q8.1** Should U1 own the base Supabase schema for all shared tables, while later units only add their own tables/migrations?

A) Yes, U1 owns shared tables and base conventions
B) Each later unit may revise U1 tables as needed
C) Put all schema ownership in U8 Orchestration
D) Other (please describe after `[Answer]:`)

[Answer]: A — U1 owns shared tables and base conventions.

**Q8.2** Should `shared-infrastructure.md` be created now as the canonical cross-unit infrastructure contract?

A) Yes, create it in U1 Infrastructure Design
B) Defer shared infrastructure doc to U8
C) Keep infrastructure contracts only inside each unit
D) Other (please describe after `[Answer]:`)

[Answer]: A — create it in U1 Infrastructure Design as the canonical cross-unit infrastructure contract.

---

## After Questions Are Answered

I will generate:

- `aidlc-docs/construction/U1/infrastructure-design/infrastructure-design.md`
- `aidlc-docs/construction/U1/infrastructure-design/deployment-architecture.md`
- `aidlc-docs/construction/shared-infrastructure.md` if Q8.2 chooses to create it now

Then I will present the 2-option completion workflow (Request Changes / Continue to Code Generation).
