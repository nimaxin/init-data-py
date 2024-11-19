from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Optional, Union

import init_data_py
from init_data_py import exceptions

from ._object import Object
from ._utils import (
    calculate_data_check_string,
    calculate_hash,
    calculate_secret_key,
    decode_query_string,
    encode_query_string,
)


@dataclass(frozen=True)
class WebAppInitData(Object):
    """NO DESCRIPTION

    Attributes:
        query_id: A unique identifier for the Mini App session, required for sending messages via the answerWebAppQuery method.
        user: An object containing data about the current user.
        receiver: An object containing data about the chat partner of the current user in the chat where the bot was launched via the attachment menu. Returned only for private chats and only for Mini Apps launched via the attachment menu.
        chat: An object containing data about the chat where the bot was launched via the attachment menu. Returned for supergroups, channels and group chats - only for Mini Apps launched via the attachment menu.
        chat_type: Type of the chat from which the Mini App was opened. Can be either “sender” for a private chat with the user opening the link, “private”, “group”, “supergroup”, or “channel”. Returned only for Mini Apps launched from direct links.
        chat_instance: Global identifier, uniquely corresponding to the chat from which the Mini App was opened. Returned only for Mini Apps launched from a direct link.
        start_param: The value of the startattach parameter, passed via link. Only returned for Mini Apps when launched from the attachment menu via link.
        can_send_after: Time in seconds, after which a message can be sent via the answerWebAppQuery method.
        auth_date: Unix time when the form was opened.
        signature: A signature of all passed parameters (except hash), which the third party can use to check their validity.
        hash: A hash of all passed parameters, which the bot server can use to check their validity.

    """

    query_id: Optional[str] = None
    user: Optional[init_data_py.WebAppUser] = None
    receiver: Optional[init_data_py.WebAppUser] = None
    chat: Optional[init_data_py.WebAppChat] = None
    chat_type: Optional[Literal["sender" "private" "supergroup" "channel"]] = None
    chat_instance: Optional[str] = None
    start_param: Optional[str] = None
    can_send_after: Optional[int] = None
    auth_date: Optional[int] = None
    signature: Optional[str] = None
    hash: Optional[str] = None
    # NOTE: order is not important but for creating same init data as telegram, I defined
    # the signature attribute before hash so the generated query string match the original one.

    @classmethod
    def from_query_string(cls, query_string: str) -> WebAppInitData:
        """NO DOCSTRING"""
        params = decode_query_string(query_string)

        data = {}
        for k, v in params.items():
            if k in {
                "query_id",
                "chat_type",
                "chat_instance",
                "start_param",
                "signature",
                "hash",
            }:
                data[k] = v
            elif k in {"can_send_after", "auth_date"}:
                casted_v = int(v)
                data[k] = casted_v
            elif k in {"user", "receiver"}:
                casted_v = init_data_py.WebAppUser.from_json(v)
                data[k] = casted_v
            elif k == "chat":
                casted_v = init_data_py.WebAppChat.from_json(v)
                data[k] = casted_v
            else:
                # NOTE: An unexpected field type could be assumed to be a string,
                # but "Errors should never pass silently."
                raise exceptions.UnexpectedFieldError(k)

        return cls(**data)

    def to_query_string(self):
        """NO DOCSTRING"""
        fields = {}
        for k, v in self.to_dict(recursive=False).items():
            if isinstance(v, Object):
                fields[k] = v.to_json()
            else:
                fields[k] = v

        return encode_query_string(fields)

    def sign(
        self, bot_token: str, auth_date: Optional[Union[int, datetime]] = None
    ) -> WebAppInitData:
        """NO DOCSTRING"""
        fields = {}
        if auth_date is None:
            fields["auth_date"] = int(datetime.now(timezone.utc).timestamp())
        elif isinstance(auth_date, datetime):
            fields["auth_date"] = int(auth_date.timestamp())
        else:
            fields["auth_date"] = auth_date

        for k, v in self.to_dict(recursive=False).items():
            if isinstance(v, Object):
                fields[k] = v.to_json()
            else:
                fields[k] = v

        secret_key = calculate_secret_key(bot_token)
        data_check_string = calculate_data_check_string(fields)
        fields["hash"] = calculate_hash(secret_key, data_check_string)
        return WebAppInitData(**fields)
