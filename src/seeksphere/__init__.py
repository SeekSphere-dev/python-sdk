"""SeekSphere SDK - Python client for SeekSphere API."""

from .client import SeekSphereClient
from .exceptions import APIError, NetworkError, SeekSphereError, ValidationError
from .types import (
    SearchMode,
    SearchRequest,
    SearchResponse,
    UpdateSchemaRequest,
    UpdateTokensRequest,
)

__version__ = "1.0.0"
__all__ = [
    "SeekSphereClient",
    "SearchMode",
    "SearchRequest",
    "SearchResponse",
    "UpdateTokensRequest",
    "UpdateSchemaRequest",
    "SeekSphereError",
    "APIError",
    "NetworkError",
    "ValidationError",
]
