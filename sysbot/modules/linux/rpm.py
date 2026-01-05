"""
RPM Package Module

This module provides methods for querying RPM packages on Linux systems,
including checking installation status and retrieving package version information.
"""
from sysbot.utils.engine import ComponentBase


class Rpm(ComponentBase):
    def is_installed(self, alias: str, name: str, **kwargs) -> bool:
        return (
            self.execute_command(alias, f"rpm -q --quiet {name} ; echo $?", **kwargs)
            == "0"
        )

    def version(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(
            alias, f"""rpm -q --queryformat="%{{VERSION}}" {name}""", **kwargs
        )

    def release(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(
            alias, f"""rpm -q --queryformat="%{{RELEASE}}" {name}""", **kwargs
        )
