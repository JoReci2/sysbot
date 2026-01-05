# SysBot

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [RobotFramework Usage](#robotframework-usage)
- [UnitTest Usage](#unittest-usage)
- [Listener Usage](#listener-usage)
- [Polarion Integration](#polarion-integration)
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
- **Database Listeners**: Store test results in SQLite, MySQL, PostgreSQL, or MongoDB
- **Polarion Integration**: Generate Polarion-compatible xUnit reports for ALM/QA integration

### Architecture

```
sysbot/
├── Sysbot.py           # Main SysBot class
├── connectors/         # Protocol-specific connectors
├── plugins/            # Plugins utilities (data, vault, robot/listener)
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

### Optional Dependencies

For specific features, you can install additional dependencies:

```bash
# Install with all database support
pip install sysbot[all_databases]

# Install with specific database support
pip install sysbot[mysql]        # MySQL support only
pip install sysbot[postgresql]   # PostgreSQL support only
pip install sysbot[mongodb]      # MongoDB support only
```

## Quickstart

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

### Secret Management

SysBot provides a built-in secret management system for secure storage and retrieval of sensitive data like passwords, tokens, and configuration values. Secrets can be stored directly or loaded from external sources like files or HashiCorp Vault.

```python
from sysbot.Sysbot import Sysbot
bot = Sysbot()

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

**Local Bash Execution:**
```python
from sysbot.Sysbot import Sysbot

bot = Sysbot()

# Open a local bash session (no actual connection is made)
bot.open_session(
    alias="local_bash",
    protocol="local",
    product="bash",
    host="localhost",  # Required but not used
    port=0  # Required but not used
)

# Execute commands locally
result = bot.execute_command("local_bash", "ls -la")
print(result)

bot.close_session("local_bash")
```

**Local PowerShell Execution:**
```python
from sysbot.Sysbot import Sysbot

bot = Sysbot()

# Open a local PowerShell session (no actual connection is made)
bot.open_session(
    alias="local_ps",
    protocol="local",
    product="powershell",
    host="localhost",  # Required but not used
    port=0  # Required but not used
)

# Execute PowerShell commands locally
result = bot.execute_command("local_ps", "Get-Process | Select-Object -First 5")
print(result)

bot.close_session("local_ps")
```

#### HTTP/HTTPS

SysBot provides a generic HTTP/HTTPS connector with support for 9 authentication methods.

**Supported Authentication Methods:**
1. **API Key (`apikey`)** - API Key authentication via headers or query parameters
2. **Basic Auth (`basicauth`)** - Standard HTTP Basic Authentication
3. **OAuth 1.0 (`oauth1`)** - OAuth 1.0 authentication (RFC 5849)
4. **OAuth 2.0 (`oauth2`)** - OAuth 2.0 Bearer token authentication
5. **JWT (`jwt`)** - JSON Web Token authentication with automatic token generation
6. **SAML (`saml`)** - SAML assertion/token authentication
7. **HMAC (`hmac`)** - HMAC signature-based authentication
8. **Certificate (`certificate`)** - Client certificate authentication (mutual TLS)
9. **OpenID Connect (`openidconnect`)** - OpenID Connect authentication

**Usage Examples:**

Basic Authentication:
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

API Key Authentication:
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
Suite Setup       Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
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
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password   is_secret=True
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

### Basic UnitTest Example

```python
import unittest
from sysbot.Sysbot import Sysbot

class TestSystemConnections(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.bot = Sysbot()
    
    def tearDown(self):
        """Clean up after tests."""
        self.bot.close_all_sessions()
    
    def test_ssh_connection(self):
        """Test SSH connection to a system."""
        self.bot.open_session(
            alias="test_server",
            protocol="ssh",
            product="bash",
            host="192.168.1.100",
            port=22,
            login="testuser",
            password="testpass"
        )
        
        result = self.bot.execute_command("test_server", "echo 'Hello World'")
        self.assertIn("Hello World", result)
    
    def test_http_api_call(self):
        """Test HTTP API connection."""
        self.bot.open_session(
            alias="api",
            protocol="http",
            product="basicauth",
            host="api.example.com",
            port=443,
            login="user",
            password="pass"
        )
        
        result = self.bot.execute_command(
            "api",
            "/health",
            options={"method": "GET"}
        )
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
```

### Module Testing with UnitTest

```python
import unittest
from sysbot.Sysbot import Sysbot

class TestLinuxModules(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up class fixtures."""
        cls.bot = Sysbot("linux.systemd", "linux.dnf")
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

## Listener Usage

SysBot includes Robot Framework listener plugins that can store test results in various databases. Each database type has its own independent, self-contained listener. The listeners create a hierarchical structure: Campaign → Suite → Test Case → Keyword.

### Available Listeners

- **SQLite**: Lightweight file-based database, perfect for local testing
- **MySQL**: Popular relational database for team environments
- **PostgreSQL**: Enterprise-grade relational database
- **MongoDB**: NoSQL document database for flexible schemas

### Usage with Robot Framework

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

### Listener Parameters

The listener accepts two parameters:
1. **Database Connection**: Connection string or path to database
2. **Campaign Name**: Name of the test campaign for organizing results

### Data Structure

The listeners store test execution data in a hierarchical format:

- **Campaign**: Top-level container for test executions
  - **Suite**: Test suite information
    - **Test Case**: Individual test cases
      - **Keyword**: Keywords executed within tests

Each level stores relevant metadata including:
- Execution timestamps
- Status (PASS/FAIL)
- Error messages
- Statistics

### Installation Requirements

```bash
# Install with all database support
pip install sysbot[all_databases]

# Or install specific database support
pip install sysbot[mysql]        # MySQL support only
pip install sysbot[postgresql]   # PostgreSQL support only
pip install sysbot[mongodb]      # MongoDB support only
```

## Polarion Integration

SysBot includes a Polarion plugin that enables integration with Siemens Polarion ALM/QA for test result management. The plugin provides:

- **xUnit Post-processor**: Converts Robot Framework output to Polarion-compatible xUnit XML using rebot
- **Test Case Mapping**: Links Robot Framework tests to Polarion test cases via tags
- **Custom Properties**: Supports Polarion custom fields and metadata

### Linking Tests to Polarion

Use tags in your Robot Framework tests to establish links with Polarion test cases:

```robot
*** Test Cases ***
Login Functionality Test
    [Documentation]    Validates user login with valid credentials
    [Tags]    polarion-id:TEST-001    polarion-title:Login Test    polarion-priority:High
    # Test steps...

User Management Test
    [Documentation]    Test user creation and deletion
    [Tags]    polarion-id:TEST-002    polarion-testEnvironment:Production
    # Test steps...
```

### Tag Format

- `polarion-id:TEST-XXX` - Links to Polarion test case ID (required for mapping)
- `polarion-title:Test Name` - Sets Polarion test case title
- `polarion-{property}:{value}` - Custom Polarion properties (e.g., `polarion-priority:High`, `polarion-assignee:jdoe`)

### Generating Polarion-Compatible xUnit

**Using Python API:**
```python
from sysbot.utils.polarion import Polarion

polarion = Polarion()
polarion.generate_xunit(
    output_xml='output.xml',
    xunit_file='polarion_results.xml',
    project_id='MYPROJECT',
    test_run_id='RUN-001',
    custom_properties={'environment': 'test', 'version': '1.0'}
)
```

**Using Command Line:**
```bash
# Run Robot Framework tests
robot --outputdir results tests/

# Generate Polarion xUnit using Python
python -c "from sysbot.utils.polarion import Polarion; \
    polarion = Polarion(); \
    polarion.generate_xunit('results/output.xml', 'results/polarion.xml', \
    project_id='PROJ', test_run_id='RUN-001')"
```

### Importing into Polarion

Once you have the Polarion-compatible xUnit file:

1. **Manual Import**: Use Polarion's UI to import the xUnit file
2. **Scheduled Import**: Configure Polarion's scheduled xUnit importer
3. **API Import**: Use tools like `dump2polarion` or Polarion's REST API

### Generated xUnit Content

The generated xUnit file includes:
- Test case IDs for proper mapping to existing Polarion test cases
- Test execution results (pass/fail/error)
- Execution time and timestamps
- Custom properties for filtering and reporting
- Project and test run associations

## Additional Resources

### Documentation

SysBot includes comprehensive Google-style docstrings for all modules, classes, and methods. You can generate and browse the documentation locally using pdoc3.

#### Viewing Documentation with pdoc3

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