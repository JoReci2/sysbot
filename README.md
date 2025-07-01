# SysBot

A system automation and management tool that provides a unified interface for connecting to and managing various systems through different protocols.

## Features

- **Multi-protocol Support**: SSH, HTTP, WinRM, and more
- **SSH Tunneling**: Support for nested SSH tunnels
- **File Operations**: Execute scripts and retrieve results remotely
- **Cross-platform**: Support for Linux and Windows systems
- **Robot Framework Integration**: Built-in support for Robot Framework automation
- **Type Safety**: Full type hints and static analysis support

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

## Quick Start

### Basic SSH Connection

```python
from sysbot.connectors import ConnectorHandler

# Create a connector handler
handler = ConnectorHandler()

# Open an SSH session to a Linux system
handler.open_session(
    alias="my_linux_server",
    protocol="ssh",
    product="linux",
    host="192.168.1.100",
    port=22,
    login="username",
    password="password"
)

# Execute a command
result = handler.execute_command("my_linux_server", "ls -la")
print(result)

# Close all sessions
handler.close_all_sessions()
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
handler.open_session(
    alias="tunneled_server",
    protocol="ssh",
    product="linux",
    host="192.168.3.100",
    port=22,
    login="final_user",
    password="final_pass",
    tunnel_config=tunnel_config
)
```

### File Execution

```python
# Execute a script file on Linux
script_content = """
#!/bin/bash
echo "Hello from remote system"
date
whoami
"""

result = handler.execute_file("my_linux_server", script_content)
print(result)
```

## Supported Protocols

### SSH
- **Linux**: Full support for Linux systems via SSH
- **Windows**: Support for Windows systems via SSH (requires SSH server)

### HTTP
- **Redfish**: Support for Redfish API connections

### WinRM
- **Windows**: Native Windows Remote Management support

## Architecture

```
sysbot/
├── connectors/          # Protocol-specific connectors
│   ├── ConnectorHandler.py  # Main handler class
│   ├── ssh/            # SSH protocol implementations
│   │   ├── linux.py    # Linux SSH connector
│   │   ├── windows.py  # Windows SSH connector
│   │   └── utils/      # SSH utilities
│   ├── http/           # HTTP protocol implementations
│   └── winrm/          # WinRM protocol implementations
├── dataloaders/        # Data loading utilities
└── utils/              # General utilities
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black sysbot/
```

### Type Checking

```bash
mypy sysbot/
```

### Linting

```bash
flake8 sysbot/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Thibault SCIRE - [GitHub](https://github.com/thibaultscire)

## Acknowledgments

- [Paramiko](https://www.paramiko.org/) for SSH functionality
- [Robot Framework](https://robotframework.org/) for automation framework
- [SSHTunnel](https://github.com/pahaz/sshtunnel) for SSH tunneling support 