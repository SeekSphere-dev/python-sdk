"""SeekSphere API client."""

import json
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import APIError, NetworkError, ValidationError
from .types import (
    APIResponse,
    SchemaResponse,
    SDKConfig,
    SearchMode,
    SearchRequest,
    SearchResponse,
    TokensResponse,
    UpdateSchemaRequest,
    UpdateTokensRequest,
)


class SeekSphereClient:
    """Client for interacting with SeekSphere API."""

    def __init__(self, config: SDKConfig) -> None:
        """Initialize the SeekSphere client.

        Args:
            config: Configuration dictionary containing base_url, api_key, and optional timeout
        """
        self.base_url = config["base_url"].rstrip("/")
        self.api_key = config["api_key"]  # org_id is used as api_key
        self.timeout = config.get("timeout", 30)

        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "X-Org-Id": self.api_key,
                "X-User-Id": "node_sdk",  # Fixed user_id for SDK
            }
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> dict:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint path
            data: Request payload
            headers: Additional headers

        Returns:
            Response data as dictionary

        Raises:
            APIError: For HTTP error responses
            NetworkError: For network-related issues
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=request_headers,
                timeout=self.timeout,
            )

            # Handle HTTP errors
            if not response.ok:
                error_data = {}
                try:
                    error_data = response.json()
                except (json.JSONDecodeError, ValueError):
                    pass

                error_message = error_data.get(
                    "error", f"HTTP {response.status_code}: {response.reason}"
                )
                raise APIError(
                    message=f"API Error: {error_message}",
                    status_code=response.status_code,
                    response_data=error_data,
                )

            # Parse response
            try:
                return response.json()
            except (json.JSONDecodeError, ValueError) as e:
                raise APIError(f"Invalid JSON response: {e}")

        except requests.exceptions.Timeout:
            raise NetworkError("Request timeout")
        except requests.exceptions.SSLError as e:
            raise NetworkError(f"SSL error: {e}")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Connection error")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {e}")

    def search(
        self, request: SearchRequest, mode: SearchMode = "sql_only"
    ) -> SearchResponse:
        """Search using the API.

        Args:
            request: Search request containing query
            mode: Search mode, either 'sql_only' or 'full'

        Returns:
            Search response

        Raises:
            ValidationError: For invalid input
            APIError: For API errors
            NetworkError: For network issues
        """
        if not request.get("query") or not isinstance(request["query"], str):
            raise ValidationError("Query string is required")

        if mode not in ["sql_only", "full"]:
            raise ValidationError("Mode must be either 'sql_only' or 'full'")

        headers = {"X-Mode": mode}
        return self._make_request("POST", "/search", data=request, headers=headers)

    def update_tokens(self, request: UpdateTokensRequest) -> APIResponse:
        """Update tokens mapping.

        Args:
            request: Update tokens request

        Returns:
            API response

        Raises:
            ValidationError: For invalid input
            APIError: For API errors
            NetworkError: For network issues
        """
        if not isinstance(request.get("tokens"), dict):
            raise ValidationError("Tokens must be a dictionary")

        # Validate tokens format
        for key, value in request["tokens"].items():
            if not isinstance(key, str):
                raise ValidationError("All token keys must be strings")
            if not isinstance(value, list):
                raise ValidationError("All token values must be lists")
            if not all(isinstance(item, str) for item in value):
                raise ValidationError("All token values must be lists of strings")

        return self._make_request("PUT", "/org/tokens", data=request)

    def update_schema(self, request: UpdateSchemaRequest) -> APIResponse:
        """Update search schema.

        Args:
            request: Update schema request

        Returns:
            API response

        Raises:
            ValidationError: For invalid input
            APIError: For API errors
            NetworkError: For network issues
        """
        if "search_schema" not in request:
            raise ValidationError("search_schema is required")

        return self._make_request("PUT", "/org/search_schema", data=request)

    def get_tokens(self) -> TokensResponse:
        """Get current tokens mapping.

        Returns:
            Current tokens

        Raises:
            APIError: For API errors
            NetworkError: For network issues
        """
        return self._make_request("GET", "/org/tokens")

    def get_schema(self) -> SchemaResponse:
        """Get current search schema.

        Returns:
            Current schema

        Raises:
            APIError: For API errors
            NetworkError: For network issues
        """
        return self._make_request("GET", "/org/search_schema")

    def health_check(self) -> dict:
        """Check API health status.

        Returns:
            Health status response

        Raises:
            APIError: For API errors
            NetworkError: For network issues
        """
        return self._make_request("GET", "/health")
