from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from types import MappingProxyType
from typing import Any

from init_data_py import errors

__all__ = ["Chat", "User"]


def _require_int(value: Any, name: str) -> None:
    # bool is a subclass of int, so isinstance(True, int) is True.
    if not isinstance(value, int) or isinstance(value, bool):
        raise errors.MalformedFieldError(
            name, value=repr(value), reason="not an integer"
        )


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


@dataclass(frozen=True, slots=True, kw_only=True)
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


@dataclass(frozen=True, slots=True, kw_only=True)
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
