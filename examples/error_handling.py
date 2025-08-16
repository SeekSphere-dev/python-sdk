"""Error handling examples for SeekSphere SDK."""

from seeksphere import SeekSphereClient, APIError, NetworkError, ValidationError


def demonstrate_error_handling():
    """Demonstrate different types of error handling."""
    
    # Initialize client with potentially problematic config
    client = SeekSphereClient({
        "base_url": "http://localhost:3004",
        "api_key": "test-org-id",
        "timeout": 5  # Short timeout for demonstration
    })

    print("🔍 Demonstrating error handling scenarios...\n")

    # Example 1: Validation Error
    print("1️⃣ Testing validation errors...")
    try:
        # Empty query should raise ValidationError
        client.search({"query": ""})
    except ValidationError as e:
        print(f"✅ Caught ValidationError: {e}")
    
    try:
        # Invalid mode should raise ValidationError
        client.search({"query": "test"}, mode="invalid_mode")
    except ValidationError as e:
        print(f"✅ Caught ValidationError: {e}")
    
    try:
        # Invalid tokens format should raise ValidationError
        client.update_tokens({"tokens": "not_a_dict"})
    except ValidationError as e:
        print(f"✅ Caught ValidationError: {e}")
    
    print()

    # Example 2: API Error (if server returns error)
    print("2️⃣ Testing API errors...")
    try:
        # This might cause an API error if org doesn't exist
        client.get_tokens()
    except APIError as e:
        print(f"✅ Caught APIError: {e}")
        print(f"   Status Code: {getattr(e, 'status_code', 'Unknown')}")
        print(f"   Response Data: {getattr(e, 'response_data', {})}")
    except Exception as e:
        print(f"ℹ️ Different error occurred: {type(e).__name__}: {e}")
    
    print()

    # Example 3: Network Error
    print("3️⃣ Testing network errors...")
    # Create client with invalid URL to trigger network error
    bad_client = SeekSphereClient({
        "base_url": "http://invalid-url-that-does-not-exist.com",
        "api_key": "test-org-id",
        "timeout": 2
    })
    
    try:
        bad_client.health_check()
    except NetworkError as e:
        print(f"✅ Caught NetworkError: {e}")
    except Exception as e:
        print(f"ℹ️ Different error occurred: {type(e).__name__}: {e}")
    
    print()

    # Example 4: Comprehensive error handling
    print("4️⃣ Comprehensive error handling pattern...")
    
    def safe_api_call():
        """Demonstrate comprehensive error handling pattern."""
        try:
            result = client.search({"query": "test search"})
            print(f"✅ Success: {result.get('success', False)}")
            return result
        except ValidationError as e:
            print(f"❌ Input validation failed: {e}")
            # Handle validation errors - maybe prompt user for correct input
            return None
        except APIError as e:
            print(f"❌ API request failed: {e}")
            if hasattr(e, 'status_code'):
                if e.status_code == 401:
                    print("   → Authentication issue - check your API key")
                elif e.status_code == 404:
                    print("   → Resource not found - check your org_id")
                elif e.status_code == 429:
                    print("   → Rate limited - wait before retrying")
                elif e.status_code >= 500:
                    print("   → Server error - try again later")
            return None
        except NetworkError as e:
            print(f"❌ Network issue: {e}")
            print("   → Check your internet connection and API URL")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {type(e).__name__}: {e}")
            # Log the error for debugging
            return None
    
    safe_api_call()
    
    print("\n🎯 Error handling demonstration complete!")


def retry_with_backoff_example():
    """Example of implementing retry logic with exponential backoff."""
    import time
    import random
    
    print("\n🔄 Demonstrating retry with backoff...")
    
    client = SeekSphereClient({
        "base_url": "http://localhost:3004",
        "api_key": "test-org-id"
    })
    
    def api_call_with_retry(max_retries=3):
        """API call with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                result = client.search({"query": "retry test"})
                print(f"✅ Success on attempt {attempt + 1}")
                return result
            except APIError as e:
                if hasattr(e, 'status_code') and e.status_code == 429:
                    # Rate limited - implement exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"⏳ Rate limited, waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    # Other API errors shouldn't be retried
                    print(f"❌ API error (no retry): {e}")
                    break
            except NetworkError as e:
                # Network errors can be retried
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"⏳ Network error, waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}: {e}")
                time.sleep(wait_time)
                continue
            except Exception as e:
                # Unexpected errors shouldn't be retried
                print(f"❌ Unexpected error (no retry): {e}")
                break
        
        print(f"❌ Failed after {max_retries} attempts")
        return None
    
    api_call_with_retry()


if __name__ == "__main__":
    demonstrate_error_handling()
    retry_with_backoff_example()