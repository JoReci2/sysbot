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
    ├── __init__.py
    ├── module1.py      # e.g., systemd.py, dnf.py, firewall.py
    └── module2.py
```

Modules are simple Python files placed directly in the category directory, each containing a class that inherits from `ComponentBase`.

### Module Implementation

A typical module looks like this:

```python
# sysbot/modules/linux/systemd.py
from sysbot.utils.engine import ComponentBase


class Systemd(ComponentBase):
    """Module for managing systemd services."""
    
    def is_active(self, alias: str, name: str, **kwargs) -> str:
        """Check if a systemd service is active.
        
        Args:
            alias: The session alias to use
            name: The service name
            **kwargs: Additional arguments passed to execute_command
            
        Returns:
            The command output
        """
        return self.execute_command(alias, f"systemctl is-active {name}", **kwargs)
    
    def is_enabled(self, alias: str, name: str, **kwargs) -> str:
        """Check if a systemd service is enabled.
        
        Args:
            alias: The session alias to use
            name: The service name
            **kwargs: Additional arguments passed to execute_command
            
        Returns:
            The command output
        """
        return self.execute_command(alias, f"systemctl is-enabled {name}", **kwargs)
    
    def start(self, alias: str, name: str, **kwargs) -> str:
        """Start a systemd service.
        
        Args:
            alias: The session alias to use
            name: The service name
            **kwargs: Additional arguments passed to execute_command
            
        Returns:
            The command output
        """
        return self.execute_command(alias, f"systemctl start {name}", **kwargs)
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
import sysbot

# Load specific modules only
bot = sysbot.Sysbot("linux.systemd", "linux.dnf")

# Or load all available modules
bot = sysbot.Sysbot()

# Open a session and use the module
bot.open_session("server", "ssh", "bash", "192.168.1.100", 22, "user", "pass")
result = bot.linux.systemd.is_active("server", "sshd")
```

## Connectors Development

Connectors are the low-level interfaces that handle protocol-specific communication. They are located in the `sysbot/connectors/` directory.

### Connector Structure

Connectors must implement a standard interface to work with the SysBot engine:

```python
# sysbot/connectors/myprotocol.py
from sysbot.utils.engine import ConnectorInterface


class Myprotocol(ConnectorInterface):
    """Connector for MyProtocol."""
    
    def __init__(self, port=None):
        """Initialize the connector with default port.
        
        Args:
            port (int): Default port for this protocol.
        """
        super().__init__()
        self.default_port = port
    
    def open_session(self, host, port=None, login=None, password=None):
        """Open a session to the target system.
        
        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port of the service. If None, uses default_port.
            login (str): Username for the session.
            password (str): Password for the session.
        
        Returns:
            object: A session object (can be any type: connection, dict, etc.)
        
        Raises:
            Exception: If there is an error opening the session.
        """
        if port is None:
            port = self.default_port
        
        # Implement your connection logic here
        # Return a session object that will be passed to execute_command and close_session
        pass
    
    def execute_command(self, session, command, **kwargs):
        """Execute a command through the protocol.
        
        Args:
            session: The session object returned by open_session
            command (str): The command to execute
            **kwargs: Additional options for command execution (e.g., runas, password)
        
        Returns:
            str: The command output
        
        Raises:
            Exception: If there is an error executing the command
        """
        # Implement command execution logic
        pass
    
    def close_session(self, session):
        """Close an open session.
        
        Args:
            session: The session object to close.
        
        Raises:
            Exception: If there is an error closing the session.
        """
        # Implement session cleanup logic
        pass
```

### Required Methods

Every connector must implement these three mandatory methods:

* `open_session(host, port, login, password)`: Open a connection/session to the target system
* `execute_command(session, command, **kwargs)`: Execute a command through the protocol
* `close_session(session)`: Close an open session and clean up resources

### Connector Registration

To register a new connector with SysBot:

1. Create the connector class in `sysbot/connectors/`
2. The connector will be automatically discovered based on the protocol name
3. The protocol name should match the filename (e.g., `myprotocol.py` for protocol `myprotocol`)

### Connector Best Practices

* **Error Handling**: Always catch and handle connection errors gracefully
* **Resource Cleanup**: Implement proper cleanup in `close_session()`
* **Session Management**: Design session objects to hold all necessary connection state
* **Timeouts**: Implement sensible timeout values
* **SSL/TLS**: Support secure connections when applicable
* **Authentication**: Support multiple authentication methods if relevant
* **Logging**: Use logging for debugging and error tracking

### Example: HTTP Connector

The HTTP Basic Auth connector is a good reference implementation. This is a simplified version showing the core logic. The actual implementation in the codebase uses helper methods from the BaseHttp parent class:

```python
# sysbot/connectors/http.py (Basicauth class - simplified example)
from sysbot.utils.engine import ConnectorInterface
from requests.auth import HTTPBasicAuth
import requests


