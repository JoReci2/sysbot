# Connector Refactoring - December 2024

## Overview

This document describes the refactoring of the SysBot connector architecture to improve maintainability, consistency, and usability.

## Changes Made

### 1. Consolidated Connector Structure

**Before:**
```
sysbot/connectors/
├── ssh/
│   ├── __init__.py
│   ├── bash.py
│   └── powershell.py
├── winrm/
│   ├── __init__.py
│   └── powershell.py
├── socket/
│   ├── __init__.py
│   ├── tcp.py
│   └── udp.py
└── http/
    ├── __init__.py
    ├── basicauth.py
    └── vsphere.py
```

**After:**
```
sysbot/connectors/
├── ssh.py          # Contains Bash and Powershell classes
├── winrm.py        # Contains Powershell class
├── socket.py       # Contains Tcp and Udp classes
├── http.py         # Contains Basicauth and Vsphere classes
└── localhost.py    # NEW: Contains Bash and Powershell classes (local execution)
```

### 2. Standardized Response Format

All connectors now return a standardized dictionary response:

```python
{
    "StatusCode": 0,           # 0 for success, non-zero for errors
    "Result": <actual_result>, # The actual result data
    "Error": None,             # Error message if StatusCode != 0
    "Metadata": {              # Additional context information
        "host": "example.com",
        "port": 22,
        "protocol": "ssh",
        "shell": "bash"
    }
}
```

**Example Usage:**

```python
from sysbot.Sysbot import Sysbot

bot = Sysbot()

# Open session returns standardized response
response = bot.open_session(
    alias="server1",
    protocol="ssh",
    product="bash",
    host="192.168.1.100",
    port=22,
    login="user",
    password="pass"
)

# Execute command - returns just the result for backward compatibility
result = bot.execute_command("server1", "ls -la")
print(result)  # Direct command output

# For error handling, connectors return full response dict
# The Sysbot class handles this transparently
```

### 3. Default Ports

Connectors now define default ports that are used when port is not specified:

| Connector | Default Port |
|-----------|-------------|
| SSH       | 22          |
| WinRM     | 5986        |
| HTTP      | 443         |
| Socket    | None (required) |
| Localhost | None (not applicable) |

**Example:**

```python
# Port parameter is now optional for connectors with defaults
bot.open_session(
    alias="server1",
    protocol="ssh",
    product="bash",
    host="192.168.1.100",
    port=None,  # Will use default port 22
    login="user",
    password="pass"
)
```

### 4. New Localhost Connector

A new `localhost` connector has been added for executing commands locally without network connections:

```python
# Execute commands on localhost
bot.open_session(
    alias="local",
    protocol="localhost",
    product="bash",  # or "powershell"
    host=None,
    port=None,
    login=None,
    password=None
)

result = bot.execute_command("local", "echo 'Hello from localhost'")
print(result)  # Hello from localhost
```

### 5. Backward Compatibility

The refactoring maintains backward compatibility:

- Existing code continues to work without modifications
- The `TunnelingManager.get_protocol()` method tries the new structure first, then falls back to old structure
- The `Sysbot` class handles both old (direct object) and new (dict) response formats
- API signatures remain unchanged

## Benefits

1. **Simpler Structure**: One file per protocol instead of multiple subdirectories
2. **Consistent Responses**: All connectors return standardized response format with StatusCode, Result, Error, and Metadata
3. **Better Error Handling**: Errors are now returned in a structured format rather than exceptions only
4. **Default Ports**: Less repetitive code when using standard ports
5. **Local Execution**: New localhost connector for testing and local automation
6. **Easier Maintenance**: Less code duplication across connector files

## Migration Guide

### No Changes Required

If you're using the high-level `Sysbot` API, no changes are required. Your existing code will continue to work.

### For Direct Connector Usage

If you're directly instantiating connectors (advanced usage), you should update your code to handle the new response format:

**Before:**
```python
from sysbot.connectors.ssh.bash import Bash

connector = Bash()
session = connector.open_session("192.168.1.100", 22, "user", "pass")
result = connector.execute_command(session, "ls -la")
```

**After:**
```python
from sysbot.connectors.ssh import Bash

connector = Bash()
response = connector.open_session("192.168.1.100", 22, "user", "pass")

if response["StatusCode"] == 0:
    session = response["Result"]
    cmd_response = connector.execute_command(session, "ls -la")
    if cmd_response["StatusCode"] == 0:
        result = cmd_response["Result"]
        print(result)
    else:
        print(f"Command failed: {cmd_response['Error']}")
else:
    print(f"Session failed: {response['Error']}")
```

## Testing

All connectors have been tested with a custom test script that verifies:
- Connector loading from the new structure
- Default port configuration
- Standardized response format
- Backward compatibility

## Future Improvements

Potential future enhancements:
- Additional connectors (e.g., SNMP, Telnet)
- Enhanced metadata in responses
- Connection pooling and reuse
- Async/await support for connectors
