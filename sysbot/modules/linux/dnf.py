"""
DNF Package Manager Module

This module provides methods for interacting with the DNF package manager on
RHEL/Fedora-based Linux systems, including repository management and package
operations.
"""
from sysbot.utils.engine import ComponentBase
import configparser
from io import StringIO


class Dnf(ComponentBase):
    """DNF package manager operations class for RHEL/Fedora-based systems."""

    def repolist(self, alias: str, **kwargs) -> list:
        """
        Get list of DNF repositories.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing repository information,
            each with 'id' and 'name' keys.
        """
        output = self.execute_command(alias, "dnf repolist", **kwargs)
        repos = []
        # Locate the header line (e.g. "repo id    repo name") and parse
        # only the lines that follow it, skipping any metadata lines printed
        # before the table (e.g. "Last metadata expiration check: …").
        header_found = False
        for line in output.splitlines():
            if not header_found:
                if line.lstrip().lower().startswith("repo id"):
                    header_found = True
                continue
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if parts:
                repos.append({"id": parts[0], "name": parts[1].strip() if len(parts) > 1 else ""})
        return repos

    def repofile(self, alias: str, file: str, **kwargs) -> dict:
        """
        Parse a DNF repository configuration file.

        Args:
            alias: Session alias for the connection.
            file: Path to the repository configuration file.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary with repository configuration sections and their values.
        """
        output = self.execute_command(alias, f"cat {file}", **kwargs)
        config = configparser.ConfigParser(strict=False, interpolation=None)
        config.read_file(StringIO(output))
        data = {section: dict(config.items(section)) for section in config.sections()}
        return data
