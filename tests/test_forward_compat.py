import unittest

from init_data_py import (
    UnsignedInitData,
    User,
    is_valid_by_hash,
    parse,
    sign,
    validate_by_hash,
)
from tests import vectors


class TestForwardCompatibility(unittest.TestCase):
    """Fields Telegram adds later must not break anything.

    0.2.x raised UnexpectedFormatError for an unknown top level field and
    a bare TypeError for an unknown field inside user.
    """

    def test_an_unknown_top_level_field_is_kept(self):
        query_string = vectors.PLAIN.query_string + "&brand_new_field=42"
        init_data = parse(query_string)

        self.assertEqual(init_data.get("brand_new_field"), "42")
        self.assertEqual(dict(init_data.extra), {"brand_new_field": "42"})
        self.assertEqual(init_data.to_query_string(), query_string)

    def test_an_unknown_user_field_is_kept(self):
        query_string = (
            "auth_date=1&hash=" + "a" * 64 + "&user=%7B%22id%22%3A1%2C%22first"
            "_name%22%3A%22x%22%2C%22brand_new%22%3A9%7D"
        )
        self.assertEqual(
            dict(parse(query_string).user.extra), {"brand_new": 9}
        )

    def test_an_unknown_field_is_covered_by_the_hash(self):
        vector = vectors.PLAIN
        query_string = sign(
            UnsignedInitData(
                user=User(id=1, first_name="x"), extra={"brand_new": "42"}
            ),
            vector.bot_token,
            auth_date=vector.auth_date,
        )
        init_data = validate_by_hash(
            query_string, vector.bot_token, now=vector.issued_at
        )
        self.assertEqual(dict(init_data.extra), {"brand_new": "42"})

        # Adding one afterwards changes what was signed, so it must fail.
        self.assertFalse(
            is_valid_by_hash(
                query_string + "&added_later=1",
                vector.bot_token,
                now=vector.issued_at,
            )
        )

    def test_an_unknown_chat_type_is_accepted(self):
        query_string = (
            "auth_date=1&hash=" + "a" * 64 + "&chat_type=brand_new_kind"
        )
        self.assertEqual(parse(query_string).chat_type, "brand_new_kind")
