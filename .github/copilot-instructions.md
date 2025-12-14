# GitHub Copilot Instructions for SysBot

## Project Overview

SysBot is a system test automation library designed for testing infrastructure through multiple protocols (SSH, WinRM, HTTP, Socket). It provides a unified interface for Robot Framework test automation.

## Code Style and Standards

### General Guidelines

- Follow PEP 8 Python style guidelines
- Use type hints where applicable (Python 3.7+)
- Keep line length to 120 characters maximum
- Use meaningful variable and function names
- Add docstrings to all public classes and methods

### Naming Conventions

- **Classes**: PascalCase (e.g., `Sysbot`, `ComponentBase`)
- **Functions/Methods**: snake_case (e.g., `open_session`, `execute_command`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_PORT`, `SSH_PORT`)
- **Private methods**: Prefix with underscore (e.g., `_internal_method`)

### Import Organization

1. Standard library imports
2. Third-party imports
3. Local application imports

Use absolute imports from the `sysbot` package root.

## Architecture Patterns

### Connector Pattern

All connectors must:
- Inherit from appropriate base classes
- Return standardized dictionary responses with: `StatusCode`, `Result`, `Error`, `Metadata`
- Handle connection lifecycle (open, execute, close)
- Support optional `port` parameter with defaults from `config.py`

Example connector response:
```python
{
    "StatusCode": 0,
    "Result": "command output",
    "Error": "",
    "Metadata": {}
}
```

### Module Pattern

Modules extend `ComponentBase` and:
- Are organized by OS type: `linux/`, `windows/`
- Provide system-specific functionality
- Use the connector layer for command execution
- Return structured data (preferably dictionaries or lists)

### Plugin Pattern

Plugins follow the data plugin pattern:
- Optional `key` parameter stores results in secret manager
- When `key` is provided, return `"Imported"`
- When `key` is not provided, return data directly
- Extend `ComponentBase`

## Security Best Practices

### SSL/TLS Configuration

Always set minimum TLS version to 1.2:
```python
context.minimum_version = ssl.TLSVersion.TLSv1_2
```

### Input Sanitization

- For PowerShell commands: Escape single quotes by replacing `'` with `''`
- For shell commands: Use parameterized commands when possible
- Validate user inputs before using in system commands

### Secret Management

- Never hardcode credentials
- Use the built-in secret manager for sensitive data
- Support secret references in method parameters with `is_secret` flag

## Error Handling

### Exception Chaining

Use exception chaining to preserve original tracebacks:
```python
try:
    # operation
except Exception as e:
    raise Exception("Context about what failed") from e
```

### Empty Response Handling

Check for empty outputs before JSON parsing:
```python
if not output:
    return {}
return json.loads(output)
```

## Testing

### Robot Framework Tests

- Use `.robot` extension
- Follow structure: Settings, Variables, Keywords, Test Cases
- Use SUITE scope for Sysbot library
- Include `Suite Setup` and `Suite Teardown`

Example structure:
```robot
*** Settings ***
Library        sysbot.Sysbot

*** Variables ***
${HOST}=       192.168.1.100

*** Test Cases ***
Test Case Name
    [Documentation]    Description
    Open Session    alias    protocol    product    ${HOST}    port    login    password
    ${result}=    Execute Command    alias    command
    Should Be Equal    ${result["StatusCode"]}    ${0}
```

### Unit Tests

- Use pytest for Python unit tests
- Mock external connections
- Test error conditions and edge cases

## Documentation

### Docstring Format

Use Google-style docstrings:
```python
def method_name(param1, param2):
    """Short description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
    """
```

### AsciiDoc Documentation

- Documentation files are in `/docs` directory
- Use AsciiDoc format (.adoc)
- Include code examples
- Follow existing structure: index, setup, quickstart, references

## Development Workflow

### Code Quality Checks

Run before committing:
```bash
# Lint with ruff
ruff check sysbot

# Pre-commit hooks
pre-commit run --all-files

# Security scan
bandit -r sysbot

# Complexity analysis
radon cc sysbot -a
```

### Testing

```bash
# Run Robot Framework tests
tox -e robot

# Run specific test
robot tests/path/to/test.robot
```

### Building

```bash
# Build package
python -m build

# Install in development mode
pip install -e .
```

## Common Patterns

### Opening a Session

```python
bot.open_session(
    alias="unique_name",
    protocol="ssh",  # ssh, winrm, http, socket
    product="bash",  # bash, powershell, basicauth, tcp, udp
    host="hostname",
    port=22,  # Optional, uses defaults
    login="username",
    password="password",
    tunnel_config=[]  # Optional SSH tunnels
)
```

### Using Modules

```python
# Load specific modules
bot = Sysbot("linux.systemd", "windows.adcs")

# Use module methods
result = bot.linux.systemd.list_units("session_alias")
```

### Secret Management

```python
# Add secret
bot.add_secret("key", "value")

# Get secret with dot notation
value = bot.get_secret("key.nested.path")

# Use plugin with key storage
bot.plugins.data.yaml("file.yml", key="data")
bot.get_secret("data.field")
```

## Specific Technologies

### SSH Connections

- Use Netmiko library for SSH
- Automatic device type detection
- Support for tunneling through jump hosts

### WinRM Connections

- PowerShell commands are base64 encoded
- No need for manual quote escaping
- Use `ConvertTo-Json` for structured output

### Windows PowerShell Modules

When creating Windows modules:
- Import required PowerShell modules at method level
- Use `ConvertTo-Json -Depth 10` for complex objects
- Handle empty results gracefully
- Escape user inputs in cmdlet parameters

### Linux Bash Modules

When creating Linux modules:
- Use appropriate command-line tools
- Parse output into structured data
- Handle different distributions if applicable

## Contribution Guidelines

1. Create feature branches from `main`
2. Write tests for new functionality
3. Update documentation
4. Run all quality checks (tox)
5. Submit pull request with clear description
6. Reference related issues

## Performance Considerations

- Reuse sessions when possible (caching built-in)
- Close sessions when done
- Use `close_all_sessions()` in cleanup
- Be mindful of network latency in loops

## Common Pitfalls to Avoid

- Don't hardcode IP addresses or credentials in tests
- Don't skip error handling
- Don't forget to close sessions
- Don't commit test data or secrets
- Don't use shell=True without input validation
- Don't disable SSL verification in production code

## Resources

- Robot Framework: https://robotframework.org/
- Netmiko Documentation: https://github.com/ktbyers/netmiko
- PyWinRM Documentation: https://github.com/diyan/pywinrm
