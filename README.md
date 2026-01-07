# SysBot

A comprehensive Python library for system test automation with support for multiple protocols (SSH, WinRM, HTTP, Socket), secret management, and seamless integration with Robot Framework and various database systems.

## Key Features

- **Multi-protocol Support**: SSH, HTTP, WinRM, Socket, and more
- **SSH Tunneling**: Support for nested SSH tunnels with automatic management
- **Cross-platform**: Support for Linux and Windows systems
- **Robot Framework Integration**: Built-in support for Robot Framework automation
- **Modular Architecture**: Dynamic components loading and discovery (modules and plugins)
- **Secret Management**: Secure storage and retrieval of sensitive data
- **Database Listeners**: Store test results in SQLite, MySQL, PostgreSQL, or MongoDB
- **Polarion Integration**: Generate Polarion-compatible xUnit reports for ALM/QA integration

## Installation

```bash
pip install sysbot
```

For specific features with database support:

```bash
# Install with all database support
pip install sysbot[all_databases]

# Install with development dependencies
pip install sysbot[dev]
```

## Quick Start

```python
import sysbot

bot = sysbot.Sysbot()

# Open an SSH session
bot.open_session(
    alias="my_server",
    protocol="ssh",
    product="bash",
    host="192.168.1.100",
    port=22,
    login="username",
    password="password"
)

# Execute a command
result = bot.execute_command("my_server", "ls -la")
print(result)

# Close all sessions
bot.close_all_sessions()
```

## Documentation

### Read the Full Documentation with pdoc3

SysBot includes comprehensive documentation embedded in the package. To read the complete documentation:

1. **Install pdoc3** (included with development dependencies):
   ```bash
   pip install sysbot[dev]
   # or
   pip install pdoc3
   ```

2. **Start the documentation server**:
   ```bash
   pdoc3 --http localhost:8080 sysbot
   ```

3. **Open your browser** and navigate to `http://localhost:8080/sysbot`

The documentation includes:
- Complete API reference with detailed docstrings
- Module-level documentation
- Usage examples and guides
- Complete README embedded in the package

### Generate Static Documentation

You can also generate static HTML documentation:

```bash
pdoc3 --html --output-dir docs sysbot
```

The generated HTML files will be in the `docs/` directory.

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on:
- Development environment setup
- Code standards and style guide
- Testing requirements
- Pull request process
- Module and connector development

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Thibault SCIRE - [GitHub](https://github.com/thibaultscire)

## Links

- **PyPI**: [https://pypi.org/project/sysbot/](https://pypi.org/project/sysbot/)
- **Repository**: [https://github.com/JoReci2/sysbot](https://github.com/JoReci2/sysbot)
- **Issues**: [https://github.com/JoReci2/sysbot/issues](https://github.com/JoReci2/sysbot/issues)
