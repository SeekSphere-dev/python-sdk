"""Basic usage examples for SeekSphere SDK."""

import asyncio

from seeksphere import APIError, NetworkError, SeekSphereClient, ValidationError


def main():
    """Demonstrate basic SDK usage."""
    # Initialize the client
    client = SeekSphereClient(
        {
            "base_url": "http://localhost:3004",  # Replace with your API URL
            "api_key": "your-org-id-here",  # Replace with your actual org_id
            "timeout": 30,
        }
    )

    try:
        # Example 1: Health check
        print("🔍 Checking API health...")
        health = client.health_check()
        print(f"✅ API Status: {health.get('status', 'unknown')}")
        print()

        # Example 2: Search with sql_only mode
        print("🔍 Searching with sql_only mode...")
        search_result = client.search(
            {"query": "show me all users from last month"}, mode="sql_only"
        )
        print(f"✅ Search successful: {search_result.get('success', False)}")
        print(f"   Mode: {search_result.get('mode')}")
        print(f"   Org ID: {search_result.get('org_id')}")
        print()

        # Example 3: Search with full mode
        print("🔍 Searching with full mode...")
        full_search_result = client.search(
            {"query": "analyze customer behavior trends"}, mode="full"
        )
        print(f"✅ Full search successful: {full_search_result.get('success', False)}")
        print()

        # Example 4: Update tokens
        print("🔧 Updating tokens...")
        update_tokens_result = client.update_tokens(
            {
                "tokens": {
                    "product_categories": [
                        "electronics",
                        "clothing",
                        "books",
                        "sports",
                    ],
                    "user_types": ["premium", "standard", "trial", "enterprise"],
                    "regions": ["north", "south", "east", "west", "central"],
                    "status_types": ["active", "inactive", "pending", "suspended"],
                }
            }
        )
        print(f"✅ Tokens updated: {update_tokens_result.get('success', False)}")
        print(f"   Message: {update_tokens_result.get('message', 'No message')}")
        print()

        # Example 5: Get current tokens
        print("📋 Getting current tokens...")
        current_tokens = client.get_tokens()
        print(f"✅ Retrieved tokens for org: {current_tokens.get('org_id')}")
        print(f"   Token categories: {list(current_tokens.get('tokens', {}).keys())}")
        print()

        # Example 6: Update schema
        print("🔧 Updating schema...")
        update_schema_result = client.update_schema(
            {
                "search_schema": {
                    "version": "1.0",
                    "tables": {
                        "users": {
                            "columns": ["id", "name", "email", "created_at", "status"],
                            "types": [
                                "int",
                                "varchar",
                                "varchar",
                                "datetime",
                                "varchar",
                            ],
                            "primary_key": "id",
                        },
                        "orders": {
                            "columns": [
                                "id",
                                "user_id",
                                "amount",
                                "status",
                                "created_at",
                            ],
                            "types": ["int", "int", "decimal", "varchar", "datetime"],
                            "primary_key": "id",
                            "foreign_keys": {"user_id": "users.id"},
                        },
                        "products": {
                            "columns": ["id", "name", "category", "price", "stock"],
                            "types": ["int", "varchar", "varchar", "decimal", "int"],
                            "primary_key": "id",
                        },
                    },
                    "relationships": [
                        {
                            "from": "orders.user_id",
                            "to": "users.id",
                            "type": "many_to_one",
                        },
                        {
                            "from": "order_items.order_id",
                            "to": "orders.id",
                            "type": "many_to_one",
                        },
                    ],
                }
            }
        )
        print(f"✅ Schema updated: {update_schema_result.get('success', False)}")
        print(f"   Message: {update_schema_result.get('message', 'No message')}")
        print()

        # Example 7: Get current schema
        print("📋 Getting current schema...")
        current_schema = client.get_schema()
        print(f"✅ Retrieved schema for org: {current_schema.get('org_id')}")
        schema_data = current_schema.get("search_schema", {})
        if isinstance(schema_data, dict) and "tables" in schema_data:
            print(f"   Tables: {list(schema_data['tables'].keys())}")
        print()

        print("🎉 All examples completed successfully!")

    except ValidationError as e:
        print(f"❌ Validation Error: {e}")
    except APIError as e:
        print(f"❌ API Error: {e}")
        if hasattr(e, "status_code"):
            print(f"   Status Code: {e.status_code}")
        if hasattr(e, "response_data"):
            print(f"   Response Data: {e.response_data}")
    except NetworkError as e:
        print(f"❌ Network Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


if __name__ == "__main__":
    main()
