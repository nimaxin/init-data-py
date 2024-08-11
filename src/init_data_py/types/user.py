from typing import Literal, Optional

from .object import Object


class User(Object):
    """Represent a [WebAppUser](https://core.telegram.org/bots/webapps#webappuser).

    Parameters:
        id (int):
            A unique identifier for the user or bot. This number may have more than 32 significant bits and some programming languages may have difficulty/silent defects in interpreting it. It has at most 52 significant bits, so a 64-bit integer or a double-precision float type is safe for storing this identifier.

        is_bot (boolean, optional):
            True, if this user is a bot. Returns in the `receiver` field only.

        first_name (`str`):
            First name of the user or bot.

        last_name (`str`, optional):
            Last name of the user or bot.

        username (`str`, optional):
            Username of the user or bot.

        language_code (`str`, optional):
            IETF language tag of the user's language. Returns in user field only.

        is_premium (True, optional):
            True, if this user is a Telegram Premium user.

        added_to_attachment_menu (True, optional):
            True, if this user added the bot to the attachment menu.

        allows_write_to_pm (True, optional):
            True, if this user allowed the bot to message them.

        photo_url (`str`, optional):
            URL of the user's profile photo. The photo can be in .jpeg or .svg formats. Only returned for Mini Apps launched from the attachment menu.
    """

    def __init__(
        self,
        *,
        id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        language_code: Optional[str] = None,
        is_premium: Optional[Literal[True]] = None,
        is_bot: Optional[bool] = None,
        added_to_attachment_menu: Optional[Literal[True]] = None,
        allows_write_to_pm: Optional[Literal[True]] = None,
        photo_url: Optional[str] = None,
    ) -> None:
        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
        self.is_premium = is_premium
        self.added_to_attachment_menu = added_to_attachment_menu
        self.allows_write_to_pm = allows_write_to_pm
        self.photo_url = photo_url
        # NOTE: The order of the attributes is important.
