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
