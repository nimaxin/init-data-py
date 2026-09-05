"""Building and signing your own init data."""

from __future__ import annotations

import urllib.parse
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone

from init_data_py import _crypto
from init_data_py.models import UnsignedInitData

__all__ = ["sign"]

#: Produced by sign(), so passing them in is a mistake.
_RESERVED = frozenset({"auth_date", "hash"})


def _to_pairs(
    payload: UnsignedInitData | Mapping[str, str] | Iterable[tuple[str, str]],
) -> list[tuple[str, str]]:
    if isinstance(payload, UnsignedInitData):
        return payload.to_pairs()
    items = payload.items() if isinstance(payload, Mapping) else payload
    return [(str(key), str(value)) for key, value in items]


def _resolve_auth_date(auth_date: int | float | datetime | None) -> int:
    if auth_date is None:
        return int(datetime.now(timezone.utc).timestamp())
    if isinstance(auth_date, datetime):
        if auth_date.tzinfo is None:
            raise ValueError("auth_date must be timezone-aware")
        return int(auth_date.timestamp())
    return int(auth_date)


def sign(
    payload: UnsignedInitData | Mapping[str, str] | Iterable[tuple[str, str]],
    bot_token: str,
    *,
    auth_date: int | float | datetime | None = None,
    token_hashed: bool = False,
) -> str:
    """Build a signed init data query string.

    Mostly useful for tests and fixtures: real init data comes from
    Telegram. Values are used exactly as given, so what you pass is what
    gets hashed.

    Parameters:
        payload (:obj:`~init_data_py.UnsignedInitData` | ``dict`` | ``iterable``):
            The fields to sign. A mapping or an iterable of pairs lets
            you control the exact strings.

        bot_token (``str``):
            The bot token, or its digest when ``token_hashed`` is set.

        auth_date (``int`` | ``float`` | ``datetime``, *optional*):
            When the Mini App was opened. Defaults to now. A datetime
            must be timezone-aware.

        token_hashed (``bool``, *optional*):
            Treat ``bot_token`` as the output of ``hash_token()``.

    Returns:
        ``str``: A query string ending in ``hash``, ready to parse.

    Raises:
        ValueError: The payload already carries ``auth_date`` or
            ``hash``, or a naive datetime was given.
    """
    pairs = _to_pairs(payload)
    for key, _ in pairs:
        if key in _RESERVED:
            raise ValueError(
                f"{key!r} is produced by sign(), not passed to it"
            )

    pairs.append(("auth_date", str(_resolve_auth_date(auth_date))))
    pairs.sort()

    secret = _crypto.secret_key(bot_token, token_hashed=token_hashed)
    data_check_string = _crypto.build_data_check_string(pairs)
    pairs.append(("hash", _crypto.compute_hash(data_check_string, secret)))
    return urllib.parse.urlencode(pairs)
