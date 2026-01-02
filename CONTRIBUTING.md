# Contributing

Thank you for your interest in contributing to SysBot! This document explains how to contribute effectively to the project.

## Table of Contents

* [Code of Conduct](#code-of-conduct)
* [How to Contribute](#how-to-contribute)
* [Development Environment Setup](#development-environment-setup)
* [Code Standards](#code-standards)
* [Testing](#testing)
* [Pull Request Process](#pull-request-process)
* [Bug Reports](#bug-reports)
* [Feature Requests](#feature-requests)
* [Modules Development](#modules-development)
* [Connectors Development](#connectors-development)
* [Plugins Development](#plugins-development)

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct. Be respectful and constructive in all your interactions.

## How to Contribute

There are several ways to contribute:

* Report bugs
* Propose new features
* Improve documentation
* Fix bugs
* Add new features

## Development Environment Setup

1. Fork the repository
2. Clone your fork locally:

   ```bash
   git clone https://github.com/your-username/sysbot.git
   cd sysbot
   ```

3. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

4. Install development dependencies:

   ```bash
   pip install build ruff bandit radon safety
   ```

5. Install the package in development mode:

   ```bash
   pip install -e .
   ```

## Code Standards

### Code Style

* Follow PEP 8 for Python style
* Use `ruff` for automatic formatting and linting
* Use `radon` for code complexity
* Use `bandit` for security checks
* Use `safety` for dependency checks

### Naming Conventions

* Functions and variables: `snake_case`
* Classes: `PascalCase`
* Constants: `UPPER_CASE`
* Modules: `lowercase`

### Documentation

* Document all public functions with docstrings
* Use Google format for docstrings
* Include usage examples when appropriate

Docstring example:

```python
def example_function(param1: str, param2: int) -> bool:
    """Example function with docstring.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this exception is raised
    """
```

## Testing

* Write tests for any new functionality
* Maintain high test coverage (>80%)
* Use `robot framework` or `unittest` for testing
* Place tests in the `tests/` folder

Running tests:

```bash
# All tests
robot -d tests/

# Specific tests
robot -d tests/test_specific.robot
```

## Pull Request Process

1. Create a branch for your feature:

   ```bash
   git checkout -b feature/feature-name
   ```

2. Commit your changes with descriptive messages:

   ```bash
   git commit -m "feat: add new feature X"
   ```

3. Push your branch:

   ```bash
   git push origin feature/feature-name
   ```

4. Create a pull request on GitHub

5. Ensure that:

   * All tests pass
   * Code follows standards
   * Documentation is updated if necessary
   * Pull request has a clear description

### Commit Convention

Use Conventional Commits convention:

* `feat:`: new feature
* `fix:`: bug fix
* `docs:`: documentation
* `style:`: formatting, missing semicolons, etc.
* `refactor:`: code refactoring
* `test:`: adding tests
* `chore:`: maintenance

## Bug Reports

Before reporting a bug:

1. Check it doesn't already exist in issues
2. Make sure you're using the latest version

To report a bug, include:

* Clear description of the problem
* Steps to reproduce
* Expected vs actual behavior
* Python and system version
* Complete error logs

Issue template:

```
**Bug Description**
Clear and concise description of the bug.

**Reproduction**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
Clear description of what should happen.

**Environment**
- OS: [e.g. macOS 12.0]
- Python: [e.g. 3.9.0]
- SysBot: [e.g. 1.0.0]
```

## Feature Requests

To propose a new feature:

1. Check it doesn't already exist
2. Describe the problem it solves
3. Propose a solution
4. Give usage examples

## Questions and Support

* For general questions: use GitHub Discussions
* For bugs: create an issue
* For major contributions: contact maintainers first

## Modules Development

Modules in SysBot provide high-level abstractions for interacting with specific systems or services. They are automatically discovered and loaded from the `sysbot/modules/` directory.

### Module Structure

Each module should follow this structure:

```
sysbot/modules/
└── category/           # e.g., linux, windows, network
    └── subcategory/    # e.g., systemd, dnf, firewall
        ├── __init__.py
        └── module.py
```

### Module Implementation

A typical module looks like this:

```python
# sysbot/modules/linux/systemd/__init__.py
from sysbot.modules.linux.systemd.systemd import Systemd

__all__ = ['Systemd']
```

```python
# sysbot/modules/linux/systemd/systemd.py
class Systemd:
    """Module for managing systemd services."""
    
    def __init__(self, engine):
        """Initialize the module with the engine instance.
        
        Args:
            engine: The Sysbot engine instance for executing commands
        """
        self.engine = engine
    
    def status(self, alias: str, service: str) -> str:
        """Get the status of a systemd service.
        
        Args:
            alias: The session alias to use
            service: The service name
            
        Returns:
            The status output
        """
        cmd = f"systemctl status {service}"
        return self.engine.execute_command(alias, cmd)
    
    def start(self, alias: str, service: str) -> str:
        """Start a systemd service.
        
        Args:
            alias: The session alias to use
            service: The service name
            
        Returns:
            The command output
        """
        cmd = f"systemctl start {service}"
        return self.engine.execute_command(alias, cmd)
```

### Module Best Practices

* **Naming**: Use lowercase for module directories and PascalCase for classes
* **Documentation**: Provide comprehensive docstrings for all public methods
* **Error Handling**: Handle errors gracefully and provide meaningful error messages
* **Dependencies**: Document any system dependencies or required commands
* **Testing**: Write tests for your module functionality
* **Scope**: Keep modules focused on a single responsibility

### Module Usage

Once implemented, modules are automatically discovered and can be used as shown below. When instantiating Sysbot, you can optionally specify which modules to load using dot notation (e.g., `"linux.systemd"`), or load all modules by not passing any arguments:

```python
from sysbot.Sysbot import Sysbot

# Load specific modules only
bot = Sysbot("linux.systemd", "linux.dnf")

# Or load all available modules
bot = Sysbot()

# Open a session and use the module
bot.open_session("server", "ssh", "bash", "192.168.1.100", 22, "user", "pass")
result = bot.linux.systemd.status("server", "sshd")
```

## Connectors Development

Connectors are the low-level interfaces that handle protocol-specific communication. They are located in the `sysbot/connectors/` directory.

### Connector Structure

Connectors must implement a standard interface to work with the SysBot engine:

```python
# sysbot/connectors/myprotocol.py
class MyProtocolConnector:
    """Connector for MyProtocol."""
    
    def __init__(self, **kwargs):
        """Initialize the connector with connection parameters.
        
        Args:
            **kwargs: Connection parameters (host, port, login, password, etc.)
        """
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.login = kwargs.get('login')
        self.password = kwargs.get('password')
        self.connection = None
    
    def connect(self):
        """Establish the connection.
        
        Returns:
            The connection object
            
        Raises:
            ConnectionError: If connection fails
        """
        # Implement connection logic
        pass
    
    def disconnect(self):
        """Close the connection."""
        # Implement disconnection logic
        pass
    
    def execute(self, command: str, **options) -> str:
        """Execute a command through the protocol.
        
        Args:
            command: The command to execute
            **options: Additional options for command execution
            
        Returns:
            The command output
            
        Raises:
            RuntimeError: If execution fails
        """
        # Implement command execution
        pass
    
    def is_connected(self) -> bool:
        """Check if the connection is active.
        
        Returns:
            True if connected, False otherwise
        """
        # Implement connection check
        pass
```

### Required Methods

Every connector must implement these methods:

* `connect()`: Establish the connection
* `disconnect()`: Close the connection
* `execute(command, **options)`: Execute a command
* `is_connected()`: Check connection status

### Connector Registration

To register a new connector with SysBot:

1. Create the connector class in `sysbot/connectors/`
2. The connector will be automatically discovered based on the protocol name
3. The protocol name should match the filename (e.g., `myprotocol.py` for protocol `myprotocol`)

### Connector Best Practices

* **Error Handling**: Always catch and handle connection errors gracefully
* **Resource Cleanup**: Implement proper cleanup in `disconnect()`
* **Connection Pooling**: Consider connection reuse when appropriate
* **Timeouts**: Implement sensible timeout values
* **SSL/TLS**: Support secure connections when applicable
* **Authentication**: Support multiple authentication methods if relevant
* **Logging**: Use logging for debugging and error tracking

### Example: HTTP Connector

The HTTP connector is a good reference implementation:

```python
# sysbot/connectors/http.py
import requests

class HttpConnector:
    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.port = kwargs.get('port', 443)
        self.use_https = kwargs.get('use_https', True)
        self.base_url = f"{'https' if self.use_https else 'http'}://{self.host}:{self.port}"
        self.session = None
    
    def connect(self):
        self.session = requests.Session()
        return self.session
    
    def disconnect(self):
        if self.session:
            self.session.close()
    
    def execute(self, endpoint: str, **options):
        method = options.get('method', 'GET')
        response = self.session.request(method, f"{self.base_url}{endpoint}", **options)
        return response.text
    
    def is_connected(self):
        return self.session is not None
```

## Plugins Development

Plugins extend SysBot's functionality by providing reusable utilities. They are located in the `sysbot/plugins/` directory.

### Plugin Types

SysBot supports several types of plugins:

* **Data Plugins**: For data manipulation and loading (CSV, YAML, JSON, etc.)
* **Robot Plugins**: For Robot Framework integration (listeners, libraries)
* **Integration Plugins**: For external system integration (Vault, Polarion, etc.)

### Plugin Structure

A typical plugin structure:

```
sysbot/plugins/
├── __init__.py
├── myplugin.py           # Plugin implementation
└── robot/                # Robot Framework plugins
    └── listener/         # Listener plugins
        └── mylistener.py
```

### Data Plugin Example

```python
# sysbot/plugins/mydata.py
class MyDataPlugin:
    """Plugin for handling custom data format."""
    
    def __init__(self, engine):
        """Initialize the plugin with the engine instance.
        
        Args:
            engine: The Sysbot engine instance
        """
        self.engine = engine
    
    def load(self, filepath: str, key: str = None) -> dict:
        """Load data from a file.
        
        Args:
            filepath: Path to the data file
            key: Optional key for storing in secrets
            
        Returns:
            The loaded data
        """
        # Implement data loading
        data = self._parse_file(filepath)
        
        if key:
            self.engine.add_secret(key, data)
        
        return data
    
    def _parse_file(self, filepath: str) -> dict:
        """Parse the data file."""
        # Implement parsing logic
        pass
```

### Robot Framework Listener Plugin

Listeners are special plugins for Robot Framework integration:

```python
# sysbot/plugins/robot/listener/mylistener.py
class MyListener:
    """Robot Framework listener for custom functionality."""
    
    ROBOT_LISTENER_API_VERSION = 3
    
    def __init__(self, *args):
        """Initialize the listener with arguments from Robot Framework."""
        # Parse arguments passed from robot command line
        pass
    
    def start_suite(self, data, result):
        """Called when a test suite starts."""
        pass
    
    def end_suite(self, data, result):
        """Called when a test suite ends."""
        pass
    
    def start_test(self, data, result):
        """Called when a test case starts."""
        pass
    
    def end_test(self, data, result):
        """Called when a test case ends."""
        pass
```

### Plugin Registration

Plugins are automatically registered when they are placed in the correct location:

1. **Data plugins**: Add to `sysbot/plugins/` and import in `__init__.py`
2. **Robot listeners**: Add to `sysbot/plugins/robot/listener/`

### Plugin Best Practices

* **Loose Coupling**: Plugins should not depend on specific modules or connectors
* **Documentation**: Provide clear documentation on plugin usage
* **Error Handling**: Handle errors gracefully with meaningful messages
* **Dependencies**: Document any external dependencies (e.g., database drivers)
* **Configuration**: Support configuration through initialization parameters
* **Testing**: Write comprehensive tests for plugin functionality
* **Versioning**: Consider API versioning for public plugins

### Using Plugins

Plugins can be accessed through the main Sysbot instance:

```python
from sysbot.Sysbot import Sysbot

bot = Sysbot()

# Data plugin usage
data = bot.plugins.data.yaml('/path/to/file.yml', key='mydata')

# Vault plugin usage
bot.plugins.vault.dump_engine(
    token="token",
    url="https://vault.example.com:8200",
    engine_name="secret",
    key="vault_secrets"
)
```

Robot Framework listeners are used differently:

```bash
robot --listener sysbot.plugins.robot.listener.mylistener.MyListener:arg1:arg2 tests/
```

## Acknowledgments

Thanks to all contributors who have helped improve SysBot!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
