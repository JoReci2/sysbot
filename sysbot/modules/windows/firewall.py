"""
Windows Firewall Module

This module provides methods for managing and querying Windows Firewall settings,
including profiles, rules, and security configurations using PowerShell cmdlets.
"""
from sysbot.utils.engine import ComponentBase
import json
from typing import Dict, List


class Firewall(ComponentBase):
    @staticmethod
    def _validate_profile_name(profile: str) -> str:
        valid_profiles = ["Domain", "Private", "Public"]
        if profile not in valid_profiles:
            raise ValueError(
                f"Invalid profile name: {profile}. Must be one of {valid_profiles}"
            )
        return profile

    def getProfiles(self, alias: str, **kwargs) -> List[Dict]:
        command = "Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getProfile(self, alias: str, profile: str, **kwargs) -> Dict:
        validated_profile = self._validate_profile_name(profile)
        command = f"Get-NetFirewallProfile -Name {validated_profile} | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction, LogAllowed, LogBlocked, LogFileName, LogMaxSizeKilobytes | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getRules(self, alias: str, **kwargs) -> List[Dict]:
        command = "Get-NetFirewallRule | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getRule(self, alias: str, name: str, **kwargs) -> Dict:
        command = f"Get-NetFirewallRule -Name '{name}' | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile, Description | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getRulesByDisplayName(
        self, alias: str, display_name: str, **kwargs
    ) -> List[Dict]:
        command = f"Get-NetFirewallRule -DisplayName '{display_name}' | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getEnabledRules(self, alias: str, **kwargs) -> List[Dict]:
        command = "Get-NetFirewallRule -Enabled True | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getInboundRules(self, alias: str, **kwargs) -> List[Dict]:
        command = "Get-NetFirewallRule -Direction Inbound | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getOutboundRules(self, alias: str, **kwargs) -> List[Dict]:
        command = "Get-NetFirewallRule -Direction Outbound | Select-Object Name, DisplayName, Enabled, Direction, Action, Profile | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getPortFilters(self, alias: str, **kwargs) -> List[Dict]:
        command = "Get-NetFirewallPortFilter | Select-Object Protocol, LocalPort, RemotePort | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def getAddressFilters(self, alias: str, **kwargs) -> List[Dict]:
        command = "Get-NetFirewallAddressFilter | Select-Object LocalAddress, RemoteAddress | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
