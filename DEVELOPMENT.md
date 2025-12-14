# Development Tools

This document describes the development tools available in the SysBot project.

## Setup

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Code Quality Tools

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

## Testing

### Robot Framework Tests

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

Documentation is written in AsciiDoc format in the `docs/` directory.

### Building Documentation Locally

```bash
# Install AsciiDoc tools
sudo apt-get install asciidoctor ruby-asciidoctor-pdf

# Build HTML documentation
cd docs
asciidoctor index.adoc

# Build PDF documentation
asciidoctor-pdf -o documentation.pdf index.adoc
```

### Documentation CI/CD

Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the `main` branch. See `.github/workflows/docs.yml`.

## CI/CD Workflows

### Release Workflow

Triggered when a tag is pushed to the repository:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The release workflow:
1. Builds the Python package
2. Publishes to PyPI (when configured)
3. Generates SBOM (Software Bill of Materials)
4. Runs vulnerability scanning
5. Builds PDF documentation
6. Creates GitHub release with release notes from milestone

Configuration: `.github/workflows/release.yml`

### Documentation Workflow

Automatically builds and deploys documentation to GitHub Pages when changes are pushed to `main`.

Configuration: `.github/workflows/docs.yml`

## GitHub Copilot

GitHub Copilot instructions are configured in `.github/copilot-instructions.md`. This file contains:
- Project overview and architecture
- Code style and naming conventions
- Security best practices
- Common patterns and examples
- Testing guidelines

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
   
   # Or run individually
   tox -e lint
   tox -e radon
   tox -e bandit
   tox -e robot
   ```

4. **Creating a release:**
   ```bash
   # Tag the release
   git tag v1.0.0
   git push origin v1.0.0
   
   # GitHub Actions will automatically:
   # - Build and publish package
   # - Generate SBOM
   # - Run security scans
   # - Build documentation
   # - Create release notes
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
