import hashlib
import hmac
import urllib.parse

SECRET_KEY = b"WebAppData"
PROD_PUBLIC_KEY = "e7bf03a2fa4602af4580703d88dda5bb59f32ed8b02a56c187fe7d34caed242d"
TEST_PUBLIC_KEY = "40055058a4ee38156a06562e52eece92a771bcd8346a8c4615cb7376eddf72ec"


def calculate_secret_key(bot_token: str) -> hmac.HMAC:
    return hmac.new(SECRET_KEY, bot_token.encode(), hashlib.sha256)


def calculate_data_check_string(data: dict) -> str:
    return "\n".join(f"{k}={v}" for k, v in sorted(data.items()))


def calculate_hash(secret_key: hmac.HMAC, data_check_string: str) -> str:
    return hmac.new(
        secret_key.digest(), data_check_string.encode(), hashlib.sha256
    ).hexdigest()


def decode_query_string(query_string: str) -> dict:
    return {
        k: urllib.parse.unquote(v)
        for k, v in [s.split("=", 1) for s in query_string.split("&")]
    }


def encode_query_string(data: dict) -> str:
    return urllib.parse.urlencode(data)
