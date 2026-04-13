# Component Dependencies

## High-level

```
+-------------------+       +-------------------+       +-------------------+
|   Pipeline A      |       |   Pipeline B      |       |   Pipeline C      |
|   Style Study     |       |   Production      |       |   Measure + Learn |
+---------+---------+       +---------+---------+       +---------+---------+
          |                           |                           |
          |  writes StyleProfile      | reads StyleProfile        | reads PublishedVideo
          |                           | writes PublishedVideo     | writes Metrics + Signals
          v                           v                           v
+------------------------------------------------------------------------+
|                         Shared Foundation (U1)                         |
|      Supabase (rows)    +    R2 (artifacts)    +    CostLedger         |
+------------------------------------------------------------------------+
          ^                           ^                           ^
          |                           |                           |
          | uses adapters             | uses adapters             | uses adapters
          v                           v                           v
+------------------------------------------------------------------------+
|                       Adapter Framework (U2)                           |
|  Source  |  TTS  |  StockMedia  |  GenerativeVideo  |  Publish         |
+------------------------------------------------------------------------+

                            Surfaces over Shared Foundation:

+-------------------+       +-------------------+
|  Telegram Bot     |       |   Web UI          |
|  (U6)             |       |   Next.js (U7)    |
+-------------------+       +-------------------+
    push alerts +               read + write
    approvals                   config/approvals
```

## Dependency rules (enforced)

1. **No pipeline calls another pipeline.** All cross-pipeline communication is via Supabase rows + R2 refs.
2. **No pipeline calls Web UI or Telegram Bot directly** — except `AlertPublisher` inside pipelines, which writes to Telegram via the bot token (pipeline → Telegram Bot API is acceptable).
3. **Web UI does not invoke GHA or pipelines.** It only reads from and writes to Supabase. (Pause/resume a channel is a config write; the next scheduled pipeline run observes it.)
4. **Adapters depend only on Shared Foundation** — never on pipeline code.
5. **Shared Foundation depends on no other layer.**

## Topological build order

```
U1 Shared Foundation
      |
      v
U2 Adapter Framework
      |
      +-----------------------+---------------------+
      v                       v                     v
U3 Pipeline A           U4 Pipeline B         U5 Pipeline C
  (Style Study)          (Production)          (Measure)
                              |
                    +---------+---------+
                    v                   v
               U6 Telegram Bot      U7 Web UI
                              |
                              v
                        U8 Orchestration
                        (GHA workflows, cron)
```

## Critical cross-component contracts

| Producer → Consumer | Contract | Persisted as |
|---------------------|----------|--------------|
| Pipeline A → Pipeline B | `StyleProfile(channel_id, version)` — immutable | Supabase `style_profiles` + R2 sample blobs |
| Pipeline B → Pipeline C | `PublishedVideo` lineage (trend_id, style_profile_version, plan_hash, platform_id) | Supabase `published_videos` |
| Pipeline C → Pipeline A | `StyleSignal` priors for next style study | Supabase `style_signals` |
| Pipeline C → Pipeline B | `TrendSignal` priors for next trend scout | Supabase `trend_signals` |
| Pipeline B → Telegram Bot | Approval request | Supabase `approval_requests` + TG send |
| Telegram Bot → Pipeline B | Approval decision | Supabase `approval_requests.decision` |
| Web UI → Pipeline B | Config change | Supabase `channels` row update |
| `CostLedger` (all pipelines) | Spend attribution | Supabase `cost_ledger` |

## Extension compliance touchpoints

- **Security Baseline**: enforced at `SecretsProvider`, every `*Adapter`, `SupabaseClient` (RLS), `AuthGate` (Web UI), `ApprovalBot` (authorized operator only).
- **PBT (full)**: applied to `IdempotencyGuard`, `CostLedger.remaining_budget`, `BudgetGovernor.preflight`, `StyleProfileRepository.version`, `PostingSchedulerGuard`, plan/profile serializers, state transitions in `ApprovalGate`.
