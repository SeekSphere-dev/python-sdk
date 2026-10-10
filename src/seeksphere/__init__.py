"""SeekSphere SDK - Python client for SeekSphere API."""

from .client import SeekSphereClient
from .exceptions import APIError, NetworkError, SeekSphereError, ValidationError
from .types import (
    SearchMode,
    SearchRequest,
    SearchResponse,
    SearchSource,
    TokenMap,
    UpdateSchemaRequest,
    UpdateTokensRequest,
)

__version__ = "2.0.0"
__all__ = [
    "SeekSphereClient",
    "SearchMode",
    "SearchRequest",
    "SearchResponse",
    "SearchSource",
    "TokenMap",
    "UpdateTokensRequest",
    "UpdateSchemaRequest",
    "SeekSphereError",
    "APIError",
    "NetworkError",
    "ValidationError",
]
