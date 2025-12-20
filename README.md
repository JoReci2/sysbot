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

### HTTP/HTTPS

SysBot provides a generic HTTP/HTTPS connector with support for 9 authentication methods. Each authentication method is implemented as a separate, self-contained class.

#### Supported Authentication Methods

1. **API Key (`apikey`)** - API Key authentication via headers or query parameters
2. **Basic Auth (`basicauth`)** - Standard HTTP Basic Authentication
3. **OAuth 1.0 (`oauth1`)** - OAuth 1.0 authentication (RFC 5849)
4. **OAuth 2.0 (`oauth2`)** - OAuth 2.0 Bearer token authentication
5. **JWT (`jwt`)** - JSON Web Token authentication with automatic token generation
6. **SAML (`saml`)** - SAML assertion/token authentication
7. **HMAC (`hmac`)** - HMAC signature-based authentication
8. **Certificate (`certificate`)** - Client certificate authentication (mutual TLS)
9. **OpenID Connect (`openidconnect`)** - OpenID Connect authentication

#### Usage Examples

##### Basic Authentication
```python
bot.open_session(
    alias="my_api",
    protocol="http",
    product="basicauth",
    host="api.example.com",
    port=443,
    login="username",
    password="password"
)

result = bot.execute_command("my_api", "/users", options={"method": "GET"})
```

##### API Key Authentication
```python
bot.open_session(
    alias="my_api",
    protocol="http",
    product="apikey",
    host="api.example.com",
    port=443,
    api_key="your-api-key-here",
    api_key_header="X-API-Key"  # Custom header name (optional)
)

result = bot.execute_command("my_api", "/data", options={"method": "GET"})
```

##### OAuth 2.0 Authentication
```python
bot.open_session(
    alias="my_api",
    protocol="http",
    product="oauth2",
    host="api.example.com",
    port=443,
    client_id="your-client-id",
    client_secret="your-client-secret",
    access_token="your-access-token"
)

result = bot.execute_command("my_api", "/protected", options={"method": "GET"})
```

##### JWT Authentication
```python
bot.open_session(
    alias="my_api",
    protocol="http",
    product="jwt",
    host="api.example.com",
    port=443,
    login="user@example.com",
    secret_key="your-secret-key",
    algorithm="HS256"
)

result = bot.execute_command("my_api", "/secure", options={"method": "GET"})
```

##### Certificate Authentication
```python
bot.open_session(
    alias="my_api",
    protocol="http",
    product="certificate",
    host="api.example.com",
    port=443,
    cert_file="/path/to/client.crt",
    key_file="/path/to/client.key",
    ca_bundle="/path/to/ca-bundle.crt"  # Optional
)

result = bot.execute_command("my_api", "/secure", options={"method": "GET"})
```

##### POST Request with JSON Data
```python
result = bot.execute_command(
    "my_api",
    "/users",
    options={
        "method": "POST",
        "json": {"name": "John Doe", "email": "john@example.com"}
    }
)
```

#### HTTP/HTTPS Configuration

- **SSL Verification**: Enabled by default for security. Can be disabled per request:
  ```python
  result = bot.execute_command("my_api", "/endpoint", options={"verify": False})
  ```

- **HTTP vs HTTPS**: Configure via port (80 for HTTP, 443 for HTTPS) or use `use_https` parameter

- **Request Options**: All authentication methods support:
  - `method`: HTTP method (GET, POST, PUT, DELETE, etc.)
  - `headers`: Custom HTTP headers
  - `params`: URL query parameters
  - `data`: Request body data
  - `json`: JSON request body
  - `verify`: SSL certificate verification (default: True)

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
├── plugins/            # Plugins utilities (data, vault, robot/listener)
├── utils/
│   └── engine.py       # Engine class
└── modules/            # Modules
```

## Database Listener Plugin

SysBot includes Robot Framework listener plugins that can store test results in various databases. Each database type has its own independent, self-contained listener. The listeners create a hierarchical structure: Campaign → Suite → Test Case → Keyword.

### Available Listeners

- **SQLite**: Lightweight file-based database, perfect for local testing
- **MySQL**: Popular relational database for team environments
- **PostgreSQL**: Enterprise-grade relational database
- **MongoDB**: NoSQL document database for flexible schemas

### Usage

Each listener is used directly with its specific class:

```bash
# Store results in SQLite
robot --listener sysbot.plugins.robot.listener.sqlite.Sqlite:results.db:MyCampaign tests/

# Store results in MySQL
robot --listener sysbot.plugins.robot.listener.mysql.Mysql:mysql://user:pass@localhost/testdb:MyCampaign tests/

# Store results in PostgreSQL
robot --listener sysbot.plugins.robot.listener.postgresql.Postgresql:postgresql://user:pass@localhost/testdb:MyCampaign tests/

# Store results in MongoDB
robot --listener sysbot.plugins.robot.listener.mongodb.Mongodb:mongodb://localhost:27017/testdb:MyCampaign tests/
```

**Installation**: 
- `pip install sysbot[all_databases]` - Install with all database support
- `pip install sysbot[mysql]` - MySQL support only
- `pip install sysbot[postgresql]` - PostgreSQL support only
- `pip install sysbot[mongodb]` - MongoDB support only

For more details, see the [documentation](https://joreci2.github.io/sysbot/) or browse the [docs](docs/) directory.

## Documentation

Complete documentation is available in English and French:

- **English**: [View Documentation](https://joreci2.github.io/sysbot/)
- **French**: [Voir la Documentation](https://joreci2.github.io/sysbot/fr/)

### Documentation Sections

- **User Manual**
  - Setup & Installation
  - Quick Start
  - Robot Framework Guide
  - Unittest Guide
  - Database Listener Plugin
- **Developer Manual**
  - Developer Guide
- **References**
  - API Reference

The documentation is built with [Antora](https://antora.org/) and uses AsciiDoc format. See [docs/README.adoc](docs/README.adoc) for information on building documentation locally.

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