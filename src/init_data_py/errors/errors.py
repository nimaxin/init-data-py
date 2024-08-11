class AuthDateMissingError(Exception):
    def __init__(self):
        super().__init__("auth_date is missing.")


class ExpiredError(Exception):
    def __init__(self):
        super().__init__("init data is expired.")


class SignInvalidError(Exception):
    def __init__(self):
        super().__init__("signature (hash) is invalid.")


class SignMissingError(Exception):
    def __init__(self):
        super().__init__("signature (hash) is missing.")


class UnexpectedFormatError(Exception):
    def __init__(self):
        super().__init__("the init data query string has unexpected format.")
