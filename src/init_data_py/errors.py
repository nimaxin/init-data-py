from __future__ import annotations

from datetime import datetime, timedelta

__all__ = [
    "InitDataError",
    "InvalidInitDataError",
    "ParseError",
    "MalformedQueryStringError",
    "MalformedAuthHeaderError",
    "DuplicateFieldError",
    "MissingFieldError",
    "AuthDateMissingError",
    "HashMissingError",
    "MalformedFieldError",
    "AuthenticityError",
    "HashInvalidError",
    "SignatureMissingError",
    "SignatureInvalidError",
    "ExpiredError",
    "MissingDependencyError",
    # Deprecated 0.2.x aliases.
    "InitDataPyError",
    "UnexpectedFormatError",
    "SignMissingError",
    "SignInvalidError",
]

_MAX_VALUE_LEN = 64


class InitDataError(Exception):
    """Base class for every error raised by this library."""


class InvalidInitDataError(InitDataError):
    """Base class for failures caused by untrusted input.

    ``is_valid()`` and ``is_valid_third_party()`` return ``False`` for
    exactly this subtree. Every other exception propagates, so a bug or a
    missing dependency can never be mistaken for a failed check.
    """


class ParseError(InvalidInitDataError):
    """The init data is not well-formed."""

    def __init__(self, message: str = "init data has an unexpected format"):
        super().__init__(message)


class MalformedQueryStringError(ParseError):
    """The query string could not be decoded into key/value pairs."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"malformed init data query string: {reason}")


class MalformedAuthHeaderError(ParseError):
    """An Authorization header did not carry the expected credential."""

    def __init__(self, *, scheme: str = "tma") -> None:
        self.scheme = scheme
        super().__init__(
            f"authorization header is not a valid {scheme!r} credential"
        )


class DuplicateFieldError(ParseError):
    """A field appeared more than once.

    Telegram never sends duplicates, so this is parameter pollution: the
    signed pair and the pair the caller reads could otherwise differ.
    """

    def __init__(self, field: str, *, count: int = 2) -> None:
        self.field = field
        self.count = count
        super().__init__(f"{field!r} appears {count} times in the init data")


class MissingFieldError(ParseError):
    """A required field is absent."""

    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(f"{field!r} is missing")


class AuthDateMissingError(MissingFieldError):
    """``auth_date`` is absent."""

    def __init__(self, field: str = "auth_date") -> None:
        super().__init__(field)


class HashMissingError(MissingFieldError):
    """``hash`` is absent."""

    def __init__(self, field: str = "hash") -> None:
        super().__init__(field)

    @property
    def third_party(self) -> bool:
        return False


class MalformedFieldError(ParseError):
    """A field is present but its value is unusable."""

    def __init__(self, field: str, *, value: str, reason: str) -> None:
        self.field = field
        self.value = value
        self.reason = reason
        shown = value[:_MAX_VALUE_LEN]
        if len(value) > _MAX_VALUE_LEN:
            shown += "..."
        super().__init__(f"{field!r} is invalid ({reason}): {shown!r}")


class AuthenticityError(InvalidInitDataError):
    """The init data is well-formed but not provably from Telegram."""


class HashInvalidError(AuthenticityError):
    """``hash`` does not match the data signed with the bot token."""

    def __init__(self) -> None:
        super().__init__("hash is invalid")

    @property
    def third_party(self) -> bool:
        return False


class SignatureMissingError(AuthenticityError):
    """``signature`` is absent, so third-party validation is impossible.

    Not a ``MissingFieldError``: clients older than Bot API 8.0 legitimately
    omit ``signature``, so it is only an error once third-party validation
    is actually requested.
    """

    def __init__(self) -> None:
        super().__init__("'signature' is missing")

    @property
    def third_party(self) -> bool:
        return True


class SignatureInvalidError(AuthenticityError):
    """``signature`` failed Ed25519 verification."""

    def __init__(self, *, bot_id: int, environment: str = "prod") -> None:
        self.bot_id = bot_id
        self.environment = environment
        super().__init__(
            f"signature is invalid for bot {bot_id} in the "
            f"{environment} environment"
        )

    @property
    def third_party(self) -> bool:
        return True


class ExpiredError(InvalidInitDataError):
    """The init data is authentic but older than the allowed lifetime."""

    def __init__(
        self,
        *,
        issued_at: datetime,
        expires_at: datetime,
        now: datetime,
    ) -> None:
        self.issued_at = issued_at
        self.expires_at = expires_at
        self.now = now
        super().__init__(
            f"init data is expired: issued at {issued_at.isoformat()}, "
            f"expired at {expires_at.isoformat()}, now {now.isoformat()}"
        )

    @property
    def expired_for(self) -> timedelta:
        return self.now - self.expires_at


class MissingDependencyError(InitDataError, ImportError):
    """An optional dependency is required but not installed.

    Deliberately outside :class:`InvalidInitDataError` so ``is_valid_*``
    raises instead of returning ``False`` -- a missing dependency must
    never look like a failed check.
    """

    def __init__(self, package: str, *, extra: str, feature: str) -> None:
        self.package = package
        self.extra = extra
        self.feature = feature
        super().__init__(
            f"{feature} requires the {package!r} package, which is not "
            f'installed. Install it with: pip install "init-data-py'
            f'[{extra}]"'
        )


# Deprecated 0.2.x names. These are the same class objects, so existing
# ``except`` clauses keep matching. Warnings are wired up in a later step,
# once the legacy modules that still raise them are gone.
InitDataPyError = InitDataError
UnexpectedFormatError = ParseError
SignMissingError = HashMissingError
SignInvalidError = HashInvalidError
