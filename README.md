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
    protocol="ssh", # or http / winrm / ect...
    product="bash",
    host="192.168.3.100",
    port=22,
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

# Using Vault plugin to dump HashiCorp Vault secrets
bot.plugins.vault.dump_engine(
    token="hvs.CAESIJ...",
    url="https://vault.example.com:8200",
    engine_name="secret",
    key="vault_secrets",
    verify_ssl=False  # Set to True for production with valid certificates
)
# Access Vault secrets using dot notation
db_url = bot.get_secret("vault_secrets.myapp/config.database_url")
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

## Contributing

Contributions are welcome! Please see [DEVELOPMENT.md](DEVELOPMENT.md) for development setup, code quality tools, and guidelines.

### Development Tools

This project uses:
- **Tox** for automated testing and quality checks
- **Ruff** for fast Python linting
- **Radon** for code complexity analysis
- **Bandit** for security vulnerability scanning
- **Pre-commit hooks** for automated code quality checks

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed instructions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Thibault SCIRE - [GitHub](https://github.com/thibaultscire)

## Acknowledgments

- [Robot Framework](https://robotframework.org/) for automation framework
- [Testinfra](https://testinfra.readthedocs.io/en/latest/) Discovered after development was well advanced but helped me to surpass myself