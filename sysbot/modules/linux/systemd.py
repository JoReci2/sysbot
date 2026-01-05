"""
Systemd Module

This module provides methods for managing systemd services on Linux systems,
including checking service status, enablement state, and failure status.
"""
from sysbot.utils.engine import ComponentBase


class Systemd(ComponentBase):
    def is_active(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(alias, f"systemctl is-active {name}", **kwargs)

    def is_enabled(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(alias, f"systemctl is-enabled {name}", **kwargs)

    def is_failed(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(alias, f"systemctl is-failed {name}", **kwargs)
