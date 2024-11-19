from dataclasses import dataclass
from typing import Optional

from ._object import Object


@dataclass(frozen=True)
class WebAppUser(Object):
    """This class represent a web app user.

    Attributes:
        id: A unique identifier for the user or bot. This number may have more than 32 significant bits and some programming languages may have difficulty/silent defects in interpreting it. It has at most 52 significant bits, so a 64-bit integer or a double-precision float type is safe for storing this identifier.
        is_bot: True, if this user is a bot. Returns in the receiver field only.
        first_name: First name of the user or bot.
        last_name: Last name of the user or bot.
        username: Username of the user or bot.
        language_code: IETF language tag of the user's language. Returns in user field only.
        is_premium: True, if this user is a Telegram Premium user.
        added_to_attachment_menu: True, if this user added the bot to the attachment menu.
        allows_write_to_pm: True, if this user allowed the bot to message them.
        photo_url: URL of the user's profile photo. The photo can be in .jpeg or .svg formats.

    """

    id: int
    is_bot: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None
    allows_write_to_pm: Optional[bool] = None
    photo_url: Optional[str] = None
    # NOTE: attributes order is important.
