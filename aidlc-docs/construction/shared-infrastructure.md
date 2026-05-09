# Shared Infrastructure Contract

**Created**: 2026-05-10
**Owner**: U1 Shared Foundation
**Applies to**: U1-U8 construction units

This document is the cross-unit infrastructure contract. Later units should extend it when they add infrastructure, not redefine the base conventions.

---

## 1. Environment Names

Canonical environment names:

- `local`
- `staging`
- `production`

Staging and production use separate Supabase projects, separate R2 buckets, and separate secret sets. Local defaults to mocks or explicit staging opt-in.

---

## 2. Supabase Ownership

U1 owns shared base tables and conventions:

- `channels`
- `pipeline_runs`
- `stage_records`
- `cost_ledger`

Later-unit ownership:

| Unit | May add |
|------|---------|
| U2 Adapter Framework | adapter registry/config support tables if needed |
| U3 Pipeline A | style profile and sample metadata tables |
| U4 Pipeline B | trend, plan, approval, publish, and video lineage tables |
| U5 Pipeline C | metrics and signal tables |
| U6 Telegram Bot | alert delivery and bot interaction tables |
| U7 Web UI | UI-specific views, RLS policies, auth-facing helper views |
| U8 Orchestration | workflow metadata and deployment support tables |

Any later unit that changes U1-owned table semantics must record the reason in its construction artifacts. Structural changes with long-term compatibility impact require an ADR.

---

## 3. Supabase Access Boundary

Server-side contexts:
- Pipelines
- Telegram bot
- Ops scripts

These use U1 `SupabaseClient` and service-role credentials.

Browser/Web UI contexts:
- Use Supabase anon/JWT credentials.
- Rely on RLS policies designed in U7.
- Must never receive service-role credentials.

There is no custom HTTP middle tier in MVP.

---

## 4. R2 Object Contract

R2 buckets are private and environment-scoped.

Canonical object prefix:

```text
channels/{channel_id}/runs/{run_id}/{artifact_kind}/{filename}
```

Initial artifact kinds:

- `samples`
- `plan`
- `scenes`
- `audio`
- `bgm`
- `composed`
- `published`

New artifact kinds may be added by later units when documented in the relevant unit's infrastructure or code artifacts. Public reads are not allowed in MVP; previews use presigned URLs.

---

## 5. Secret Naming

Canonical secret names:

```text
REEL_MIND_<KEY>
REEL_MIND_<CHANNEL_ID_UPPER_UNDERSCORE>_<KEY>
```

Rules:
- Secret values live only in GitHub Actions encrypted secrets, bot-host env, or local untracked env.
- Secret resolution goes through `SecretsProvider`.
- Secret values are never stored in Supabase, R2, repo files, or logs.
- Channel slugs convert hyphens to underscores and uppercase for env names.

---

## 6. Runtime Model

Pipelines:
- GitHub-hosted Actions runners for MVP.
- Python `>=3.12,<3.13`.
- Dependencies from committed `uv.lock`.
- One U1 client graph per process invocation.

Bot:
- Exact host deferred to U6.
- Must provide the same Python/runtime/secret/logging expectations.

Web UI:
- Next.js on Vercel.
- Uses Supabase Auth/RLS and presigned R2 URLs.

---

## 7. Logging and Metrics

Canonical log format:
- stdout JSON only.
- No pretty mode in MVP.
- Redaction processor active in U1 contexts.

Authoritative log locations:
- GitHub Actions for pipelines.
- Bot-host logs for Telegram bot.
- Vercel logs for Web UI.

Metrics are represented as structured log fields:

- `metric_name`
- `metric_type`
- `metric_value`

No external metrics or error-tracking backend is part of MVP.

---

## 8. Reliability Boundaries

U1 does not provide:

- Queue infrastructure.
- Disk spool fallback.
- Pending-ledger reconciliation tables.
- Cross-run retry orchestration.

Failure posture:
- Retry transient storage failures inside U1 according to NFR Design.
- After retry exhaustion, fail fast and surface the failure.
- Do not silently skip run records, stage records, ledger records, or artifact writes.

---

## 9. Time and Identity Conventions

Timestamps:
- DB timestamps are UTC.
- Monthly cost windows use UTC month boundaries.
- Scheduled posting slots are canonical KST ISO-8601 strings where used for Pipeline B idempotency.

IDs:
- `channel_id` is a slug matching `^[a-z0-9][a-z0-9-]{0,31}$`.
- `run_id` is deterministic for scheduled Pipeline B runs and random/synthetic where explicitly specified.
- `cost_ledger.entry_id` uses ULID.

---

## 10. Extension Enforcement

Security Baseline:
- Applies to every unit that handles credentials, tokens, user input, or external API calls.
- U1 conventions for secrets, redaction, validation, service-role isolation, and private R2 are blocking constraints.

Property-Based Testing:
- Applies to pure functions, serializers, state machines, and budget logic in later units.
- U1 defines the base PBT targets for config merge, idempotency, redaction, cost arithmetic, and run lifecycle transitions.

---

## 11. Change Control

When later units need infrastructure additions:

1. Extend this document if the addition is cross-unit.
2. Keep unit-specific details in that unit's construction artifacts.
3. Add an ADR when the change alters shared boundaries, persistence semantics, security posture, or runtime ownership.
4. Keep U1-owned invariants intact unless explicitly superseded by an approved ADR.
