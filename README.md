# SysBot

A system automation and management tool that provides a unified interface for connecting to and managing various systems through different protocols. Built with Robot Framework integration in mind.

## Features

- **Multi-protocol Support**: SSH, HTTP, WinRM, and more
- **SSH Tunneling**: Support for nested SSH tunnels with automatic management
- **File Operations**: Execute scripts and retrieve results remotely
- **Cross-platform**: Support for Linux and Windows systems
- **Robot Framework Integration**: Built-in support for Robot Framework automation with SUITE scope
- **Type Safety**: Full type hints and static analysis support
- **Modular Architecture**: Dynamic module loading and discovery
- **Data Loaders**: Extensible data import system
- **Connection Management**: Robust session caching and lifecycle management

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Install from PyPI

```bash
pip install sysbot
```

### Install from source

```bash
git clone https://github.com/thibaultscire/sysbot.git
cd sysbot
pip install -e .
```

### Development installation

```bash
git clone https://github.com/thibaultscire/sysbot.git
cd sysbot
pip install -e ".[dev]"
```

Regulary use tools to ensure the code is clean:
```bash
# Check and format the code
ruff check sysbot
ruff format sysbot
# Analyze complexity et mantenability (A=Good,B=Middle,C=Bad)
radon cc sysbot
radon mi sysbot
# Security analisys
bandit -r sysbot
safety scan
```

## Quick Start

### Basic SSH Connection

```python
from sysbot import Sysbot

# Create a SysBot instance
bot = Sysbot()

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

# Execute a command
result = bot.execute_command("my_linux_server", "ls -la")
print(result)

# Close all sessions
bot.close_all_sessions()
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

# Open session through tunnels
bot.open_session(
    alias="tunneled_server",
    protocol="ssh",
    product="bash",
    host="192.168.3.100",
    port=22,
    login="final_user",
    password="final_pass",
    tunnel_config=tunnel_config
)
```

### Using with Robot Framework

```robot
*** Settings ***
Library        sysbot.Sysbot

Suite Teardown    Close All Sessions
Suite Setup       Open Session    target    ssh    bash    ${IP}    ${PORT}   ${USER}    ${PASSWORD}

*** Test Cases ***

repolist method works
    ${output}=    Call Module    linux.dnf.repolist    target
    Should Not Be Empty    ${output}[0][name]
```

### Module System

```python
# Call functions from loaded modules
bot = Sysbot("linux.systemd", "linux.dnf") #bot = Sysbot() to load all modules
result = bot.linux.dnf.repolist("tunneled_server")

# Import data using data loaders
data = bot.import_data_from("csv", file_path="/path/to/data.csv")
```

### Session Management

```python
# Close a specific session
bot.close_session("my_linux_server")

# Close all sessions (automatically handles tunnels)
bot.close_all_sessions()
```

## Supported Protocols

### SSH
- **Bash**: Full support for bash via SSH
- **Powershell**: Support for powershell via SSH (requires SSH server)

### HTTP
- **BasicAuth**: Support for API connections
- **vsphere**: Support for ESXi and vCenter

### WinRM
- **Powershell**: Native Windows Remote Management support

### Socket
- **TCP**: Native TCP socket with ssl if needed
- **UDP**: Native UDP socket

## Architecture

```
sysbot/
├── Sysbot.py           # Main SysBot class
├── connectors/         # Protocol-specific connectors
├── dataloaders/        # Data loading utilities
├── utils/
│   └── engine.py       # Engine class
└── modules/            # Protocol-specific modules
```

## Key Components

### Connection Management
- **Connection Cache**: Centralized session management using Robot Framework's ConnectionCache
- **Automatic Cleanup**: Proper cleanup of sessions and tunnels on close
- **Alias Support**: Named connections for easy reference

### Tunneling System
- **Nested Tunnels**: Support for multiple SSH hops
- **Automatic Management**: Tunnels are automatically created and destroyed
- **JSON Configuration**: Support for tunnel configuration via JSON strings

### Module System
- **Dynamic Loading**: Modules are automatically discovered and loaded
- **Modular Functions**: Call specific functions using dot notation
- **Extensible**: Easy to add new protocol or module support

### Data Loaders
- **Pluggable System**: Support for different data sources
- **Module-based**: Each loader is a separate module
- **Flexible Input**: Support for various data formats

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

- [Paramiko](https://www.paramiko.org/) for SSH functionality
- [Robot Framework](https://robotframework.org/) for automation framework
- [SSHTunnel](https://github.com/pahaz/sshtunnel) for SSH tunneling support