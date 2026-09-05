from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, ClassVar

from init_data_py import errors

__all__ = ["Chat", "InitData", "UnsignedInitData", "User"]

#: Top level init data keys this version projects onto InitData fields.
_PROJECTED_KEYS = frozenset(
    {
        "query_id",
        "user",
        "receiver",
        "chat",
        "chat_type",
        "chat_instance",
        "start_param",
        "can_send_after",
        "auth_date",
        "hash",
        "signature",
    }
)


def _require_int(value: Any, name: str) -> None:
    # bool is a subclass of int, so isinstance(True, int) is True.
    if not isinstance(value, int) or isinstance(value, bool):
        raise errors.MalformedFieldError(
            name, value=repr(value), reason="not an integer"
        )


def _truncate(value: str, keep: int = 8) -> str:
    return repr(value if len(value) <= keep else value[:keep] + "...")


def _require_str(value: Any, name: str) -> None:
    if not isinstance(value, str):
        raise errors.MalformedFieldError(
            name, value=repr(value), reason="not a string"
        )


def _split_known(
    cls: type, data: Any, path: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Split a decoded JSON object into known fields and the rest."""
    if not isinstance(data, dict):
        raise errors.MalformedFieldError(
            path, value=repr(data), reason="not a JSON object"
        )
    names = {f.name for f in fields(cls) if f.name != "extra"}
    known = {k: v for k, v in data.items() if k in names}
    extra = {k: v for k, v in data.items() if k not in names}
    return known, extra


def _loads(value: str, path: str) -> Any:
    try:
        return json.loads(value)
    except ValueError as exc:
        raise errors.MalformedFieldError(
            path, value=value, reason=f"invalid JSON: {exc}"
        ) from exc


class _Serializable:
    """Gives User and Chat their to_dict and to_json methods.

    Field order affects to_json output only. Hashing uses the raw query
    string, so it does not care.
    """

    __slots__ = ()

    extra: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return the object as a dict, with unknown fields last."""
        data = {
            f.name: getattr(self, f.name)
            for f in fields(self)  # type: ignore[arg-type]
            if f.name != "extra" and getattr(self, f.name) is not None
        }
        data.update(self.extra)
        return data

    def to_json(self) -> str:
        """Return the object as compact JSON."""
        return json.dumps(
            self.to_dict(), separators=(",", ":"), ensure_ascii=False
        )

    def __repr__(self) -> str:
        # Unset fields are noise; a user has ten of them.
        parts = (f"{k}={v!r}" for k, v in self.to_dict().items())
        return f"{type(self).__name__}({', '.join(parts)})"


@dataclass(frozen=True, slots=True, kw_only=True, repr=False)
class User(_Serializable):
    """A Telegram user who opened the Mini App.

    Anyone can send a fake query string, so do not trust these values
    until validation passes.
    See https://core.telegram.org/bots/webapps#webappuser

    Parameters:
        id (``int``):
            Unique identifier for this user or bot. It has at most 52
            significant bits, so a 64-bit integer is safe for storing it.

        is_bot (``bool``, *optional*):
            True, if this user is a bot. Sent in the ``receiver`` field
            only.

        first_name (``str``):
            First name of the user or bot.

        last_name (``str``, *optional*):
            Last name of the user or bot.

        username (``str``, *optional*):
            Username of the user or bot, without the leading @.

        language_code (``str``, *optional*):
            IETF language tag of the user's language. Sent in the ``user``
            field only.

        is_premium (``bool``, *optional*):
            True, if this user has Telegram Premium.

        added_to_attachment_menu (``bool``, *optional*):
            True, if this user added the bot to their attachment menu.

        allows_write_to_pm (``bool``, *optional*):
            True, if this user allowed the bot to message them.

        photo_url (``str``, *optional*):
            URL of the user's profile photo, in .jpeg or .svg format.

        extra (``dict``, *optional*):
            Fields Telegram sent that this version does not know about,
            kept so a new field cannot break parsing. Ignored when
            comparing two users.
    """

    id: int
    is_bot: bool | None = None
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool | None = None
    added_to_attachment_menu: bool | None = None
    allows_write_to_pm: bool | None = None
    photo_url: str | None = None
    # compare=False because a mappingproxy is unhashable.
    extra: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        _require_int(self.id, "user.id")
        _require_str(self.first_name, "user.first_name")
        object.__setattr__(self, "extra", MappingProxyType(dict(self.extra)))

    @classmethod
    def from_dict(cls, data: Any, *, path: str = "user") -> User:
        """Build from a decoded JSON object, keeping unknown keys.

        `path` prefixes error messages, so a bad receiver reports
        "receiver.id" and not "user.id".
        """
        known, extra = _split_known(cls, data, path)
        for name in ("id", "first_name"):
            if known.get(name) is None:
                raise errors.MissingFieldError(f"{path}.{name}")
        return cls(**known, extra=extra)

    @classmethod
    def from_json(cls, value: str, *, path: str = "user") -> User:
        """Build from the raw JSON string Telegram sent."""
        return cls.from_dict(_loads(value, path), path=path)


@dataclass(frozen=True, slots=True, kw_only=True, repr=False)
class Chat(_Serializable):
    """A chat a Mini App was opened from.

    Only sent when the app is opened from the attachment menu.
    See https://core.telegram.org/bots/webapps#webappchat

    Parameters:
        id (``int``):
            Unique identifier for this chat. It has at most 52 significant
            bits, so a 64-bit integer is safe for storing it.

        type (``str``):
            Type of chat, usually "group", "supergroup" or "channel". Any
            string is accepted, because Telegram can add new ones, so do
            not match on it exhaustively.

        title (``str``):
            Title of the chat.

        username (``str``, *optional*):
            Username of the chat, without the leading @.

        photo_url (``str``, *optional*):
            URL of the chat photo, in .jpeg or .svg format.

        extra (``dict``, *optional*):
            Fields Telegram sent that this version does not know about,
            kept so a new field cannot break parsing. Ignored when
            comparing two chats.
    """

    id: int
    type: str
    title: str
    username: str | None = None
    photo_url: str | None = None
    extra: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        _require_int(self.id, "chat.id")
        _require_str(self.type, "chat.type")
        _require_str(self.title, "chat.title")
        object.__setattr__(self, "extra", MappingProxyType(dict(self.extra)))

    @classmethod
    def from_dict(cls, data: Any, *, path: str = "chat") -> Chat:
        """Build from a decoded JSON object, keeping unknown keys."""
        known, extra = _split_known(cls, data, path)
        for name in ("id", "type", "title"):
            if known.get(name) is None:
                raise errors.MissingFieldError(f"{path}.{name}")
        return cls(**known, extra=extra)

    @classmethod
    def from_json(cls, value: str, *, path: str = "chat") -> Chat:
        """Build from the raw JSON string Telegram sent."""
        return cls.from_dict(_loads(value, path), path=path)


@dataclass(frozen=True, slots=True, kw_only=True, repr=False)
class InitData:
    """Init data received from a Mini App, exactly as Telegram sent it.

    Built by ``parse()``; you do not construct this yourself. ``pairs``
    holds the decoded key/value pairs in their original order and is what
    gets hashed, so the bytes Telegram signed are never rebuilt from the
    fields below. That is what makes a field this version does not know
    about harmless.

    Parsing proves nothing about authenticity. Only trust these values
    after ``validate_by_hash()`` or ``validate_by_signature()`` passes.

    Parameters:
        query_string (``str``):
            The raw string Telegram sent, kept verbatim.

        pairs (``tuple``):
            The decoded key/value pairs, in the order they arrived. The
            only field used when comparing two objects.

        auth_date (``int``):
            Unix time when the Mini App was opened.

        hash (``str``):
            Hex HMAC-SHA256 of the data-check-string, keyed by the bot
            token.

        signature (``str``, *optional*):
            Base64url Ed25519 signature, for third-party validation. Only
            sent by clients from Bot API 8.0 onwards.

        query_id (``str``, *optional*):
            Session identifier, needed to call answerWebAppQuery.

        user (:obj:`~init_data_py.User`, *optional*):
            The user who opened the Mini App.

        receiver (:obj:`~init_data_py.User`, *optional*):
            The chat partner, for apps opened from the attachment menu in
            a private chat.

        chat (:obj:`~init_data_py.Chat`, *optional*):
            The chat the app was opened from, for apps opened from the
            attachment menu.

        chat_type (``str``, *optional*):
            Type of chat the app was opened from. Any string, because
            Telegram can add new ones.

        chat_instance (``str``, *optional*):
            Identifier of the chat the app was opened from. Always a
            string, never parse it as a number.

        start_param (``str``, *optional*):
            Value of the startapp query parameter. Attacker controlled,
            so treat it as untrusted text.

        can_send_after (``int``, *optional*):
            Seconds to wait before answerWebAppQuery may be called.
    """

    _REDACTED: ClassVar[frozenset[str]] = frozenset(
        {"hash", "signature", "query_id"}
    )

    query_string: str = field(compare=False)
    pairs: tuple[tuple[str, str], ...]
    auth_date: int = field(compare=False)
    hash: str = field(compare=False)
    signature: str | None = field(default=None, compare=False)
    query_id: str | None = field(default=None, compare=False)
    user: User | None = field(default=None, compare=False)
    receiver: User | None = field(default=None, compare=False)
    chat: Chat | None = field(default=None, compare=False)
    chat_type: str | None = field(default=None, compare=False)
    chat_instance: str | None = field(default=None, compare=False)
    start_param: str | None = field(default=None, compare=False)
    can_send_after: int | None = field(default=None, compare=False)

    @property
    def issued_at(self) -> datetime:
        """``auth_date`` as a timezone-aware UTC datetime."""
        return datetime.fromtimestamp(self.auth_date, timezone.utc)

    @property
    def extra(self) -> Mapping[str, str]:
        """Fields Telegram sent that this version does not know about."""
        return MappingProxyType(
            {k: v for k, v in self.pairs if k not in _PROJECTED_KEYS}
        )

    def get(self, key: str, default: str | None = None) -> str | None:
        """Return a raw value straight from the query string."""
        for name, value in self.pairs:
            if name == key:
                return value
        return default

    def to_query_string(self) -> str:
        """Return the raw string Telegram sent, unchanged."""
        return self.query_string

    def __repr__(self) -> str:
        # Init data is a bearer credential for as long as it is valid, so
        # a repr must never put a whole one in a log or a traceback.
        parts = []
        for f in fields(self):
            if f.name in ("query_string", "pairs"):
                continue
            value = getattr(self, f.name)
            if value is None:
                continue
            if f.name in self._REDACTED and isinstance(value, str):
                parts.append(f"{f.name}={_truncate(value)}")
            else:
                parts.append(f"{f.name}={value!r}")
        return "InitData(" + ", ".join(parts) + ")"


@dataclass(frozen=True, slots=True, kw_only=True)
class UnsignedInitData:
    """The fields to put into new init data, before signing it.

    Deliberately has no ``auth_date``, ``hash`` or ``signature``, because
    ``sign()`` produces those rather than accepting them. Pass one of
    these to ``sign()`` to get a signed query string back.

    Parameters:
        query_id (``str``, *optional*):
            Session identifier, needed to call answerWebAppQuery.

        user (:obj:`~init_data_py.User`, *optional*):
            The user the init data is for.

        receiver (:obj:`~init_data_py.User`, *optional*):
            The chat partner.

        chat (:obj:`~init_data_py.Chat`, *optional*):
            The chat the app was opened from.

        chat_type (``str``, *optional*):
            Type of chat the app was opened from.

        chat_instance (``str``, *optional*):
            Identifier of the chat the app was opened from.

        start_param (``str``, *optional*):
            Value of the startapp query parameter.

        can_send_after (``int``, *optional*):
            Seconds to wait before answerWebAppQuery may be called.

        extra (``dict``, *optional*):
            Any other fields to include, used verbatim. Lets you build
            init data carrying a field this version does not know about.
    """

    query_id: str | None = None
    user: User | None = None
    receiver: User | None = None
    chat: Chat | None = None
    chat_type: str | None = None
    chat_instance: str | None = None
    start_param: str | None = None
    can_send_after: int | None = None
    extra: Mapping[str, str] = field(default_factory=dict)

    def to_pairs(self) -> list[tuple[str, str]]:
        """Return the fields as query-string pairs, ready to be signed."""
        pairs: list[tuple[str, str]] = []
        for f in fields(self):
            if f.name == "extra":
                continue
            value = getattr(self, f.name)
            if value is None:
                continue
            if isinstance(value, _Serializable):
                pairs.append((f.name, value.to_json()))
            else:
                pairs.append((f.name, str(value)))
        pairs.extend(self.extra.items())
        return pairs
