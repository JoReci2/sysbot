# Contributing to SysBot

Thank you for your interest in contributing to SysBot! This document explains how to contribute effectively to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Environment Setup](#development-environment-setup)
- [Development Tools](#development-tools)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [CI/CD Workflows](#cicd-workflows)
- [Pull Request Process](#pull-request-process)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct. Be respectful and constructive in all your interactions.

## How to Contribute

There are several ways to contribute:

- Report bugs
- Propose new features
- Improve documentation
- Fix bugs
- Add new features

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
   pip install -r requirements-dev.txt
   ```

5. Install the package in development mode:

   ```bash
   pip install -e .
   ```

6. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

## Development Tools

### Tox

Tox is configured to run multiple test environments for code quality checks.

#### Available Environments

```bash
# List all available tox environments
tox list

# Run all environments
tox

# Run specific environment
tox -e lint
tox -e radon
tox -e bandit
tox -e robot
tox -e docs
```

### Linting with Ruff

Ruff is a fast Python linter that replaces multiple tools.

```bash
# Check code style
ruff check sysbot

# Fix auto-fixable issues
ruff check --fix sysbot

# Format code
ruff format sysbot
```

Configuration is in `pyproject.toml` under `[tool.ruff]`.

### Pre-commit Hooks

Pre-commit hooks automatically run checks before committing code.

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
```

Configuration is in `.pre-commit-config.yaml`.

### Code Complexity with Radon

Radon analyzes code complexity and maintainability.

```bash
# Cyclomatic complexity
radon cc sysbot -a

# Maintainability index
radon mi sysbot

# Raw metrics
radon raw sysbot

# Halstead metrics
radon hal sysbot
```

### Security Scanning with Bandit

Bandit scans for common security issues.

```bash
# Run security scan
bandit -r sysbot

# Generate JSON report
bandit -r sysbot -f json -o bandit-report.json
```

Configuration is in `pyproject.toml` under `[tool.bandit]`.

## Code Standards

### Code Style

- Follow PEP 8 for Python style
- Use `ruff` for automatic formatting and linting
- Use `radon` for code complexity checks
- Use `bandit` for security checks
- Maximum line length: 120 characters

### Naming Conventions

- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Modules: `lowercase`

### Documentation

Document all public functions with docstrings using Google format.

**Docstring example:**

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

### Robot Framework Tests

Write tests for any new functionality and maintain high test coverage (>80%).

```bash
# Run all Robot Framework tests
robot tests/

# Run specific test file
robot tests/modules/linux/file.robot

# Run with tox
tox -e robot
```

### Python Tests

```bash
# Run pytest (if available)
pytest tests/
```

## Documentation

Documentation is written in AsciiDoc format and built using Antora.

### Building Documentation Locally

```bash
# Install Node.js and npm (if not already installed)
# Then install Antora
npm install -g @antora/cli@3.1 @antora/site-generator@3.1

# Build documentation with Antora
antora --fetch antora-playbook.yml

# The generated site will be in build/site/

# For PDF generation, you also need asciidoctor-pdf
sudo apt-get install ruby-asciidoctor-pdf
```

### Documentation CI/CD

Documentation is automatically built with Antora and deployed to GitHub Pages when changes are pushed to the `main` branch. See `.github/workflows/docs.yml`.

## CI/CD Workflows

### Release Workflow

Triggered when a tag is pushed to the repository:

```bash
# Tag the release (use semantic version format without 'v' prefix)
git tag 1.0.0
git push origin 1.0.0
```

The release workflow automatically:
1. Builds the Python package
2. Publishes to GitHub Packages
3. Generates SBOM (Software Bill of Materials)
4. Runs vulnerability scanning
5. Builds complete PDF documentation using Antora
6. Creates GitHub release with release notes from milestone

Configuration: `.github/workflows/release.yml`

### Documentation Workflow

Automatically builds documentation with Antora and deploys to GitHub Pages when changes are pushed to `main`.

Configuration: `.github/workflows/docs.yml`

### CI Workflow

Runs on pull requests and pushes to main:
- Lint checks with ruff
- Security scanning with bandit
- Complexity analysis with radon
- Installation verification

Configuration: `.github/workflows/ci.yml`

## Pull Request Process

1. Create a branch for your feature:

   ```bash
   git checkout -b feature/feature-name
   ```

2. Make your changes following the code standards

3. Run all quality checks before submitting:

   ```bash
   # Run all quality checks
   tox
   
   # Or run individually
   tox -e lint
   tox -e radon
   tox -e bandit
   tox -e robot
   ```

4. Commit your changes with descriptive messages:

   ```bash
   git commit -m "feat: add new feature X"
   ```

5. Push your branch:

   ```bash
   git push origin feature/feature-name
   ```

6. Create a pull request on GitHub

7. Ensure that:
   - All tests pass
   - Code follows standards
   - Documentation is updated if necessary
   - Pull request has a clear description

### Commit Convention

Use Conventional Commits convention:

- `feat:` - new feature
- `fix:` - bug fix
- `docs:` - documentation changes
- `style:` - formatting, missing semicolons, etc.
- `refactor:` - code refactoring
- `test:` - adding tests
- `chore:` - maintenance tasks

## Bug Reports

Before reporting a bug:

1. Check it doesn't already exist in issues
2. Make sure you're using the latest version

To report a bug, include:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python and system version
- Complete error logs

**Issue template:**

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

## Quick Development Workflow

1. **Before starting work:**
   ```bash
   # Install pre-commit hooks (once)
   pre-commit install
   ```

2. **During development:**
   - Pre-commit hooks run automatically on commit
   - Or run manually: `pre-commit run --all-files`

3. **Before submitting PR:**
   ```bash
   # Run all quality checks
   tox
   ```

## Troubleshooting

### Tox Issues

If tox fails to create environments:
```bash
# Remove all tox environments and recreate
tox -r
```

### Pre-commit Issues

If pre-commit hooks fail:
```bash
# Update hooks to latest versions
pre-commit autoupdate

# Clear cache
pre-commit clean
```

### Ruff Issues

If ruff reports false positives:
- Add `# noqa: CODE` comment to ignore specific line
- Update `pyproject.toml` to adjust rules

## Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Tox Documentation](https://tox.wiki/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Radon Documentation](https://radon.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Robot Framework Documentation](https://robotframework.org/)

## GitHub Copilot

GitHub Copilot instructions are configured in `.github/copilot-instructions.md`. This file contains:
- Project overview and architecture
- Code style and naming conventions
- Security best practices
- Common patterns and examples
- Testing guidelines

## Questions and Support

- For general questions: use GitHub Discussions
- For bugs: create an issue
- For major contributions: contact maintainers first

## Acknowledgments

Thanks to all contributors who have helped improve SysBot!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).
