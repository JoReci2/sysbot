# GitHub Copilot Instructions for SysBot

## Project Overview

SysBot is a system test automation tool that provides a unified interface for connecting to and testing various systems through different protocols. It is built with Robot Framework integration in mind and supports SSH, HTTP, WinRM, and Socket protocols.

## Architecture

```
sysbot/
├── Sysbot.py           # Main SysBot class with ROBOT_LIBRARY_SCOPE = "SUITE"
├── connectors/         # Protocol-specific connectors (SSH, WinRM, HTTP, Socket)
├── plugins/            # Plugin utilities for data import and processing
├── utils/              # Utility classes and engine components
│   ├── engine.py       # ComponentMeta, ComponentLoader, Cache, TunnelingManager
│   └── helper.py       # Windows, Timezone, Security utility classes
└── modules/            # System-specific modules (Linux, Windows)
    ├── linux/          # Linux system modules
    └── windows/        # Windows system modules (ADDS, ADCS, DNS, WSUS, Veeam, etc.)
```

## Code Style and Conventions

### General Python Style
- Follow PEP 8 style guide
- Use `ruff` for automatic formatting and linting
- Use `bandit` for security checks
- Use `radon` for code complexity analysis
- Use `safety` for dependency vulnerability checks

### Naming Conventions
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Modules: `lowercase`

### Documentation
- Document all public functions with Google-style docstrings
- Include Args, Returns, and Raises sections in docstrings
- Include usage examples when appropriate

Example:
```python
def example_function(param1: str, param2: int) -> bool:
    """Example function with docstring.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this exception is raised
    """
```

## Module and Plugin Patterns

### Module Structure
- All modules extend `ComponentBase` from `sysbot.utils.engine`
- Use `self.execute_command(alias, command, **kwargs)` to run commands
- Windows modules use PowerShell cmdlets with `ConvertTo-Json` for structured output

Example:
```python
from sysbot.utils.engine import ComponentBase
import json

class MyModule(ComponentBase):
    def get_data(self, alias: str, **kwargs) -> dict:
        """Get data from the system."""
        command = "Get-Something | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
```

### Plugin Structure
- Plugins extend `ComponentBase` and follow the data plugin pattern
- Optional `key` parameter stores results in secret manager, returning "Imported"
- Without `key`, returns data directly

### Windows PowerShell Modules
- Use PowerShell cmdlets with `ConvertTo-Json` for structured output
- PowerShell commands are base64 encoded before transmission via WinRM, so manual quote escaping is NOT necessary
- For methods returning single objects, return as dict
- For methods returning lists:
  - Check for empty output and return `[]` to prevent JSONDecodeError
  - Wrap single objects in a list since ConvertTo-Json returns single objects (not arrays) for one result

Example:
```python
def get_items(self, alias: str, filter: str = "*", **kwargs) -> list:
    """Get items matching filter."""
    command = f"Get-ADItem -Filter '{filter}' | ConvertTo-Json"
    output = self.execute_command(alias, command, **kwargs)
    if not output or output.strip() == "":
        return []
    result = json.loads(output)
    # Wrap single objects in a list
    if isinstance(result, dict):
        return [result]
    return result
```

## Error Handling

### Exception Chaining
- Always use exception chaining with `raise Exception(...) from e` to preserve original tracebacks
- Check for empty output before JSON parsing to prevent JSONDecodeError

Example:
```python
try:
    # Some operation
    pass
except Exception as e:
    raise Exception(f"Failed to perform operation: {str(e)}") from e
```

### Empty Output Handling
- Methods returning dicts: Check for empty output and return `{}`
- Methods returning lists: Check for empty output and return `[]`

## Security Best Practices

### SSL/TLS Configuration
- SSL/TLS connections must use minimum version TLS 1.2
- Set `context.minimum_version = ssl.TLSVersion.TLSv1_2`

### Input Validation
- PowerShell commands are base64 encoded before transmission, so manual quote escaping is not necessary
- However, always validate and sanitize user inputs
- Use html_escape as a sanitizer to avoid cross-site scripting vulnerabilities when applicable

### Secrets Management
- Use the built-in secret manager for sensitive data
- Never commit secrets into source code
- Access secrets via `self._cache.secrets.get(key)`

## Testing

### Test Framework
- Use Robot Framework for integration tests
- Place tests in the `tests/` directory
- Maintain test coverage >80%

### Robot Framework Test Structure
- Robot Framework test files should have a single Settings section
- Include Name, Library, Suite Setup, and Suite Teardown declarations
- Use `SUITE` scope for Sysbot library

Example:
```robot
*** Settings ***
Name           Test Name
Library        sysbot.Sysbot
Suite Setup    Setup Keywords
Suite Teardown Close All Sessions

*** Variables ***
${HOST}        192.168.1.100
${PORT}        22

*** Test Cases ***
Test Case Name
    Open Session    alias    ssh    bash    ${HOST}    ${PORT}    user    pass
    ${result}=      Execute Command    alias    ls -la
    Should Contain  ${result}    total
```

### Windows Module Testing
- Windows module Robot Framework tests use winrm connector on port 5986 with powershell shell type
- Follow the same structure as ADDS tests with Settings, Variables, Keywords, and Test Cases sections

## Connection Management

### Session Lifecycle
- Use `open_session()` to establish connections
- Use `close_session(alias)` to close specific sessions
- Use `close_all_sessions()` to clean up all sessions (automatically handles tunnels)
- Sessions are cached with the alias as the key

### SSH Tunneling
- Support for nested SSH tunnels with automatic management
- Tunnels are automatically cleaned up when sessions are closed

## Build and Development

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install development dependencies
pip install build ruff bandit radon safety

# Install package in development mode
pip install -e .
```

### Running Tests
```bash
# Run all tests
robot -d tests/

# Run specific test
robot -d tests/test_specific.robot
```

### Code Quality Checks
```bash
# Run linting
ruff check .

# Run security checks
bandit -r sysbot/

# Check code complexity
radon cc sysbot/ -a

# Check dependency vulnerabilities
safety check
```

## Commit Convention

Use Conventional Commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Formatting, missing semicolons, etc.
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance

## License

This project is licensed under the MIT License. All contributions must comply with the MIT License terms.
