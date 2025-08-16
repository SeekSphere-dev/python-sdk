# SeekSphere SDK

[![CI](https://github.com/seeksphere/seeksphere-sdk/workflows/CI/badge.svg)](https://github.com/seeksphere/seeksphere-sdk/actions)
[![PyPI version](https://badge.fury.io/py/seeksphere-sdk.svg)](https://badge.fury.io/py/seeksphere-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/seeksphere-sdk.svg)](https://pypi.org/project/seeksphere-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive Python SDK for interacting with the SeekSphere API. This SDK provides a clean, type-safe interface for search operations, token management, schema updates, and more.

## Features

- 🔍 **Search Operations**: Support for both `sql_only` and `full` search modes
- 🔧 **Token Management**: Create, update, and retrieve token mappings
- 📊 **Schema Management**: Manage and update search schemas
- 🛡️ **Error Handling**: Comprehensive error handling with custom exception types
- 🔄 **Automatic Retries**: Built-in retry logic with exponential backoff
- 📝 **Type Safety**: Full type hints and TypedDict support
- 🧪 **Well Tested**: Comprehensive test suite with 90%+ coverage
- 🚀 **Production Ready**: Robust error handling and logging

## Installation

```bash
pip install seeksphere-sdk
```

### Development Installation

```bash
git clone https://github.com/seeksphere/seeksphere-sdk
cd seeksphere-sdk
make setup-dev
```

## Quick Start

```python
from seeksphere import SeekSphereClient

# Initialize the client
client = SeekSphereClient({
    "base_url": "https://your-api-domain.com",
    "api_key": "your-org-id",  # org_id is used as the API key
    "timeout": 30  # optional, defaults to 30 seconds
})

# Search
result = client.search({"query": "your search query"}, mode="sql_only")

# Update tokens
client.update_tokens({
    "tokens": {
        "category1": ["token1", "token2"],
        "category2": ["token3", "token4"]
    }
})

# Update schema
client.update_schema({
    "search_schema": {
        # your schema object
    }
})
```

## API Methods

### `search(request, mode="sql_only")`
Perform a search query.

**Parameters:**
- `request`: Dictionary with `query` key containing the search string
- `mode`: Search mode, either `"sql_only"` or `"full"` (default: `"sql_only"`)

**Returns:** Search results dictionary

**Example:**
```python
# SQL-only search
result = client.search({"query": "show me all users"}, mode="sql_only")

# Full search
result = client.search({"query": "analyze customer trends"}, mode="full")
```

### `update_tokens(request)`
Update the tokens mapping.

**Parameters:**
- `request`: Dictionary with `tokens` key containing a mapping of categories to token lists

**Returns:** Success response dictionary

**Example:**
```python
client.update_tokens({
    "tokens": {
        "product_categories": ["electronics", "clothing", "books"],
        "user_types": ["premium", "standard", "trial"]
    }
})
```

### `update_schema(request)`
Update the search schema.

**Parameters:**
- `request`: Dictionary with `search_schema` key containing the schema object

**Returns:** Success response dictionary

**Example:**
```python
client.update_schema({
    "search_schema": {
        "tables": {
            "users": {
                "columns": ["id", "name", "email"],
                "types": ["int", "varchar", "varchar"]
            }
        }
    }
})
```

### `get_tokens()`
Get the current tokens mapping.

**Returns:** Dictionary with current tokens and org_id

**Example:**
```python
tokens = client.get_tokens()
print(tokens["tokens"])  # Current tokens mapping
```

### `get_schema()`
Get the current search schema.

**Returns:** Dictionary with current schema and org_id

**Example:**
```python
schema = client.get_schema()
print(schema["search_schema"])  # Current schema
```

### `health_check()`
Check the API health status.

**Returns:** Health status dictionary

**Example:**
```python
health = client.health_check()
print(health["status"])  # Should be "healthy"
```

## Configuration

The SDK automatically sets the following headers:
- `X-Org-Id`: Your provided `api_key` (org_id)
- `X-User-Id`: `"node_sdk"`
- `Content-Type`: `"application/json"`

## Error Handling

The SDK provides specific exception types:

```python
from seeksphere import SeekSphereClient, APIError, NetworkError, ValidationError

client = SeekSphereClient(config)

try:
    result = client.search({"query": "test"})
except ValidationError as e:
    print(f"Validation error: {e}")
except APIError as e:
    print(f"API error: {e} (Status: {e.status_code})")
except NetworkError as e:
    print(f"Network error: {e}")
```

### Exception Types

- `ValidationError`: Raised for invalid input parameters
- `APIError`: Raised for HTTP error responses (4xx, 5xx)
- `NetworkError`: Raised for network-related issues (timeouts, connection errors)
- `SeekSphereError`: Base exception class

## Advanced Usage

### Custom Timeout and Retry

```python
client = SeekSphereClient({
    "base_url": "https://api.seeksphere.com",
    "api_key": "your-org-id",
    "timeout": 60  # 60 seconds timeout
})
```

The SDK automatically retries failed requests with exponential backoff for:
- HTTP 429 (Too Many Requests)
- HTTP 5xx (Server Errors)

### Type Hints

The SDK is fully typed and supports type checking with mypy:

```python
from seeksphere import SeekSphereClient, SearchRequest, SearchResponse

client: SeekSphereClient = SeekSphereClient(config)
request: SearchRequest = {"query": "search term"}
response: SearchResponse = client.search(request)
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/seeksphere/seeksphere-sdk
cd seeksphere-sdk
make setup-dev
```

This will install the package in development mode, install all development dependencies, and set up pre-commit hooks.

### Available Make Commands

```bash
make help                 # Show all available commands
make test                 # Run tests
make test-cov            # Run tests with coverage
make lint                # Run linting checks
make format              # Format code
make type-check          # Run type checking
make security            # Run security checks
make build               # Build package
make clean               # Clean build artifacts
make check-all           # Run all checks
make release-check       # Check if ready for release
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run only fast tests
make test-fast

# Run integration tests
make test-integration
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **bandit**: Security scanning
- **pytest**: Testing framework
- **pre-commit**: Git hooks for code quality

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the test suite (`make check-all`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Release Process

1. Update version in `pyproject.toml` and `src/seeksphere/__init__.py`
2. Update `CHANGELOG.md` with new version details
3. Run `make release-check` to ensure everything is ready
4. Create a new release on GitHub
5. The CI/CD pipeline will automatically publish to PyPI

## Security

If you discover a security vulnerability, please send an email to security@seeksphere.com. All security vulnerabilities will be promptly addressed.

## Support

- 📖 [Documentation](https://docs.seeksphere.com)
- 🐛 [Issue Tracker](https://github.com/seeksphere/seeksphere-sdk/issues)
- 💬 [Discussions](https://github.com/seeksphere/seeksphere-sdk/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ by the SeekSphere team
- Thanks to all contributors who help improve this SDK