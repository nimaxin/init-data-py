import base64
import unittest
import urllib.parse
from datetime import timedelta
from unittest import mock

from init_data_py import (
    TELEGRAM_PUBLIC_KEYS,
    _crypto,
    _ed25519,
    errors,
    is_ed25519_available,
    is_valid_by_signature,
    validate_by_signature,
)
from tests import vectors

BOT_ID = 7244657541
AUTH_DATE = vectors.PLAIN.auth_date
ISSUED_AT = vectors.PLAIN.issued_at


def make_signed(private_key, *, bot_id=BOT_ID, pairs=None):
    """Build init data signed with a throwaway key.

    Telegram's private key is not available, so third party validation
    can only be exercised against a key we generate ourselves.
    """
    pairs = pairs or [
        ("auth_date", str(AUTH_DATE)),
        ("user", '{"id":1,"first_name":"xin"}'),
        ("hash", "a" * 64),
    ]
    message = _crypto.build_data_check_string(
        pairs,
        exclude=_crypto.ED25519_EXCLUDED,
        prefix=f"{bot_id}:WebAppData\n",
    )
    signature = (
        base64.urlsafe_b64encode(private_key.sign(message.encode()))
        .decode()
        .rstrip("=")
    )
    return urllib.parse.urlencode([*pairs, ("signature", signature)])


@unittest.skipUnless(is_ed25519_available(), "requires the ed25519 extra")
class TestValidateBySignature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519

        cls.private_key = ed25519.Ed25519PrivateKey.generate()
        cls.public_key = (
            cls.private_key.public_key()
            .public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            )
            .hex()
        )
        cls.query_string = make_signed(cls.private_key)

    def test_accepts_a_valid_signature(self):
        init_data = validate_by_signature(
            self.query_string,
            BOT_ID,
            public_key=self.public_key,
            now=ISSUED_AT,
        )
        self.assertEqual(init_data.user.id, 1)

    def test_signature_is_unpadded_base64url(self):
        signature = urllib.parse.parse_qs(self.query_string)["signature"][0]
        self.assertNotIn("=", signature)

    def test_rejects_another_bots_id(self):
        # bot_id is part of the signed message, so it cannot be swapped.
        with self.assertRaises(errors.SignatureInvalidError):
            validate_by_signature(
                self.query_string,
                BOT_ID + 1,
                public_key=self.public_key,
                now=ISSUED_AT,
            )

    def test_rejects_a_tampered_payload(self):
        tampered = self.query_string.replace("xin", "eve")
        self.assertFalse(
            is_valid_by_signature(
                tampered, BOT_ID, public_key=self.public_key, now=ISSUED_AT
            )
        )

    def test_rejects_a_signature_from_another_key(self):
        self.assertFalse(
            is_valid_by_signature(self.query_string, BOT_ID, now=ISSUED_AT)
        )

    def test_rejects_expired_data(self):
        self.assertFalse(
            is_valid_by_signature(
                self.query_string,
                BOT_ID,
                public_key=self.public_key,
                now=ISSUED_AT + timedelta(days=2),
            )
        )

    def test_requires_a_signature_field(self):
        with self.assertRaises(errors.SignatureMissingError):
            validate_by_signature(
                vectors.PLAIN.query_string,
                BOT_ID,
                public_key=self.public_key,
                expires_in=0,
            )

    def test_error_carries_context(self):
        with self.assertRaises(errors.SignatureInvalidError) as caught:
            validate_by_signature(
                self.query_string,
                BOT_ID + 1,
                public_key=self.public_key,
                now=ISSUED_AT,
            )
        self.assertEqual(caught.exception.bot_id, BOT_ID + 1)
        self.assertEqual(caught.exception.environment, "prod")
        self.assertTrue(caught.exception.third_party)

    def test_rejects_an_unknown_environment(self):
        with self.assertRaises(ValueError):
            validate_by_signature(
                self.query_string,
                BOT_ID,
                environment="staging",
                now=ISSUED_AT,
            )


class TestPublicKeys(unittest.TestCase):
    def test_both_environments_carry_a_32_byte_key(self):
        self.assertEqual(set(TELEGRAM_PUBLIC_KEYS), {"prod", "test"})
        for environment, key in TELEGRAM_PUBLIC_KEYS.items():
            with self.subTest(environment=environment):
                self.assertEqual(len(bytes.fromhex(key)), 32)


class TestMissingExtra(unittest.TestCase):
    """A missing extra must raise, never look like a rejected signature."""

    def test_missing_dependency_is_not_swallowed(self):
        missing = errors.MissingDependencyError(
            "cryptography", extra="ed25519", feature="Test"
        )
        with mock.patch.object(_ed25519, "_load", side_effect=missing):
            with self.assertRaises(errors.MissingDependencyError):
                is_valid_by_signature(
                    "auth_date=1&hash=" + "a" * 64 + "&signature=AbC",
                    BOT_ID,
                    expires_in=0,
                )

    def test_it_is_outside_the_rejection_branch(self):
        self.assertNotIsInstance(
            errors.MissingDependencyError(
                "cryptography", extra="ed25519", feature="Test"
            ),
            errors.InvalidInitDataError,
        )

    def test_it_is_also_an_import_error(self):
        self.assertIsInstance(
            errors.MissingDependencyError(
                "cryptography", extra="ed25519", feature="Test"
            ),
            ImportError,
        )
