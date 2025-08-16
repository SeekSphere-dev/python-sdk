"""Advanced usage examples for SeekSphere SDK."""

import time
import logging
from typing import Dict, Any, Optional
from seeksphere import SeekSphereClient, APIError, NetworkError, ValidationError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeekSphereManager:
    """Advanced wrapper for SeekSphere client with additional functionality."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the manager with configuration."""
        self.client = SeekSphereClient(config)
        self.org_id = config["api_key"]
        self.retry_attempts = 3
        self.retry_delay = 1.0
    
    def safe_api_call(self, operation: str, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Make API call with comprehensive error handling and retry logic."""
        for attempt in range(self.retry_attempts):
            try:
                method = getattr(self.client, operation)
                result = method(*args, **kwargs)
                logger.info(f"✅ {operation} succeeded on attempt {attempt + 1}")
                return result
                
            except ValidationError as e:
                logger.error(f"❌ Validation error in {operation}: {e}")
                return None  # Don't retry validation errors
                
            except APIError as e:
                if hasattr(e, 'status_code'):
                    if e.status_code == 429:  # Rate limited
                        wait_time = self.retry_delay * (2 ** attempt)
                        logger.warning(f"⏳ Rate limited, waiting {wait_time}s before retry")
                        time.sleep(wait_time)
                        continue
                    elif e.status_code >= 500:  # Server errors
                        wait_time = self.retry_delay * (2 ** attempt)
                        logger.warning(f"⏳ Server error, waiting {wait_time}s before retry")
                        time.sleep(wait_time)
                        continue
                    else:  # Client errors (4xx) - don't retry
                        logger.error(f"❌ API error in {operation}: {e}")
                        return None
                else:
                    logger.error(f"❌ API error in {operation}: {e}")
                    return None
                    
            except NetworkError as e:
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"⏳ Network error, waiting {wait_time}s before retry: {e}")
                time.sleep(wait_time)
                continue
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in {operation}: {e}")
                return None
        
        logger.error(f"❌ {operation} failed after {self.retry_attempts} attempts")
        return None
    
    def batch_update_tokens(self, token_batches: Dict[str, Dict[str, list]]) -> Dict[str, bool]:
        """Update tokens in batches with individual success tracking."""
        results = {}
        
        for batch_name, tokens in token_batches.items():
            logger.info(f"🔄 Updating token batch: {batch_name}")
            result = self.safe_api_call("update_tokens", {"tokens": tokens})
            results[batch_name] = result is not None and result.get("success", False)
            
            if results[batch_name]:
                logger.info(f"✅ Token batch '{batch_name}' updated successfully")
            else:
                logger.error(f"❌ Token batch '{batch_name}' failed to update")
        
        return results
    
    def validate_and_update_schema(self, schema: Dict[str, Any]) -> bool:
        """Validate schema structure before updating."""
        # Basic schema validation
        if not isinstance(schema, dict):
            logger.error("Schema must be a dictionary")
            return False
        
        if "search_schema" not in schema:
            logger.error("Schema must contain 'search_schema' key")
            return False
        
        search_schema = schema["search_schema"]
        if not isinstance(search_schema, dict):
            logger.error("search_schema must be a dictionary")
            return False
        
        # Validate tables structure if present
        if "tables" in search_schema:
            tables = search_schema["tables"]
            if not isinstance(tables, dict):
                logger.error("tables must be a dictionary")
                return False
            
            for table_name, table_def in tables.items():
                if not isinstance(table_def, dict):
                    logger.error(f"Table definition for '{table_name}' must be a dictionary")
                    return False
                
                required_fields = ["columns", "types"]
                for field in required_fields:
                    if field not in table_def:
                        logger.error(f"Table '{table_name}' missing required field: {field}")
                        return False
                
                columns = table_def["columns"]
                types = table_def["types"]
                
                if not isinstance(columns, list) or not isinstance(types, list):
                    logger.error(f"Table '{table_name}' columns and types must be lists")
                    return False
                
                if len(columns) != len(types):
                    logger.error(f"Table '{table_name}' columns and types length mismatch")
                    return False
        
        logger.info("✅ Schema validation passed")
        
        # Update schema
        result = self.safe_api_call("update_schema", schema)
        return result is not None and result.get("success", False)
    
    def search_with_fallback(self, query: str, preferred_mode: str = "full") -> Optional[Dict[str, Any]]:
        """Search with fallback to different mode if preferred fails."""
        modes = [preferred_mode, "sql_only" if preferred_mode == "full" else "full"]
        
        for mode in modes:
            logger.info(f"🔍 Attempting search with mode: {mode}")
            result = self.safe_api_call("search", {"query": query}, mode=mode)
            
            if result and result.get("success"):
                logger.info(f"✅ Search succeeded with mode: {mode}")
                return result
            else:
                logger.warning(f"⚠️ Search failed with mode: {mode}")
        
        logger.error("❌ Search failed with all modes")
        return None
    
    def health_monitor(self, check_interval: int = 30, max_checks: int = 10) -> bool:
        """Monitor API health with periodic checks."""
        logger.info(f"🏥 Starting health monitoring (interval: {check_interval}s, max checks: {max_checks})")
        
        healthy_checks = 0
        total_checks = 0
        
        for i in range(max_checks):
            total_checks += 1
            logger.info(f"🔍 Health check {i + 1}/{max_checks}")
            
            result = self.safe_api_call("health_check")
            
            if result and result.get("status") == "healthy":
                healthy_checks += 1
                logger.info("✅ API is healthy")
            else:
                logger.warning("⚠️ API health check failed")
            
            if i < max_checks - 1:  # Don't sleep after last check
                time.sleep(check_interval)
        
        health_ratio = healthy_checks / total_checks
        logger.info(f"📊 Health monitoring complete: {healthy_checks}/{total_checks} checks passed ({health_ratio:.1%})")
        
        return health_ratio >= 0.8  # Consider healthy if 80%+ checks pass


def demonstrate_advanced_features():
    """Demonstrate advanced SDK features."""
    # Initialize manager
    manager = SeekSphereManager({
        "base_url": "http://localhost:3004",
        "api_key": "your-org-id-here",
        "timeout": 30
    })
    
    print("🚀 Starting advanced SeekSphere SDK demonstration\n")
    
    # 1. Health monitoring
    print("1️⃣ Health Monitoring")
    is_healthy = manager.health_monitor(check_interval=2, max_checks=3)
    print(f"Overall health status: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}\n")
    
    # 2. Batch token updates
    print("2️⃣ Batch Token Updates")
    token_batches = {
        "user_attributes": {
            "user_types": ["premium", "standard", "trial", "enterprise"],
            "user_status": ["active", "inactive", "pending", "suspended"],
            "subscription_tiers": ["basic", "pro", "enterprise", "custom"]
        },
        "product_categories": {
            "electronics": ["smartphones", "laptops", "tablets", "accessories"],
            "clothing": ["shirts", "pants", "dresses", "shoes"],
            "books": ["fiction", "non-fiction", "textbooks", "comics"]
        },
        "geographic_regions": {
            "continents": ["north_america", "south_america", "europe", "asia", "africa", "oceania"],
            "countries": ["usa", "canada", "uk", "germany", "france", "japan", "australia"],
            "time_zones": ["pst", "est", "gmt", "cet", "jst", "aest"]
        }
    }
    
    batch_results = manager.batch_update_tokens(token_batches)
    successful_batches = sum(1 for success in batch_results.values() if success)
    print(f"Batch update results: {successful_batches}/{len(batch_batches)} batches successful\n")
    
    # 3. Schema validation and update
    print("3️⃣ Schema Validation and Update")
    complex_schema = {
        "search_schema": {
            "version": "2.0",
            "tables": {
                "users": {
                    "columns": ["id", "username", "email", "first_name", "last_name", "created_at", "updated_at", "status"],
                    "types": ["bigint", "varchar", "varchar", "varchar", "varchar", "timestamp", "timestamp", "varchar"],
                    "primary_key": "id",
                    "indexes": ["email", "username", "status"]
                },
                "orders": {
                    "columns": ["id", "user_id", "total_amount", "currency", "status", "created_at", "updated_at"],
                    "types": ["bigint", "bigint", "decimal", "varchar", "varchar", "timestamp", "timestamp"],
                    "primary_key": "id",
                    "foreign_keys": {"user_id": "users.id"},
                    "indexes": ["user_id", "status", "created_at"]
                },
                "products": {
                    "columns": ["id", "name", "description", "category", "price", "currency", "stock_quantity", "created_at"],
                    "types": ["bigint", "varchar", "text", "varchar", "decimal", "varchar", "integer", "timestamp"],
                    "primary_key": "id",
                    "indexes": ["category", "price"]
                },
                "order_items": {
                    "columns": ["id", "order_id", "product_id", "quantity", "unit_price", "total_price"],
                    "types": ["bigint", "bigint", "bigint", "integer", "decimal", "decimal"],
                    "primary_key": "id",
                    "foreign_keys": {"order_id": "orders.id", "product_id": "products.id"}
                }
            },
            "relationships": [
                {"from": "orders.user_id", "to": "users.id", "type": "many_to_one"},
                {"from": "order_items.order_id", "to": "orders.id", "type": "many_to_one"},
                {"from": "order_items.product_id", "to": "products.id", "type": "many_to_one"}
            ],
            "views": {
                "user_order_summary": {
                    "query": "SELECT u.id, u.username, COUNT(o.id) as order_count, SUM(o.total_amount) as total_spent FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.username"
                }
            }
        }
    }
    
    schema_updated = manager.validate_and_update_schema(complex_schema)
    print(f"Schema update result: {'✅ Success' if schema_updated else '❌ Failed'}\n")
    
    # 4. Advanced search with fallback
    print("4️⃣ Advanced Search with Fallback")
    search_queries = [
        "Show me the top 10 customers by total order value in the last 6 months",
        "Find all products with low stock (less than 10 items) in the electronics category",
        "Analyze user registration trends by month for the current year",
        "List all pending orders with their customer details and total values"
    ]
    
    for i, query in enumerate(search_queries, 1):
        print(f"Query {i}: {query[:50]}...")
        result = manager.search_with_fallback(query, preferred_mode="full")
        if result:
            print(f"✅ Search successful (mode: {result.get('mode', 'unknown')})")
        else:
            print("❌ Search failed")
        print()
    
    # 5. Get current state
    print("5️⃣ Current State Retrieval")
    current_tokens = manager.safe_api_call("get_tokens")
    current_schema = manager.safe_api_call("get_schema")
    
    if current_tokens:
        token_categories = list(current_tokens.get("tokens", {}).keys())
        print(f"✅ Current tokens retrieved: {len(token_categories)} categories")
        print(f"   Categories: {', '.join(token_categories[:5])}{'...' if len(token_categories) > 5 else ''}")
    else:
        print("❌ Failed to retrieve current tokens")
    
    if current_schema:
        schema_data = current_schema.get("search_schema", {})
        if isinstance(schema_data, dict) and "tables" in schema_data:
            table_names = list(schema_data["tables"].keys())
            print(f"✅ Current schema retrieved: {len(table_names)} tables")
            print(f"   Tables: {', '.join(table_names)}")
        else:
            print("✅ Current schema retrieved (structure unknown)")
    else:
        print("❌ Failed to retrieve current schema")
    
    print("\n🎉 Advanced demonstration complete!")


if __name__ == "__main__":
    demonstrate_advanced_features()