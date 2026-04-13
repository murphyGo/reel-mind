# U1 Shared Foundation — NFR Requirements Plan

**Unit**: U1 Shared Foundation
**Stage**: NFR Requirements Assessment
**Created**: 2026-04-13
**AIDLC rule**: `construction/nfr-requirements.md`

## Scope Recap

U1 is a library (no long-running process, no network listener). It is consumed by:
- Pipelines A/B/C (Python; GHA ephemeral runners; max 6h)
- Telegram bot worker (Python; long-poll or webhook; small)
- Ops scripts (manual CLI)

It is **not** consumed by the Web UI directly — U7 talks to Supabase + R2 through its own Next.js layer. That keeps U1's NFR scope narrow.

NFR focus for U1:
- **Security** (most load-bearing given secrets + service-role access)
- **Reliability / error taxonomy** (feeds U2 retry policy)
- **Observability** (stdout-JSON only; already decided)
- **Maintainability** (type safety, test coverage, PBT)
- **Performance** (thresholds, not SLOs — this is a library)
- **Availability** (largely delegated to Supabase/R2 SLAs)

## Planning Checklist

- [x] **P1** Answer questions below (block until done)
- [x] **P2** Write `aidlc-docs/construction/U1/nfr-requirements/nfr-requirements.md` with NFR-UNIT-U1-001… entries, each tagged by category and linked to blocking constraints / metrics
- [x] **P3** Write `aidlc-docs/construction/U1/nfr-requirements/tech-stack-decisions.md` with chosen libraries and their rationale
- [x] **P4** Present completion (2-option workflow) — user approved Continue 2026-04-14

---

## Open Questions

Please fill in `[Answer]:` tags. If a question seems like infrastructure-level detail, answer at the "requirement" level (the **what**, not the **how** — the how lives in NFR Design / Infrastructure Design).

### Q1 — Scalability & load expectations

**Q1.1** At walking-skeleton launch: 1 channel × ~1 publish/day × ~2 approval cycles. At 12-month target ($1K/mo revenue goal): how many channels + publishes/day do you want U1 to comfortably handle without redesign? (A rough upper bound is enough.)

[Answer]: I expect U1 to comfortably handle up to 10 channels with the 1/day publish frequency and approval cycles (2) without redesign. This means U1 should be designed to support up to 10 parallel runs of Pipeline A and Pipeline B without significant performance degradation.

