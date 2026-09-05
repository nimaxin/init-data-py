"""Tools for using and validating Telegram Mini App init data."""

from init_data_py import errors
from init_data_py.models import Chat, InitData, UnsignedInitData, User
from init_data_py.parsing import parse, strip_auth_header
from init_data_py.signing import sign
from init_data_py.validation import (
    DEFAULT_EXPIRES_IN,
    TELEGRAM_PUBLIC_KEYS,
    Environment,
    ExpiresIn,
    hash_token,
    is_ed25519_available,
    is_valid_by_hash,
    is_valid_by_signature,
    validate_by_hash,
    validate_by_signature,
)

__version__ = "1.0.0rc1"

__all__ = [
    "Chat",
    "DEFAULT_EXPIRES_IN",
    "Environment",
    "ExpiresIn",
    "InitData",
    "TELEGRAM_PUBLIC_KEYS",
    "UnsignedInitData",
    "User",
    "errors",
    "hash_token",
    "is_ed25519_available",
    "is_valid_by_hash",
    "is_valid_by_signature",
    "parse",
    "sign",
    "strip_auth_header",
    "validate_by_hash",
    "validate_by_signature",
]
