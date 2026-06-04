# SysBot

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [RobotFramework Usage](#robotframework-usage)
- [UnitTest Usage](#unittest-usage)
- [Additional Resources](#additional-resources)
- [License](#license)
- [Author](#author)

## Overview

SysBot is a system test tool that provides a unified interface for connecting to and testing various systems through different protocols. Built with Robot Framework integration in mind, it offers a modular architecture that simplifies system automation and testing.

### Key Features

- **Multi-protocol Support**: SSH, HTTP, WinRM, Socket, and more
- **SSH Tunneling**: Support for nested SSH tunnels with automatic management
- **Cross-platform**: Support for Linux and Windows systems
- **Robot Framework Integration**: Built-in support for Robot Framework automation with GLOBAL scope
- **Modular Architecture**: Dynamic components loading and discovery (modules and plugins)
- **Connection Management**: Robust session caching and lifecycle management
- **Secret Management**: Secure storage and retrieval of sensitive data

### Architecture

```
sysbot/
├── Sysbot.py           # Main SysBot class
├── connectors/         # Protocol-specific connectors
├── plugins/            # Plugins utilities (data, vault)
├── utils/
│   └── engine.py       # Engine class
└── modules/            # Modules
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Install from PyPI

```bash
pip install sysbot
```

### Install with development dependency

```bash
pip install sysbot[dev]
```

## Quickstart

### Basic SSH Connection

```python
import sysbot

bot = sysbot.Sysbot()

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

### Secret Management

SysBot provides a built-in secret management system for secure storage and retrieval of sensitive data like passwords, tokens, and configuration values. Secrets can be stored directly or loaded from external sources like files or HashiCorp Vault.

```python
import sysbot

bot = sysbot.Sysbot()

# Using plugins with secret management
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

### Module System

```python
# Import sysbot to access loaded components (all modules/plugins loaded by default)
import sysbot

bot = sysbot.Sysbot()

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

### Supported Protocols

#### SSH
- **Bash**: Full support for bash via SSH
- **Powershell**: Support for powershell via SSH (requires SSH server)

#### Local Execution
- **Bash**: Execute bash/shell commands locally without SSH
- **Powershell**: Execute PowerShell commands locally without SSH or WinRM

SysBot provides local execution connectors that allow running commands directly on the local machine without the overhead of SSH or WinRM connections. This is useful for:
- Running commands on the local system during automation
- Testing without remote systems
- Avoiding connection overhead for local operations

#### HTTP/HTTPS

SysBot provides a generic HTTP/HTTPS connector with support for 10 authentication methods.

**Supported Authentication Methods:**
1. **API Key (`apikey`)** - API Key authentication via headers or query parameters
2. **Basic Auth (`basicauth`)** - Standard HTTP Basic Authentication
3. **Redfish (`redfish`)** - Redfish Session Service token authentication
4. **OAuth 1.0 (`oauth1`)** - OAuth 1.0 authentication (RFC 5849)
5. **OAuth 2.0 (`oauth2`)** - OAuth 2.0 Bearer authentication
6. **JWT (`jwt`)** - JSON Web Token authentication with automatic token generation
7. **SAML (`saml`)** - SAML assertion/token authentication
8. **HMAC (`hmac`)** - HMAC signature-based authentication
9. **Certificate (`certificate`)** - Client certificate authentication (mutual TLS)
10. **OpenID Connect (`openidconnect`)** - OpenID Connect authentication

#### WinRM
- **Powershell**: Native Windows Remote Management support

#### Socket
- **TCP**: Native TCP socket with SSL if needed
- **UDP**: Native UDP socket

## RobotFramework Usage

SysBot is designed to work seamlessly with Robot Framework, providing powerful automation capabilities with a simple syntax.

### Basic Robot Framework Test

```robot
*** Settings ***
Library        sysbot.Sysbot
Suite Setup       Call Components    plugins.data.yaml    /path/to/connexion.yml    key=connexion
Suite Teardown    Close All Sessions

*** Variables ***
${HOST}=       192.168.1.112
${PORT}=       22
${USER}=       sysbot
${PASSWORD}=   P@ssw0rd

*** Test Cases ***

Open Session without secret
    Open Session    target    ssh    bash    ${HOST}    ${PORT}   ${USER}    ${PASSWORD}
    Close All Sessions

Open Session with secret
    Open Session    target    ssh    bash    connexion.host    connexion.port   connexion.username    connexion.password   is_secret=True
    Close All Sessions
```

### Using Modules in Robot Framework

Modules can be loaded and used to perform specific operations on target systems:

```robot
*** Settings ***
Library        sysbot.Sysbot    linux.systemd    linux.dnf

*** Test Cases ***

Check System Service
    Open Session    server1    ssh    bash    ${HOST}    ${PORT}    ${USER}    ${PASSWORD}
    ${status}=    Linux Dnf Repolist    server1
    Log    ${status}
    Close All Sessions
```

### Secret Management in Robot Framework

```robot
*** Settings ***
Library        sysbot.Sysbot

*** Test Cases ***

Using Secrets
    Add Secret    db_password    MySecretPassword
    ${password}=    Get Secret    db_password
    Log    Using password: ${password}
    Remove Secret    db_password
```

## UnitTest Usage

SysBot can be used in Python unittest for system testing scenarios.

### Module Testing with UnitTest

```python
import unittest
import Sysbot

class TestLinuxModules(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up class fixtures."""
        cls.bot = sysbot.Sysbot("linux.systemd", "linux.dnf")
        cls.bot.open_session(
            alias="linux_server",
            protocol="ssh",
            product="bash",
            host="192.168.1.100",
            port=22,
            login="user",
            password="pass"
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class fixtures."""
        cls.bot.close_all_sessions()
    
    def test_systemd_service_status(self):
        """Test checking systemd service status."""
        result = self.bot.linux.systemd.status("linux_server", "sshd")
        self.assertIsNotNone(result)
    
    def test_dnf_repolist(self):
        """Test listing DNF repositories."""
        result = self.bot.linux.dnf.repolist("linux_server")
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
```

## Additional Resources

### Documentation

SysBot includes comprehensive Google-style docstrings for all modules, classes, and methods.

#### Online Documentation

The complete documentation is available online at **[https://joreci2.github.io/sysbot/](https://joreci2.github.io/sysbot/)**

#### Viewing Documentation Locally with pdoc3

Install pdoc3 as a development dependency:

```bash
pip install pdoc3
```

Generate and serve interactive HTML documentation:

```bash
# Start a local documentation server (recommended)
pdoc3 --http localhost:8080 sysbot

# Or generate static HTML files
pdoc3 --html --output-dir docs sysbot
```

Then open your browser and navigate to `http://localhost:8080/sysbot` to browse the complete API documentation.

The documentation includes:
- **Module-level docstrings**: Purpose and overview of each module
- **Class documentation**: Detailed class descriptions and initialization parameters
- **Method documentation**: Comprehensive Args, Returns, and Raises sections
- **Package structure**: Hierarchical organization of all components

### Error Handling

SysBot provides comprehensive error handling:

- **Connection Errors**: Detailed error messages for connection failures
- **Tunnel Management**: Automatic cleanup on tunnel failures
- **Session Validation**: Verification of session validity before operations
- **Module Errors**: Clear error messages for module and function calls

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Thibault SCIRE - [GitHub](https://github.com/thibaultscire)

## Links

- **Documentation**: [https://joreci2.github.io/sysbot/](https://joreci2.github.io/sysbot/)
- **PyPI**: [https://pypi.org/project/sysbot/](https://pypi.org/project/sysbot/)
- **Repository**: [https://github.com/JoReci2/sysbot](https://github.com/JoReci2/sysbot)
- **Issues**: [https://github.com/JoReci2/sysbot/issues](https://github.com/JoReci2/sysbot/issues)
