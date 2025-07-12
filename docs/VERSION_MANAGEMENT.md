# SysBot Version Management

The SysBot version management system allows you to version your functions and Robot Framework keywords efficiently, ensuring backward compatibility while enabling feature evolution.

## Overview

The `VersionManager` class in `sysbot.utils.versionManager` provides a decorator-based system for versioning functions. This is particularly useful for:

- **Connector evolution**: Update connector methods while maintaining backward compatibility
- **Robot Framework keywords**: Version your keywords for different test requirements
- **API compatibility**: Maintain multiple versions of functions simultaneously
- **Gradual migration**: Allow users to migrate to newer versions at their own pace

## Basic Usage

### 1. Import the Version Manager

```python
from sysbot.utils.versionManager import version_manager
```

### 2. Version Your Functions

```python
@version_manager.versioned("1.0.0", default="1.0.0")
def connect_to_server(host, port):
    return f"Basic connection to {host}:{port}"

@version_manager.versioned("2.0.0")
def connect_to_server(host, port, timeout=30):
    return f"Connection to {host}:{port} with {timeout}s timeout"
```

### 3. Use Versioned Functions

```python
# Get specific version
func_v1 = version_manager.get_versioned_function("connect_to_server", "1.0.0")
result_v1 = func_v1("example.com", 80)

# Get default version (if no version specified)
func_default = version_manager.get_versioned_function("connect_to_server")
result_default = func_default("example.com", 80)
```

## Connector Integration

Connectors can inherit from `ConnectorInterface` which provides built-in version management support:

```python
from sysbot.utils.ConnectorInterface import ConnectorInterface
from sysbot.utils.versionManager import version_manager

class MyConnector(ConnectorInterface):
    def __init__(self):
        super().__init__()
        self.set_connector_version("2.0.0")
    
    @version_manager.versioned("1.0.0", default="1.0.0")
    def execute_command(self, command):
        return f"v1: {command}"
    
    @version_manager.versioned("2.0.0")
    def execute_command(self, command, timeout=30):
        return f"v2: {command} (timeout: {timeout}s)"
    
    def run_command(self, command, version=None):
        func = self.get_versioned_method("execute_command", version)
        return func(self, command)
```

## Robot Framework Compatibility

The version manager is fully compatible with Robot Framework:

```python
@version_manager.versioned("1.0.0", "2.0.0", default="2.0.0")
def send_http_request(url, method="GET"):
    """Robot Framework keyword for sending HTTP requests."""
    return f"HTTP {method} to {url}"

# In Robot Framework:
# *** Keywords ***
# Send Basic Request
#     ${result}=    Send HTTP Request    https://example.com
#     RETURN    ${result}
```

## Version Management API

### Decorator Options

```python
@version_manager.versioned("1.0.0", "1.1.0", "2.0.0", default="2.0.0")
def my_function():
    pass
```

- **Multiple versions**: List all versions this function supports
- **default**: Specify which version to use when none is specified

### Query Functions

```python
# List all versioned functions
functions = version_manager.list_functions()

# List versions for a specific function
versions = version_manager.list_versions("my_function")

# Get/set default version
default = version_manager.get_default_version("my_function")
version_manager.set_default_version("my_function", "2.0.0")
```

## Real-World Example

See `examples/version_management_example.py` for a complete demonstration of:

- Database connector with evolving features
- Robot Framework keywords with version support
- Practical usage patterns
- Migration strategies

## Best Practices

1. **Semantic Versioning**: Use semantic versioning (e.g., "1.0.0", "1.1.0", "2.0.0")
2. **Default Versions**: Always specify a default version for new functions
3. **Backward Compatibility**: Keep older versions available during transition periods
4. **Documentation**: Document what changed between versions
5. **Testing**: Test all supported versions to ensure they work correctly

## Migration Strategy

1. **Phase 1**: Add new version alongside existing version
2. **Phase 2**: Set new version as default
3. **Phase 3**: Deprecate old version (keep it functional)
4. **Phase 4**: Remove old version after migration period

## Error Handling

The version manager provides clear error messages:

```python
# Function not found
version_manager.get_versioned_function("nonexistent", "1.0.0")
# ValueError: Function 'nonexistent' not found

# Version not found
version_manager.get_versioned_function("my_function", "3.0.0")
# ValueError: Version '3.0.0' of 'my_function' not found. Available versions: ['1.0.0', '2.0.0']
```

This ensures that version-related issues are caught early and debugged easily.