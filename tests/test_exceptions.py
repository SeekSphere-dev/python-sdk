"""Tests for SeekSphere exceptions."""

import pytest
from seeksphere.exceptions import SeekSphereError, APIError, NetworkError, ValidationError


class TestExceptions:
    """Test exception classes."""

    def test_seeksphere_error_base(self):
        """Test base SeekSphereError."""
        error = SeekSphereError("Base error")
        assert str(error) == "Base error"
        assert isinstance(error, Exception)

    def test_api_error_basic(self):
        """Test APIError with basic message."""
        error = APIError("API failed")
        assert str(error) == "API failed"
        assert error.status_code is None
        assert error.response_data == {}
        assert isinstance(error, SeekSphereError)

    def test_api_error_with_status_code(self):
        """Test APIError with status code."""
        error = APIError("API failed", status_code=404)
        assert str(error) == "API failed"
        assert error.status_code == 404
        assert error.response_data == {}

    def test_api_error_with_response_data(self):
        """Test APIError with response data."""
        response_data = {"error": "Not found", "code": "RESOURCE_NOT_FOUND"}
        error = APIError("API failed", status_code=404, response_data=response_data)
        assert str(error) == "API failed"
        assert error.status_code == 404
        assert error.response_data == response_data

    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, SeekSphereError)

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"
        assert isinstance(error, SeekSphereError)

    def test_exception_inheritance(self):
        """Test exception inheritance chain."""
        api_error = APIError("test")
        network_error = NetworkError("test")
        validation_error = ValidationError("test")
        
        assert isinstance(api_error, SeekSphereError)
        assert isinstance(network_error, SeekSphereError)
        assert isinstance(validation_error, SeekSphereError)
        
        assert isinstance(api_error, Exception)
        assert isinstance(network_error, Exception)
        assert isinstance(validation_error, Exception)