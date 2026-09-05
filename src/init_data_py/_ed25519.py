"""Ed25519 verification, and the only place cryptography is touched.

The import happens inside the functions, so importing this package never
pulls in cryptography and the core stays dependency free.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from init_data_py import errors

#: Telegram's Ed25519 public keys, hex encoded, by environment.
TELEGRAM_PUBLIC_KEYS: Mapping[str, str] = MappingProxyType(
    {
        "prod": (
            "e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d"
        ),
        "test": (
            "40055058a4ee38156a06562e52eece92a771bcd8346a8c4615cb7376eddf72ec"
        ),
    }
)


def _load() -> tuple[Any, type[BaseException]]:
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric import ed25519
    except ImportError as exc:
        raise errors.MissingDependencyError(
            "cryptography",
            extra="ed25519",
            feature="Third party signature validation",
        ) from exc
    return ed25519.Ed25519PublicKey, InvalidSignature


def is_available() -> bool:
    """Return whether third party validation can run in this install."""
    try:
        _load()
    except errors.MissingDependencyError:
        return False
    return True


def verify(public_key: bytes, signature: bytes, message: bytes) -> bool:
    """Return whether ``signature`` covers ``message`` under the key.

    Raises:
        MissingDependencyError: The ``ed25519`` extra is not installed.
        ValueError: The public key is not a valid Ed25519 key.
    """
    public_key_cls, invalid_signature = _load()
    key = public_key_cls.from_public_bytes(public_key)
    try:
        key.verify(signature, message)
    except invalid_signature:
        return False
    return True
