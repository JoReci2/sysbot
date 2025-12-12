# SysBot

A system test tool that provides a unified interface for connecting to and test various systems through different protocols. Built with Robot Framework integration in mind.

## Features

- **Multi-protocol Support**: SSH, HTTP, WinRM, and more
- **SSH Tunneling**: Support for nested SSH tunnels with automatic management
- **Cross-platform**: Support for Linux and Windows systems
- **Robot Framework Integration**: Built-in support for Robot Framework automation with SUITE scope
- **Modular Architecture**: Dynamic components loading and discovery (module and plugins)
- **Connection Management**: Robust session caching and lifecycle management
- **Secret Management**: Secure storage and retrieval of sensitive data

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Install from PyPI

```bash
pip install sysbot
```

## Quick Start

### Basic SSH Connection

```python
from sysbot.Sysbot import Sysbot

# Create a SysBot instance
bot = Sysbot()

# Open an SSH session to a Linux system (port defaults to 22)
bot.open_session(
    alias="my_linux_server",
    protocol="ssh",
    product="bash",
    host="192.168.1.100",
    login="username",
    password="password"
)

# Execute a command
result = bot.execute_command("my_linux_server", "ls -la")
print(result)

# Get full structured response
full_response = bot.execute_command("my_linux_server", "uname -a", get_full_response=True)
print(f"Status: {full_response['StatusCode']}")
print(f"Result: {full_response['Result']}")
print(f"Metadata: {full_response['Metadata']}")

# Close all sessions
bot.close_all_sessions()
```

### Localhost Execution

```python
from sysbot.Sysbot import Sysbot

bot = Sysbot()

# Open a localhost session (no credentials needed)
bot.open_session(
    alias="local",
    protocol="localhost",
    product="bash",
    host="localhost"
)

# Execute commands on the local system
result = bot.execute_command("local", "echo Hello from localhost")
print(result)  # Output: Hello from localhost

bot.close_session("local")
```

### SSH Tunneling

```python
# Configure nested SSH tunnels
tunnel_config = [
    {
        "ip": "192.168.1.1",
        "port": 22,
        "username": "user1",
        "password": "pass1"
    },
    {
        "ip": "192.168.2.1", 
        "port": 22,
        "username": "user2",
        "password": "pass2"
    }
]

# Open session through tunnels (port defaults to 22)
bot.open_session(
    alias="tunneled_server",
    protocol="ssh", # or http / winrm / etc...
    product="bash",
    host="192.168.3.100",
    login="final_user",
    password="final_pass",
    tunnel_config=tunnel_config
)
```

### Using secret management and plugins

```python
from sysbot.Sysbot import Sysbot
bot = Sysbot()

# If secret is not used
my_import = bot.plugins.data.csv("/path/to/file")
my_import[0][name]

# With secret usage
bot.plugins.data.csv("/path/to/file", key="my_secret")
secret_data = bot.get_secret("my_secret.0.name")

# Secret management without plugin
bot.add_secret("new_secret", "very_secret_value")
bot.get_secret("new_secret")
bot.remove_secret("new_secret")
```

### Using with Robot Framework

```robot
*** Settings ***
Library        sysbot.Sysbot

*** Variables ***
${HOST}=       192.168.1.112
${PORT}=       22
${USER}=       sysbot
${PASSWORD}=   P@ssw0rd

*** Settings ***
Suite Setup       Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
Suite Teardown    Close All Sessions

*** Test Cases ***

Open Session without secret
    Open Session    target    ssh    bash    ${HOST}    ${PORT}   ${USER}    ${PASSWORD}
    Close All Sessions

Open Session with secret
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password   is_secret=True
    Close All Sessions
```

### Module System

```python
# Call functions from loaded modules
bot = Sysbot("linux.systemd", "linux.dnf") # bot = Sysbot() to load all modules

# Open an SSH session to a Linux system
bot.open_session(
    alias="my_linux_server",
    protocol="ssh",
    product="bash",
    host="192.168.1.100",
    port=22,
    login="username",
    password="password"
)

result = bot.linux.dnf.repolist("my_linux_server")
```

### Session Management

```python
# Close a specific session
bot.close_session("my_linux_server")

# Close all sessions (automatically handles tunnels)
bot.close_all_sessions()
```

## Supported Protocols

SysBot now uses a unified connector architecture with standardized response formats and default ports.

### SSH (Port 22)
- **Bash**: Generic SSH connector using Netmiko with automatic device type detection
  - Supports Linux, Unix, network devices, and other SSH-enabled systems
  - Automatic device type detection for optimized handling
- **Powershell**: PowerShell over SSH for Windows systems with SSH server enabled

### WinRM (Port 5986 - HTTPS)
- **Powershell**: Native Windows Remote Management support for Windows systems

### HTTP/HTTPS
- **HTTP (Port 80)** / **HTTPS (Port 443)**
  - **BasicAuth**: RESTful API connections with basic authentication
  - **vsphere**: VMware vSphere/ESXi connections (uses pyVmomi)

### Socket
- **TCP**: Raw TCP socket with optional SSL/TLS support (requires explicit port)
- **UDP**: Connectionless UDP socket communication (requires explicit port)

### Localhost
- **Bash**: Execute commands directly on the local system without network connection
  - Automatically detects OS (Windows/Linux) and uses appropriate shell
  - No credentials required

## Connector Features

### Default Ports
All connectors now support default ports - you can omit the port parameter and the connector will use the standard port for the protocol.

### Structured Response Format
All connectors now return a standardized response format:
```python
{
    "StatusCode": 0,           # 0 = success, non-zero = error
    "Result": "command output", # The actual result data
    "Error": None,             # Error message if any
    "Metadata": {              # Additional information
        "host": "hostname",
        "port": 22,
        # ... connector-specific metadata
    }
}
```

By default, `execute_command` returns just the `Result` field for backward compatibility. Use `get_full_response=True` to get the complete structured response.

## Architecture

```
sysbot/
├── Sysbot.py           # Main SysBot class
├── connectors/         # Protocol-specific connectors
│   ├── config.py       # Default ports and response format
│   ├── ssh/            # SSH connectors (Netmiko-based)
│   ├── winrm/          # WinRM connectors
│   ├── http/           # HTTP/HTTPS connectors
│   ├── socket/         # Socket connectors (TCP/UDP)
│   └── localhost/      # Local execution connector
├── plugins/            # Plugins utilities
├── utils/
│   └── engine.py       # Engine class
└── modules/            # Modules
```

## Error Handling

SysBot provides comprehensive error handling:

- **Connection Errors**: Detailed error messages for connection failures
- **Tunnel Management**: Automatic cleanup on tunnel failures
- **Session Validation**: Verification of session validity before operations
- **Module Errors**: Clear error messages for module and function calls

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Thibault SCIRE - [GitHub](https://github.com/thibaultscire)

## Acknowledgments

- [Robot Framework](https://robotframework.org/) for automation framework
- [Testinfra](https://testinfra.readthedocs.io/en/latest/) Discovered after development was well advanced but helped me to surpass myself