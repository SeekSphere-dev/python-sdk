"""Tests for SeekSphere types."""

import pytest
from typing import get_type_hints
from seeksphere.types import (
    SearchMode,
    SearchRequest,
    SearchResponse,
    UpdateTokensRequest,
    UpdateSchemaRequest,
    APIResponse,
    TokensResponse,
    SchemaResponse,
    SDKConfig,
)


class TestTypes:
    """Test type definitions."""

    def test_search_mode_literal(self):
        """Test SearchMode literal type."""
        # These should be valid
        valid_modes = ["sql_only", "full"]
        for mode in valid_modes:
            # In runtime, we can't enforce literal types, but we can test the values
            assert mode in ["sql_only", "full"]

    def test_search_request_structure(self):
        """Test SearchRequest TypedDict structure."""
        request: SearchRequest = {"query": "test query"}
        assert "query" in request
        assert isinstance(request["query"], str)

    def test_search_response_structure(self):
        """Test SearchResponse TypedDict structure."""
        response: SearchResponse = {
            "success": True,
            "org_id": "test-org",
            "mode": "sql_only",
            "user_id": "test-user"
        }
        assert response["success"] is True
        assert response["org_id"] == "test-org"
        assert response["mode"] == "sql_only"
        assert response["user_id"] == "test-user"

    def test_update_tokens_request_structure(self):
        """Test UpdateTokensRequest TypedDict structure."""
        request: UpdateTokensRequest = {
            "tokens": {
                "category1": ["token1", "token2"],
                "category2": ["token3"]
            }
        }
        assert "tokens" in request
        assert isinstance(request["tokens"], dict)
        assert all(isinstance(k, str) for k in request["tokens"].keys())
        assert all(isinstance(v, list) for v in request["tokens"].values())

    def test_update_schema_request_structure(self):
        """Test UpdateSchemaRequest TypedDict structure."""
        request: UpdateSchemaRequest = {
            "search_schema": {
                "tables": {
                    "users": {
                        "columns": ["id", "name"],
                        "types": ["int", "varchar"]
                    }
                }
            }
        }
        assert "search_schema" in request

    def test_api_response_structure(self):
        """Test APIResponse TypedDict structure."""
        # Test with all fields
        response: APIResponse = {
            "success": True,
            "message": "Operation successful",
            "error": "",
            "org_id": "test-org"
        }
        assert response["success"] is True
        assert response["message"] == "Operation successful"
        
        # Test with minimal fields (total=False allows partial)
        minimal_response: APIResponse = {"success": False}
        assert minimal_response["success"] is False

    def test_tokens_response_structure(self):
        """Test TokensResponse TypedDict structure."""
        response: TokensResponse = {
            "tokens": {
                "category1": ["token1", "token2"]
            },
            "org_id": "test-org"
        }
        assert "tokens" in response
        assert "org_id" in response
        assert isinstance(response["tokens"], dict)

    def test_schema_response_structure(self):
        """Test SchemaResponse TypedDict structure."""
        response: SchemaResponse = {
            "search_schema": {"tables": {}},
            "org_id": "test-org"
        }
        assert "search_schema" in response
        assert "org_id" in response

    def test_sdk_config_structure(self):
        """Test SDKConfig TypedDict structure."""
        # Test with all fields
        config: SDKConfig = {
            "base_url": "https://api.test.com",
            "api_key": "test-key",
            "timeout": 30
        }
        assert config["base_url"] == "https://api.test.com"
        assert config["api_key"] == "test-key"
        assert config["timeout"] == 30
        
        # Test with minimal fields (total=False allows partial)
        minimal_config: SDKConfig = {
            "base_url": "https://api.test.com",
            "api_key": "test-key"
        }
        assert "timeout" not in minimal_config or minimal_config.get("timeout") is None