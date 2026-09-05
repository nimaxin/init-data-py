"""Real init data captured from Telegram, with the tokens that signed it."""

from datetime import datetime, timezone
from typing import NamedTuple


class Vector(NamedTuple):
    query_string: str
    bot_token: str
    auth_date: int
    #: Set when the payload carries a signature, so it can also be checked
    #: against Telegram's public key.
    bot_id: int | None = None

    @property
    def issued_at(self) -> datetime:
        return datetime.fromtimestamp(self.auth_date, timezone.utc)


PLAIN = Vector(
    query_string=(
        "query_id=AAF03wc0AgAAAHTfBzROOCVW&user=%7B%22id%22%3A5167898484%2C%22"
        "first_name%22%3A%22xin%22%2C%22last_name%22%3A%22%22%2C%22username%22"
        "%3A%22pvnimaxin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write"
        "_to_pm%22%3Atrue%7D&auth_date=1722938610&hash=8654c8c617c143abf656f4f"
        "159be2539880a56f58c2d9be622f90c0346aa162b"
    ),
    bot_token="7244657541:AAEgqk0HDC3WD5cdbnGMdd6L0TJ74FDp97Y",
    auth_date=1722938610,
)

#: Non ASCII names, which must survive as UTF-8 in the data-check-string.
UTF8 = Vector(
    query_string=(
        "query_id=AAF2GVE4AwAAAHYZUTgHczdc&user=%7B%22id%22%3A7387289974%2C%22"
        "first_name%22%3A%22%D0%90%D1%80%D1%82%D1%91%D0%BC%22%2C%22last_name%22"
        "%3A%22%D0%9E%D0%BD%D1%83%D1%84%D1%80%D0%B8%D0%B9%22%2C%22username%22"
        "%3A%22typexin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to"
        "_pm%22%3Atrue%7D&auth_date=1724048856&hash=53b22bc70a748dae613a5aa9189"
        "0b387b9cc0356c5dcffca173816b6e40a17e5"
    ),
    bot_token="7244657541:AAHAJP25XehV6N02kiLLAEi2el-xLsSw29w",
    auth_date=1724048856,
)

#: photo_url arrives with escaped slashes. Telegram hashed those bytes, so
#: the value must never be re-serialized before hashing.
ESCAPED_SLASH = Vector(
    query_string=(
        "query_id=AAF03wc0AgAAAHTfBzTtHPDB&user=%7B%22id%22%3A5167898484%2C%22"
        "first_name%22%3A%22xin%22%2C%22last_name%22%3A%22%22%2C%22username%22"
        "%3A%22pvnimaxin%22%2C%22language_code%22%3A%22en%22%2C%22allows_write"
        "_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2F"
        "i%5C%2Fuserpic%5C%2F320%5C%2FYpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1z"
        "FgIVth6Wzacz7P2nGNCcp9j.svg%22%7D&auth_date=1731441609&hash=f4bac82fe8"
        "f20abdc03126af489751752e830227b58241ec2f9dd67913909ee0"
    ),
    bot_token="7244657541:AAFMjYH4kc3U9zG0GWnxYfW-QKICVzDwvEw",
    auth_date=1731441609,
)

#: Captured from a current client, so it carries a signature as well as a
#: hash. Both must validate: signature takes part in the hash, and is left
#: out only when checking the signature itself. The photo_url here also
#: arrives with escaped slashes.
SIGNED = Vector(
    query_string=(
        "user=%7B%22id%22%3A5167898484%2C%22first_name%22%3A%22xin%22%2C%22"
        "last_name%22%3A%22%22%2C%22username%22%3A%22pvnimaxin%22%2C%22"
        "language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22"
        "photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F"
        "320%5C%2FYpcdHFmoxukmQ537mOZhe-Woot_k2xrmbdAIrGK1zFgIVth6Wzacz7P2nGN"
        "Ccp9j.svg%22%7D&chat_instance=8207002646956202621&chat_type=private"
        "&auth_date=1788639560&signature=5TpQXmcWfc12P3GMFaHQzBri6FNu6QWrkH4y"
        "sQX3CuT0Jdh3LhOEjd0jvso0fnOa_YCpJXZiid-DpZXidvVPAQ&hash=2c450512f189"
        "adbf7e7027e5f32fd7954c00fb21218265320b9a6b9c2139891f"
    ),
    bot_token="7082182952:AAFN9rxuCROAv-lBtSXSSaR3ZMQsP0KW95I",
    auth_date=1788639560,
    bot_id=7082182952,
)

ALL = (PLAIN, UTF8, ESCAPED_SLASH, SIGNED)

#: The subset that can be checked against Telegram's public key.
SIGNED_ALL = tuple(vector for vector in ALL if vector.bot_id is not None)
