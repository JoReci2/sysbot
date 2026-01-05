"""
Windows Firewall Module

This module provides methods for managing and querying Windows Firewall settings,
including profiles, rules, and security configurations using PowerShell cmdlets.
"""
from sysbot.utils.engine import ComponentBase
import json
from typing import Dict, List


class Firewall(ComponentBase):
    """Windows Firewall management class using PowerShell NetFirewall cmdlets."""

    @staticmethod
    def _validate_profile_name(profile: str) -> str:
        valid_profiles = ["Domain", "Private", "Public"]
        if profile not in valid_profiles:
            raise ValueError(
                f"Invalid profile name: {profile}. Must be one of {valid_profiles}"
            )
        return profile

    def getProfiles(self, alias: str, **kwargs) -> List[Dict]:
        """
        Get all firewall profiles.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing profile information including Name, Enabled,
            DefaultInboundAction, and DefaultOutboundAction.
        """
        command = "Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getProfile(self, alias: str, profile: str, **kwargs) -> Dict:
        """
        Get a specific firewall profile by name.

        Args:
            alias: Session alias for the connection.
            profile: Profile name (Domain, Private, or Public).
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing profile details including Name, Enabled, DefaultInboundAction,
            DefaultOutboundAction, LogAllowed, LogBlocked, LogFileName, and LogMaxSizeKilobytes.
        """
        validated_profile = self._validate_profile_name(profile)
        command = f"Get-NetFirewallProfile -Name {validated_profile} | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction, LogAllowed, LogBlocked, LogFileName, LogMaxSizeKilobytes | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getRules(self, alias: str, **kwargs) -> List[Dict]:
        """
        Get all firewall rules.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing rule information including Name, DisplayName,
            Enabled, Direction, Action, and Profile.
        """
        command = "Get-NetFirewallRule | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getRule(self, alias: str, name: str, **kwargs) -> Dict:
        """
        Get a specific firewall rule by name.

        Args:
            alias: Session alias for the connection.
            name: Rule name.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing rule details including Name, DisplayName, Enabled,
            Direction, Action, Profile, and Description.
        """
        command = f"Get-NetFirewallRule -Name '{name}' | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile, Description | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getRulesByDisplayName(
        self, alias: str, display_name: str, **kwargs
    ) -> List[Dict]:
        """
        Get firewall rules by display name.

        Args:
            alias: Session alias for the connection.
            display_name: Display name to search for.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing matching rule information.
        """
        command = f"Get-NetFirewallRule -DisplayName '{display_name}' | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getEnabledRules(self, alias: str, **kwargs) -> List[Dict]:
        """
        Get all enabled firewall rules.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing enabled rule information.
        """
        command = "Get-NetFirewallRule -Enabled True | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getInboundRules(self, alias: str, **kwargs) -> List[Dict]:
        """
        Get all inbound firewall rules.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing inbound rule information.
        """
        command = "Get-NetFirewallRule -Direction Inbound | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getOutboundRules(self, alias: str, **kwargs) -> List[Dict]:
        """
        Get all outbound firewall rules.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing outbound rule information.
        """
        command = "Get-NetFirewallRule -Direction Outbound | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getPortFilters(self, alias: str, **kwargs) -> List[Dict]:
        """
        Get port filters for firewall rules.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing port filter information including Protocol,
            LocalPort, and RemotePort.
        """
        command = "Get-NetFirewallPortFilter | Select-Object Protocol, LocalPort, RemotePort | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getAddressFilters(self, alias: str, **kwargs) -> List[Dict]:
        """
        Get address filters for firewall rules.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing address filter information including
            LocalAddress and RemoteAddress.
        """
        command = "Get-NetFirewallAddressFilter | Select-Object LocalAddress, RemoteAddress | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
