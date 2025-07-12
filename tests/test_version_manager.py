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

# Add the parent directory to the Python path so we can import sysbot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sysbot.utils.versionManager import VersionManager, version_manager


class TestVersionManager(unittest.TestCase):
    """Test cases for the VersionManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.vm = VersionManager()
    
    def test_versioned_decorator_single_version(self):
        """Test the versioned decorator with a single version."""
        @self.vm.versioned("1.0.0")
        def test_function():
            return "version 1.0.0"
        
        # Test that the function is registered
        result = self.vm.get_versioned_function("test_function", "1.0.0")
        self.assertEqual(result(), "version 1.0.0")
    
    def test_versioned_decorator_multiple_versions(self):
        """Test the versioned decorator with multiple versions."""
        @self.vm.versioned("1.0.0", "1.1.0", "2.0.0")
        def multi_version_function():
            return "multi-version function"
        
        # Test that all versions are registered
        for version in ["1.0.0", "1.1.0", "2.0.0"]:
            result = self.vm.get_versioned_function("multi_version_function", version)
            self.assertEqual(result(), "multi-version function")
    
    def test_versioned_decorator_with_default(self):
        """Test the versioned decorator with a default version."""
        @self.vm.versioned("1.0.0", "2.0.0", default="2.0.0")
        def function_with_default():
            return "function with default"
        
        # Test default version retrieval
        result = self.vm.get_versioned_function("function_with_default")
        self.assertEqual(result(), "function with default")
        
        # Test explicit version retrieval
        result = self.vm.get_versioned_function("function_with_default", "1.0.0")
        self.assertEqual(result(), "function with default")
    
    def test_different_function_versions(self):
        """Test that different versions can have different implementations."""
        @self.vm.versioned("1.0.0")
        def evolving_function():
            return "version 1.0.0"
        
        @self.vm.versioned("2.0.0")
        def evolving_function():  # Same name, different implementation
            return "version 2.0.0"
        
        # Test that different versions return different results
        result_v1 = self.vm.get_versioned_function("evolving_function", "1.0.0")
        result_v2 = self.vm.get_versioned_function("evolving_function", "2.0.0")
        
        self.assertEqual(result_v1(), "version 1.0.0")
        self.assertEqual(result_v2(), "version 2.0.0")
    
    def test_get_versioned_function_not_found(self):
        """Test error handling when function is not found."""
        with self.assertRaises(ValueError) as context:
            self.vm.get_versioned_function("nonexistent_function", "1.0.0")
        
        self.assertIn("Function 'nonexistent_function' not found", str(context.exception))
    
    def test_get_versioned_function_version_not_found(self):
        """Test error handling when version is not found."""
        @self.vm.versioned("1.0.0")
        def existing_function():
            return "test"
        
        with self.assertRaises(ValueError) as context:
            self.vm.get_versioned_function("existing_function", "2.0.0")
        
        self.assertIn("Version '2.0.0' of 'existing_function' not found", str(context.exception))
    
    def test_list_versions(self):
        """Test listing versions for a function."""
        @self.vm.versioned("1.0.0", "1.1.0", "2.0.0")
        def test_function():
            return "test"
        
        versions = self.vm.list_versions("test_function")
        self.assertEqual(set(versions), {"1.0.0", "1.1.0", "2.0.0"})
        
        # Test for non-existent function
        self.assertEqual(self.vm.list_versions("nonexistent"), [])
    
    def test_list_functions(self):
        """Test listing all versioned functions."""
        @self.vm.versioned("1.0.0")
        def function_one():
            return "one"
        
        @self.vm.versioned("1.0.0")
        def function_two():
            return "two"
        
        functions = self.vm.list_functions()
        self.assertIn("function_one", functions)
        self.assertIn("function_two", functions)
    
    def test_get_default_version(self):
        """Test getting the default version."""
        @self.vm.versioned("1.0.0", "2.0.0", default="2.0.0")
        def function_with_default():
            return "test"
        
        default = self.vm.get_default_version("function_with_default")
        self.assertEqual(default, "2.0.0")
        
        # Test for function without explicit default (should use first version)
        @self.vm.versioned("3.0.0", "4.0.0")
        def function_auto_default():
            return "test"
        
        auto_default = self.vm.get_default_version("function_auto_default")
        self.assertEqual(auto_default, "3.0.0")
    
    def test_set_default_version(self):
        """Test setting the default version."""
        @self.vm.versioned("1.0.0", "2.0.0")
        def test_function():
            return "test"
        
        # Change default version
        self.vm.set_default_version("test_function", "2.0.0")
        default = self.vm.get_default_version("test_function")
        self.assertEqual(default, "2.0.0")
        
        # Test error for invalid version
        with self.assertRaises(ValueError):
            self.vm.set_default_version("test_function", "3.0.0")
        
        # Test error for non-existent function
        with self.assertRaises(ValueError):
            self.vm.set_default_version("nonexistent", "1.0.0")
    
    def test_global_version_manager(self):
        """Test that global version manager instance works."""
        @version_manager.versioned("1.0.0")
        def global_function():
            return "global test"
        
        result = version_manager.get_versioned_function("global_function", "1.0.0")
        self.assertEqual(result(), "global test")
    
    def test_function_metadata_preservation(self):
        """Test that function metadata is preserved after decoration."""
        @self.vm.versioned("1.0.0")
        def documented_function():
            """This is a test function."""
            return "test"
        
        # Check that wrapper preserves metadata
        func = self.vm.get_versioned_function("documented_function", "1.0.0")
        self.assertEqual(func.__name__, "documented_function")
        self.assertEqual(func.__doc__, "This is a test function.")


if __name__ == '__main__':
    unittest.main()