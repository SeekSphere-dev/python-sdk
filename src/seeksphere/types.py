"""Type definitions for SeekSphere SDK."""

from typing import Any, Dict, List, Literal, Optional, TypedDict

# Type aliases
SearchMode = Literal["sql_only", "full"]


class SearchRequest(TypedDict):
    """Request payload for search endpoint."""

    query: str


class SearchResponse(TypedDict):
    """Response from search endpoint."""

    success: bool
    org_id: str
    mode: str
    user_id: str
    # Additional fields may be present


class UpdateTokensRequest(TypedDict):
    """Request payload for updating tokens."""

    tokens: Dict[str, List[str]]


class UpdateSchemaRequest(TypedDict):
    """Request payload for updating schema."""

    search_schema: Any


class APIResponse(TypedDict, total=False):
    """Generic API response structure."""

    success: bool
    message: str
    error: str
    org_id: str


class TokensResponse(TypedDict):
    """Response from get tokens endpoint."""

    tokens: Dict[str, List[str]]
    org_id: str


class SchemaResponse(TypedDict):
    """Response from get schema endpoint."""

    search_schema: Any
    org_id: str


class SDKConfig(TypedDict, total=False):
    """Configuration for SeekSphere SDK."""

    base_url: str
    api_key: str  # This is the org_id
    timeout: Optional[int]
