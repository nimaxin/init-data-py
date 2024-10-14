class InitDataPyError(Exception):
    pass


class AuthDateMissingError(InitDataPyError):
    def __init__(self):
        super().__init__("auth_date is missing.")


class ExpiredError(InitDataPyError):
    def __init__(self):
        super().__init__("init data is expired.")


class SignInvalidError(InitDataPyError):
    def __init__(self):
        super().__init__("signature (hash) is invalid.")


class SignMissingError(InitDataPyError):
    def __init__(self):
        super().__init__("signature (hash) is missing.")


class UnexpectedFormatError(InitDataPyError):
    def __init__(self):
        super().__init__("the init data query string has unexpected format.")
