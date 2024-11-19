from dataclasses import dataclass
from typing import Literal, Optional

from ._object import Object


@dataclass(frozen=True)
class WebAppChat(Object):
    """This object represents a chat.

    Attributes:
        id: Unique identifier for this chat. This number may have more than 32 significant bits and some programming languages may have difficulty/silent defects in interpreting it. But it has at most 52 significant bits, so a signed 64-bit integer or double-precision float type are safe for storing this identifier.
        type: Type of chat, can be either 'group', 'supergroup' or 'channel'.
        title: Title of the chat.
        username: Username of the chat
        photo_url: URL of the chat's photo. The photo can be in .jpeg or .svg formats. Only returned for Mini Apps launched from the attachment menu.

    """

    id: int
    type: Literal["group", "supergroup", "channel"]
    title: str
    username: Optional[str] = None
    photo_url: Optional[str] = None
    # NOTE: attributes order is important.
