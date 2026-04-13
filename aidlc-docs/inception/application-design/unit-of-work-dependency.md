# Unit-of-Work Dependencies

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
 (Style Study)            (Production)          (Measure+Learn)
                              |
                    +---------+---------+
                    v                   v
               U6 Telegram Bot     U7 Web UI
                              |
                              v
                        U8 Orchestration
```

## Explicit dependencies

| Unit | Depends on | Reason |
|------|-----------|--------|
| U1 | — | Foundation; no upstream |
| U2 | U1 | Adapters use `SupabaseClient`, `R2Client`, `Logger`, `CostLedger`, `SecretsProvider` |
| U3 | U1, U2 | Uses foundation + `SourceAdapter` for samples |
| U4 | U1, U2 | Uses foundation + Source/TTS/StockMedia/Publish/GenerativeVideo adapters |
| U4 | U3 (runtime-optional) | Reads latest `StyleProfile`; if absent, falls back to bootstrap profile |
| U5 | U1, U2 | Uses foundation + `PublishAdapter.fetch_metrics` |
| U6 | U1 | Reads/writes `approval_requests`; reads operator chat config |
| U6 | U4 (contract-only) | Must agree on approval state machine |
| U7 | U1 | Reads/writes Supabase with RLS |
| U7 | U4 (contract-only) | Must agree on approval + config schemas |
| U8 | U3, U4, U5, U6, U7 | Orchestrates runtime; must know each pipeline's entrypoint |

## MVP critical path (shortest path to walking skeleton)

```
U1  ->  U2  ->  U4  ->  U6  ->  U7 (MVP subset)  ->  U8
```

U3 and U5 are post-MVP (v1). A bootstrap `StyleProfile` is manually authored for the first channel to unblock U4.

## Parallelization opportunities

Once U1 and U2 are complete, the following can proceed in parallel:
- U3 (Style Study)
- U4 (Production — critical)
- U6 (Telegram Bot)
- U7 (Web UI)

Sequential dependency that must be enforced:
- U4's Publisher contract must stabilize before U6's approval state machine is finalized.
- U4's approval-row schema must stabilize before U7's `ApprovalQueueView` is finalized.
- U8 must come last — it wraps the rest.
