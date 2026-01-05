"""
DNF Package Manager Module

This module provides methods for interacting with the DNF package manager on
RHEL/Fedora-based Linux systems, including repository management and package
operations.
"""
from sysbot.utils.engine import ComponentBase
import json
import configparser
from io import StringIO


class Dnf(ComponentBase):
    """DNF package manager operations class for RHEL/Fedora-based systems."""

    def repolist(self, alias: str, **kwargs) -> dict:
        """
        Get list of DNF repositories.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing repository information in JSON format.
        """
        output = self.execute_command(alias, "dnf repolist --json", **kwargs)
        return json.loads(output)

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
