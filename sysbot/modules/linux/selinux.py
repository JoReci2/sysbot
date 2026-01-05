"""
SELinux Module

This module provides methods for querying and managing SELinux (Security-Enhanced Linux)
security contexts, status, and boolean settings on Linux systems.
"""
from sysbot.utils.engine import ComponentBase


class Selinux(ComponentBase):
    """SELinux security management class for Linux systems."""

    def sestatus(self, alias: str, **kwargs) -> dict:
        """
        Get SELinux status information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing SELinux status information with normalized keys.
        """
        output = self.execute_command(alias, "sestatus", **kwargs)

        def normalize_key(key: str) -> str:
            return key.strip().lower().replace(" ", "_")

        data = {}
        for line in output.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                data[normalize_key(key)] = value.strip()
        return data

    def getenforce(self, alias: str, **kwargs) -> str:
        """
        Get the current SELinux enforcement mode.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            SELinux mode: Enforcing, Permissive, or Disabled.
        """
        return self.execute_command(alias, "getenforce", **kwargs)

    def context_id(self, alias: str, **kwargs) -> str:
        """
        Get the SELinux security context of the current user.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            SELinux security context string.
        """
        return self.execute_command(alias, "id -Z", **kwargs)

    def context_ps(self, alias: str, process: str, **kwargs) -> str:
        """
        Get SELinux security contexts for processes matching a name.

        Args:
            alias: Session alias for the connection.
            process: Process name to search for.
            **kwargs: Additional command execution options.

        Returns:
            Process list with SELinux security contexts.
        """
        return self.execute_command(alias, f"ps -axZ | grep {process}", **kwargs)

    def context_file(self, alias: str, filename: str, **kwargs) -> str:
        """
        Get SELinux security context for a file.

        Args:
            alias: Session alias for the connection.
            filename: Path to the file.
            **kwargs: Additional command execution options.

        Returns:
            File information with SELinux security context.
        """
        return self.execute_command(alias, f"ls -Z {filename}", **kwargs)

    def getsebool(self, alias: str, **kwargs) -> dict:
        """
        Get all SELinux boolean values.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary of SELinux booleans and their current values.
        """
        output = self.execute_command(alias, "getsebool -a", **kwargs)

        def normalize_key(key: str) -> str:
            return key.strip().lower().replace(" ", "_")

        data = {}
        for line in output.splitlines():
            if "-->" in line:
                key, value = line.split("-->", 1)
                data[normalize_key(key)] = value.strip()

        return data
