"""Checking that init data really came from Telegram."""

from __future__ import annotations

import hmac
from datetime import datetime, timedelta, timezone
from typing import TypeAlias

from init_data_py import _crypto, errors
from init_data_py.models import InitData
from init_data_py.parsing import parse

__all__ = ["ExpiresIn", "hash_token", "is_valid_by_hash", "validate_by_hash"]

#: Accepted forms for a lifetime: seconds, a timedelta, or 0/None to
#: switch the expiry check off.
ExpiresIn: TypeAlias = "int | float | timedelta | None"

#: One day, the same lifetime Telegram's own examples assume.
DEFAULT_EXPIRES_IN = 86400

hash_token = _crypto.hash_token


def _coerce(init_data: str | bytes | InitData) -> InitData:
    if isinstance(init_data, InitData):
        return init_data
    return parse(init_data)


def _resolve_expires_in(expires_in: ExpiresIn) -> float | None:
    """Return a positive number of seconds, or None to skip the check."""
    if expires_in is None:
        return None
    if isinstance(expires_in, timedelta):
        seconds = expires_in.total_seconds()
    else:
        seconds = float(expires_in)
    if seconds < 0:
        # A ValueError, not an InvalidInitDataError: this is a mistake in
        # the calling code, so is_valid_* must not swallow it.
        raise ValueError("expires_in must not be negative")
    return seconds or None


def _check_not_expired(
    init_data: InitData, expires_in: ExpiresIn, now: datetime | None
) -> None:
    seconds = _resolve_expires_in(expires_in)
    if seconds is None:
        return
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    expires_at = init_data.issued_at + timedelta(seconds=seconds)
    if now > expires_at:
        raise errors.ExpiredError(
            issued_at=init_data.issued_at, expires_at=expires_at, now=now
        )


def validate_by_hash(
    init_data: str | bytes | InitData,
    bot_token: str,
    *,
    expires_in: ExpiresIn = DEFAULT_EXPIRES_IN,
    token_hashed: bool = False,
    now: datetime | None = None,
) -> InitData:
    """Check init data against your bot token, and return it parsed.

    This is the usual check, for a backend that owns the bot. Use
    ``validate_by_signature()`` instead when you do not have the token.

    Parameters:
        init_data (``str`` | ``bytes`` | :obj:`~init_data_py.InitData`):
            Raw init data, or an already parsed object.

        bot_token (``str``):
            The bot token, or its digest when ``token_hashed`` is set.

        expires_in (``int`` | ``float`` | ``timedelta``, *optional*):
            How long init data stays usable, in seconds. Pass 0 or None
            to accept init data of any age, which allows replay.

        token_hashed (``bool``, *optional*):
            Treat ``bot_token`` as the output of ``hash_token()``, so the
            real token never has to reach this service.

        now (``datetime``, *optional*):
            Timezone-aware moment to measure expiry against. Defaults to
            the current UTC time.

    Returns:
        :obj:`~init_data_py.InitData`: The validated init data.

    Raises:
        InvalidInitDataError: Any reason the data is not acceptable. See
            the subclasses for the specific cause.
        ValueError: ``expires_in`` is negative, or ``now`` is naive.
    """
    data = _coerce(init_data)
    _check_not_expired(data, expires_in, now)

    expected = _crypto.compute_hash(
        _crypto.build_data_check_string(data.pairs),
        _crypto.secret_key(bot_token, token_hashed=token_hashed),
    )
    if not hmac.compare_digest(expected, data.hash):
        raise errors.HashInvalidError()
    return data


def is_valid_by_hash(
    init_data: str | bytes | InitData,
    bot_token: str,
    *,
    expires_in: ExpiresIn = DEFAULT_EXPIRES_IN,
    token_hashed: bool = False,
    now: datetime | None = None,
) -> bool:
    """Return whether ``validate_by_hash()`` would accept the init data.

    Only returns False for data that is genuinely unacceptable. Mistakes
    in your own code still raise, so a bug cannot look like a rejection.
    """
    try:
        validate_by_hash(
            init_data,
            bot_token,
            expires_in=expires_in,
            token_hashed=token_hashed,
            now=now,
        )
    except errors.InvalidInitDataError:
        return False
    return True
