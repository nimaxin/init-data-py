import time
import unittest

from init_data_py import InitData, errors, types


class TestValidateInitData(unittest.TestCase):
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
            auth_date=1722938610,
            hash="8654c8c617c143abf656f4f159be2539880a56f58c2d9be622f90c0346aa162b",
        )
        self.bot_token = "7244657541:AAEgqk0HDC3WD5cdbnGMdd6L0TJ74FDp97Y"

        self.utf8_qs = "query_id=AAF2GVE4AwAAAHYZUTgHczdc&user=%7B%22id%22%3A7387289974%2C%22first_name%22%3A%22%D0%90%D1%80%D1%82%D1%91%D0%BC%22%2C%22last_name%22%3A%22%D0%9E%D0%BD%D1%83%D1%84%D1%80%D0%B8%D0%B9%22%2C%22username%22%3A%22typexin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1724048856&hash=53b22bc70a748dae613a5aa91890b387b9cc0356c5dcffca173816b6e40a17e5"

    def test_utf8_support(self):
        query_string = "query_id=AAF2GVE4AwAAAHYZUTgHczdc&user=%7B%22id%22%3A7387289974%2C%22first_name%22%3A%22%D0%90%D1%80%D1%82%D1%91%D0%BC%22%2C%22last_name%22%3A%22%D0%9E%D0%BD%D1%83%D1%84%D1%80%D0%B8%D0%B9%22%2C%22username%22%3A%22typexin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1724048856&hash=53b22bc70a748dae613a5aa91890b387b9cc0356c5dcffca173816b6e40a17e5"
        bot_token = "7244657541:AAHAJP25XehV6N02kiLLAEi2el-xLsSw29w"
        init_data = InitData.parse(query_string)
        self.assertTrue(init_data.validate(bot_token))

    def test_valid_init_data(self):
        self.assertTrue(self.init_data.validate(self.bot_token))

    def test_invalid_init_data(self):
        self.init_data.hash = "invalid hash"
        with self.assertRaises(errors.SignInvalidError):
            self.init_data.validate(self.bot_token)

    def test_sign_missing_init_data(self):
        self.init_data.hash = None
        with self.assertRaises(errors.SignMissingError):
            self.init_data.validate(self.bot_token)

    def test_auth_date_missing_init_data(self):
        self.init_data.auth_date = None
        with self.assertRaises(errors.AuthDateMissingError):
            self.init_data.validate(self.bot_token)

    def test_expired_init_data(self):
        lifetime = 10
        self.init_data.auth_date = int(time.time()) - lifetime
        with self.assertRaises(errors.ExpiredError):
            self.init_data.validate(self.bot_token, lifetime)
