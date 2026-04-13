# Vision Document: Reel-Mind

## Project Overview
Reel-Mind is a 24/7 autonomous content factory that runs a portfolio of faceless, single-subject short-form video channels. It decomposes the content lifecycle into three independently-scheduled pipelines — Style Study, Content Production, and Measure & Learn — orchestrated by Claude and deployed on GitHub Actions. A Web UI plus a Telegram bot provide observability and a configurable human approval gate.

## Goals
- Run end-to-end: trend discovery → style-aware planning → hybrid video generation → optional approval → publishing → metrics → learning.
- Support N parallel channels from the same codebase, each with its own subject, schedule, budget, and approval mode.
- Reach ~$1,000/month net ad/affiliate revenue from the channel portfolio.
- Operate unattended once per-channel approval mode is switched off.
- Maintain full traceability from published video back to source trend, style profile version, and generation prompts.

## Scope

### In Scope
- Style Study pipeline (A): per-channel style learning and versioned StyleProfiles.
- Content Production pipeline (B): trend-scout, planning, hybrid video generation, approval gate, publishing.
- Measure & Learn pipeline (C): metrics ingestion and feedback into A and B.
- Multi-channel orchestration and per-channel configuration.
- Pluggable adapters for sources, generative-video providers, and publishing platforms.
- Web dashboard (Next.js + Supabase) and Telegram approval/alert bot.
- Budget governance with hard per-channel caps.
- Account warmup and posting-cadence enforcement.
- MVP walking skeleton: 1 Korean-language YouTube Shorts channel, asset-assembly only, approval-gated.

### Out of Scope
- Live-action / on-camera content.
- Multi-user SaaS.
- Paid ad campaigns / promotion automation.
- Long-form video (>3 min).
- Non-YouTube platforms in MVP.
- Languages other than Korean in MVP.

## Stakeholders
- **Primary operator**: the builder — responsible for approvals during warmup, config changes, and monitoring.
- **End viewers**: Korean short-form audiences on YouTube Shorts.
- **Platforms**: YouTube (MVP), Instagram/TikTok (future) — policy and ToS stakeholders.

## Success Criteria
- MVP: one Korean YouTube Shorts channel publishing on a KST schedule, end-to-end, approval-gated, with Web UI + Telegram observability.
- Portfolio: ~$1,000/month net revenue.
- Reliability: no undetected pipeline failure persists >24h.
- Scale readiness: adding a second channel requires only config + secrets, not code changes.
