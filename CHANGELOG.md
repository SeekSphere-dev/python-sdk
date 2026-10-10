# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-10

### Changed
- **Breaking**: Authentication now uses a real per-org API key sent as `X-Api-Key`,
  created via `POST /org/api-keys` on a signed-in session. The previous scheme
  (sending the org ID as `X-Org-Id` with a fixed `X-User-Id: node_sdk`) no longer
  works against the current API.
- `update_tokens()` now accepts numeric token values (`str`, `int`, or `float`),
  matching the API's token map type.
- `SearchResponse` typing updated to match the current API contract (`source`,
  `processing_time_ms`, `pattern_used`, `cached`, etc.).
- `APIError` now carries the API's machine-readable `code` when present.
- Documented that `update_tokens()` and `update_schema()` require a signed-in
  user session and return `403 forbidden` for API-key callers.

## [1.0.0] - 2025-01-16

### Added
- Initial release of SeekSphere Python SDK
- Core client functionality for SeekSphere API
- Support for search operations with `sql_only` and `full` modes
- Token management (get/update tokens)
- Schema management (get/update search schema)
- Health check endpoint support
- Comprehensive error handling with custom exception types:
  - `APIError` for HTTP error responses
  - `NetworkError` for network-related issues
  - `ValidationError` for input validation errors
- Automatic retry mechanism with exponential backoff
- Full type hints support with TypedDict definitions
- Comprehensive test suite with 90%+ coverage
- Integration tests and edge case testing
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks for code quality
- Security scanning with bandit and safety

### Features
- **Client Configuration**: Flexible configuration with base URL, API key, and timeout
- **Session Management**: Persistent HTTP sessions with retry strategies
- **Request/Response Handling**: JSON-based communication with proper error handling
- **Type Safety**: Full typing support for better IDE integration and type checking
- **Validation**: Input validation for all API methods
- **Documentation**: Comprehensive README with examples and API documentation

### Dependencies
- `requests>=2.25.0` for HTTP client functionality
- `typing-extensions>=4.0.0` for Python <3.10 compatibility

### Development Dependencies
- `pytest>=7.0.0` for testing framework
- `pytest-cov>=4.0.0` for coverage reporting
- `black>=22.0.0` for code formatting
- `isort>=5.0.0` for import sorting
- `mypy>=1.0.0` for type checking
- `bandit>=1.7.0` for security scanning
- `safety>=2.0.0` for vulnerability checking

### API Methods
- `search(request, mode)` - Perform search queries
- `update_tokens(request)` - Update token mappings
- `update_schema(request)` - Update search schema
- `get_tokens()` - Retrieve current tokens
- `get_schema()` - Retrieve current schema
- `health_check()` - Check API health status

### Configuration
- Supports Python 3.8+
- MIT License
- Comprehensive error handling and logging
- Automatic request retries for transient failures
- Configurable timeouts and retry strategies