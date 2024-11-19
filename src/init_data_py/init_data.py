from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from init_data_py import exceptions
from init_data_py._utils import (
    calculate_data_check_string,
    calculate_hash,
    calculate_secret_key,
    decode_query_string,
)


@dataclass(frozen=True)
class InitData:
    """NO DESCRIPTION

    Attributes:
        query_string: A string with raw data transferred to the Mini App, convenient for validating data. (`window.Telegram.WebApp.initData`)

    """

    query_string: str

    def validate_by_hash(self, bot_token: str, lifetime: Optional[timedelta] = None):
        """
        Validates the integrity of data received from Telegram's Mini App by comparing
        the received hash with the expected hash computed from the data-check-string
        and the bot's token.

        Parameters:
            bot_token: The bot's token used to generate the secret key for hash calculation.
            lifetime: The time window for which the data is considered valid.
                If not specified, no expiration check is performed. Defaults to None.

        Raises:
            MissingRequiredFieldError: If any required field (auth_date or hash) is missing in the received data.
            ExpiredInitDataError: If the received data is older than the specified lifetime.
            InvalidHashError: If the hash validation fails, indicating that the data is not from Telegram or has been modified.


        Returns:
            bool: True if the hash matches the calculated hash, indicating the data's integrity is valid;
                False otherwise.

        """
        fields = decode_query_string(self.query_string)

        auth_timestamp = fields.get("auth_date")
        if auth_timestamp is None:
            raise exceptions.MissingRequiredFieldError("auth_date")

        if lifetime is not None:
            auth_datetime = datetime.fromtimestamp(int(auth_timestamp), timezone.utc)
            curr_datetime = datetime.now(timezone.utc)

            if auth_datetime + lifetime < curr_datetime:
                raise exceptions.ExpiredInitDataError()

        received_hash = fields.pop("hash", None)
        if received_hash is None:
            raise exceptions.MissingRequiredFieldError("hash")

        secret_key = calculate_secret_key(bot_token)
        data_check_string = calculate_data_check_string(fields)
        calculated_hash = calculate_hash(secret_key, data_check_string)

        if received_hash != calculated_hash:
            raise exceptions.InvalidHashError()
        else:
            return True

    def validate_by_signature(
        self, bot_id: int, pub_key: str, lifetime: Optional[timedelta] = None
    ):
        """
        Validates the integrity of data received from Telegram's Mini App by verifying
        the received signature against the calculated signature using the bot's public key.

        Parameters:
            bot_id: The bot's unique identifier.
            pub_key: The public key used to verify the received signature.
            lifetime: The time window for which the data is considered valid.
                If not specified, no expiration check is performed. Defaults to None.

        Raises:
            MissingRequiredFieldError: If any required field (auth_date, signature, or hash) is missing in the received data.
            ExpiredInitDataError: If the received data is older than the specified lifetime.
            InvalidSignatureError: If the signature verification fails, indicating that the data is not from Telegram or has been modified.

        Returns:
            bool: True if the received signature is valid and the data's integrity is confirmed;
                False if the signature verification fails.

        """
        fields = decode_query_string(self.query_string)

        auth_timestamp = fields.get("auth_date")
        if auth_timestamp is None:
            raise exceptions.MissingRequiredFieldError("auth_date")

        if lifetime is not None:
            auth_datetime = datetime.fromtimestamp(int(auth_timestamp), timezone.utc)
            curr_datetime = datetime.now(timezone.utc)

            if auth_datetime + lifetime < curr_datetime:
                raise exceptions.ExpiredInitDataError()

        receiver_signature = fields.pop("signature", None)
        if receiver_signature is None:
            raise exceptions.MissingRequiredFieldError("signature")

        received_hash = fields.pop("hash", None)
        if received_hash is None:
            raise exceptions.MissingRequiredFieldError("hash")

        data_check_string = calculate_data_check_string(fields)
        data_check_string = f"{bot_id}:WebAppData\n{data_check_string}"

        pub_key_bytes = binascii.unhexlify(pub_key)
        receiver_signature = receiver_signature.replace("-", "+").replace("_", "/")
        padding = "=" * (-len(receiver_signature) % 4)
        signature_bytes = base64.b64decode(receiver_signature + padding)

        public_key = Ed25519PublicKey.from_public_bytes(pub_key_bytes)

        try:
            public_key.verify(signature_bytes, data_check_string.encode("utf-8"))
            return True
        except Exception:
            raise exceptions.InvalidInitDataError()
