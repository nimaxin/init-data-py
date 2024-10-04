import hashlib
import hmac
import json
import time
import urllib.parse
import warnings
from datetime import datetime, timedelta
from typing import Literal, Optional

from init_data_py import errors, types


class InitData:
    """Represent a [WebAppInitData](https://core.telegram.org/bots/webapps#webappinitdata).

    Parameters:
        query_id (`str`, optional):
            A unique identifier for the Mini App session, required for sending messages via the answerWebAppQuery method.

        user (`init_data_py.types.User`, optional):
            An object containing data about the current user.

        receiver (`init_data_py.types.User`, optional):
            An object containing data about the chat partner of the current user in the chat where the bot was launched via the attachment menu. Returned only for private chats and only for Mini Apps launched via the attachment menu.

        chat (`init_data_py.types.Chat`, optional):
            An object containing data about the chat where the bot was launched via the attachment menu. Returned for supergroups, channels and group chats - only for Mini Apps launched via the attachment menu.

        chat_type (`str`, optional):
            Type of the chat from which the Mini App was opened. Can be either "sender" for a private chat with the user opening the link, "private", "group", "supergroup", or "channel". Returned only for Mini Apps launched from direct links.

        chat_instance (`str`, optional):
            Global identifier, uniquely corresponding to the chat from which the Mini App was opened. Returned only for Mini Apps launched from a direct link.

        start_param (`str`, optional):
            The value of the startattach parameter, passed via link. Only returned for Mini Apps when launched from the attachment menu via link.

        can_send_after (`int`, optional):
            Time in seconds, after which a message can be sent via the answerWebAppQuery method.

        auth_date (`int`, optional):
            Unix time when the form was opened.

        hash (`str`, optional):
            A hash of all passed parameters, which the bot server can use to check their validity.
    """

    def __init__(
        self,
        *,
        query_id: Optional[str] = None,
        user: Optional["types.User"] = None,
        receiver: Optional["types.User"] = None,
        chat: Optional["types.Chat"] = None,
        chat_type: Optional[
            Literal["sender", "private", "group", "supergroup", "channel"]
        ] = None,
        chat_instance: Optional[str] = None,
        start_param: Optional[str] = None,
        can_send_after: Optional[int] = None,
        auth_date: Optional[int] = None,
        hash: Optional[str] = None,
    ) -> None:
        self.query_id = query_id
        self.user = user
        self.receiver = receiver
        self.chat = chat
        self.chat_type = chat_type
        self.chat_instance = chat_instance
        self.start_param = start_param
        self.can_send_after = can_send_after
        self.auth_date = auth_date
        self.hash = hash

    def validate(
        self,
        bot_token: str,
        lifetime: Optional[int] = None,
        raise_error: bool = True,
    ):
        """Validates the init data authenticity.

        Parameters:
            bot_token (`str`):
                The token associated with the bot, used to either launch the webapp or sign the init data.

            lifetime (`int`, optional):
                The maximum validity period of the init data in seconds.
                Recommended for security. Default is `None`.

            raise_error (`bool`, optional):
                In case True, raises an exception on invalid data, If False, returns False instead of raising an error.

        Returns:
            `bool`:
                True if the data is valid; otherwise, returns False.

        Raises:
            `errors.SignMissingError`: In case the signature (hash) is missing.
            `errors.AuthDateMissingError`: In case the auth_date is missing.
            `errors.ExpiredError`: In case the init data has expired based on the provided lifetime.
            `errors.SignInvalidError`: In case the signature (hash) is invalid.
        """
        if self.hash is None:
            if raise_error:
                raise errors.SignMissingError()
            return False

        if self.auth_date is None:
            if raise_error:
                raise errors.AuthDateMissingError()
            return False

        if lifetime is not None:
            auth_date = datetime.fromtimestamp(self.auth_date)
            expire_date = auth_date + timedelta(seconds=lifetime)
            if datetime.now() > expire_date:
                if raise_error:
                    raise errors.ExpiredError()
                return False

        if self.hash != self.calculate_hash(bot_token):
            if raise_error:
                raise errors.SignInvalidError()
            return False

        return True

    def sign(self, bot_token: str, auth_date: Optional[int] = None):
        """Sign the init data using the provided bot token.

        Parameters:
            bot_token (`str`):
                The bot token used to generate the signature for init data.

            auth_date (`init`):
                The timestamp (without timezone) representing the authorization date. If not provided, the current timestamp will be used.

        Returns:
            `InitData`:
                This current updated init data by setting the `auth_date` and generated signature (`hash`) attributes.
        """
        self.auth_date = auth_date if auth_date is not None else int(time.time())
        self.hash = self.calculate_hash(bot_token)

        return self

    def calculate_hash(
        self,
        bot_token: str,
    ):
        """Calculates a hash based on the bot token and the current `InitData` object.

        Parameters:
            bot_token (`str`):
                The bot token used to generate the secret key for hash computation.

        Returns:
            `str`:
                The calculated hash, derived from the init data attributes and the generated secret key.
        """
        init_data = self.to_dict(nested=False)
        init_data.pop("hash", None)
        sorted_attrs = sorted(init_data.items())
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted_attrs
        ).encode()
        secret_key = hmac.new(
            b"WebAppData", bot_token.encode(), hashlib.sha256
        ).digest()

        return hmac.new(
            secret_key, data_check_string, hashlib.sha256
        ).hexdigest()

    @classmethod
    def from_query_string(cls, query_string: str):
        warnings.warn(
            "The 'from_query_string' method is deprecated and will be removed in near stable version. Use 'parse' instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        return cls.parse(query_string)

    @classmethod
    def parse(cls, query_string: str):
        """Create an InitData object from a query string.

        Parameters:
            query_string (`str`):
                The query string from `window.WebApp.initData` to parse and convert into an InitData object.

        Returns:
            `InitData`:
                An object of InitData with attributes set according to the values in the query_string.

        Raises:
            `errors.SignMissingError`: In case the signature (hash) is missing.
            `errors.AuthDateMissingError`: In case the auth_date is missing.
            `errors.UnexpectedFormatError`: In case the the format of the query string is unexpected.
        """
        parsed_qs = dict(urllib.parse.parse_qsl(query_string))

        if not parsed_qs:
            raise errors.UnexpectedFormatError()

        init_data = {}

        for k, v in parsed_qs.items():
            if k in {
                "hash",
                "query_id",
                "chat_type",
                "chat_instance",
                "start_param",
            }:
                init_data[k] = v

            elif k in {"auth_date", "can_send_after"}:
                init_data[k] = int(v)  # type: ignore
            elif k in {"user", "receiver"}:
                try:
                    init_data[k] = types.User.from_json(v)
                except json.decoder.JSONDecodeError:
                    raise errors.UnexpectedFormatError()
            elif k == "chat":
                try:
                    init_data[k] = types.Chat.from_json(v)
                except json.decoder.JSONDecodeError:
                    raise errors.UnexpectedFormatError()
            else:
                raise errors.UnexpectedFormatError()

        hash = parsed_qs.get("hash")
        if hash is None:
            raise errors.UnexpectedFormatError()

        auth_date = parsed_qs.get("auth_date")
        if auth_date is None:
            raise errors.UnexpectedFormatError()

        return cls(**init_data)  # type: ignore

    def to_json(self):
        """Returns a JSON serialized representation of the object."""
        return json.dumps(self.to_dict(nested=True), ensure_ascii=False)

    def to_dict(self, nested=True):
        """Returns a dictionary representation of the object.

        Parameters:
            nested (`bool`):
                If True, nested objects will be converted to dictionaries; if False, nested objects will be represented as serialized JSON.
        """
        init_data_attrs = {
            k: v for k, v in self.__dict__.items() if v is not None
        }
        init_data = {}

        for k, v in init_data_attrs.items():
            if isinstance(v, (types.User, types.Chat)):
                if nested:
                    init_data[k] = v.to_dict()
                    continue
                init_data[k] = v.to_json()
            elif k in {"auth_date", "can_send_after"}:
                init_data[k] = int(v)
            else:
                init_data[k] = str(v)

        return init_data

    def to_query_string(self):
        """Returns a query string representation of the object."""
        init_data = self.to_dict(nested=False)

        return urllib.parse.urlencode(init_data)

    def __str__(self) -> str:
        return json.dumps(self.to_dict(nested=True), indent=4)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        for attr in self.__dict__:
            try:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            except AttributeError:
                return False

        return True
