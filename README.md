# init-data-py

![Package version](https://img.shields.io/pypi/v/init-data-py?color=%2334D058&label=pypi%20package)
![Downloads](https://img.shields.io/pepy/dt/init-data-py)
![Supported Python versions](https://img.shields.io/pypi/pyversions/init-data-py)
![License](https://img.shields.io/github/license/nimaxin/init-data-py)

Parse, validate and sign [Telegram Mini App init data](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app).

Init data is the signed string a Mini App receives in
`window.Telegram.WebApp.initData` and sends to your backend. Validate it before
trusting anything inside it.

## Installation

```bash
pip install init-data-py
```

The core has no dependencies. Validating with Telegram's public key instead of
your bot token needs one extra:

```bash
pip install "init-data-py[ed25519]"
```

Requires Python 3.10 or newer.

## Validating with your bot token

The usual case, for a backend that owns the bot.

```python
from init_data_py import validate_by_hash

init_data = validate_by_hash(query_string, bot_token)
print(init_data.user.id)
```

`validate_by_hash` returns the parsed init data, or raises an error if it is
invalid.

### Expiry

Init data expires after one day by default. Pass `expires_in` to change it, or
`0` to turn the check off. Turning it off lets an old query string be replayed
forever, so prefer a short lifetime.

```python
from datetime import timedelta

validate_by_hash(query_string, bot_token, expires_in=3600)
validate_by_hash(query_string, bot_token, expires_in=timedelta(hours=1))
validate_by_hash(query_string, bot_token, expires_in=0)  # no expiry check
```

### Getting a boolean

If you only want `True` or `False`, use `is_valid_by_hash`:

```python
from init_data_py import is_valid_by_hash

if not is_valid_by_hash(query_string, bot_token):
    raise PermissionError
```

## Validating without the bot token

A third party that needs to trust init data for a bot it does not own can
verify Telegram's Ed25519 signature instead. This needs the `ed25519` extra,
and only clients from Bot API 8.0 onwards send the `signature` field.

```python
from init_data_py import validate_by_signature

init_data = validate_by_signature(query_string, bot_id)
init_data = validate_by_signature(query_string, bot_id, environment="test")
```

`is_valid_by_signature` is the boolean form.

## Parsing without validating

`parse` only reads the query string. It does not validate anything, so do not
trust the result until a validator has passed.

```python
from init_data_py import parse

init_data = parse(query_string)
init_data.user  # a User, or None
init_data.chat  # a Chat, or None
init_data.issued_at  # auth_date as a UTC datetime
init_data.extra  # fields this version does not know about
```

## Signing

Useful for tests and fixtures. Real init data comes from Telegram.

```python
from init_data_py import UnsignedInitData, User, sign

query_string = sign(
    UnsignedInitData(user=User(id=5167898484, first_name="xin")),
    bot_token,
)
```

## Errors

Everything raised by this library inherits from `errors.InitDataError`.
Everything caused by bad init data inherits from `errors.InvalidInitDataError`.
The ones you will see most:

- `ParseError`: the query string is malformed or a required field is missing
- `HashInvalidError`: the hash does not match
- `SignatureInvalidError`: the signature does not match
- `ExpiredError`: the init data is too old

```python
from init_data_py import errors, validate_by_hash

try:
    init_data = validate_by_hash(query_string, bot_token)
except errors.ExpiredError:
    ...
except errors.InvalidInitDataError:
    ...
```

## Migrating from 0.2.x

| 0.2.x | 1.0 |
| --- | --- |
| `InitData.parse(qs)` | `parse(qs)` |
| `InitData.from_query_string(qs)` | `parse(qs)` |
| `init_data.validate(token)` | `validate_by_hash(qs, token)` |
| `init_data.validate(token, raise_error=False)` | `is_valid_by_hash(qs, token)` |
| `init_data.validate(token, lifetime=3600)` | `validate_by_hash(qs, token, expires_in=3600)` |
| `InitData(user=user).sign(token)` | `sign(UnsignedInitData(user=user), token)` |
| `from init_data_py.types import User` | `from init_data_py import User` |

Other changes:

- Init data now expires after one day by default. Pass `expires_in=0` to keep
  the old behaviour.
- Fields the library does not recognise no longer cause an error.
- The old error names are kept as aliases, so existing `except` clauses keep
  working.

## Development

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra ed25519                        # set up the environment
uv run python -m unittest discover --verbose   # run the tests
uv run ruff check .                            # lint
uv run ruff format .                           # format
uv run mypy                                    # type check
```

## License

This library is licensed under the [MIT License](LICENCE).
