# Connector Refactoring - Implementation Summary

## Overview
This document summarizes the comprehensive refactoring of the SysBot connector system as requested in the issue "connector: refactoring".

## Requirements Met

### ✅ 1. Generic Connectors
- SSH connectors are now generic and work with switches, firewalls, Windows, Linux, etc.
- Implemented using Netmiko with automatic device type detection
- Single SSH connector handles all SSH-capable systems

### ✅ 2. Simplified API
- Connectors now use simple parameter structure: `connectors.ssh.bash`
- Consistent interface across all connector types
- Optional parameters with sensible defaults

### ✅ 3. Default Ports Defined
- SSH: 22
- WinRM: 5986 (HTTPS)
- HTTP: 80
- HTTPS: 443
- Socket: Explicit port required
- Port parameter is now optional

### ✅ 4. Structured Response Format
All connectors return:
```python
{
    "StatusCode": 0,        # 0 = success, non-zero = error
    "Result": "output",     # Command output/result
    "Error": None,          # Error message if any
    "Metadata": {           # Additional context
        "host": "hostname",
        "port": 22,
        # ... connector-specific info
    }
}
```

### ✅ 5. HTTP Connectors Use Only Requests
- Removed any non-requests HTTP dependencies
- All HTTP/HTTPS connectors now exclusively use the `requests` library
- Proper status code validation (2xx for success)

### ✅ 6. Netmiko for All SSH Connections
- SSH connectors migrated from raw Paramiko to Netmiko
- Automatic device type detection enabled
- Better compatibility with network devices, servers, and systems

### ✅ 7. Localhost Connector
- New connector for local command execution
- No credentials or network connection required
- Automatically detects OS (Windows/Linux)
- Falls back to localhost when no session is open

### ✅ 8. Five Main Connector Types
Reduced to the specified connector types:
1. **ssh** - Generic SSH using Netmiko (bash, powershell)
2. **winrm** - Windows Remote Management (powershell)
3. **http** - HTTP connections (basicauth, vsphere)
4. **https** - HTTPS connections (basicauth, vsphere)
5. **socket** - Raw sockets (tcp, udp)
6. **localhost** - Local execution (bonus addition)

## Implementation Details

### Backward Compatibility
- `Sysbot.execute_command()` maintains backward compatibility
- Returns just the Result field by default for existing modules
- Use `get_full_response=True` to access full structured response

### Error Handling
- SSH connectors implement heuristic error detection (Netmiko limitation)
- Checks output for common error indicators
- Metadata includes notes about error detection methods

### Security Enhancements
- TLS 1.2 minimum for SSL/TLS connections
- Security warnings added for credential handling
- Documentation about potential log exposure

### Testing
- 11 new unit tests covering core functionality
- All tests pass successfully
- Backward compatibility verified
- Zero security vulnerabilities (CodeQL verified)

## Files Modified

### Core Connector Files
- `sysbot/connectors/config.py` - New file for defaults and response format
- `sysbot/connectors/ssh/bash.py` - Refactored with Netmiko
- `sysbot/connectors/ssh/powershell.py` - Refactored with Netmiko
- `sysbot/connectors/winrm/powershell.py` - Updated with structured responses
- `sysbot/connectors/http/basicauth.py` - Standardized on requests
- `sysbot/connectors/http/vsphere.py` - Updated response format
- `sysbot/connectors/socket/tcp.py` - Structured responses
- `sysbot/connectors/socket/udp.py` - Structured responses
- `sysbot/connectors/localhost/bash.py` - New connector

### Supporting Files
- `sysbot/Sysbot.py` - Updated for new response format and optional ports
- `README.md` - Comprehensive documentation updates
- `tests/test_connectors.py` - New unit tests

## Usage Examples

### SSH with Default Port
```python
from sysbot.Sysbot import Sysbot

bot = Sysbot()
bot.open_session(
    alias="server",
    protocol="ssh",
    product="bash",
    host="192.168.1.100",  # port defaults to 22
    login="user",
    password="pass"
)
```

### Localhost Execution
```python
bot.open_session(
    alias="local",
    protocol="localhost",
    product="bash",
    host="localhost"  # No credentials needed
)
result = bot.execute_command("local", "echo Hello")
```

### Full Response Access
```python
response = bot.execute_command(
    "server", 
    "ls -la", 
    get_full_response=True
)
print(f"Status: {response['StatusCode']}")
print(f"Result: {response['Result']}")
print(f"Metadata: {response['Metadata']}")
```

## Migration Guide for Users

### Port Parameter Now Optional
**Before:**
```python
bot.open_session("alias", "ssh", "bash", "host", 22, "user", "pass")
```

**After:**
```python
bot.open_session("alias", "ssh", "bash", "host", login="user", password="pass")
# Or still with explicit port:
bot.open_session("alias", "ssh", "bash", "host", 22, "user", "pass")
```

### Accessing Full Response
**Before:**
```python
result = bot.execute_command("alias", "command")
# result is just a string
```

**After:**
```python
# Still works the same for backward compatibility:
result = bot.execute_command("alias", "command")

# But can also get full response:
response = bot.execute_command("alias", "command", get_full_response=True)
status = response["StatusCode"]
result = response["Result"]
error = response["Error"]
metadata = response["Metadata"]
```

## Testing Results

All unit tests pass:
- ✅ Config and response format tests
- ✅ Localhost connector tests
- ✅ Sysbot integration tests
- ✅ Backward compatibility tests
- ✅ Default port handling tests

Code quality:
- ✅ No CodeQL security alerts
- ✅ Code review feedback addressed
- ✅ Security warnings documented
- ✅ Error handling improved

## Benefits

1. **Consistency**: All connectors now have the same response format
2. **Observability**: Structured responses with metadata for debugging
3. **Simplicity**: Default ports reduce boilerplate code
4. **Compatibility**: Netmiko provides better device support
5. **Flexibility**: Full response available when needed
6. **Security**: Security considerations documented
7. **Testing**: Local testing without network infrastructure

## Conclusion

The connector refactoring successfully meets all requirements from the issue while maintaining backward compatibility with existing code. The implementation provides a more robust, consistent, and user-friendly API for all connector types.
