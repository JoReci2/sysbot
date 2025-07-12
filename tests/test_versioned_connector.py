"""
MIT License

Copyright (c) 2024 Thibault SCIRE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add the parent directory to the Python path so we can import sysbot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sysbot.utils.versionManager import version_manager


class TestVersionedConnector(unittest.TestCase):
    """Test cases for versioned connector functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear any previous registrations to avoid conflicts
        version_manager._function_versions.clear()
        version_manager._default_versions.clear()
        version_manager._robot_keywords.clear()
    
    def test_connector_version_methods(self):
        """Test basic version management in connectors."""
        # Mock the ConnectorInterface to avoid import issues
        class MockConnectorInterface:
            def __init__(self):
                self.version_manager = version_manager
                self._connector_version = "1.0.0"
            
            def set_connector_version(self, version):
                self._connector_version = version
            
            def get_connector_version(self):
                return self._connector_version
            
            def get_versioned_method(self, method_name, version=None):
                return self.version_manager.get_versioned_function(method_name, version)
        
        # Create a mock connector with versioned methods
        class MockConnector(MockConnectorInterface):
            def __init__(self):
                super().__init__()
            
            @version_manager.versioned("1.0.0", default="1.0.0")
            def process_data(self, data):
                return f"v1.0.0: {data.upper()}"
            
            @version_manager.versioned("2.0.0")
            def process_data(self, data):
                return f"v2.0.0: {data.lower()}"
        
        # Test connector
        connector = MockConnector()
        
        # Test version methods
        self.assertEqual(connector.get_connector_version(), "1.0.0")
        connector.set_connector_version("2.0.0")
        self.assertEqual(connector.get_connector_version(), "2.0.0")
        
        # Test versioned method access
        v1_method = connector.get_versioned_method("process_data", "1.0.0")
        v2_method = connector.get_versioned_method("process_data", "2.0.0")
        
        self.assertEqual(v1_method(connector, "Hello"), "v1.0.0: HELLO")
        self.assertEqual(v2_method(connector, "Hello"), "v2.0.0: hello")
        
        # Test default version
        default_method = connector.get_versioned_method("process_data")
        self.assertEqual(default_method(connector, "Hello"), "v1.0.0: HELLO")
    
    def test_function_versioning_workflow(self):
        """Test a complete versioning workflow similar to how connectors would work."""
        
        # Simulate evolving a function through versions
        @version_manager.versioned("1.0.0")
        def connect_to_server(host, port=22):
            return {"version": "1.0.0", "host": host, "port": port, "method": "basic"}
        
        @version_manager.versioned("1.1.0") 
        def connect_to_server(host, port=22, timeout=30):
            return {"version": "1.1.0", "host": host, "port": port, "timeout": timeout, "method": "with_timeout"}
        
        @version_manager.versioned("2.0.0", default="2.0.0")
        def connect_to_server(host, port=22, timeout=30, secure=True):
            return {"version": "2.0.0", "host": host, "port": port, "timeout": timeout, "secure": secure, "method": "secure"}
        
        # Test different versions
        v1_func = version_manager.get_versioned_function("connect_to_server", "1.0.0")
        result_v1 = v1_func("example.com")
        self.assertEqual(result_v1["version"], "1.0.0")
        self.assertEqual(result_v1["method"], "basic")
        
        v1_1_func = version_manager.get_versioned_function("connect_to_server", "1.1.0")
        result_v1_1 = v1_1_func("example.com", timeout=60)
        self.assertEqual(result_v1_1["version"], "1.1.0")
        self.assertEqual(result_v1_1["method"], "with_timeout")
        self.assertEqual(result_v1_1["timeout"], 60)
        
        v2_func = version_manager.get_versioned_function("connect_to_server", "2.0.0")
        result_v2 = v2_func("example.com", secure=False)
        self.assertEqual(result_v2["version"], "2.0.0")
        self.assertEqual(result_v2["method"], "secure")
        self.assertEqual(result_v2["secure"], False)
        
        # Test default version (should be 2.0.0)
        default_func = version_manager.get_versioned_function("connect_to_server")
        result_default = default_func("example.com")
        self.assertEqual(result_default["version"], "2.0.0")
    
    def test_robot_framework_compatibility(self):
        """Test Robot Framework keyword compatibility."""
        
        @version_manager.versioned("1.0.0", "2.0.0", default="2.0.0")
        def robot_keyword_example(message):
            """This is a Robot Framework compatible keyword."""
            return f"Robot says: {message}"
        
        # Add robot metadata manually (simulating Robot Framework decorator)
        robot_keyword_example.robot_name = "Robot Keyword Example"
        
        # Test that the function works normally
        func = version_manager.get_versioned_function("robot_keyword_example")
        result = func("Hello World")
        self.assertEqual(result, "Robot says: Hello World")
        
        # Test version listing
        versions = version_manager.list_versions("robot_keyword_example")
        self.assertIn("1.0.0", versions)
        self.assertIn("2.0.0", versions)
        
        # Test default version
        default_version = version_manager.get_default_version("robot_keyword_example")
        self.assertEqual(default_version, "2.0.0")
    
    def test_multiple_connectors_isolation(self):
        """Test that multiple connectors can use versioning independently."""
        
        # Connector A functions
        @version_manager.versioned("1.0.0")
        def connector_a_method(data):
            return f"ConnectorA-v1: {data}"
        
        @version_manager.versioned("2.0.0")
        def connector_a_method(data):
            return f"ConnectorA-v2: {data}"
        
        # Connector B functions (same method name, different implementation)
        @version_manager.versioned("1.0.0")
        def connector_b_method(data):
            return f"ConnectorB-v1: {data}"
        
        @version_manager.versioned("1.5.0")
        def connector_b_method(data):
            return f"ConnectorB-v1.5: {data}"
        
        # Test that both connectors work independently
        a_v1 = version_manager.get_versioned_function("connector_a_method", "1.0.0")
        a_v2 = version_manager.get_versioned_function("connector_a_method", "2.0.0")
        b_v1 = version_manager.get_versioned_function("connector_b_method", "1.0.0")
        b_v1_5 = version_manager.get_versioned_function("connector_b_method", "1.5.0")
        
        self.assertEqual(a_v1("test"), "ConnectorA-v1: test")
        self.assertEqual(a_v2("test"), "ConnectorA-v2: test")
        self.assertEqual(b_v1("test"), "ConnectorB-v1: test")
        self.assertEqual(b_v1_5("test"), "ConnectorB-v1.5: test")
        
        # Test version listings
        a_versions = version_manager.list_versions("connector_a_method")
        b_versions = version_manager.list_versions("connector_b_method")
        
        self.assertEqual(set(a_versions), {"1.0.0", "2.0.0"})
        self.assertEqual(set(b_versions), {"1.0.0", "1.5.0"})


if __name__ == '__main__':
    unittest.main()