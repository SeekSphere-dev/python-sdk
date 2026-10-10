"""Type definitions for SeekSphere SDK."""

from typing import Any, Dict, List, Literal, Optional, Union, TypedDict

# Type aliases
SearchMode = Literal["sql_only", "full"]
SearchSource = Literal["cache", "pattern", "llm"]
TokenValue = Union[str, int, float]
TokenMap = Dict[str, List[TokenValue]]


class SearchRequest(TypedDict):
    """Request payload for search endpoint."""

    query: str


class SearchResponse(TypedDict, total=False):
    """Response from search endpoint."""

    success: bool
    org_id: str
    mode: SearchMode
    user_id: Optional[str]
    query: str
    sql: str
    source: SearchSource
    processing_time_ms: float
    pattern_used: Optional[Dict[str, Any]]
    extracted_values: Optional[Dict[str, Any]]
    learned: Optional[bool]
    pattern_learning_enabled: Optional[bool]
    cached: Optional[bool]
    # Additional fields may be present


class UpdateTokensRequest(TypedDict):
    """Request payload for updating tokens."""

    tokens: TokenMap


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

    tokens: TokenMap
    org_id: str


class SchemaResponse(TypedDict):
    """Response from get schema endpoint."""

    search_schema: Any
    org_id: str


class SDKConfig(TypedDict, total=False):
    """Configuration for SeekSphere SDK."""

    base_url: str
    api_key: str  # Per-org API key created via POST /org/api-keys, sent as X-Api-Key
    timeout: Optional[int]
