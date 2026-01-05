"""
Windows User Management Module

This module provides methods for managing and querying user and group information
on Windows systems using WMI (Windows Management Instrumentation).
"""
from sysbot.utils.engine import ComponentBase
import json


class Users(ComponentBase):
    """Windows user and group management class using WMI."""

    def win32_useraccount(self, alias: str, **kwargs) -> dict:
        """
        Get user account information using WMI Win32_UserAccount class.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing user account details including FullName, LocalAccount,
            Domain, Lockout status, Name, PasswordChangeable, PasswordRequired, and SID.
        """
        command = "Get-WmiObject -Class Win32_UserAccount | Select-Object FullName, LocalAccount, Domain, Lockout, Name, PasswordChangeable, PasswordRequired, SID | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def win32_group(self, alias: str, **kwargs) -> dict:
        """
        Get group information using WMI Win32_Group class.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing group details including Name, Domain, LocalAccount, and SID.
        """
        command = "Get-WmiObject -Class Win32_Group | Select-Object Name, Domain, LocalAccount, SID | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
