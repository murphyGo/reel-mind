# U1 Code Generation Step 2 — Config and Secrets

## Summary

Implemented:

- `src/reel_mind/foundation/config.py`
  - `deep_merge`
  - stable canonical config hashing
  - `ConfigLoader`
  - defaults normalization from existing `config/defaults.yaml`
- `src/reel_mind/foundation/secrets.py`
  - canonical `REEL_MIND_<KEY>` and `REEL_MIND_<CHANNEL>_<KEY>` env-var naming
  - `SecretsProvider`
  - `OAuthRefreshResult`
- `config/defaults.yaml`
  - added default adapter keys needed for `ChannelConfig` validation.
- `pyproject.toml`
  - aligned YAML dependency to `ruamel-yaml`.

## Tests

Added:

- `tests/unit/foundation/test_config.py`
- `tests/unit/foundation/test_secrets.py`

The tests cover right-biased deep merge, stable config hashing, default+row config loading, unknown-channel errors, env-var naming, invalid secret keys, missing secret errors, and refresh callback behavior.

## Notes

`uv.lock` is now intentionally in the U1 code-generation scope because U1 NFR Requirements selected lockfile-enforced dependency management.
