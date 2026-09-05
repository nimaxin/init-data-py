import unittest
from datetime import timedelta

from init_data_py import errors, is_valid_by_hash, parse, validate_by_hash
from tests import vectors


class TestValidateByHash(unittest.TestCase):
    def test_accepts_real_init_data(self):
        for vector in vectors.ALL:
            with self.subTest(auth_date=vector.auth_date):
                init_data = validate_by_hash(
                    vector.query_string, vector.bot_token, now=vector.issued_at
                )
                self.assertEqual(
                    init_data.to_query_string(), vector.query_string
                )

    def test_accepts_an_already_parsed_object(self):
        vector = vectors.PLAIN
        init_data = parse(vector.query_string)
        self.assertIs(
            validate_by_hash(
                init_data, vector.bot_token, now=vector.issued_at
            ),
            init_data,
        )

    def test_rejects_a_tampered_hash(self):
        vector = vectors.PLAIN
        tampered = vector.query_string[:-1] + (
            "c" if vector.query_string[-1] != "c" else "d"
        )
        with self.assertRaises(errors.HashInvalidError):
            validate_by_hash(tampered, vector.bot_token, now=vector.issued_at)

    def test_rejects_the_wrong_token(self):
        vector = vectors.PLAIN
        with self.assertRaises(errors.HashInvalidError):
            validate_by_hash(
                vector.query_string, "1:WRONG", now=vector.issued_at
            )

    def test_expiry_is_on_by_default(self):
        vector = vectors.PLAIN
        self.assertFalse(
            is_valid_by_hash(vector.query_string, vector.bot_token)
        )

    def test_expiry_boundaries(self):
        vector = vectors.PLAIN
        cases = [
            (timedelta(hours=1), True),
            (timedelta(seconds=86400), True),
            (timedelta(seconds=86401), False),
        ]
        for offset, expected in cases:
            with self.subTest(offset=offset):
                self.assertEqual(
                    is_valid_by_hash(
                        vector.query_string,
                        vector.bot_token,
                        now=vector.issued_at + offset,
                    ),
                    expected,
                )

    def test_expiry_can_be_switched_off(self):
        vector = vectors.PLAIN
        for expires_in in (0, None):
            with self.subTest(expires_in=expires_in):
                self.assertTrue(
                    is_valid_by_hash(
                        vector.query_string,
                        vector.bot_token,
                        expires_in=expires_in,
                    )
                )

    def test_expiry_accepts_a_timedelta(self):
        vector = vectors.PLAIN
        self.assertTrue(
            is_valid_by_hash(
                vector.query_string,
                vector.bot_token,
                expires_in=timedelta(hours=2),
                now=vector.issued_at + timedelta(hours=1),
            )
        )

    def test_expired_error_carries_the_times(self):
        vector = vectors.PLAIN
        now = vector.issued_at + timedelta(hours=30)
        with self.assertRaises(errors.ExpiredError) as caught:
            validate_by_hash(vector.query_string, vector.bot_token, now=now)

        error = caught.exception
        self.assertEqual(error.issued_at, vector.issued_at)
        self.assertEqual(error.now, now)
        self.assertEqual(error.expired_for, timedelta(hours=6))

    def test_is_valid_hides_rejections_but_not_mistakes(self):
        vector = vectors.PLAIN
        self.assertFalse(
            is_valid_by_hash(
                vector.query_string, "1:WRONG", now=vector.issued_at
            )
        )
        with self.assertRaises(ValueError):
            is_valid_by_hash(
                vector.query_string, vector.bot_token, expires_in=-1
            )


class TestSignatureTakesPartInTheHash(unittest.TestCase):
    """A signature field must be hashed, not skipped.

    Only hash is left out of the data-check-string. Dropping signature
    too would break every current client, and the mistake is invisible
    against older captures that have no signature at all.
    """

    def test_real_signed_init_data_validates_by_hash(self):
        for vector in vectors.SIGNED_ALL:
            with self.subTest(auth_date=vector.auth_date):
                init_data = validate_by_hash(
                    vector.query_string, vector.bot_token, expires_in=0
                )
                self.assertIsNotNone(init_data.signature)

    def test_dropping_the_signature_changes_the_hash(self):
        vector = vectors.SIGNED_ALL[0]
        without = "&".join(
            part
            for part in vector.query_string.split("&")
            if not part.startswith("signature=")
        )
        self.assertFalse(
            is_valid_by_hash(without, vector.bot_token, expires_in=0)
        )
