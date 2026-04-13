# Requirements Reference

## Intent Analysis
- **Request Clarity**: Clear
- **Request Type**: New Project (Greenfield)
- **Scope**: Large (multi-pipeline orchestration + Web UI + multi-adapter system)
- **Complexity**: High (24/7 autonomous operation, multi-channel concurrency, cost governance, platform ToS, feedback loops)

## Source
Primary requirements document: `docs/requirements.md`
Refinement questions: `docs/refinement-questions.md`
Refinement log: `docs/refinement-log.md`

## Extension Configuration
- **Security Baseline**: ENABLED — blocking constraints apply to credential handling (FR-012, NFR-002), input validation, platform token storage, and least-privilege boundaries across all adapters and the Web UI.
- **Property-Based Testing (full)**: ENABLED — blocking constraints apply to pipeline logic (Pipelines A/B/C), adapter interfaces, plan/profile serialization, budget accounting, and state transitions.

## Traceability Summary
- **Functional Requirements**: FR-001 through FR-014 (see `docs/requirements.md` §2)
- **Non-Functional Requirements**: NFR-001 through NFR-009 (see `docs/requirements.md` §3)
- **Technical Decisions**: see `docs/requirements.md` §4
- **Out of Scope**: see `docs/requirements.md` §6
- **Open Questions**: see `docs/requirements.md` §7 — deferred to construction or per-channel launch

## Architecture Summary (from refinement)
Three independently-scheduled pipelines communicating only through persisted artifacts:
- **Pipeline A** (Style Study) — per channel, slow cadence → produces versioned `StyleProfile`
- **Pipeline B** (Content Production) — per channel, per posting slot → trend-scout, plan, generate, approve, publish
- **Pipeline C** (Measure & Learn) — per channel, slow cadence → ingests metrics, updates priors consumed by A and B

Supporting surfaces:
- **Web UI** (Next.js + Supabase) — operator observability + approvals
- **Telegram bot** — push alerts + approvals
- **GitHub Actions** — scheduled runtime (matrix per channel per pipeline)

## MVP Anchors
- 1 channel, YouTube Shorts, Korean-language, KST scheduling
- Asset-assembly only at first (generative-video opt-in, budget-capped)
- Approval gate `required` (flippable per-channel after confidence)
- Web UI MVP scope: Channels overview + Approval queue
