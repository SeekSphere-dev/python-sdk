"""Exception classes for SeekSphere SDK."""


class SeekSphereError(Exception):
    """Base exception for SeekSphere SDK."""

    pass


class APIError(SeekSphereError):
    """Exception raised for API errors."""

    def __init__(
        self, message: str, status_code: int = None, response_data: dict = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class NetworkError(SeekSphereError):
    """Exception raised for network-related errors."""

    pass


class ValidationError(SeekSphereError):
    """Exception raised for validation errors."""

    pass
