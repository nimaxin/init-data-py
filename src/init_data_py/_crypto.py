"""Hashing primitives shared by validation and signing.

Everything here works on the raw key/value pairs decoded from the query
string. Nothing rebuilds a value from a parsed model, which is what makes
the result match the bytes Telegram actually signed.
"""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import Collection, Iterable

#: Constant Telegram keys the bot token with.
_WEB_APP_DATA = b"WebAppData"

#: Keys left out of the data-check-string when hashing with the bot token.
#:
#: Only `hash` is excluded, because the hash cannot cover itself.
#: `signature` is a normal signed field here, and is left out only on the
#: Ed25519 path, where the spec excludes it explicitly.
#: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
HMAC_EXCLUDED: frozenset[str] = frozenset({"hash"})

#: Keys left out when verifying Telegram's Ed25519 signature.
ED25519_EXCLUDED: frozenset[str] = frozenset({"hash", "signature"})


def secret_key(bot_token: str, *, token_hashed: bool = False) -> bytes:
    """Derive the key that init data hashes are computed with.

    Parameters:
        bot_token (``str``):
            The bot token, or its hex digest when ``token_hashed`` is set.

        token_hashed (``bool``, *optional*):
            Treat ``bot_token`` as the output of ``hash_token()``, so the
            real token never has to reach the validating service.

    Returns:
        ``bytes``: The key to compute the data-check-string HMAC with.
    """
    if token_hashed:
        return bytes.fromhex(bot_token)
    return hmac.digest(_WEB_APP_DATA, bot_token.encode(), hashlib.sha256)


def hash_token(bot_token: str) -> str:
    """Return the hex digest of a bot token, for ``token_hashed=True``."""
    return secret_key(bot_token).hex()


def build_data_check_string(
    pairs: Iterable[tuple[str, str]],
    *,
    exclude: Collection[str] = HMAC_EXCLUDED,
    prefix: str = "",
) -> str:
    """Join the pairs into the string Telegram signs.

    Parameters:
        pairs (``iterable``):
            Decoded key/value pairs, used exactly as they were received.

        exclude (``collection``, *optional*):
            Keys to leave out. See ``HMAC_EXCLUDED`` and
            ``ED25519_EXCLUDED``.

        prefix (``str``, *optional*):
            Text to put in front, used by the Ed25519 path to prepend
            ``"<bot_id>:WebAppData\n"``.

    Returns:
        ``str``: ``key=value`` lines, sorted, separated by newlines.
    """
    # Sort the joined lines, not the keys. The two orders differ when one
    # key is a prefix of another, because "=" sorts below letters but
    # above digits.
    lines = sorted(
        f"{key}={value}" for key, value in pairs if key not in exclude
    )
    return prefix + "\n".join(lines)


def compute_hash(data_check_string: str, key: bytes) -> str:
    """Return the hex HMAC-SHA256 of the data-check-string."""
    return hmac.digest(key, data_check_string.encode(), hashlib.sha256).hex()
