from sysbot.utils.engine import ComponentBase
import json
from typing import Dict, List


class Firewall(ComponentBase):
    def getProfiles(self, alias: str, **kwargs) -> Dict:
        """Get all firewall profiles (Domain, Private, Public).

        Args:
            alias: Connection alias
            **kwargs: Additional arguments for execute_command

        Returns:
            Dictionary containing firewall profile information
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
        """
        command = f"Get-NetFirewallProfile -Name {profile} | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction, LogAllowed, LogBlocked, LogFileName, LogMaxSizeKilobytes | ConvertTo-Json"
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
        command = f"Get-NetFirewallRule -Name '{name}' | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile, Description | ConvertTo-Json"
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
        command = f"Get-NetFirewallRule -DisplayName '{display_name}' | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
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
        command = "Get-NetFirewallRule -Enabled True | Select-Object Name, DisplayName, Direction, Action, Profile | ConvertTo-Json"
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
        command = "Get-NetFirewallRule -Direction Inbound | Select-Object Name, DisplayName, Enabled, Action, Profile | ConvertTo-Json"
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
        command = "Get-NetFirewallRule -Direction Outbound | Select-Object Name, DisplayName, Enabled, Action, Profile | ConvertTo-Json"
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
