from sysbot.utils.engine import ComponentBase
import json
from typing import Dict, List


class Firewall(ComponentBase):
    @staticmethod
    def _escape_powershell_string(value: str) -> str:
        """Escape special characters in PowerShell strings to prevent injection.

        Args:
            value: String to escape

        Returns:
            Escaped string safe for PowerShell
        """
        # Escape single quotes by doubling them (PowerShell convention)
        return value.replace("'", "''")

    @staticmethod
    def _validate_profile_name(profile: str) -> str:
        """Validate and sanitize firewall profile name.

        Args:
            profile: Profile name to validate

        Returns:
            Validated profile name

        Raises:
            ValueError: If profile name is invalid
        """
        valid_profiles = ["Domain", "Private", "Public"]
        if profile not in valid_profiles:
            raise ValueError(
                f"Invalid profile name: {profile}. Must be one of {valid_profiles}"
            )
        return profile

    def getProfiles(self, alias: str, **kwargs) -> List[Dict]:
        """Get all firewall profiles (Domain, Private, Public).

        Args:
            alias: Connection alias
            **kwargs: Additional arguments for execute_command

        Returns:
            List of dictionaries containing firewall profile information
        """
        command = "Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getProfile(self, alias: str, profile: str, **kwargs) -> Dict:
        """Get specific firewall profile information.

        Args:
            alias: Connection alias
            profile: Profile name (Domain, Private, or Public)
            **kwargs: Additional arguments for execute_command

        Returns:
            Dictionary containing specific profile information

        Raises:
            ValueError: If profile name is invalid
        """
        validated_profile = self._validate_profile_name(profile)
        command = f"Get-NetFirewallProfile -Name {validated_profile} | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction, LogAllowed, LogBlocked, LogFileName, LogMaxSizeKilobytes | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getRules(self, alias: str, **kwargs) -> List[Dict]:
        """Get all firewall rules.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments for execute_command

        Returns:
            List of dictionaries containing firewall rules
        """
        command = "Get-NetFirewallRule | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getRule(self, alias: str, name: str, **kwargs) -> Dict:
        """Get specific firewall rule by name.

        Args:
            alias: Connection alias
            name: Rule name
            **kwargs: Additional arguments for execute_command

        Returns:
            Dictionary containing rule information
        """
        escaped_name = self._escape_powershell_string(name)
        command = f"Get-NetFirewallRule -Name '{escaped_name}' | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile, Description | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getRulesByDisplayName(
        self, alias: str, display_name: str, **kwargs
    ) -> List[Dict]:
        """Get firewall rules by display name.

        Args:
            alias: Connection alias
            display_name: Display name pattern
            **kwargs: Additional arguments for execute_command

        Returns:
            List of dictionaries containing matching rules
        """
        escaped_display_name = self._escape_powershell_string(display_name)
        command = f"Get-NetFirewallRule -DisplayName '{escaped_display_name}' | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getEnabledRules(self, alias: str, **kwargs) -> List[Dict]:
        """Get all enabled firewall rules.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments for execute_command

        Returns:
            List of dictionaries containing enabled rules
        """
        command = "Get-NetFirewallRule -Enabled True | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getInboundRules(self, alias: str, **kwargs) -> List[Dict]:
        """Get all inbound firewall rules.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments for execute_command

        Returns:
            List of dictionaries containing inbound rules
        """
        command = "Get-NetFirewallRule -Direction Inbound | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getOutboundRules(self, alias: str, **kwargs) -> List[Dict]:
        """Get all outbound firewall rules.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments for execute_command

        Returns:
            List of dictionaries containing outbound rules
        """
        command = "Get-NetFirewallRule -Direction Outbound | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getPortFilters(self, alias: str, **kwargs) -> List[Dict]:
        """Get firewall port filters.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments for execute_command

        Returns:
            List of dictionaries containing port filter information
        """
        command = "Get-NetFirewallPortFilter | Select-Object Protocol, LocalPort, RemotePort | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getAddressFilters(self, alias: str, **kwargs) -> List[Dict]:
        """Get firewall address filters.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments for execute_command

        Returns:
            List of dictionaries containing address filter information
        """
        command = "Get-NetFirewallAddressFilter | Select-Object LocalAddress, RemoteAddress | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
