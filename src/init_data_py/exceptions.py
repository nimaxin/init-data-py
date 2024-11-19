class InitDataPyError(Exception):
    """Base class for all library errors."""

    pass


class InitDataValidationError(InitDataPyError):
    """Base class for all validation errors."""

    pass


class ExpiredInitDataError(InitDataValidationError):
    """Raised when the init data is expired."""

    def __init__(self, message="The data has expired."):
        super().__init__(message)


class InvalidHashError(InitDataValidationError):
    """Raised when the hash validation fails."""

    def __init__(self, message="Hash validation failed."):
        super().__init__(message)


class InvalidSignatureError(InitDataValidationError):
    """Raised when signature verification fails."""

    def __init__(self, message="Signature verification failed."):
        super().__init__(message)


class UnexpectedFieldError(InitDataValidationError):
    """Raised when unexpected fields are found in init data."""

    def __init__(self, field: str, message=None):
        if message is None:
            message = f"Unexpected field '{field}' found in the init data."
        super().__init__(message)


class MissingRequiredFieldError(InitDataValidationError):
    """Raised when a required field is missing in init data."""

    def __init__(self, field: str, message=None):
        if message is None:
            message = f"Missing required field: '{field}'."
        super().__init__(message)
