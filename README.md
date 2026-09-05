# init-data-py

![Package version](https://img.shields.io/pypi/v/init-data-py?color=%2334D058&label=pypi%20package)
![Downloads](https://img.shields.io/pepy/dt/init-data-py)
![Supported Python versions](https://img.shields.io/pypi/pyversions/init-data-py)
![License](https://img.shields.io/github/license/nimaxin/init-data-py)

Parse, validate and sign [Telegram Mini App init data](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app).

Init data is the signed payload a Mini App receives in
`window.Telegram.WebApp.initData` and sends to your backend. Anyone can post a
made up query string to that backend, so the signature has to be checked before
anything inside it is trusted.

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

## Quick start

```python
from init_data_py import validate_by_hash

init_data = validate_by_hash(query_string, bot_token)
print(init_data.user.id)
```

`validate_by_hash` returns the parsed init data and raises if anything is
wrong, so there is never a moment where you are holding data you have not
checked yet.

## Validating

### With your bot token

The usual case, for a backend that owns the bot.

```python
from init_data_py import errors, validate_by_hash

try:
    init_data = validate_by_hash(query_string, bot_token)
except errors.ExpiredError as error:
    ...  # error.issued_at, error.expires_at, error.expired_for
except errors.InvalidInitDataError:
    ...  # anything else wrong with it
```

Init data expires after one day by default. Pass `expires_in` to change it, or
`0` to turn the check off. Turning it off lets an old query string be replayed
forever, so prefer a short lifetime.

```python
validate_by_hash(query_string, bot_token, expires_in=3600)
validate_by_hash(query_string, bot_token, expires_in=timedelta(hours=1))
validate_by_hash(query_string, bot_token, expires_in=0)  # no expiry check
```

If you only want a boolean, use `is_valid_by_hash`. It returns `False` when the
init data is unacceptable, but still raises if your own call was wrong, so a
mistake in your code never looks like a rejected user.

```python
from init_data_py import is_valid_by_hash

if not is_valid_by_hash(query_string, bot_token):
    raise PermissionError
```

### Keeping the bot token out of the service

`hash_token` turns a bot token into the digest that validation actually uses.
Store that instead of the token and pass `token_hashed=True`.

```python
from init_data_py import hash_token, validate_by_hash

digest = hash_token(bot_token)  # do this once, somewhere safe
validate_by_hash(query_string, digest, token_hashed=True)
```

### Without the bot token

A third party that needs to trust init data for a bot it does not own can
verify Telegram's Ed25519 signature instead. This needs the `ed25519` extra,
and only clients from Bot API 8.0 onwards send the `signature` field.

```python
from init_data_py import validate_by_signature

init_data = validate_by_signature(query_string, bot_id)
init_data = validate_by_signature(query_string, bot_id, environment="test")
```

`is_valid_by_signature` is the boolean form. If the extra is not installed,
both raise `MissingDependencyError` rather than reporting a bad signature, so a
packaging mistake can never be mistaken for a forged request.

## Parsing without validating

`parse` only reads the query string. It proves nothing about where the data
came from, so do not trust anything it returns until a validator has passed.

```python
from init_data_py import parse

init_data = parse(query_string)
init_data.user.id
init_data.issued_at  # timezone aware UTC datetime
init_data.to_query_string()  # exactly the string that was parsed
```

Fields this version does not know about are kept rather than rejected, so a
field Telegram adds later cannot break parsing:

```python
init_data.get("some_new_field")  # raw value from the query string
init_data.extra  # every field with no attribute of its own
init_data.user.extra  # the same, inside user and chat
```

## Reading the Authorization header

Mini App backends usually receive init data as `Authorization: tma <init data>`.

```python
from init_data_py import strip_auth_header, validate_by_hash

raw = strip_auth_header(request.headers["Authorization"])
init_data = validate_by_hash(raw, bot_token)
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

`sign` returns a new query string and changes nothing in place. It produces
`auth_date` and `hash` itself, so passing either one in is an error. A mapping
or a list of pairs works too, when you want to control the exact strings.

## Errors

Everything raised by this library inherits from `InitDataError`. Everything
caused by bad init data inherits from `InvalidInitDataError`, which is exactly
what the `is_valid_*` functions turn into `False`.

```
InitDataError
├── InvalidInitDataError
│   ├── ParseError
│   │   ├── MalformedQueryStringError
│   │   ├── MalformedAuthHeaderError
│   │   ├── DuplicateFieldError
│   │   ├── MissingFieldError
│   │   │   ├── AuthDateMissingError
│   │   │   └── HashMissingError
│   │   └── MalformedFieldError
│   ├── AuthenticityError
│   │   ├── HashInvalidError
│   │   ├── SignatureMissingError
│   │   └── SignatureInvalidError
│   └── ExpiredError
└── MissingDependencyError
```

`MissingDependencyError` sits outside `InvalidInitDataError` on purpose. A
missing optional dependency raises instead of quietly reporting invalid data.

## Migrating from 0.2.x

Version 1.0 replaces the `InitData` class with functions. The old class
rebuilt the signed string from parsed fields, which produced hashes Telegram
would reject whenever a value held a slash or the JSON key order differed.

| 0.2.x | 1.0 |
| --- | --- |
| `InitData.parse(qs)` | `parse(qs)` |
| `InitData.from_query_string(qs)` | `parse(qs)` |
| `init_data.validate(token)` | `validate_by_hash(qs, token)` |
| `init_data.validate(token, raise_error=False)` | `is_valid_by_hash(qs, token)` |
| `init_data.validate(token, lifetime=3600)` | `validate_by_hash(qs, token, expires_in=3600)` |
| `InitData(user=user).sign(token)` | `sign(UnsignedInitData(user=user), token)` |
| `init_data.calculate_hash(token)` | not public, use `validate_by_hash` |
| `from init_data_py.types import User` | `from init_data_py import User` |
| `errors.InitDataPyError` | `errors.InitDataError` |
| `errors.UnexpectedFormatError` | `errors.ParseError` |
| `errors.SignMissingError` | `errors.HashMissingError` |
| `errors.SignInvalidError` | `errors.HashInvalidError` |

The old error names are kept as aliases of the new classes, so existing
`except` clauses keep working.

Two behaviour changes worth knowing:

- **Init data now expires by default.** 0.2.x accepted init data of any age
  unless you passed `lifetime`. Pass `expires_in=0` for the old behaviour.
- **Unknown fields no longer raise.** 0.2.x rejected any field it did not
  recognise, which broke every time Telegram added one.

## Development

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra ed25519                        # set up the environment
uv run python -m unittest discover --verbose   # run the tests
uv run ruff check .                            # lint
uv run ruff format .                           # format
uv run mypy                                    # type check
uv build                                       # build the distributions
```

The test suite must also pass without the extra, since the core is meant to
have no dependencies:

```bash
uv sync && uv run python -m unittest discover
```

## License

This library is licensed under the [MIT License](LICENCE).
