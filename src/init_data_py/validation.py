"""Checking that init data really came from Telegram."""

from __future__ import annotations

import base64
import binascii
import hmac
from datetime import datetime, timedelta, timezone
from typing import Literal, TypeAlias

from init_data_py import _crypto, _ed25519, errors
from init_data_py.models import InitData
from init_data_py.parsing import parse

__all__ = [
    "Environment",
    "ExpiresIn",
    "TELEGRAM_PUBLIC_KEYS",
    "hash_token",
    "is_ed25519_available",
    "is_valid_by_hash",
    "is_valid_by_signature",
    "validate_by_hash",
    "validate_by_signature",
]

#: Accepted forms for a lifetime: seconds, a timedelta, or 0/None to
#: switch the expiry check off.
ExpiresIn: TypeAlias = "int | float | timedelta | None"

#: Which set of Telegram servers signed the init data.
Environment: TypeAlias = Literal["prod", "test"]

#: One day, the same lifetime Telegram's own examples assume.
DEFAULT_EXPIRES_IN = 86400

TELEGRAM_PUBLIC_KEYS = _ed25519.TELEGRAM_PUBLIC_KEYS
hash_token = _crypto.hash_token
is_ed25519_available = _ed25519.is_available


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


def _resolve_public_key(
    environment: Environment, public_key: str | bytes | None
) -> bytes:
    if public_key is None:
        try:
            public_key = TELEGRAM_PUBLIC_KEYS[environment]
        except KeyError:
            raise ValueError(
                f"unknown environment {environment!r}, expected one of "
                f"{sorted(TELEGRAM_PUBLIC_KEYS)}"
            ) from None
    if isinstance(public_key, str):
        return bytes.fromhex(public_key)
    return public_key


def _decode_signature(signature: str) -> bytes:
    # Telegram sends unpadded base64url.
    padded = signature + "=" * (-len(signature) % 4)
    try:
        return base64.urlsafe_b64decode(padded)
    except (binascii.Error, ValueError) as exc:
        raise errors.MalformedFieldError(
            "signature", value=signature, reason="not valid base64url"
        ) from exc


def validate_by_signature(
    init_data: str | bytes | InitData,
    bot_id: int,
    *,
    environment: Environment = "prod",
    public_key: str | bytes | None = None,
    expires_in: ExpiresIn = DEFAULT_EXPIRES_IN,
    now: datetime | None = None,
) -> InitData:
    """Check init data against Telegram's public key, without the token.

    This is for third parties: anyone who needs to trust init data for a
    bot they do not own, and so cannot use ``validate_by_hash()``. Only
    clients from Bot API 8.0 onwards send the ``signature`` this needs.

    Requires the ``ed25519`` extra::

        pip install "init-data-py[ed25519]"

    Parameters:
        init_data (``str`` | ``bytes`` | :obj:`~init_data_py.InitData`):
            Raw init data, or an already parsed object.

        bot_id (``int``):
            Identifier of the bot the Mini App belongs to, which is the
            part of its token before the colon.

        environment (``str``, *optional*):
            Which Telegram network signed it, "prod" or "test".

        public_key (``str`` | ``bytes``, *optional*):
            Overrides the built-in key for ``environment``, as hex or raw
            bytes. Useful if Telegram rotates a key before this package
            catches up.

        expires_in (``int`` | ``float`` | ``timedelta``, *optional*):
            How long init data stays usable, in seconds. Pass 0 or None
            to accept init data of any age, which allows replay.

        now (``datetime``, *optional*):
            Timezone-aware moment to measure expiry against. Defaults to
            the current UTC time.

    Returns:
        :obj:`~init_data_py.InitData`: The validated init data.

    Raises:
        InvalidInitDataError: Any reason the data is not acceptable. See
            the subclasses for the specific cause.
        MissingDependencyError: The ``ed25519`` extra is not installed.
        ValueError: ``expires_in`` is negative, ``now`` is naive, or the
            environment is unknown.
    """
    data = _coerce(init_data)
    if data.signature is None:
        raise errors.SignatureMissingError()
    _check_not_expired(data, expires_in, now)

    key = _resolve_public_key(environment, public_key)
    message = _crypto.build_data_check_string(
        data.pairs,
        exclude=_crypto.ED25519_EXCLUDED,
        prefix=f"{bot_id}:WebAppData\n",
    )
    if not _ed25519.verify(
        key, _decode_signature(data.signature), message.encode()
    ):
        raise errors.SignatureInvalidError(
            bot_id=bot_id, environment=environment
        )
    return data


def is_valid_by_signature(
    init_data: str | bytes | InitData,
    bot_id: int,
    *,
    environment: Environment = "prod",
    public_key: str | bytes | None = None,
    expires_in: ExpiresIn = DEFAULT_EXPIRES_IN,
    now: datetime | None = None,
) -> bool:
    """Return whether ``validate_by_signature()`` would accept the data.

    A missing ``ed25519`` extra raises rather than returning False, so a
    packaging mistake can never look like a rejected signature.
    """
    try:
        validate_by_signature(
            init_data,
            bot_id,
            environment=environment,
            public_key=public_key,
            expires_in=expires_in,
            now=now,
        )
    except errors.InvalidInitDataError:
        return False
    return True