class Basicauth(ConnectorInterface):
    """HTTP connector with Basic Authentication."""
    
    def __init__(self, port=443, use_https=True):
        """Initialize Basic Auth connector.
        
        Args:
            port (int): Default port (default: 443).
            use_https (bool): Whether to use HTTPS (default: True).
        """
        super().__init__()
        self.default_port = port
        self.use_https = use_https
    
    def open_session(self, host, port=None, login=None, password=None):
        """Open a session with Basic authentication.
        
        Args:
            host (str): Hostname or IP address.
            port (int): Port. If None, uses default_port.
            login (str): Username.
            password (str): Password.
        
        Returns:
            dict: Session configuration containing connection details.
        """
        if port is None:
            port = self.default_port
        
        return {
            "host": host,
            "port": port,
            "login": login,
            "password": password,
            "use_https": self.use_https
        }
    
    def execute_command(self, session, command, options=None):
        """Execute an HTTP request with Basic authentication.
        
        Args:
            session (dict): Session configuration.
            command (str): API endpoint path.
            options (dict): Optional request parameters (method, params, headers, data, json, verify).
        
        Returns:
            bytes: Response content.
        """
        protocol = "https" if session["use_https"] else "http"
        url = f"{protocol}://{session['host']}:{session['port']}{command}"
        
        # Extract parameters from options
        method = options.get("method", "GET") if options else "GET"
        headers = options.get("headers") if options else None
        params = options.get("params") if options else None
        data = options.get("data") if options else None
        json_data = options.get("json") if options else None
        verify = options.get("verify", True) if options else True
        
        auth = HTTPBasicAuth(session["login"], session["password"])
        
        response = requests.request(
            method=method,
            url=url,
            auth=auth,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            verify=verify
        )
        response.raise_for_status()
        return response.content
    
    def close_session(self, session):
        """Close the session (no-op for Basic auth).
        
        Args:
            session (dict): Session configuration.
        """
        pass
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
```

### Data Plugin Example

Plugins inherit from `ComponentBase` and the class name must match the filename (capitalized). For example, `mydata.py` should have class `Mydata`:

```python
# sysbot/plugins/mydata.py
from sysbot.utils.engine import ComponentBase


class Mydata(ComponentBase):
    """Plugin for handling custom data format."""
    
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
            self._sysbot._cache.secrets.register(key, data)
        
        return data
    
    def _parse_file(self, filepath: str) -> dict:
        """Parse the data file."""
        # Implement parsing logic
        pass
```

### Robot Framework Listener Plugin

Listeners are special plugins for Robot Framework integration:

```python
# sysbot/utils/robot/listener/mylistener.py
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
2. **Robot listeners**: Add to `sysbot/utils/robot/listener/`

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
robot --listener sysbot.utils.robot.listener.mylistener.MyListener:arg1:arg2 tests/
```

## Release Process

### Publishing to PyPI

SysBot uses an automated GitHub Actions workflow to publish releases to PyPI. The workflow is triggered automatically when a version tag is pushed to the repository.

**Important**: SysBot uses `setuptools_scm` for automatic versioning. The package version is automatically determined from git tags, so you **do not need to manually update the version** in `setup.py`.

#### Prerequisites

Before publishing a release, ensure that:

1. **PyPI Trusted Publishing is configured** (recommended) or a PyPI API token is set up:
   - For trusted publishing: Configure the publisher in PyPI project settings
   - For API token: Add `PYPI_API_TOKEN` to repository secrets

#### Creating a Release

1. **Ensure your changes are committed and pushed**:
   ```bash
   git add .
   git commit -m "Your changes description"
   git push origin main
   ```

2. **Create and push a version tag**:
   ```bash
   git tag -a X.Y.Z -m "Release version X.Y.Z"
   git push origin X.Y.Z
   ```

   The version in the tag will automatically be used as the package version.

3. **Monitor the workflow**:
   - Go to the Actions tab in GitHub
   - Watch the "Publish Python Package to PyPI" workflow
   - The workflow will build and publish the package automatically

#### Version Tag Format

- Tags must use semantic versioning format: `MAJOR.MINOR.PATCH`
- Examples: `0.2.0`, `1.0.0`, `2.1.3`
- Do not prefix tags with `v`
- The exact tag version will be used as the package version on PyPI

#### Automatic Versioning with setuptools_scm

SysBot uses `setuptools_scm` to automatically determine the package version from git tags:

- **Tagged commits**: Use the exact tag version (e.g., tag `0.2.0` → package version `0.2.0`)
- **Development commits**: Use a development version (e.g., `0.2.1.dev5+g1234abcd`)
- The version is embedded in the package at build time and accessible via `sysbot.__version__`

#### Workflow Steps

The automated workflow performs the following steps:

1. **Checkout**: Fetches the full git history to enable version detection
2. **Build**: Creates both wheel (`.whl`) and source (`.tar.gz`) distributions with the version from the git tag
3. **Publish**: Uploads the distributions to PyPI using trusted publishing

#### Troubleshooting

If the workflow fails:

- **Authentication errors**: Verify PyPI trusted publishing is configured or API token is valid
- **Version conflicts**: Ensure the version tag hasn't already been published to PyPI
- **Build errors**: Check that all dependencies are correctly specified in `setup.py`
- **Version detection errors**: Ensure the git tag follows the semantic versioning format (X.Y.Z) without a 'v' prefix

## Acknowledgments

Thanks to all contributors who have helped improve SysBot!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
