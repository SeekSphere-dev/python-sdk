"""Tests for SeekSphere client."""

from unittest.mock import Mock, patch

import pytest
import requests

from seeksphere import APIError, NetworkError, SeekSphereClient, ValidationError


@pytest.fixture
def client():
    """Create a test client."""
    return SeekSphereClient(
        {"base_url": "https://api.test.com", "api_key": "test-org-id", "timeout": 30}
    )


@pytest.fixture
def mock_response():
    """Create a mock response."""
    response = Mock()
    response.ok = True
    response.json.return_value = {"success": True, "data": "test"}
    return response


class TestSeekSphereClient:
    """Test cases for SeekSphereClient."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = SeekSphereClient(
            {
                "base_url": "https://api.test.com",
                "api_key": "test-org-id",
                "timeout": 60,
            }
        )

        assert client.base_url == "https://api.test.com"
        assert client.api_key == "test-org-id"
        assert client.timeout == 60
        assert client.session.headers["X-Org-Id"] == "test-org-id"
        assert client.session.headers["X-User-Id"] == "node_sdk"

    def test_client_initialization_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base_url."""
        client = SeekSphereClient(
            {"base_url": "https://api.test.com/", "api_key": "test-org-id"}
        )

        assert client.base_url == "https://api.test.com"

    @patch("requests.Session.request")
    def test_search_success(self, mock_request, client, mock_response):
        """Test successful search."""
        mock_request.return_value = mock_response
        mock_response.json.return_value = {
            "success": True,
            "org_id": "test-org-id",
            "mode": "sql_only",
            "user_id": "node_sdk",
        }

        result = client.search({"query": "test query"}, mode="sql_only")

        assert result["success"] is True
        assert result["org_id"] == "test-org-id"
        mock_request.assert_called_once()

    def test_search_validation_error_empty_query(self, client):
        """Test search with empty query raises ValidationError."""
        with pytest.raises(ValidationError, match="Query string is required"):
            client.search({"query": ""})

    def test_search_validation_error_invalid_mode(self, client):
        """Test search with invalid mode raises ValidationError."""
        with pytest.raises(ValidationError, match="Mode must be either"):
            client.search({"query": "test"}, mode="invalid")

    @patch("requests.Session.request")
    def test_update_tokens_success(self, mock_request, client, mock_response):
        """Test successful token update."""
        mock_request.return_value = mock_response

        result = client.update_tokens({"tokens": {"category": ["token1", "token2"]}})

        assert result["success"] is True
        mock_request.assert_called_once()

    def test_update_tokens_validation_error(self, client):
        """Test update tokens with invalid format raises ValidationError."""
        with pytest.raises(ValidationError, match="Tokens must be a dictionary"):
            client.update_tokens({"tokens": "not_a_dict"})

    def test_update_tokens_validation_error_invalid_values(self, client):
        """Test update tokens with invalid values raises ValidationError."""
        with pytest.raises(ValidationError, match="All token values must be lists"):
            client.update_tokens({"tokens": {"key": "not_a_list"}})

    @patch("requests.Session.request")
    def test_update_schema_success(self, mock_request, client, mock_response):
        """Test successful schema update."""
        mock_request.return_value = mock_response

        result = client.update_schema({"search_schema": {"tables": {}}})

        assert result["success"] is True
        mock_request.assert_called_once()

    def test_update_schema_validation_error(self, client):
        """Test update schema without search_schema raises ValidationError."""
        with pytest.raises(ValidationError, match="search_schema is required"):
            client.update_schema({})

    @patch("requests.Session.request")
    def test_get_tokens_success(self, mock_request, client, mock_response):
        """Test successful get tokens."""
        mock_request.return_value = mock_response
        mock_response.json.return_value = {
            "tokens": {"category": ["token1"]},
            "org_id": "test-org-id",
        }

        result = client.get_tokens()

        assert "tokens" in result
        assert result["org_id"] == "test-org-id"
        mock_request.assert_called_once()

    @patch("requests.Session.request")
    def test_get_schema_success(self, mock_request, client, mock_response):
        """Test successful get schema."""
        mock_request.return_value = mock_response
        mock_response.json.return_value = {
            "search_schema": {"tables": {}},
            "org_id": "test-org-id",
        }

        result = client.get_schema()

        assert "search_schema" in result
        assert result["org_id"] == "test-org-id"
        mock_request.assert_called_once()

    @patch("requests.Session.request")
    def test_health_check_success(self, mock_request, client, mock_response):
        """Test successful health check."""
        mock_request.return_value = mock_response
        mock_response.json.return_value = {"status": "healthy"}

        result = client.health_check()

        assert result["status"] == "healthy"
        mock_request.assert_called_once()

    @patch("requests.Session.request")
    def test_api_error_handling(self, mock_request, client):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.reason = "Bad Request"
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_request.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            client.search({"query": "test"})

        assert exc_info.value.status_code == 400
        assert "Invalid request" in str(exc_info.value)

    @patch("requests.Session.request")
    def test_network_error_handling(self, mock_request, client):
        """Test network error handling."""
        mock_request.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        with pytest.raises(NetworkError, match="Connection error"):
            client.search({"query": "test"})

    @patch("requests.Session.request")
    def test_timeout_error_handling(self, mock_request, client):
        """Test timeout error handling."""
        mock_request.side_effect = requests.exceptions.Timeout("Request timeout")

        with pytest.raises(NetworkError, match="Request timeout"):
            client.search({"query": "test"})
