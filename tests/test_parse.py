import unittest

from init_data_py import InitData, errors, types


class TestParseInitData(unittest.TestCase):
    def setUp(self) -> None:
        self.query_string = "query_id=AAF03wc0AgAAAHTfBzROOCVW&user=%7B%22id%22%3A5167898484%2C%22first_name%22%3A%22xin%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22pvnimaxin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1722938610&hash=8654c8c617c143abf656f4f159be2539880a56f58c2d9be622f90c0346aa162b"
        self.expected_init_data = InitData(
            query_id="AAF03wc0AgAAAHTfBzROOCVW",
            user=types.User(
                id=5167898484,
                first_name="xin",
                last_name="",
                username="pvnimaxin",
                language_code="en",
                allows_write_to_pm=True,
            ),
            auth_date=1722938610,
            hash="8654c8c617c143abf656f4f159be2539880a56f58c2d9be622f90c0346aa162b",
        )

    def test_valid_query_string(self):
        init_data = InitData.parse(self.query_string)
        self.assertEqual(init_data, self.expected_init_data)

    def test_invalid_query_string(self):
        with self.assertRaises(errors.UnexpectedFormatError):
            InitData.parse(self.query_string.upper())
