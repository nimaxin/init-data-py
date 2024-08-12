import unittest

from init_data_py import InitData


class TestToQueryString(unittest.TestCase):
    def test_from_query_string_to_query_string(self):
        query_string = "query_id=AAF03wc0AgAAAHTfBzROOCVW&user=%7B%22id%22%3A5167898484%2C%22first_name%22%3A%22xin%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22pvnimaxin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1722938610&hash=8654c8c617c143abf656f4f159be2539880a56f58c2d9be622f90c0346aa162b"
        init_data = InitData.parse(query_string)
        generated_query_string = init_data.to_query_string()
        self.assertEqual(generated_query_string, query_string)
