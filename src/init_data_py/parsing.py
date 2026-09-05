"""Turning a raw init data query string into an :class:`InitData`."""

from __future__ import annotations

import re
import urllib.parse
from datetime import datetime, timezone

from init_data_py import errors
from init_data_py.models import Chat, InitData, User

__all__ = ["parse", "strip_auth_header"]

_DIGITS = re.compile(r"[0-9]{1,19}")
_SIGNED_DIGITS = re.compile(r"-?[0-9]{1,19}")
_HEX_64 = re.compile(r"[0-9a-fA-F]{64}")
_BASE64URL = re.compile(r"[A-Za-z0-9_-]+={0,2}")


def _decode(init_data: str | bytes) -> str:
    if isinstance(init_data, bytes):
        try:
            return init_data.decode()
        except UnicodeDecodeError as exc:
            raise errors.MalformedQueryStringError("not valid UTF-8") from exc
    return init_data


def _decode_pairs(query_string: str) -> list[tuple[str, str]]:
    """Decode the query string, rejecting anything ambiguous.

    Duplicate keys are refused rather than silently collapsed: the pair
    that gets hashed and the pair the caller reads could otherwise be
    different ones.
    """
    # parse_qsl returns [] for an empty string instead of applying
    # strict_parsing, and "empty" is a clearer complaint than "auth_date
    # is missing".
    if not query_string.strip():
        raise errors.MalformedQueryStringError("empty")

    try:
        pairs = urllib.parse.parse_qsl(
            query_string, keep_blank_values=True, strict_parsing=True
        )
    except ValueError as exc:
        raise errors.MalformedQueryStringError(str(exc)) from exc

    seen: dict[str, int] = {}
    for key, _ in pairs:
        if not key:
            raise errors.MalformedQueryStringError("empty field name")
        seen[key] = seen.get(key, 0) + 1
    for key, count in seen.items():
        if count > 1:
            raise errors.DuplicateFieldError(key, count=count)
    return pairs


def _parse_timestamp(value: str) -> int:
    if not _DIGITS.fullmatch(value):
        raise errors.MalformedFieldError(
            "auth_date", value=value, reason="not a Unix timestamp"
        )
    seconds = int(value)
    try:
        datetime.fromtimestamp(seconds, timezone.utc)
    except (OverflowError, OSError, ValueError) as exc:
        raise errors.MalformedFieldError(
            "auth_date", value=value, reason="out of range"
        ) from exc
    return seconds


def _parse_int(value: str, field: str) -> int:
    if not _SIGNED_DIGITS.fullmatch(value):
        raise errors.MalformedFieldError(
            field, value=value, reason="not an integer"
        )
    return int(value)


def _parse_hash(value: str) -> str:
    if not _HEX_64.fullmatch(value):
        raise errors.MalformedFieldError(
            "hash", value=value, reason="not 64 hex characters"
        )
    # Lowercased so the constant-time compare never sees mixed case.
    return value.lower()


def _parse_signature(value: str) -> str:
    if not _BASE64URL.fullmatch(value):
        raise errors.MalformedFieldError(
            "signature", value=value, reason="not base64url"
        )
    return value


def parse(init_data: str | bytes) -> InitData:
    """Read a raw init data query string.

    Parsing says nothing about authenticity, only about shape. Use
    ``validate_by_hash()`` or ``validate_by_signature()`` to find out
    whether Telegram really sent it.

    Fields this version does not recognise are kept as-is and reachable
    through ``InitData.extra``, so a new Telegram field cannot break
    parsing.

    Parameters:
        init_data (``str`` | ``bytes``):
            The value of ``window.Telegram.WebApp.initData``.

    Returns:
        :obj:`~init_data_py.InitData`: The parsed init data.

    Raises:
        MalformedQueryStringError: The string is not a usable query
            string, or a field name is empty.
        DuplicateFieldError: A field appears more than once.
        AuthDateMissingError: ``auth_date`` is absent.
        HashMissingError: ``hash`` is absent.
        MalformedFieldError: A field is present but unusable.
    """
    query_string = _decode(init_data)
    pairs = _decode_pairs(query_string)

    auth_date: int | None = None
    hash_value: str | None = None
    signature: str | None = None
    query_id: str | None = None
    user: User | None = None
    receiver: User | None = None
    chat: Chat | None = None
    chat_type: str | None = None
    chat_instance: str | None = None
    start_param: str | None = None
    can_send_after: int | None = None

    for key, value in pairs:
        match key:
            case "auth_date":
                auth_date = _parse_timestamp(value)
            case "hash":
                hash_value = _parse_hash(value)
            case "signature":
                signature = _parse_signature(value)
            case "can_send_after":
                can_send_after = _parse_int(value, key)
            case "user":
                user = User.from_json(value, path="user")
            case "receiver":
                receiver = User.from_json(value, path="receiver")
            case "chat":
                chat = Chat.from_json(value)
            case "query_id":
                query_id = value
            case "chat_type":
                chat_type = value
            case "chat_instance":
                chat_instance = value
            case "start_param":
                # Caller controlled, so never interpreted as anything
                # other than text.
                start_param = value
            case _:
                # Unknown fields stay in `pairs` and surface through
                # InitData.extra. They are never an error.
                pass

    if auth_date is None:
        raise errors.AuthDateMissingError()
    if hash_value is None:
        raise errors.HashMissingError()

    return InitData(
        query_string=query_string,
        pairs=tuple(pairs),
        auth_date=auth_date,
        hash=hash_value,
        signature=signature,
        query_id=query_id,
        user=user,
        receiver=receiver,
        chat=chat,
        chat_type=chat_type,
        chat_instance=chat_instance,
        start_param=start_param,
        can_send_after=can_send_after,
    )


def strip_auth_header(header: str, *, scheme: str = "tma") -> str:
    """Pull the init data out of an ``Authorization`` header.

    Mini App backends receive init data as ``Authorization: tma <init
    data>``. This only splits the string; pass the result to ``parse()``
    or one of the validators.

    Parameters:
        header (``str``):
            The full header value.

        scheme (``str``, *optional*):
            Expected scheme, matched case-insensitively.

    Returns:
        ``str``: The credential part of the header.

    Raises:
        MalformedAuthHeaderError: The scheme does not match, or there is
            nothing after it.
    """
    parts = header.strip().split(None, 1)
    if len(parts) != 2 or parts[0].lower() != scheme.lower():
        raise errors.MalformedAuthHeaderError(scheme=scheme)
    credential = parts[1].strip()
    if not credential:
        raise errors.MalformedAuthHeaderError(scheme=scheme)
    return credential
