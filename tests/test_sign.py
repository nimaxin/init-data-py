import unittest

from init_data_py import InitData, types


class TestSignInitData(unittest.TestCase):
    def setUp(self) -> None:
        self.init_data = InitData(
            query_id="AAF03wc0AgAAAHTfBzROOCVW",
            user=types.User(
                id=5167898484,
                first_name="xin",
                last_name="",
                username="pvnimaxin",
                language_code="en",
                allows_write_to_pm=True,
            ),
        )
        self.bot_token = "7244657541:AAEgqk0HDC3WD5cdbnGMdd6L0TJ74FDp97Y"

        self.expected_auth_date = 1722938610
        self.expected_hash = (
            "8654c8c617c143abf656f4f159be2539880a56f58c2d9be622f90c0346aa162b"
        )

    def test_sign(self):
        init_data = self.init_data.sign(
            bot_token=self.bot_token,
            auth_date=self.expected_auth_date,
        )
        self.assertEqual(self.init_data.hash, self.expected_hash)
        self.assertEqual(self.init_data.auth_date, self.expected_auth_date)
        self.assertIsInstance(init_data, InitData)
