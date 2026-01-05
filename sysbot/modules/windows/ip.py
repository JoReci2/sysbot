"""
Windows Network Interface Module

This module provides methods for managing and querying network interfaces,
IP addresses, routes, and network configuration on Windows systems using
CIM/WMI classes.
"""
from sysbot.utils.engine import ComponentBase
from sysbot.utils.helper import Windows
import json


class Ip(ComponentBase):
    """Windows network interface management class using CIM/WMI."""

    def addr(self, alias: str, **kwargs) -> dict:
        """
        Get network adapter IP configuration.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing network adapter configuration including DHCPEnabled,
            IPAddress, IPSubnet, DefaultIPGateway, DNSServerSearchOrder, ServiceName, Index, and MTU.
        """
        command = Windows.get_cim_class(
            namespace=r"root\cimv2",
            classname="Win32_NetworkAdapterConfiguration",
            property="DHCPEnabled, IPAddress, IPSubnet, DefaultIPGateway, DNSServerSearchOrder, ServiceName, Index, MTU",
        )
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def link(self, alias: str, **kwargs) -> dict:
        """
        Get network adapter link layer information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing network adapter information including Name, Status,
            LinkSpeed, PhysicalMediaType, and MacAddress.
        """
        command = Windows.get_cim_class(
            namespace="root/StandardCimv2",
            classname="MSFT_NetAdapter",
            property="Name, Status, LinkSpeed, PhysicalMediaType, MacAddress",
        )
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def route(self, alias: str, **kwargs) -> dict:
        """
        Get network routing table.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing routing information including InterfaceAlias, NextHop,
            State, and DestinationPrefix.
        """
        command = Windows.get_cim_class(
            namespace="root/StandardCimv2",
            classname="MSFT_NetRoute",
            property="InterfaceAlias, NextHop, State, DestinationPrefix",
        )
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def resolve(self, alias: str, fqdn: str, **kwargs) -> dict:
        """
        Resolve a fully qualified domain name to IP address(es).

        Args:
            alias: Session alias for the connection.
            fqdn: Fully qualified domain name to resolve.
            **kwargs: Additional command execution options.

        Returns:
            JSON-parsed result containing the resolved IP address(es) as a list or single value.
        """
        command = f"(Resolve-DnsName {fqdn}).IPAddress | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def ping(self, alias: str, host: str, **kwargs) -> dict:
        """
        Test network connectivity to a host using Test-Connection.

        Args:
            alias: Session alias for the connection.
            host: Hostname or IP address to ping.
            **kwargs: Additional command execution options.

        Returns:
            String result from PowerShell ('True' or 'False') indicating connectivity status.
        """
        command = f"Test-Connection -ComputerName {host} -Count 1 -Quiet"
        return self.execute_command(alias, command, **kwargs)
