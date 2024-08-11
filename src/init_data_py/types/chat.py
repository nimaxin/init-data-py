from typing import Literal, Optional

from .object import Object


class Chat(Object):
    """
    Represent a [WebAppChat](https://core.telegram.org/bots/webapps#webappchat).

    Parameters:
        id (int):
            Unique identifier for this chat. This number may have more than 32 significant bits and some programming languages may have difficulty/silent defects in interpreting it. But it has at most 52 significant bits, so a signed 64-bit integer or double-precision float type are safe for storing this identifier.

        type (`str`):
            Type of chat, can be either "group", "supergroup" or "channel".

        title (`str`):
            Title of the chat.

        username (`str`, optional):
            Username of the chat.

        photo_url (`str`, optional):
            URL of the chat's photo. The photo can be in .jpeg or .svg formats. Only returned for Mini Apps launched from the attachment menu.
    """

    def __init__(
        self,
        *,
        id: int,
        type: Literal["group", "supergroup", "channel"],
        title: str,
        username: Optional[str] = None,
        photo_url: Optional[str] = None,
    ) -> None:
        self.id = id
        self.type = type
        self.title = title
        self.username = username
        self.photo_url = photo_url
        # NOTE: The order of the attributes is important.
