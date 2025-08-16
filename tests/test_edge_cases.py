"""Edge case tests for SeekSphere SDK."""

import pytest
from unittest.mock import Mock, patch
import json
import requests

from seeksphere import SeekSphereClient, APIError, NetworkError, ValidationError


@pytest.fixture
def client():
    """Create test client."""
    return SeekSphereClient({
        "base_url": "https://api.test.com",
        "api_key": "test-org-id",
        "timeout": 30
    })


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_config_values(self):
        """Test handling of empty config values."""
        # Empty base_url should work but result in empty string after rstrip
        client1 = SeekSphereClient({"base_url": "", "api_key": "test"})
        assert client1.base_url == ""
        
        # Empty api_key should work (though not recommended)
        client2 = SeekSphereClient({"base_url": "https://api.test.com", "api_key": ""})
        assert client2.api_key == ""

    def test_base_url_variations(self):
        """Test different base URL formats."""
        # With trailing slash
        client1 = SeekSphereClient({
            "base_url": "https://api.test.com/",
            "api_key": "test"
        })
        assert client1.base_url == "https://api.test.com"
        
        # With multiple trailing slashes
        client2 = SeekSphereClient({
            "base_url": "https://api.test.com///",
            "api_key": "test"
        })
        assert client2.base_url == "https://api.test.com"
        
        # With path
        client3 = SeekSphereClient({
            "base_url": "https://api.test.com/v1/",
            "api_key": "test"
        })
        assert client3.base_url == "https://api.test.com/v1"

    def test_search_query_edge_cases(self, client):
        """Test search with edge case queries."""
        # Very long query
        long_query = "a" * 10000
        with pytest.raises(ValidationError, match="Query string is required"):
            client.search({"query": ""})
        
        # Query with special characters
        special_query = "SELECT * FROM users WHERE name = 'O''Reilly' AND age > 25;"
        # This should not raise validation error (only empty queries should)
        try:
            with patch('requests.Session.request') as mock_request:
                mock_resp = Mock()
                mock_resp.ok = True
                mock_resp.json.return_value = {"success": True}
                mock_request.return_value = mock_resp
                
                client.search({"query": special_query})
        except ValidationError:
            pytest.fail("Should not raise ValidationError for non-empty query")
        
        # Query with unicode characters
        unicode_query = "SELECT * FROM users WHERE name = 'José' AND city = '北京'"
        try:
            with patch('requests.Session.request') as mock_request:
                mock_resp = Mock()
                mock_resp.ok = True
                mock_resp.json.return_value = {"success": True}
                mock_request.return_value = mock_resp
                
                client.search({"query": unicode_query})
        except ValidationError:
            pytest.fail("Should not raise ValidationError for unicode query")

    def test_tokens_validation_edge_cases(self, client):
        """Test token validation with edge cases."""
        # Empty tokens dict
        with pytest.raises(ValidationError, match="Tokens must be a dictionary"):
            client.update_tokens({"tokens": None})
        
        # Tokens with empty lists
        try:
            with patch('requests.Session.request') as mock_request:
                mock_resp = Mock()
                mock_resp.ok = True
                mock_resp.json.return_value = {"success": True}
                mock_request.return_value = mock_resp
                
                client.update_tokens({"tokens": {"category": []}})
        except ValidationError:
            pytest.fail("Should not raise ValidationError for empty token lists")
        
        # Tokens with non-string keys
        with pytest.raises(ValidationError, match="All token keys must be strings"):
            client.update_tokens({"tokens": {123: ["token1"]}})
        
        # Tokens with non-list values
        with pytest.raises(ValidationError, match="All token values must be lists"):
            client.update_tokens({"tokens": {"category": "not_a_list"}})
        
        # Tokens with non-string list items
        with pytest.raises(ValidationError, match="All token values must be lists of strings"):
            client.update_tokens({"tokens": {"category": ["token1", 123, "token2"]}})
        
        # Very large token structure
        large_tokens = {
            f"category_{i}": [f"token_{i}_{j}" for j in range(100)]
            for i in range(50)
        }
        try:
            with patch('requests.Session.request') as mock_request:
                mock_resp = Mock()
                mock_resp.ok = True
                mock_resp.json.return_value = {"success": True}
                mock_request.return_value = mock_resp
                
                client.update_tokens({"tokens": large_tokens})
        except ValidationError:
            pytest.fail("Should not raise ValidationError for large but valid token structure")

    @patch('requests.Session.request')
    def test_malformed_json_response(self, mock_request, client):
        """Test handling of malformed JSON responses."""
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_request.return_value = mock_resp
        
        with pytest.raises(APIError, match="Invalid JSON response"):
            client.health_check()

    @patch('requests.Session.request')
    def test_empty_response_body(self, mock_request, client):
        """Test handling of empty response body."""
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = {}
        mock_request.return_value = mock_resp
        
        result = client.health_check()
        assert result == {}

    @patch('requests.Session.request')
    def test_http_error_without_json_body(self, mock_request, client):
        """Test handling of HTTP errors without JSON body."""
        mock_resp = Mock()
        mock_resp.ok = False
        mock_resp.status_code = 500
        mock_resp.reason = "Internal Server Error"
        mock_resp.json.side_effect = json.JSONDecodeError("No JSON", "", 0)
        mock_request.return_value = mock_resp
        
        with pytest.raises(APIError) as exc_info:
            client.health_check()
        
        assert exc_info.value.status_code == 500
        assert "HTTP 500: Internal Server Error" in str(exc_info.value)

    @patch('requests.Session.request')
    def test_network_timeout_scenarios(self, mock_request, client):
        """Test different network timeout scenarios."""
        # Connection timeout
        mock_request.side_effect = requests.exceptions.ConnectTimeout("Connection timeout")
        with pytest.raises(NetworkError, match="Request timeout"):
            client.health_check()
        
        # Read timeout
        mock_request.side_effect = requests.exceptions.ReadTimeout("Read timeout")
        with pytest.raises(NetworkError, match="Request timeout"):
            client.health_check()
        
        # Generic timeout
        mock_request.side_effect = requests.exceptions.Timeout("Timeout")
        with pytest.raises(NetworkError, match="Request timeout"):
            client.health_check()

    @patch('requests.Session.request')
    def test_various_connection_errors(self, mock_request, client):
        """Test various connection error scenarios."""
        # DNS resolution error
        mock_request.side_effect = requests.exceptions.ConnectionError("DNS lookup failed")
        with pytest.raises(NetworkError, match="Connection error"):
            client.health_check()
        
        # Connection refused
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection refused")
        with pytest.raises(NetworkError, match="Connection error"):
            client.health_check()
        
        # SSL error
        mock_request.side_effect = requests.exceptions.SSLError("SSL handshake failed")
        with pytest.raises(NetworkError, match="SSL error: SSL handshake failed"):
            client.health_check()
        
        # Generic request exception
        mock_request.side_effect = requests.exceptions.RequestException("Generic request error")
        with pytest.raises(NetworkError, match="Network error: Generic request error"):
            client.health_check()

    def test_invalid_search_mode_types(self, client):
        """Test invalid search mode types."""
        with pytest.raises(ValidationError, match="Mode must be either"):
            client.search({"query": "test"}, mode="invalid")
        
        with pytest.raises(ValidationError, match="Mode must be either"):
            client.search({"query": "test"}, mode=123)
        
        with pytest.raises(ValidationError, match="Mode must be either"):
            client.search({"query": "test"}, mode=None)

    def test_request_parameter_types(self, client):
        """Test various request parameter types."""
        # Non-dict request
        with pytest.raises(AttributeError):
            client.search("not_a_dict")
        
        # Missing query key
        with pytest.raises(ValidationError, match="Query string is required"):
            client.search({})
        
        # Non-string query
        with pytest.raises(ValidationError, match="Query string is required"):
            client.search({"query": 123})
        
        # None query
        with pytest.raises(ValidationError, match="Query string is required"):
            client.search({"query": None})

    @patch('requests.Session.request')
    def test_response_status_code_edge_cases(self, mock_request, client):
        """Test handling of various HTTP status codes."""
        status_codes = [200, 201, 204, 400, 401, 403, 404, 429, 500, 502, 503, 504]
        
        for status_code in status_codes:
            mock_resp = Mock()
            mock_resp.ok = status_code < 400
            mock_resp.status_code = status_code
            mock_resp.reason = f"Status {status_code}"
            
            if status_code < 400:
                mock_resp.json.return_value = {"success": True}
                mock_request.return_value = mock_resp
                
                result = client.health_check()
                assert result["success"] is True
            else:
                mock_resp.json.return_value = {"error": f"Error {status_code}"}
                mock_request.return_value = mock_resp
                
                with pytest.raises(APIError) as exc_info:
                    client.health_check()
                
                assert exc_info.value.status_code == status_code

    def test_config_type_validation(self):
        """Test configuration type validation."""
        # Test with missing required fields
        with pytest.raises(KeyError):
            SeekSphereClient({})
        
        with pytest.raises(KeyError):
            SeekSphereClient({"base_url": "https://api.test.com"})
        
        with pytest.raises(KeyError):
            SeekSphereClient({"api_key": "test"})
        
        # Test with extra fields (should be ignored)
        client = SeekSphereClient({
            "base_url": "https://api.test.com",
            "api_key": "test",
            "extra_field": "ignored"
        })
        assert client.base_url == "https://api.test.com"
        assert client.api_key == "test"

    @patch('requests.Session.request')
    def test_unicode_handling(self, mock_request, client):
        """Test Unicode character handling in requests and responses."""
        # Unicode in request
        unicode_tokens = {
            "tokens": {
                "中文": ["北京", "上海"],
                "español": ["madrid", "barcelona"],
                "العربية": ["الرياض", "دبي"]
            }
        }
        
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"success": True, "message": "Unicode handled ✓"}
        mock_request.return_value = mock_resp
        
        result = client.update_tokens(unicode_tokens)
        assert result["success"] is True
        assert "✓" in result["message"]
        
        # Verify Unicode was properly sent
        call_args = mock_request.call_args
        sent_data = call_args[1]['json']
        assert "中文" in sent_data["tokens"]
        assert "español" in sent_data["tokens"]