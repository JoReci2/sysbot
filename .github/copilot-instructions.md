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
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
├── README.md               # Main documentation
├── antora-playbook.yml     # Antora documentation configuration
├── docs/                   # Project documentation
├── pyproject.toml          # Build configuration
├── setup.py                # Installation configuration
├── sysbot/                 # Main source code
│   ├── connectors/         # Protocol-specific connectors
│   ├── dataloaders/        # Data loading utilities
│   └── utils/              # General utilities
└── tests/                  # Unit tests
```

## Development Best Practices

### Unit Tests
- **Keep tests up to date**: Each new feature must be accompanied by corresponding tests
- **Code coverage**: Aim for high test coverage for critical code
- **Pre-commit testing**: Run all tests before each commit with `pytest tests/`
- **Test isolation**: Each test must be independent and reproducible

### Code Conventions
- Follow PEP 8 conventions
- Use type annotations for all public functions
- Prioritize readability and maintainability
- Avoid unnecessary external dependencies
- Document complex functions with usage examples