import pytest
from init_data_py import InitData


@pytest.mark.parametrize(
    "query_string, bot_token",
    [
        (
            "query_id=AAF03wc0AgAAAHTfBzQGXB7v&user=%7B%22id%22%3A5167898484%2C%22first_name%22%3A%22xin%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22pvnimaxin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FYpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1zFgIVth6Wzacz7P2nGNCcp9j.svg%22%7D&auth_date=1731875744&signature=b1XX1Z-3ItQ4jvVRCCCaR-JeDve525ROkhbu_ZAt2tczwNBMR1F4oubq9p_OD02MuwcJxzprWAOjGutw0OskCw&hash=b29843e9031f21accbb4b59339241be79bbc22fbb566774b0641474567ffe1d5",
            "7244657541:AAFTqbgwOQFrGF6zzp0pZoMYB-06wC5mtnU",
        )
    ],
)
def test_init_data__valid(query_string, bot_token):
    init_data = InitData(query_string)
    assert init_data.validate_by_hash(bot_token)


def test_method_validate_by_signature():
    qs = "query_id=AAF03wc0AgAAAHTfBzQGXB7v&user=%7B%22id%22%3A5167898484%2C%22first_name%22%3A%22xin%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22pvnimaxin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FYpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1zFgIVth6Wzacz7P2nGNCcp9j.svg%22%7D&auth_date=1731875744&signature=b1XX1Z-3ItQ4jvVRCCCaR-JeDve525ROkhbu_ZAt2tczwNBMR1F4oubq9p_OD02MuwcJxzprWAOjGutw0OskCw&hash=b29843e9031f21accbb4b59339241be79bbc22fbb566774b0641474567ffe1d5"
    bi = 7244657541
    pk = "e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d"

    init_data = InitData(qs)
    assert init_data.validate_by_signature(bi, pk)
