"""
Systemd Module

This module provides methods for managing systemd services on Linux systems,
including checking service status, enablement state, and failure status.
"""
from sysbot.utils.engine import ComponentBase


class Systemd(ComponentBase):
    """Systemd service management class for Linux systems."""

    def is_active(self, alias: str, name: str, **kwargs) -> str:
        """
        Check if a systemd service is active.

        Args:
            alias: Session alias for the connection.
            name: Name of the systemd service.
            **kwargs: Additional command execution options.

        Returns:
            Service active state (active, inactive, failed, etc.).
        """
        return self.execute_command(alias, f"systemctl is-active {name}", **kwargs)

    def is_enabled(self, alias: str, name: str, **kwargs) -> str:
        """
        Check if a systemd service is enabled.

        Args:
            alias: Session alias for the connection.
            name: Name of the systemd service.
            **kwargs: Additional command execution options.

        Returns:
            Service enabled state (enabled, disabled, etc.).
        """
        return self.execute_command(alias, f"systemctl is-enabled {name}", **kwargs)

    def is_failed(self, alias: str, name: str, **kwargs) -> str:
        """
        Check if a systemd service has failed.

        Args:
            alias: Session alias for the connection.
            name: Name of the systemd service.
            **kwargs: Additional command execution options.

        Returns:
            Service failed state (failed, active, inactive, etc.).
        """
        return self.execute_command(alias, f"systemctl is-failed {name}", **kwargs)
