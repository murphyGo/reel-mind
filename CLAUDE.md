# Reel-Mind

## Overview
24/7 autonomous AI pipeline that runs a portfolio of faceless, single-subject short-form video channels. Orchestrated by Claude, deployed via GitHub Actions. MVP: one Korean-language YouTube Shorts channel, asset-assembly only, approval-gated.

Architecture: three independent pipelines (A Style Study / B Content Production / C Measure & Learn) communicating only through Supabase + R2, plus a Next.js Web UI and a Telegram bot on top of the shared state.

---

## Important: Before Development

Run `/dev-reel-mind` to:
1. See current construction stage and unit progress
2. Get the next task to work on (from AIDLC per-stage plan files)
3. Follow the AIDLC Construction workflow

---

## Quick Commands

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `/dev-reel-mind` | AIDLC Construction executor | Start here for any development work |
| `/scaffold` | Generate project directory structure | After init, before first code |
| `/code-review git` | Review code changes | Before committing |
| `/tech-debt` | Manage technical debt | Track and prioritize issues |
| `/cross-check` | Verify requirements | After completing a unit |

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `aidlc-docs/aidlc-state.md` | **Start here** — AIDLC state and construction progress |
| `aidlc-docs/inception/plans/execution-plan.md` | Which construction stages apply per unit |
| `aidlc-docs/inception/application-design/` | Components, methods, services, dependencies |
| `docs/requirements.md` | Functional + Non-Functional requirements (source of truth) |
| `docs/DESIGN.md` | Architecture summary derived from AIDLC application design |
| `docs/TECH-DEBT.md` | Technical debt registry |
| `docs/sessions/` | Per-step session logs |
| `docs/adr/` | Architecture Decision Records |

---

## Units of Work

| # | Unit | MVP | Status |
|---|------|-----|--------|
| U1 | Shared Foundation | ✅ | Pending |
| U2 | Adapter Framework | ✅ | Pending |
| U3 | Pipeline A — Style Study | v1 | Pending |
| U4 | Pipeline B — Content Production | ✅ | Pending |
| U5 | Pipeline C — Measure & Learn | v1 | Pending |
| U6 | Telegram Bot | ✅ | Pending |
| U7 | Web UI | ✅ (subset) | Pending |
| U8 | Orchestration | ✅ | Pending |

MVP critical path: U1 → U2 → U4 → U6 → U7 → U8.

---

## Development Workflow

```
1. /dev-reel-mind       → Get next AIDLC construction step
2. Implement            → Follow the plan, meet acceptance criteria
3. /code-review git     → Review before committing
4. Commit               → Save your work
5. /dev-reel-mind       → Mark complete, get next step
```

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Pipelines | Python 3.12, Claude Agent SDK, ffmpeg, moviepy |
| State / Metadata | Supabase (Postgres + Auth + Realtime) |
| Artifacts | Cloudflare R2 |
| Web UI | Next.js 15 (App Router), Tailwind, shadcn/ui, Vercel |
| Approval / Alerts | Telegram bot |
| Runtime | GitHub Actions (cron + matrix per channel) |
| Models | Claude Opus 4.6 (creative), Claude Haiku 4.5 (mechanical) |
| Language / Timezone (MVP) | Korean (`ko`) / Asia/Seoul (KST) |

---

## Invariants / Guardrails

- **Pipelines write-only to Supabase**; Web UI reads + writes config/approval. No HTTP API between them.
- **Secrets only in GHA encrypted secrets**; accessed via `SecretsProvider.get(channel_id, key)`. Never in DB or repo.
- **Publishing is idempotent** via `IdempotencyGuard` (deterministic `run_id` from channel + pipeline + slot).
- **Every paid API call** writes a `cost_ledger` entry attributed to `(channel_id, pipeline, run_id)`.
- **Adapter retries live inside the adapter** (exp backoff, jitter, max 3); pipelines see terminal outcomes only.
- **StyleProfile rows are immutable** — new versions only.
- **Monthly generative-video cap: $20/channel** (hard). Pre-flight estimate falls back to asset-assembly when cap would be exceeded.
- **Security Baseline + PBT (full) extensions enabled** — blocking constraints.

---

## Code Style

- Python: type-annotated, `ruff` + `mypy` clean.
- TypeScript: strict mode, ESLint + Prettier.
- Requirements traceability: reference FR/NFR IDs in code comments where non-obvious.
- Application code in workspace root; AIDLC docs only under `aidlc-docs/`.