**Q1.2** Is there a burst case to worry about (e.g. backfilling a new channel's StyleProfile runs many Pipeline A samples at once)? If yes, roughly how many parallel runs?

[Answer]: Yes, there is a potential burst case when backfilling a new channel's StyleProfile, which could trigger multiple Pipeline A runs simultaneously. I would estimate that in such a scenario, we might see up to 5 parallel Pipeline A runs for the new channel during the backfill process. U1 should be designed to handle this level of concurrency without significant performance issues.

### Q2 — Performance thresholds (not SLOs — "should not be slower than X")

**Q2.1** `ConfigLoader.load_channel_config` — acceptable upper bound per call (runs once per pipeline invocation)? e.g. 500ms, 2s, 5s. Supabase round-trip dominates.

[Answer]: Given that `ConfigLoader.load_channel_config` runs once per pipeline invocation and involves a round-trip to Supabase, an acceptable upper bound for this call would be around 1 second. This allows for some variability in network latency while still ensuring that the pipeline can start promptly.

**Q2.2** `CostLedger.month_spend_all_providers(channel_id)` — this gets called by `BudgetGovernor.preflight` before every generative plan. Acceptable upper bound? e.g. 200ms, 1s. Dictates whether we need a summary table vs. live sum.

[Answer]: Since `CostLedger.month_spend_all_providers(channel_id)` is called before every generative plan, it should ideally return results within 200ms to ensure a smooth user experience during the preflight check. If the current implementation cannot meet this threshold, we may need to consider implementing a summary table that aggregates monthly spend per channel to achieve faster lookups.

**Q2.3** `R2Client.put` for composed video (typical 1080x1920 @ 30s shorts, ~10–30 MB). Acceptable upper bound for the put call? e.g. 30s, 2min.

[Answer]: For `R2Client.put` when uploading a composed video of typical size (10–30 MB), an acceptable upper bound for the put call would be around 60 seconds. This allows for some variability in network conditions while ensuring that the upload process does not become a bottleneck in the pipeline.

**Q2.4** `R2Client.presigned_url` — called from Web UI approval preview. Should feel instant? (<100ms is standard for SigV4 local-sign.)

[Answer]: For `R2Client.presigned_url`, since it is called from the Web UI approval preview, it should ideally feel instant to the user. A response time of under 100ms would be ideal, as this is the standard for SigV4 local signing. If we find that generating presigned URLs consistently exceeds this threshold, we may need to investigate optimizations or caching strategies.

### Q3 — Availability

**Q3.1** U1 has no service of its own — its availability = availability of Supabase + R2. Is the plan to rely on their SLAs (Supabase ~99.9% paid tier, R2 ~99.9%) without U1-level fallback (e.g. local queue, disk spool)? Simplest MVP choice is "yes, rely on upstream". Confirm.

[Answer]: Yes, the plan for U1 is to rely on the SLAs of Supabase and R2 without implementing U1-level fallbacks such as a local queue or disk spool. For the MVP, we will assume that these services will be available as per their advertised SLAs, and we will handle any outages through error handling and retries rather than building additional infrastructure for fallback.

**Q3.2** If Supabase is unreachable during a Pipeline B run, what's the desired behavior: **fail fast** (run marked failed, GHA exits non-zero, operator gets Telegram alert), or **local buffer + retry**? Fail-fast is simpler.

[Answer]: The desired behavior if Supabase is unreachable during a Pipeline B run is to **fail fast**. This means that the run will be marked as failed, GitHub Actions will exit with a non-zero status, and the operator will receive a Telegram alert about the failure. This approach is simpler and allows for quicker awareness and resolution of issues without adding complexity to the system.

### Q4 — Security

**Q4.1** Service-role Supabase key blast radius — confirmed to live only in GHA secrets + bot host env. Are there any additional controls you want for MVP, e.g. IP allow-listing at Supabase, periodic key rotation cadence, alerting on out-of-hours writes? Say "none for MVP" if that's the call.

[Answer]:  For the MVP, we will rely on the existing controls of keeping the service-role Supabase key in GitHub Actions secrets and the bot host environment variables. We will not implement additional controls such as IP allow-listing, periodic key rotation, or alerting on out-of-hours writes for the MVP. However, these are potential areas for enhancement in future iterations once we have more operational data and understand the threat landscape better.

**Q4.2** Log redaction deny-list (`api_key`, `token`, `secret`, `refresh_token`, `authorization`) — any additional keys to deny (e.g. `email`, `telegram_chat_id`, operator PII)?

[Answer]: In addition to the existing log redaction deny-list, we should also consider adding `email` and `telegram_chat_id` to the list of keys to redact. These pieces of information can be considered personally identifiable information (PII) and should be protected in logs to prevent accidental exposure. Therefore, the updated deny-list for log redaction would include: `api_key`, `token`, `secret`, `refresh_token`, `authorization`, `email`, and `telegram_chat_id`.

**Q4.3** PII posture for MVP: the only personal data is your own Telegram chat id and Supabase auth email. Is that treated as regular config (no encryption at rest beyond Supabase default), or do you want field-level encryption for any table?

[Answer]: For the MVP, we will treat the personal data (Telegram chat id and Supabase auth email) as regular configuration without implementing field-level encryption. We will rely on Supabase's default encryption at rest and access controls to protect this data. However, we will ensure that these fields are not logged or exposed in any way through our logging or error handling mechanisms.

**Q4.4** Secret rotation cadence expectation for YouTube refresh tokens, R2 keys, Supabase service key, Anthropic key, Telegram bot token — monthly? on-demand only? "never unless compromised"?

[Answer]: For the MVP, we will adopt a secret rotation cadence of "on-demand only". This means that we will rotate secrets such as YouTube refresh tokens, R2 keys, Supabase service key, Anthropic key, and Telegram bot token only when there is a specific reason to do so (e.g., suspected compromise, expiration, or access changes). We will not implement a regular monthly rotation schedule for the MVP, but this can be revisited in future iterations based on operational experience and security best practices.

**Q4.5** Do you want an automatic alarm on `SecretError` raises (missing env var) via `AlertPublisher`, or just exit non-zero and surface via GHA run failure? The latter is simpler; the former is operator-friendly.

[Answer]: For the MVP, we will choose to exit non-zero and surface the issue via GitHub Actions run failure when a `SecretError` is raised due to a missing environment variable. This approach is simpler to implement and allows the operator to quickly identify and address the issue through the existing CI/CD pipeline monitoring. We can consider implementing automatic alarms via `AlertPublisher` in future iterations for enhanced operator-friendliness once we have more operational data.

### Q5 — Reliability & error classification

**Q5.1** Retry-classification ownership is already decided (adapters in U2, not pipelines). For U1's own failure surfaces (Supabase transient error, R2 5xx, DNS blip) — should U1 **retry internally** with a small budget (e.g. 3 attempts, 200ms/600ms/1.2s backoff) before raising `RetryableStorageError`, or should it raise on first failure and let the caller decide?

[Answer]: For U1's own failure surfaces, we will implement an internal retry mechanism with a small budget before raising a `RetryableStorageError`. Specifically, we will allow for up to 3 attempts with an exponential backoff strategy (e.g., 200ms, 600ms, 1.2s) for transient errors such as Supabase transient errors, R2 5xx errors, or DNS blips. This approach allows U1 to handle common transient issues gracefully without immediately escalating to the caller, while still providing a clear signal when the issue persists beyond the retry attempts.

**Q5.2** `CostLedger.record` is critical for budget integrity. If the ledger INSERT fails **after** the paid provider call already succeeded, what's the desired behavior: (a) retry aggressively then raise; (b) log to stderr with a flag and continue (accepting ledger drift); (c) write to a local fallback file (`.reel-mind/pending-ledger.jsonl`) for later reconciliation?

[Answer]: For the critical `CostLedger.record` operation, we will choose option (a) to retry aggressively before raising an error. This means that if the ledger INSERT fails after a paid provider call has succeeded, U1 will attempt to retry the INSERT operation multiple times with a backoff strategy. If all retry attempts fail, then U1 will raise an error to ensure that the issue is surfaced and can be addressed promptly. This approach prioritizes maintaining budget integrity and ensures that any discrepancies are not silently accepted.

**Q5.3** Minimum test coverage bar for U1 — 80% line coverage? 90%? branch coverage required? The PBT extension adds properties on top.

[Answer]: For U1, we will set a minimum test coverage bar of 90% line coverage. This ensures that the majority of the code is exercised by tests, providing confidence in the reliability and correctness of the library. While branch coverage is valuable, we will focus on line coverage for the MVP to balance thoroughness with development speed. The addition of property-based testing (PBT) will further enhance our test suite by covering edge cases and input variations that may not be captured by traditional unit tests.

### Q6 — Observability

**Q6.1** Already decided: stdout JSON only in MVP; no Supabase log sink. Confirm you want the **same** stdout format in GHA, bot host, and local dev (no "pretty mode" auto-switch), or allow `REEL_MIND_LOG_FORMAT=pretty` locally?

[Answer]: For consistency and to ensure that logs are structured and machine-readable across all environments, we will use the same stdout JSON format in GitHub Actions, the bot host, and local development. We will not implement a "pretty mode" auto-switch for local development in the MVP. This approach simplifies our logging strategy and ensures that all logs can be easily aggregated and analyzed regardless of the environment they are generated in.

**Q6.2** Minimum required fields per log event (on top of the bound context): `timestamp`, `level`, `message`, `event` (structured key). Anything else mandatory for your future grep-ability? e.g. `git_sha`, `python_version`, `gha_run_id`.

[Answer]: In addition to the bound context fields, we will require the following mandatory fields for each log event to enhance grep-ability and provide useful context for debugging and analysis:
- `timestamp`: The time the log event occurred (in UTC, ISO-8601 format).
- `level`: The log level (e.g., DEBUG, INFO, WARN, ERROR).
- `message`: A static-ish template describing the event.
- `event`: A structured key that categorizes the type of event (e.g., "config_load", "cost_record", "r2_upload").
- `git_sha`: The current Git SHA of the codebase, which can help correlate logs with specific code versions.
- `python_version`: The version of Python being used, which can assist in debugging environment-specific issues.
- `gha_run_id`: The GitHub Actions run ID, which can help correlate logs with specific CI runs.
- `operator_id`: The identifier of the operator (if applicable), which can provide context for manual actions.
- `error`: A structured field for error information, including `type`, `message`, `retryable`, and `cause_chain` if an error occurred.
- `fields`: An arbitrary key/value dictionary for additional contextual information relevant to the event.
- `channel_id`, `pipeline`, `run_id`, `stage`, `trigger`: These fields will be included as part of the bound context when applicable, providing essential information for tracing events back to specific runs and stages in the pipelines.
- `service`: The name of the service or component emitting the log (e.g., "U1", "PipelineA", "TelegramBot") to help identify the source of the log event.
- `thread_id`: The identifier of the thread or process emitting the log, which can be useful for debugging concurrency issues.


**Q6.3** Metrics — is there anything U1 should emit that is **not** a log line (e.g. counter, gauge)? For MVP, logs-as-metrics is cheapest. Confirm "no separate metrics backend in MVP".

[Answer]: For the MVP, we will add prometheus-compatible metric fields to our structured log events, allowing us to use logs-as-metrics without the need for a separate metrics backend. This means that we will include fields such as `metric_name`, `metric_type` (e.g., counter, gauge), and `metric_value` in our log events when emitting metrics. This approach allows us to track important metrics while keeping our observability stack simple and cost-effective for the MVP. Therefore, we confirm "no separate metrics backend in MVP".

### Q7 — Maintainability

**Q7.1** Static type checking strictness — `mypy --strict` from day 1, or start lenient and tighten? `--strict` is painful upfront but cheap to maintain.

[Answer]: For U1, we will adopt `mypy --strict` from day 1. While this may require more effort upfront to ensure that all code is properly typed, it will provide significant benefits in terms of maintainability and reliability as the project grows. Strict type checking helps catch potential bugs early in the development process and makes it easier for developers to understand the expected types of variables and function return values, ultimately leading to a more robust codebase.

**Q7.2** Lint config — `ruff` with which preset? `E, F, I, B, UP, SIM, RUF` is a reasonable default. Any additional rule sets you want (e.g. `S` for security, `N` for pep8-naming, `ANN` for annotations)?

[Answer]: For U1, we will use `ruff` with the preset `E, F, I, B, UP, SIM, RUF` as a reasonable default for linting. In addition to this preset, we will also include the `S` rule set for security-related linting to help identify potential security issues in the codebase. This combination will provide a good balance of general code quality checks and security-focused rules to maintain a high standard of code in U1.

**Q7.3** Public-API stability promise for U1 — this is an internal library, but do you want SemVer-style discipline on breaking changes (ADR required), or just "move fast, internal-only, break freely"?

[Answer]: For U1, we will adopt a "move fast, internal-only, break freely" approach to public API stability. Since U1 is an internal library primarily consumed by our pipelines and bot, we have the flexibility to make breaking changes as needed without the overhead of maintaining strict SemVer discipline. This allows us to iterate quickly and make improvements to the library without being constrained by a formal versioning scheme. However, we will still strive to communicate any significant changes to the team to ensure that consumers of U1 are aware of updates that may affect their usage.

### Q8 — Tech-stack picks (U1 specific)

For each: confirm, or provide an alternative.

**Q8.1** **Supabase client**: `supabase-py` v2.x (sync). Async is available but the whole pipeline is synchronous-per-step — no benefit from async here. OK?

[Answer]: Yes, we will use `supabase-py` v2.x in synchronous mode for the Supabase client. Since the pipeline is designed to be synchronous per step, there is no significant benefit to using the async version of the client in this context. This choice simplifies our implementation and aligns well with the overall design of the pipelines.

**Q8.2** **R2 client**: `boto3` with S3-compatible endpoint. Alternative is `aiobotocore`. Sync boto3 matches the rest of the library.

[Answer]: Yes, we will use `boto3` in synchronous mode for the R2 client with an S3-compatible endpoint. This choice is consistent with the rest of the library, which is designed to be synchronous. Using `boto3` allows us to leverage a well-established and widely used library for interacting with S3-compatible storage, and it simplifies our implementation by avoiding the need to manage asynchronous code in this context.

**Q8.3** **Validation**: `pydantic` v2 for `ChannelConfig`, row schemas, and `ValidationResult`. Alternative is `attrs + cattrs`. Pydantic is the industry default for Supabase-adjacent Python.

[Answer]: Yes, we will use `pydantic` v2 for validation of `ChannelConfig`, row schemas, and `ValidationResult`. Pydantic is widely adopted in the Python ecosystem, especially for projects that interact with databases and APIs, making it a natural choice for our use case. It provides powerful features for data validation and parsing, which will help ensure the integrity of our data models and simplify error handling. While `attrs + cattrs` is a viable alternative, the familiarity and ecosystem support of Pydantic make it the preferred choice for this project.

**Q8.4** **Logger**: `structlog` bound-logger pattern (matches the `logger.bind(...)` API from functional design). Alternative is stdlib `logging` with a JSON formatter. Structlog is a better ergonomics fit.

[Answer]: Yes, we will use `structlog` with the bound-logger pattern for our logging implementation. This choice aligns well with the `logger.bind(...)` API from our functional design and provides better ergonomics compared to using the standard library `logging` with a JSON formatter. `structlog` allows us to easily create structured log events with contextual information, which is essential for our observability goals. Additionally, it integrates well with various logging backends and can be configured to output logs in JSON format, making it a versatile choice for our logging needs.

**Q8.5** **Money**: Python `decimal.Decimal` with `ROUND_HALF_UP` at 6 decimal places of precision for unit cost, 2 for USD totals. OK?

[Answer]: Yes, we will use Python's `decimal.Decimal` for handling money values, with a rounding strategy of `ROUND_HALF_UP`. We will maintain 6 decimal places of precision for unit costs to ensure accuracy in calculations, and round to 2 decimal places for USD totals when presenting or storing final amounts. This approach provides a good balance between precision and practicality for financial calculations in our application.

**Q8.6** **Unique IDs**: ULID for `LedgerEntry.entry_id` (sortable + compact). Python libs: `python-ulid`. Alternative is UUIDv7 via `uuid7`. Either works; ULID has tighter ecosystem for Python 3.12.

[Answer]: Yes, we will use ULID for `LedgerEntry.entry_id` as it provides a sortable and compact identifier. The `python-ulid` library is a good choice for generating ULIDs in Python 3.12, and it has a solid ecosystem. While UUIDv7 via `uuid7` is also a viable option, the advantages of ULID in terms of sorting and compactness make it the preferred choice for our unique ID generation needs.

**Q8.7** **Config file format**: YAML for `config/defaults.yaml` via `pyyaml` or `ruamel.yaml`. `ruamel.yaml` preserves comments (useful for operator edits). OK?

[Answer]: Yes, we will use YAML for our configuration file format, specifically `config/defaults.yaml`. We will utilize the `ruamel.yaml` library for parsing and writing YAML files, as it preserves comments, which can be beneficial for operator edits and maintaining readability of the configuration file. This choice allows us to have a human-friendly configuration format while also supporting the necessary features for our application.

**Q8.8** **Testing framework**: `pytest` + `hypothesis` for PBT. Any additions you want locked in (e.g. `pytest-asyncio`, `pytest-cov`, `pytest-mock`)?

[Answer]: Yes, we will use `pytest` as our primary testing framework along with `hypothesis` for property-based testing (PBT). In addition to these, we will also include `pytest-cov` for measuring test coverage and ensuring that we meet our coverage goals. We may consider adding `pytest-mock` for easier mocking in our tests, especially when dealing with external dependencies like Supabase and R2. However, since our current design is primarily synchronous, we will not include `pytest-asyncio` at this time.

**Q8.9** **Error tracking (Sentry/Honeybadger)** — MVP has none (logs-only). Confirm "no external error tracker in MVP".

[Answer]: Yes, for the MVP, we will not use any external error tracking services such as Sentry or Honeybadger. We will rely solely on our structured logging for error tracking and analysis. This approach keeps our observability stack simple and cost-effective for the MVP, while still providing us with the necessary information to monitor and debug issues through our logs. Therefore, we confirm "no external error tracker in MVP".

### Q9 — Dependencies & versioning

**Q9.1** Do you want a **lockfile-enforced** setup (`uv.lock` committed, CI checks lockfile matches `pyproject.toml`)? I see `uv.lock` is currently untracked — did you intend to commit it?

[Answer]: Yes, we will adopt a lockfile-enforced setup for our dependencies. This means that we will commit the `uv.lock` file to our repository and implement CI checks to ensure that the lockfile matches the `pyproject.toml` specifications. This approach helps to ensure consistent dependency versions across different environments and reduces the likelihood of encountering issues due to unintentional version changes. If `uv.lock` is currently untracked, we will make sure to add it to version control as part of this process.

**Q9.2** Python baseline is 3.12. Pin to 3.12.x range, or allow 3.12+ / 3.13-compat?

[Answer]: For the MVP, we will pin our Python baseline to the 3.12.x range. This allows us to ensure compatibility and stability with a specific version of Python while we are developing and testing U1. Once we have more confidence in our codebase and dependencies, we can consider allowing compatibility with Python 3.13 and beyond in future iterations. Pinning to 3.12.x for now helps us avoid any unforeseen issues that may arise from changes in newer Python versions while we are still in the early stages of development.

### Q10 — Compliance with enabled extensions

**Q10.1** **Security Baseline**: U1 handles credentials → blocking rules apply. Confirm you accept that NFR artifacts will treat the following as hard requirements: secret resolution via a single gateway; redaction in logs; no secret persistence outside GHA-encrypted secrets; service-role boundary; input validation at every public API.

[Answer]: Yes, I confirm that we will treat the following as hard requirements for U1 in compliance with the Security Baseline extension:

**Q10.2** **Property-Based Testing (full)**: U1 has pure functions (`canonicalize`, `deep_merge`, `run_id_for`) and state machines (run lifecycle). Confirm you accept blocking PBT coverage for these at Build & Test.

[Answer]: Yes, I confirm that we will implement blocking property-based testing (PBT) coverage for the pure functions and state machines in U1 at Build & Test. This means that we will define appropriate properties for our functions and state machines, and ensure that our test suite includes PBT tests that cover these properties. This approach will help us identify edge cases and ensure the robustness of our codebase.

---

## After Questions Are Answered

I will generate:

- `aidlc-docs/construction/U1/nfr-requirements/nfr-requirements.md` (NFR-UNIT-U1-### entries, grouped by category, with metrics + acceptance criteria)
- `aidlc-docs/construction/U1/nfr-requirements/tech-stack-decisions.md` (one row per library pick, with rationale + alternatives considered)

Then present the 2-option completion (Request Changes / Continue to NFR Design).
