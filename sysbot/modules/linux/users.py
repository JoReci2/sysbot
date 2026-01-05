"""
Linux User Management Module

This module provides methods for managing and querying user and group information
on Linux systems using the id and getent commands.
"""
from sysbot.utils.engine import ComponentBase


class Users(ComponentBase):
    """User and group management class for Linux systems."""

    def name(self, alias: str, **kwargs) -> str:
        """
        Get the current user name.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Current user name.
        """
        return self.execute_command(alias, "id -nu", **kwargs)

    def group(self, alias: str, **kwargs) -> list:
        """
        Get the current user's group names.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of group names the current user belongs to.
        """
        output = self.execute_command(alias, "id -Gn", **kwargs)
        return output.split()

    def uid(self, alias: str, name: str, **kwargs) -> str:
        """
        Get the user ID for a given user name.

        Args:
            alias: Session alias for the connection.
            name: User name to query.
            **kwargs: Additional command execution options.

        Returns:
            User ID (UID) as a string.
        """
        return self.execute_command(alias, f"id -u {name}", **kwargs)

    def gid(self, alias: str, name: str, **kwargs) -> str:
        """
        Get the primary group ID for a given user name.

        Args:
            alias: Session alias for the connection.
            name: User name to query.
            **kwargs: Additional command execution options.

        Returns:
            Primary group ID (GID) as a string.
        """
        return self.execute_command(alias, f"id -g {name}", **kwargs)

    def gids(self, alias: str, name: str, **kwargs) -> list:
        """
        Get all group IDs for a given user name.

        Args:
            alias: Session alias for the connection.
            name: User name to query.
            **kwargs: Additional command execution options.

        Returns:
            List of group IDs the user belongs to.
        """
        output = self.execute_command(alias, f"id -G {name}", **kwargs)
        return output.split()

    def groups(self, alias: str, name: str, **kwargs) -> list:
        """
        Get all group names for a given user name.

        Args:
            alias: Session alias for the connection.
            name: User name to query.
            **kwargs: Additional command execution options.

        Returns:
            List of group names the user belongs to.
        """
        output = self.execute_command(alias, f"id -Gn {name}", **kwargs)
        return output.split()

    def home(self, alias: str, name: str, **kwargs) -> str:
        """
        Get the home directory for a given user name.

        Args:
            alias: Session alias for the connection.
            name: User name to query.
            **kwargs: Additional command execution options.

        Returns:
            Home directory path for the user.
        """
        return self.execute_command(
            alias, f"getent passwd {name} | cut -d: -f6", **kwargs
        )

    def shell(self, alias: str, name: str, **kwargs) -> str:
        """
        Get the login shell for a given user name.

        Args:
            alias: Session alias for the connection.
            name: User name to query.
            **kwargs: Additional command execution options.

        Returns:
            Login shell path for the user.
        """
        return self.execute_command(
            alias, f"getent passwd {name} | cut -d: -f7", **kwargs
        )
