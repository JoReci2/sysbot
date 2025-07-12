# GitHub Copilot Configuration for SysBot

## Project Description

SysBot is a system automation and management tool that provides a unified interface for connecting to and managing various systems through different protocols.

### Key Features:
- **Multi-protocol support**: SSH, HTTP, WinRM and more
- **SSH tunneling**: Support for nested SSH tunnels
- **File operations**: Remote script execution and result retrieval
- **Multi-platform**: Support for Linux and Windows
- **Robot Framework integration**: Built-in support for Robot Framework automation
- **Type safety**: Complete type annotation support and static analysis

## Repository Structure

```
sysbot/
├── .github/                 # GitHub and Copilot configuration
├── .gitlab-ci.yml          # GitLab CI/CD configuration
├── docs/                   # Project documentation
├── sysbot/                 # Main source code
│   ├── __init__.py
│   ├── Helper.py           # Main utility functions
│   ├── connectors/         # Protocol-specific connectors
│   │   ├── ConnectorHandler.py  # Main handler class
│   │   ├── ssh/            # SSH protocol implementations
│   │   │   ├── linux.py    # Linux SSH connector
│   │   │   ├── windows.py  # Windows SSH connector
│   │   │   └── utils/      # SSH utilities
│   │   ├── http/           # HTTP protocol implementations
│   │   └── winrm/          # WinRM protocol implementations
│   ├── dataloaders/        # Data loading utilities
│   └── utils/              # General utilities
├── tests/                  # Unit tests
│   ├── test_Helper.py
│   ├── test_connector_handler.py
│   ├── test_dataloader_handler.py
│   └── test_listener_http.py
├── README.md               # Main documentation
├── setup.py                # Installation configuration
├── pyproject.toml          # Build configuration
└── LICENSE                 # MIT License
```

## Development Best Practices

### Unit Tests
- **Keep tests up to date**: Each new feature must be accompanied by corresponding tests
- **Code coverage**: Aim for high test coverage for critical code
- **Pre-commit testing**: Run all tests before each commit with `pytest tests/`
- **Test isolation**: Each test must be independent and reproducible

### Code Quality
- **Formatting**: Use `black sysbot/` for automatic formatting
- **Type checking**: Use `mypy sysbot/` for static type verification
- **Linting**: Use `flake8 sysbot/` for code analysis
- **Documentation**: Keep documentation up to date in README.md and docstrings

### Branch Management
- **Branch naming**: Branch names must be directly related to the associated issue
  - Recommended format: `feature/issue-<number>-<short-description>`
  - Example: `feature/issue-11-add-copilot-config`
  - For fixes: `fix/issue-<number>-<short-description>`
  - For enhancements: `enhancement/issue-<number>-<short-description>`

### Development Workflow
1. **Before each commit**:
   - Run tests: `pytest tests/`
   - Check formatting: `black --check sysbot/`
   - Check types: `mypy sysbot/`
   - Check linting: `flake8 sysbot/`

2. **Documentation**:
   - Update README.md for new features
   - Add or update docstrings for new methods/classes
   - Maintain documentation in the `docs/` folder if applicable

3. **Pull Requests**:
   - Include a clear description of changes
   - Reference the associated issue
   - Ensure all tests pass
   - Request code review before merge

### Dependencies
- **Development installation**: `pip install -e ".[dev]"`
- **Main dependencies**: robotframework, paramiko, sshtunnel, netmiko, redfish, pyVmomi, pywinrm, pyOpenSSL
- **Python**: Minimum version 3.7+

### Code Conventions
- Follow PEP 8 conventions
- Use type annotations for all public functions
- Prioritize readability and maintainability
- Avoid unnecessary external dependencies
- Document complex functions with usage examples