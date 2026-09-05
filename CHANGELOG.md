# Changelog

All notable changes to this project are documented here. This project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - unreleased

A rewrite. See the migration table in the README for the old to new mapping.

Currently available as a release candidate:

```bash
pip install "init-data-py==1.0.0rc1"
```

### Fixed

- **Hashes are computed from the query string as received.** Earlier versions
  rebuilt the signed string from parsed fields, then patched over the
  differences by escaping every slash in it. That produced hashes Telegram
  would reject whenever a value held a slash, such as `start_param=ref/abc`,
  and made the result depend on the order of keys inside the `user` JSON.
- **Unknown fields no longer raise.** A field this library does not recognise
  used to raise `UnexpectedFormatError`, and an unrecognised field inside
  `user` raised a bare `TypeError`. Both are now kept and readable through
  `extra`, so a field Telegram adds later cannot break parsing.
- Hashes are compared with `hmac.compare_digest` instead of `!=`.
- A field sent more than once is rejected instead of silently taking the last
  value, which could hash one value and hand another to the caller.
- Timestamps are timezone aware UTC rather than naive local time.
- A malformed `auth_date` raises `MalformedFieldError` instead of letting a
  `ValueError` escape.
- Objects are hashable again. Defining `__eq__` without `__hash__` had made
  them unusable in sets and as dict keys.

### Added

- `validate_by_signature` and `is_valid_by_signature`, which verify Telegram's
  Ed25519 `signature` field. For third parties that need to trust init data for
  a bot whose token they do not have. Needs the new `ed25519` extra:
  `pip install "init-data-py[ed25519]"`.
- `hash_token` and `token_hashed`, so a service can validate without ever
  holding the bot token itself.
- `strip_auth_header`, for the `Authorization: tma <init data>` convention.
- `InitData.extra`, `InitData.get`, `User.extra` and `Chat.extra` for reading
  fields this version does not know about.
- `InitData.issued_at`, `auth_date` as a timezone aware datetime.
- `is_ed25519_available` and `TELEGRAM_PUBLIC_KEYS`.
- A `py.typed` marker. Type checkers previously treated the package as
  untyped despite it being fully annotated.

### Changed

- **Init data now expires after one day by default.** It previously never
  expired unless a lifetime was passed, so replay protection was something you
  had to remember to switch on. Pass `expires_in=0` for the old behaviour.
- `validate_by_hash` returns the parsed init data, so there is no step where
  parsed but unchecked data sits in a variable.
- `validate(raise_error=False)` is replaced by `is_valid_by_hash`. The return
  type no longer depends on an argument. It reports `False` only for
  unacceptable init data, and still raises on a mistake in the calling code.
- `sign` returns a new query string instead of mutating and returning `self`.
- `chat_type` and `Chat.type` are plain strings rather than a fixed set, since
  Telegram can add values.
- `User` and `Chat` are frozen dataclasses.
- Errors carry structured data. `ExpiredError` has `issued_at`, `expires_at`
  and `expired_for`; `SignatureInvalidError` has `bot_id` and `environment`.
- `MissingDependencyError` sits outside `InvalidInitDataError`, so a missing
  optional dependency raises rather than being reported as invalid data.
- Requires Python 3.10 or newer.

### Removed

- The `InitData` class API: `parse`, `from_query_string`, `validate`, `sign`,
  `calculate_hash`, `to_dict`, `to_json` as methods.
- The `init_data_py.types` package. `User` and `Chat` come from the top level.
- `init_data_py.errors.errors`. Import from `init_data_py.errors`.

The old error names `InitDataPyError`, `UnexpectedFormatError`,
`SignMissingError` and `SignInvalidError` are kept as aliases of their
replacements, so existing `except` clauses keep working.
