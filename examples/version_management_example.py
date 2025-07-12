"""
Example: Using Version Management with SysBot Connectors

This example demonstrates how to use the version management system
with SysBot connectors and Robot Framework keywords.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sysbot.utils.versionManager import version_manager


# Example 1: Creating versioned functions for a connector
class ExampleConnector:
    """Example connector demonstrating version management."""
    
    def __init__(self):
        self.version_manager = version_manager
    
    @version_manager.versioned("1.0.0", default="1.0.0")
    def connect_to_database(self, host, port, database):
        """Connect to database - Version 1.0.0 (basic connection)"""
        return {
            "version": "1.0.0", 
            "connection": f"Basic connection to {database} at {host}:{port}",
            "features": ["basic_auth"]
        }
    
    @version_manager.versioned("1.1.0")
    def connect_to_database(self, host, port, database, username=None, password=None):
        """Connect to database - Version 1.1.0 (with authentication)"""
        auth_info = f" with auth for {username}" if username else ""
        return {
            "version": "1.1.0",
            "connection": f"Authenticated connection to {database} at {host}:{port}{auth_info}",
            "features": ["basic_auth", "user_auth"]
        }
    
    @version_manager.versioned("2.0.0")
    def connect_to_database(self, host, port, database, username=None, password=None, ssl=True, pool_size=5):
        """Connect to database - Version 2.0.0 (with SSL and connection pooling)"""
        ssl_info = " with SSL" if ssl else " without SSL"
        auth_info = f" with auth for {username}" if username else ""
        return {
            "version": "2.0.0",
            "connection": f"Pooled connection ({pool_size} connections) to {database} at {host}:{port}{auth_info}{ssl_info}",
            "features": ["basic_auth", "user_auth", "ssl_support", "connection_pooling"]
        }
    
    def get_connection(self, version=None, **kwargs):
        """Get a database connection using specified version."""
        connect_func = self.version_manager.get_versioned_function("connect_to_database", version)
        return connect_func(self, **kwargs)


# Example 2: Robot Framework compatible keywords
class RobotFrameworkKeywords:
    """Example Robot Framework keywords with version management."""
    
    @version_manager.versioned("1.0.0", default="1.0.0")
    def send_http_request(self, url, method="GET"):
        """Send HTTP Request - Version 1.0.0 (basic request)"""
        return f"HTTP {method} request to {url} (v1.0.0 - basic)"
    
    @version_manager.versioned("1.1.0")
    def send_http_request(self, url, method="GET", headers=None):
        """Send HTTP Request - Version 1.1.0 (with headers support)"""
        header_info = f" with {len(headers)} headers" if headers else ""
        return f"HTTP {method} request to {url}{header_info} (v1.1.0 - with headers)"
    
    @version_manager.versioned("2.0.0")
    def send_http_request(self, url, method="GET", headers=None, timeout=30, retry_count=3):
        """Send HTTP Request - Version 2.0.0 (with timeout and retry)"""
        header_info = f" with {len(headers)} headers" if headers else ""
        return f"HTTP {method} request to {url}{header_info}, timeout={timeout}s, retries={retry_count} (v2.0.0 - with timeout/retry)"


def demonstrate_version_usage():
    """Demonstrate how to use the version management system."""
    
    print("=== SysBot Version Management Demo ===\n")
    
    # Create connector instance
    connector = ExampleConnector()
    keywords = RobotFrameworkKeywords()
    
    print("1. Testing Database Connector Versions:")
    print("-" * 40)
    
    # Test version 1.0.0 (basic)
    result_v1 = connector.get_connection(version="1.0.0", host="localhost", port=5432, database="mydb")
    print(f"Version 1.0.0: {result_v1['connection']}")
    print(f"Features: {result_v1['features']}\n")
    
    # Test version 1.1.0 (with auth)
    result_v1_1 = connector.get_connection(version="1.1.0", host="localhost", port=5432, database="mydb", username="admin", password="secret")
    print(f"Version 1.1.0: {result_v1_1['connection']}")
    print(f"Features: {result_v1_1['features']}\n")
    
    # Test version 2.0.0 (with SSL and pooling)
    result_v2 = connector.get_connection(version="2.0.0", host="localhost", port=5432, database="mydb", username="admin", password="secret", ssl=True, pool_size=10)
    print(f"Version 2.0.0: {result_v2['connection']}")
    print(f"Features: {result_v2['features']}\n")
    
    # Test default version
    result_default = connector.get_connection(host="localhost", port=5432, database="mydb")
    print(f"Default version: {result_default['connection']}")
    print(f"Features: {result_default['features']}\n")
    
    print("2. Testing Robot Framework Keywords:")
    print("-" * 40)
    
    # Test HTTP request keyword versions
    http_v1 = version_manager.get_versioned_function("send_http_request", "1.0.0")
    http_v1_1 = version_manager.get_versioned_function("send_http_request", "1.1.0")
    http_v2 = version_manager.get_versioned_function("send_http_request", "2.0.0")
    
    print(f"Version 1.0.0: {http_v1(keywords, 'https://example.com')}")
    print(f"Version 1.1.0: {http_v1_1(keywords, 'https://example.com', headers={'User-Agent': 'SysBot'})}")
    print(f"Version 2.0.0: {http_v2(keywords, 'https://example.com', headers={'User-Agent': 'SysBot'}, timeout=60, retry_count=5)}")
    
    print("\n3. Version Management Information:")
    print("-" * 40)
    
    # Show available functions and versions
    functions = version_manager.list_functions()
    print(f"Available versioned functions: {functions}")
    
    for func_name in functions:
        versions = version_manager.list_versions(func_name)
        default_version = version_manager.get_default_version(func_name)
        print(f"  {func_name}: versions {versions}, default={default_version}")
    
    print("\n4. Practical Usage Examples:")
    print("-" * 40)
    
    print("# In Robot Framework test file:")
    print("*** Keywords ***")
    print("Connect To Database V1")
    print("    # Uses version 1.0.0 (basic connection)")
    print("    ${result} =    Get Connection    version=1.0.0    host=localhost    port=5432    database=testdb")
    print("    RETURN    ${result}")
    print("")
    print("Connect To Database V2 With SSL")
    print("    # Uses version 2.0.0 (with SSL and pooling)")  
    print("    ${result} =    Get Connection    version=2.0.0    host=localhost    port=5432    database=testdb    username=admin    password=secret    ssl=True")
    print("    RETURN    ${result}")
    print("")
    print("Send Modern HTTP Request")
    print("    # Uses version 2.0.0 with timeout and retry")
    print("    ${result} =    Send HTTP Request    url=https://api.example.com    method=POST    timeout=60    retry_count=3")
    print("    RETURN    ${result}")


if __name__ == "__main__":
    demonstrate_version_usage()