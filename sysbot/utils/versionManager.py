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

from functools import wraps
from typing import Dict, Any, Callable, List, Optional


class VersionManager:
    """
    Version manager for functions and Robot Framework keywords.
    
    This class provides versioning capabilities for functions and methods,
    making them compatible with Robot Framework while maintaining backward
    compatibility.
    """
    
    def __init__(self):
        self._function_versions: Dict[str, Dict[str, Callable]] = {}
        self._default_versions: Dict[str, str] = {}
        self._robot_keywords: Dict[str, Dict[str, Any]] = {}

    def versioned(self, *versions: str, default: Optional[str] = None):
        """
        Decorator to associate a function with multiple versions.
        
        Args:
            *versions: Version strings to associate with the function
            default: The default version to use if none specified
            
        Returns:
            Decorated function with version metadata
        """
        def decorator(func: Callable) -> Callable:
            name = func.__name__
            if name not in self._function_versions:
                self._function_versions[name] = {}

            # Register function for each version
            for version in versions:
                self._function_versions[name][version] = func
            
            # Set default version if specified
            if default and default in versions:
                self._default_versions[name] = default
            elif versions and not self._default_versions.get(name):
                # Use the first version as default if no default specified
                self._default_versions[name] = versions[0]
                
            # Store Robot Framework metadata
            if hasattr(func, 'robot_name'):
                self._robot_keywords[name] = {
                    'robot_name': func.robot_name,
                    'versions': list(versions),
                    'default': self._default_versions.get(name)
                }
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Add version metadata to wrapper
            wrapper._versions = versions
            wrapper._default_version = self._default_versions.get(name)
            
            return wrapper
        return decorator

    def get_versioned_function(self, name: str, version: Optional[str] = None) -> Callable:
        """
        Retrieve a function by name and version.
        
        Args:
            name: Function name
            version: Version to retrieve. If None, uses default version.
            
        Returns:
            The versioned function
            
        Raises:
            ValueError: If function or version not found
        """
        if name not in self._function_versions:
            raise ValueError(f"Function '{name}' not found")
            
        target_version = version or self._default_versions.get(name)
        
        if not target_version:
            available_versions = list(self._function_versions[name].keys())
            raise ValueError(f"No version specified and no default version set for '{name}'. Available versions: {available_versions}")
            
        if target_version not in self._function_versions[name]:
            available_versions = list(self._function_versions[name].keys())
            raise ValueError(f"Version '{target_version}' of '{name}' not found. Available versions: {available_versions}")
            
        return self._function_versions[name][target_version]

    def list_versions(self, name: str) -> List[str]:
        """
        List all available versions for a function.
        
        Args:
            name: Function name
            
        Returns:
            List of available versions
        """
        if name not in self._function_versions:
            return []
        return list(self._function_versions[name].keys())

    def list_functions(self) -> List[str]:
        """
        List all versioned functions.
        
        Returns:
            List of function names
        """
        return list(self._function_versions.keys())

    def get_default_version(self, name: str) -> Optional[str]:
        """
        Get the default version for a function.
        
        Args:
            name: Function name
            
        Returns:
            Default version string or None if not set
        """
        return self._default_versions.get(name)

    def set_default_version(self, name: str, version: str) -> None:
        """
        Set the default version for a function.
        
        Args:
            name: Function name
            version: Version to set as default
            
        Raises:
            ValueError: If function or version not found
        """
        if name not in self._function_versions:
            raise ValueError(f"Function '{name}' not found")
            
        if version not in self._function_versions[name]:
            available_versions = list(self._function_versions[name].keys())
            raise ValueError(f"Version '{version}' of '{name}' not found. Available versions: {available_versions}")
            
        self._default_versions[name] = version

    def get_robot_keywords(self) -> Dict[str, Dict[str, Any]]:
        """
        Get Robot Framework keyword metadata.
        
        Returns:
            Dictionary of keyword metadata
        """
        return self._robot_keywords.copy()


# Global version manager instance for easy access
version_manager = VersionManager()