import unittest

from init_data_py import (
    UnsignedInitData,
    User,
    hash_token,
    parse,
    sign,
    validate_by_hash,
)
from tests import vectors


class TestSign(unittest.TestCase):
    def test_reproduces_a_known_hash(self):
        query_string = sign(
            UnsignedInitData(
                query_id="AAF03wc0AgAAAHTfBzROOCVW",
                user=User(
                    id=5167898484,
                    first_name="xin",
                    last_name="",
                    username="pvnimaxin",
                    language_code="en",
                    allows_write_to_pm=True,
                ),
            ),
            vectors.PLAIN.bot_token,
            auth_date=vectors.PLAIN.auth_date,
        )
        self.assertEqual(
            parse(query_string).hash, parse(vectors.PLAIN.query_string).hash
        )

    def test_signed_data_validates(self):
        query_string = sign(
            UnsignedInitData(user=User(id=1, first_name="xin")),
            vectors.PLAIN.bot_token,
            auth_date=vectors.PLAIN.auth_date,
        )
        init_data = validate_by_hash(
            query_string, vectors.PLAIN.bot_token, now=vectors.PLAIN.issued_at
        )
        self.assertEqual(init_data.user.id, 1)

    def test_a_slash_in_start_param_survives(self):
        # 0.2.x escaped every slash in the data-check-string, which made
        # this hash something Telegram would never produce.
        query_string = sign(
            UnsignedInitData(
                user=User(id=1, first_name="a"), start_param="ref/abc"
            ),
            vectors.PLAIN.bot_token,
            auth_date=vectors.PLAIN.auth_date,
        )
        init_data = validate_by_hash(
            query_string, vectors.PLAIN.bot_token, now=vectors.PLAIN.issued_at
        )
        self.assertEqual(init_data.start_param, "ref/abc")

    def test_signs_from_a_token_digest(self):
        query_string = sign(
            {"query_id": "AAF0"},
            hash_token(vectors.PLAIN.bot_token),
            auth_date=vectors.PLAIN.auth_date,
            token_hashed=True,
        )
        self.assertTrue(
            validate_by_hash(
                query_string,
                vectors.PLAIN.bot_token,
                now=vectors.PLAIN.issued_at,
            )
        )

    def test_rejects_fields_it_produces(self):
        for field in ("auth_date", "hash"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    sign({field: "1"}, vectors.PLAIN.bot_token)
