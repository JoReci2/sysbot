# GitHub Copilot Instructions for SysBot

## Project Overview

SysBot is a Python library for system test automation. It provides a unified interface for managing remote system connections, executing commands, and interacting with various system modules and plugins. It supports multiple protocols (SSH, WinRM, HTTP, Socket, Local) and integrates with Robot Framework.

## Repository Structure

```
sysbot/
├── Sysbot.py              # Main Sysbot class (entry point)
├── connectors/            # Low-level protocol connectors (ssh, winrm, http, socket, local)
├── modules/               # High-level system abstractions (linux, windows, network, bmc, etc.)
│   ├── bmc/               # BMC management (iDRAC, iLO)
│   ├── container/         # Container management
│   ├── linux/             # Linux system management
│   ├── monitoring/        # Monitoring tools
│   ├── network/           # Network management
│   ├── virtualization/    # Virtualization tools
│   └── windows/           # Windows system management
├── plugins/               # Reusable utilities (data, vault, ansible)
└── utils/
    └── engine.py          # Core engine (ComponentMeta, ComponentBase, ConnectorInterface,
                           #              ComponentLoader, TunnelingManager, Cache)
```

## Architecture Principles

- **`Sysbot`** (main class) uses `ComponentMeta` as its metaclass for dynamic component loading.
- **Modules** inherit from `ComponentBase` and are auto-discovered from `sysbot/modules/`. They call `self.execute_command(alias, command)` to run commands over an active session.
- **Connectors** inherit from `ConnectorInterface` and are auto-discovered from `sysbot/connectors/`. They must implement `open_session`, `execute_command`, and `close_session`.
- **Plugins** inherit from `ComponentBase` and are located in `sysbot/plugins/`.
- **`TunnelingManager`** handles nested SSH tunnels and protocol resolution.
- **`Cache`** manages active sessions and secrets.
- Tests are maintained in the external [sysbot-tests](https://github.com/JoReci2/sysbot-tests) repository — there are no in-tree runnable tests.

## Code Style

- Follow **PEP 8**; use `ruff` for formatting and linting.
- Use `bandit` for security checks, `radon` for complexity, `safety` for dependency checks.
- **Naming conventions:**
  - Functions and variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`
  - Modules/directories: `lowercase`
- **Docstrings:** Google format for all public functions and classes. Always include `Args`, `Returns`, and `Raises` sections.

  ```python
  def example(param1: str, param2: int) -> bool:
      """Summary line.

      Args:
          param1: Description of first parameter.
          param2: Description of second parameter.

      Returns:
          Description of the return value.

      Raises:
          ValueError: When this exception is raised.
      """
  ```

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `style:` — formatting, whitespace
- `refactor:` — code refactoring
- `chore:` — maintenance

## Adding a Module

Modules live in `sysbot/modules/<category>/<module>.py`. The class must inherit from `ComponentBase`, use `PascalCase` for the class name, and call `self.execute_command(alias, command)`.

```python
# sysbot/modules/linux/mymodule.py
from sysbot.utils.engine import ComponentBase


class Mymodule(ComponentBase):
    """Module description."""

    def my_action(self, alias: str, arg: str, **kwargs) -> str:
        """Perform an action.

        Args:
            alias: The session alias to use.
            arg: Description of arg.
            **kwargs: Additional arguments forwarded to execute_command.

        Returns:
            The command output.
        """
        return self.execute_command(alias, f"some-command {arg}", **kwargs)
```

## Adding a Connector

Connectors live in `sysbot/connectors/<protocol>.py`. The class must inherit from `ConnectorInterface` and implement the three required methods.

```python
# sysbot/connectors/myprotocol.py
from sysbot.utils.engine import ConnectorInterface


class Myprotocol(ConnectorInterface):
    """Connector for MyProtocol."""

    def open_session(self, host, port=None, login=None, password=None, **kwargs):
        """Open a connection."""
        ...

    def execute_command(self, session, command, **kwargs):
        """Execute a command."""
        ...

    def close_session(self, session):
        """Close the connection."""
        ...
```

## Adding a Plugin

Plugins live in `sysbot/plugins/<plugin>.py`. The class inherits from `ComponentBase` and the class name must match the filename (capitalized).

```python
# sysbot/plugins/myplugin.py
from sysbot.utils.engine import ComponentBase


class Myplugin(ComponentBase):
    """Plugin description."""

    def my_utility(self, param: str) -> dict:
        """Utility function.

        Args:
            param: Description.

        Returns:
            Result dict.
        """
        ...
```

## BMC Module Specifics

- **iDRAC** (`sysbot/modules/bmc/idrac.py`): defaults to `system_id = 'System.Embedded.1'` for Redfish endpoints.
- **iLO** (`sysbot/modules/bmc/ilo.py`): defaults to `system_id = '1'` for Redfish endpoints.

## SSL Handling

- `Sysbot.open_session` normalizes string `verify_ssl` values (e.g., `"true"`, `"false"`) to Python booleans before forwarding them to the connector's `open_session`.
- `TunnelingManager.nested_tunnel` must forward `**kwargs` (including `verify_ssl`) to `protocol.open_session`.

## Versioning and Releases

- SysBot uses `setuptools_scm` for automatic versioning from git tags.
- Version tags must follow semantic versioning **without** a `v` prefix: `MAJOR.MINOR.PATCH` (e.g., `1.2.0`).
- Releases are published to PyPI automatically via GitHub Actions when a version tag is pushed.

## Testing

- There are no in-tree runnable tests. The test suite lives in the separate [sysbot-tests](https://github.com/JoReci2/sysbot-tests) repository.
- New features should include tests written in Robot Framework or `unittest` in sysbot-tests.
- Target test coverage: >80%.
