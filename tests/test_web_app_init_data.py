import pytest
from init_data_py import WebAppInitData, WebAppUser


def test_object_initialization():
    assert True


@pytest.mark.parametrize(
    "query_string, init_data_unsafe",
    [
        (
            "query_id=AAF03wc0AgAAAHTfBzQGXB7v&user=%7B%22id%22%3A5167898484%2C%22first_name%22%3A%22xin%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22pvnimaxin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FYpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1zFgIVth6Wzacz7P2nGNCcp9j.svg%22%7D&auth_date=1731875744&signature=b1XX1Z-3ItQ4jvVRCCCaR-JeDve525ROkhbu_ZAt2tczwNBMR1F4oubq9p_OD02MuwcJxzprWAOjGutw0OskCw&hash=b29843e9031f21accbb4b59339241be79bbc22fbb566774b0641474567ffe1d5",
            WebAppInitData(
                query_id="AAF03wc0AgAAAHTfBzQGXB7v",
                user=WebAppUser(
                    id=5167898484,
                    first_name="xin",
                    last_name="",
                    username="pvnimaxin",
                    language_code="en",
                    allows_write_to_pm=True,
                    photo_url="https://t.me/i/userpic/320/YpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1zFgIVth6Wzacz7P2nGNCcp9j.svg",
                ),
                auth_date=1731875744,
                signature="b1XX1Z-3ItQ4jvVRCCCaR-JeDve525ROkhbu_ZAt2tczwNBMR1F4oubq9p_OD02MuwcJxzprWAOjGutw0OskCw",
                hash="b29843e9031f21accbb4b59339241be79bbc22fbb566774b0641474567ffe1d5",
            ),
        )
    ],
)
def test_method_from_query_string(query_string, init_data_unsafe):
    assert init_data_unsafe == WebAppInitData.from_query_string(query_string)


@pytest.mark.parametrize(
    "query_string, init_data_unsafe",
    [
        (
            "query_id=AAF03wc0AgAAAHTfBzQGXB7v&user=%7B%22id%22%3A5167898484%2C%22first_name%22%3A%22xin%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22pvnimaxin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FYpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1zFgIVth6Wzacz7P2nGNCcp9j.svg%22%7D&auth_date=1731875744&signature=b1XX1Z-3ItQ4jvVRCCCaR-JeDve525ROkhbu_ZAt2tczwNBMR1F4oubq9p_OD02MuwcJxzprWAOjGutw0OskCw&hash=b29843e9031f21accbb4b59339241be79bbc22fbb566774b0641474567ffe1d5",
            WebAppInitData(
                query_id="AAF03wc0AgAAAHTfBzQGXB7v",
                user=WebAppUser(
                    id=5167898484,
                    first_name="xin",
                    last_name="",
                    username="pvnimaxin",
                    language_code="en",
                    allows_write_to_pm=True,
                    photo_url="https://t.me/i/userpic/320/YpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1zFgIVth6Wzacz7P2nGNCcp9j.svg",
                ),
                auth_date=1731875744,
                signature="b1XX1Z-3ItQ4jvVRCCCaR-JeDve525ROkhbu_ZAt2tczwNBMR1F4oubq9p_OD02MuwcJxzprWAOjGutw0OskCw",
                hash="b29843e9031f21accbb4b59339241be79bbc22fbb566774b0641474567ffe1d5",
            ),
        )
    ],
)
def test_method_to_query_string(query_string, init_data_unsafe):
    assert init_data_unsafe.to_query_string() == query_string


@pytest.mark.parametrize(
    "init_data_unsafe, init_data_unsafe_signed, bot_token, auth_date",
    [
        (
            WebAppInitData(
                query_id="AAF03wc0AgAAAHTfBzQGXB7v",
                user=WebAppUser(
                    id=5167898484,
                    first_name="xin",
                    last_name="",
                    username="pvnimaxin",
                    language_code="en",
                    allows_write_to_pm=True,
                    photo_url="https://t.me/i/userpic/320/YpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1zFgIVth6Wzacz7P2nGNCcp9j.svg",
                ),
                auth_date=1731875744,
                signature="b1XX1Z-3ItQ4jvVRCCCaR-JeDve525ROkhbu_ZAt2tczwNBMR1F4oubq9p_OD02MuwcJxzprWAOjGutw0OskCw",
            ),
            WebAppInitData(
                query_id="AAF03wc0AgAAAHTfBzQGXB7v",
                user=WebAppUser(
                    id=5167898484,
                    first_name="xin",
                    last_name="",
                    username="pvnimaxin",
                    language_code="en",
                    allows_write_to_pm=True,
                    photo_url="https://t.me/i/userpic/320/YpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1zFgIVth6Wzacz7P2nGNCcp9j.svg",
                ),
                auth_date=1731875744,
                signature="b1XX1Z-3ItQ4jvVRCCCaR-JeDve525ROkhbu_ZAt2tczwNBMR1F4oubq9p_OD02MuwcJxzprWAOjGutw0OskCw",
                hash="b29843e9031f21accbb4b59339241be79bbc22fbb566774b0641474567ffe1d5",
            ),
            "7244657541:AAFTqbgwOQFrGF6zzp0pZoMYB-06wC5mtnU",
            1731875744,
        )
    ],
)
def test_method_sign(init_data_unsafe, init_data_unsafe_signed, bot_token, auth_date):
    assert (
        init_data_unsafe.sign(bot_token, auth_date).hash == init_data_unsafe_signed.hash
    )
