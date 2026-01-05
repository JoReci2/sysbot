"""
Windows DNS Server Module

This module provides methods for managing and querying Windows DNS Server,
including zones, resource records, forwarders, and DNS server configuration
using PowerShell DNS Server cmdlets.
"""
from sysbot.utils.engine import ComponentBase
import json


class Dnsserver(ComponentBase):
    def get_server(self, alias: str, **kwargs) -> dict:
        """Get DNS server configuration."""
        command = "Get-DnsServer | ConvertTo-Json -Depth 3"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_zone(self, alias: str, zone_name: str, **kwargs) -> dict:
        """Get specific DNS zone by name."""
        command = f"Get-DnsServerZone -Name '{zone_name}' | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_zones(self, alias: str, **kwargs) -> list:
        """Get all DNS zones."""
        command = "Get-DnsServerZone | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_resource_records(self, alias: str, zone_name: str, **kwargs) -> list:
        """Get all DNS resource records from a zone."""
        command = f"Get-DnsServerResourceRecord -ZoneName '{zone_name}' | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_forwarder(self, alias: str, **kwargs) -> dict:
        """Get DNS server forwarders."""
        command = "Get-DnsServerForwarder | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_cache(self, alias: str, **kwargs) -> dict:
        """Get DNS server cache settings."""
        command = "Get-DnsServerCache | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_statistics(self, alias: str, **kwargs) -> dict:
        """Get DNS server statistics."""
        command = "Get-DnsServerStatistics | ConvertTo-Json -Depth 3"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_setting(self, alias: str, **kwargs) -> dict:
        """Get DNS server settings."""
        command = "Get-DnsServerSetting -All | ConvertTo-Json -Depth 3"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
