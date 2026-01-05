"""
RPM Package Module

This module provides methods for querying RPM packages on Linux systems,
including checking installation status and retrieving package version information.
"""
from sysbot.utils.engine import ComponentBase


class Rpm(ComponentBase):
    """RPM package query operations class for Linux systems."""

    def is_installed(self, alias: str, name: str, **kwargs) -> bool:
        """
        Check if an RPM package is installed.

        Args:
            alias: Session alias for the connection.
            name: Name of the RPM package.
            **kwargs: Additional command execution options.

        Returns:
            True if package is installed, False otherwise.
        """
        return (
            self.execute_command(alias, f"rpm -q --quiet {name} ; echo $?", **kwargs)
            == "0"
        )

    def version(self, alias: str, name: str, **kwargs) -> str:
        """
        Get the version of an installed RPM package.

        Args:
            alias: Session alias for the connection.
            name: Name of the RPM package.
            **kwargs: Additional command execution options.

        Returns:
            Package version string.
        """
        return self.execute_command(
            alias, f"""rpm -q --queryformat="%{{VERSION}}" {name}""", **kwargs
        )

    def release(self, alias: str, name: str, **kwargs) -> str:
        """
        Get the release of an installed RPM package.

        Args:
            alias: Session alias for the connection.
            name: Name of the RPM package.
            **kwargs: Additional command execution options.

        Returns:
            Package release string.
        """
        return self.execute_command(
            alias, f"""rpm -q --queryformat="%{{RELEASE}}" {name}""", **kwargs
        )
