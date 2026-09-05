import unittest

from init_data_py import errors, parse
from tests import vectors


class TestParse(unittest.TestCase):
    def test_reads_every_field(self):
        init_data = parse(vectors.PLAIN.query_string)

        self.assertEqual(init_data.auth_date, 1722938610)
        self.assertEqual(init_data.query_id, "AAF03wc0AgAAAHTfBzROOCVW")
        self.assertEqual(init_data.user.id, 5167898484)
        self.assertEqual(init_data.user.first_name, "xin")
        self.assertEqual(init_data.user.last_name, "")
        self.assertEqual(init_data.user.username, "pvnimaxin")
        self.assertTrue(init_data.user.allows_write_to_pm)

    def test_keeps_the_query_string_verbatim(self):
        for vector in vectors.ALL:
            with self.subTest(auth_date=vector.auth_date):
                init_data = parse(vector.query_string)
                self.assertEqual(
                    init_data.to_query_string(), vector.query_string
                )

    def test_accepts_bytes(self):
        self.assertEqual(
            parse(vectors.PLAIN.query_string.encode()),
            parse(vectors.PLAIN.query_string),
        )

    def test_issued_at_is_utc(self):
        init_data = parse(vectors.PLAIN.query_string)
        self.assertEqual(init_data.issued_at, vectors.PLAIN.issued_at)
        self.assertIsNotNone(init_data.issued_at.tzinfo)

    def test_rejects_unusable_input(self):
        cases = [
            ("", errors.MalformedQueryStringError),
            ("auth_date=1&broken", errors.MalformedQueryStringError),
            ("auth_date=1", errors.HashMissingError),
            ("hash=" + "a" * 64, errors.AuthDateMissingError),
            ("auth_date=abc&hash=" + "a" * 64, errors.MalformedFieldError),
            ("auth_date=1&hash=short", errors.MalformedFieldError),
            (
                f"auth_date=1&hash={'a' * 64}&hash={'b' * 64}",
                errors.DuplicateFieldError,
            ),
        ]
        for query_string, expected in cases:
            with self.subTest(query_string=query_string[:40]):
                with self.assertRaises(expected):
                    parse(query_string)

    def test_wrong_case_field_names_lose_the_required_ones(self):
        with self.assertRaises(errors.AuthDateMissingError):
            parse(vectors.PLAIN.query_string.upper())
