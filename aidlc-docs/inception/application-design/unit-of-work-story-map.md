# Unit ↔ Requirement Map

User Stories were skipped for this project (single-operator internal tool). This map therefore links **units** to **Functional Requirements** and **NFRs** from `docs/requirements.md`.

## FR coverage

| FR | Title | Primary Unit | Supporting Units |
|----|-------|--------------|------------------|
| FR-001 | Style Study Pipeline (A) | U3 | U1 (storage), U2 (source adapter), U8 (scheduling) |
| FR-002 | Trend Scout | U4 | U2 (source adapters), U1 (logging) |
| FR-003 | Video Planning | U4 | U1 (style profile read) |
| FR-004 | Hybrid Video Generation | U4 | U2 (tts, stock, generative adapters) |
| FR-005 | Approval Gate | U4 | U6 (Telegram surface), U7 (Web UI surface) |
| FR-006 | Multi-Platform Publishing | U4 | U2 (publish adapter), U8 (schedule) |
| FR-007 | Measure & Learn Pipeline (C) | U5 | U1, U2, U8 |
| FR-008 | Multi-Channel Orchestration | U8 | U1 (channels table), U4/U3/U5 (channel-scoped runs) |
| FR-009 | Pluggable Adapter System | U2 | U1 (registry storage, config) |
| FR-010 | Web Dashboard | U7 | U1 (shared state) |
| FR-011 | Telegram Alert/Approval Bot | U6 | U1, U4 |
| FR-012 | Per-Channel Configuration | U1 (schema) + U7 (editor UI) | — |
| FR-013 | Budget Governance | U4 (`BudgetGovernor`) + U1 (`CostLedger`) | U2 (cost reporting in adapters) |
| FR-014 | Warmup & Posting Cadence | U4 (`PostingSchedulerGuard`) | U1 (config) |

## NFR coverage

| NFR | Title | Primary Unit(s) | Notes |
|-----|-------|-----------------|-------|
| NFR-001 | Availability 24/7/365 | U8 | Cron + matrix design, resumability via `IdempotencyGuard` (U1) |
| NFR-002 | Security | U1 (`SecretsProvider`, RLS), U2 (adapter auth), U6 (operator whitelist), U7 (auth) | Security Baseline extension blocking |
| NFR-003 | Observability | U1 (`RunRecorder`), U6 (alerts), U7 (dashboards) | Stale-channel detection in U7 |
| NFR-004 | Cost Governance | U1 (`CostLedger`), U4 (`BudgetGovernor`) | |
| NFR-005 | Reproducibility | U1 (`IdempotencyGuard`), U3 (immutable StyleProfile), U4 (`plan_hash`) | |
| NFR-006 | Extensibility | U2 (adapter interfaces) | |
| NFR-007 | Platform ToS Compliance | U4 (`PostingSchedulerGuard`, AI-disclosure flag in adapter call), U2 (publish adapter) | |
| NFR-008 | Testing | All units; PBT extension applies primarily to U1, U4, U5 | |
| NFR-009 | Runtime Constraints | U8 (`HeavyRenderDispatcher` stub) | Offload when projected render > threshold |

## MVP FR subset (walking skeleton)

FRs required to declare MVP publishable:
- FR-002 (single trend source adapter)
- FR-003 (plan uses bootstrap style profile)
- FR-004 (asset-assembly only)
- FR-005 (approval required mode)
- FR-006 (YouTube Shorts only)
- FR-008 (single channel)
- FR-009 (one impl per adapter kind, interfaces complete)
- FR-010 (Channels overview + Approval queue only)
- FR-011 (alerts + approval push)
- FR-012 (config schema + editor)
- FR-013 ($20 cap enforced at 0 generative spend — i.e., guard exists but unused in MVP)
- FR-014 (warmup phase enforced)

Deferred to post-MVP v1:
- FR-001 (automated style study) — bootstrap profile used until U3 lands
- FR-007 (measure & learn) — manual metric review until U5 lands
- FR-004 generative path — stub until v1.5
