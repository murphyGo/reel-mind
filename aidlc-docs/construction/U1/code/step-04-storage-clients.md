# U1 Code Generation Step 4 — Storage Clients

## Summary

Implemented `src/reel_mind/foundation/storage.py`:

- `SupabaseClient`
  - `select_one`
  - `select_many`
  - `insert`
  - `update_where`
  - `rpc`
  - `aggregate_sum`
- `R2Client`
  - `put`
  - `get`
  - `head`
  - `presigned_url`
  - `delete`
- R2 key helpers:
  - `r2_key`
  - `validate_r2_key`
- Multipart transfer configuration constants matching U1 NFR Design.

## Tests

Added:

- `tests/unit/foundation/test_storage.py`

The tests use mocked Supabase and S3/R2 clients and cover select/sum behavior, R2 put/get/head/presign behavior, object-key validation, and presigned URL TTL bounds.
