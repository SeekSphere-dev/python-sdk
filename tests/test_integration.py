"""Integration tests for SeekSphere SDK."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import json

from seeksphere import SeekSphereClient, APIError, NetworkError, ValidationError


@pytest.fixture
def mock_server():
    """Mock server responses for integration testing."""
    class MockServer:
        def __init__(self):
            self.responses = {}
            self.request_history = []
        
        def set_response(self, endpoint, method, response_data, status_code=200):
            """Set mock response for endpoint."""
            key = f"{method.upper()}:{endpoint}"
            mock_response = Mock()
            mock_response.ok = status_code < 400
            mock_response.status_code = status_code
            mock_response.reason = "OK" if status_code < 400 else "Error"
            mock_response.json.return_value = response_data
            self.responses[key] = mock_response
        
        def get_response(self, method, url):
            """Get mock response for request."""
            # Extract endpoint from URL
            endpoint = url.split("localhost:3004")[-1] if "localhost:3004" in url else url
            key = f"{method.upper()}:{endpoint}"
            return self.responses.get(key)
    
    return MockServer()


@pytest.fixture
def client():
    """Create test client."""
    return SeekSphereClient({
        "base_url": "http://localhost:3004",
        "api_key": "test-org-id",
        "timeout": 30
    })


class TestIntegration:
    """Integration test scenarios."""

    @patch('requests.Session.request')
    def test_complete_workflow(self, mock_request, client, mock_server):
        """Test complete workflow: health check -> update schema -> update tokens -> search."""
        # Setup mock responses
        mock_server.set_response("/health", "GET", {"status": "healthy"})
        mock_server.set_response("/org/search_schema", "PUT", {"success": True, "message": "Schema updated"})
        mock_server.set_response("/org/tokens", "PUT", {"success": True, "message": "Tokens updated"})
        mock_server.set_response("/search", "POST", {
            "success": True,
            "org_id": "test-org-id",
            "mode": "sql_only",
            "user_id": "node_sdk",
            "results": []
        })
        
        def side_effect(*args, **kwargs):
            method = kwargs.get('method', args[0] if args else 'GET')
            url = kwargs.get('url', args[1] if len(args) > 1 else '')
            response = mock_server.get_response(method, url)
            if response:
                return response
            # Default response
            mock_resp = Mock()
            mock_resp.ok = True
            mock_resp.json.return_value = {"success": True}
            return mock_resp
        
        mock_request.side_effect = side_effect
        
        # 1. Health check
        health = client.health_check()
        assert health["status"] == "healthy"
        
        # 2. Update schema
        schema_result = client.update_schema({
            "search_schema": {
                "tables": {
                    "users": {"columns": ["id", "name"], "types": ["int", "varchar"]}
                }
            }
        })
        assert schema_result["success"] is True
        
        # 3. Update tokens
        tokens_result = client.update_tokens({
            "tokens": {"categories": ["electronics", "books"]}
        })
        assert tokens_result["success"] is True
        
        # 4. Search
        search_result = client.search({"query": "find all users"})
        assert search_result["success"] is True
        assert search_result["org_id"] == "test-org-id"
        
        # Verify all requests were made
        assert mock_request.call_count == 4

    @patch('requests.Session.request')
    def test_error_recovery_workflow(self, mock_request, client):
        """Test error recovery scenarios."""
        call_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            # First call fails with 500
            if call_count == 1:
                mock_resp = Mock()
                mock_resp.ok = False
                mock_resp.status_code = 500
                mock_resp.reason = "Internal Server Error"
                mock_resp.json.return_value = {"error": "Server error"}
                return mock_resp
            
            # Second call succeeds
            mock_resp = Mock()
            mock_resp.ok = True
            mock_resp.json.return_value = {"status": "healthy"}
            return mock_resp
        
        mock_request.side_effect = side_effect
        
        # First call should raise APIError
        with pytest.raises(APIError) as exc_info:
            client.health_check()
        
        assert exc_info.value.status_code == 500
        assert "Server error" in str(exc_info.value)
        
        # Second call should succeed
        result = client.health_check()
        assert result["status"] == "healthy"

    @patch('requests.Session.request')
    def test_concurrent_requests_simulation(self, mock_request, client):
        """Simulate concurrent requests behavior."""
        responses = [
            {"success": True, "request_id": 1},
            {"success": True, "request_id": 2},
            {"success": True, "request_id": 3}
        ]
        
        def side_effect(*args, **kwargs):
            # Return different response based on request data
            data = kwargs.get('json', {})
            query = data.get('query', '')
            
            if 'query1' in query:
                mock_resp = Mock()
                mock_resp.ok = True
                mock_resp.json.return_value = responses[0]
                return mock_resp
            elif 'query2' in query:
                mock_resp = Mock()
                mock_resp.ok = True
                mock_resp.json.return_value = responses[1]
                return mock_resp
            else:
                mock_resp = Mock()
                mock_resp.ok = True
                mock_resp.json.return_value = responses[2]
                return mock_resp
        
        mock_request.side_effect = side_effect
        
        # Simulate concurrent requests
        results = []
        for i in range(3):
            result = client.search({"query": f"query{i+1}"})
            results.append(result)
        
        # Verify all requests completed successfully
        assert len(results) == 3
        assert all(r["success"] for r in results)
        assert [r["request_id"] for r in results] == [1, 2, 3]

    @patch('requests.Session.request')
    def test_large_payload_handling(self, mock_request, client):
        """Test handling of large payloads."""
        # Create large schema
        large_schema = {
            "search_schema": {
                "tables": {
                    f"table_{i}": {
                        "columns": [f"col_{j}" for j in range(50)],
                        "types": ["varchar"] * 50
                    }
                    for i in range(20)
                }
            }
        }
        
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"success": True, "message": "Large schema updated"}
        mock_request.return_value = mock_resp
        
        result = client.update_schema(large_schema)
        assert result["success"] is True
        
        # Verify the request was made with large payload
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]['json'] == large_schema

    def test_session_configuration(self, client):
        """Test session is properly configured."""
        session = client.session
        
        # Check headers
        assert session.headers["Content-Type"] == "application/json"
        assert session.headers["X-Org-Id"] == "test-org-id"
        assert session.headers["X-User-Id"] == "node_sdk"
        
        # Check adapters are mounted
        assert "http://" in session.adapters
        assert "https://" in session.adapters
        
        # Check retry configuration
        http_adapter = session.adapters["http://"]
        assert hasattr(http_adapter, 'max_retries')

    @patch('requests.Session.request')
    def test_timeout_configuration(self, mock_request):
        """Test timeout configuration is respected."""
        # Create client with custom timeout
        client = SeekSphereClient({
            "base_url": "http://localhost:3004",
            "api_key": "test-org-id",
            "timeout": 60
        })
        
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"status": "healthy"}
        mock_request.return_value = mock_resp
        
        client.health_check()
        
        # Verify timeout was passed to request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]['timeout'] == 60

    @patch('requests.Session.request')
    def test_custom_headers_in_search(self, mock_request, client):
        """Test custom headers are properly set for search requests."""
        mock_resp = Mock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"success": True}
        mock_request.return_value = mock_resp
        
        # Test sql_only mode
        client.search({"query": "test"}, mode="sql_only")
        
        call_args = mock_request.call_args
        headers = call_args[1]['headers']
        assert headers["X-Mode"] == "sql_only"
        
        # Test full mode
        client.search({"query": "test"}, mode="full")
        
        call_args = mock_request.call_args
        headers = call_args[1]['headers']
        assert headers["X-Mode"] == "full"