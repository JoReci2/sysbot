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
    def addr(self, alias: str, **kwargs) -> dict:
        command = Windows.get_cim_class(
            namespace=r"root\cimv2",
            classname="Win32_NetworkAdapterConfiguration",
            property="DHCPEnabled, IPAddress, IPSubnet, DefaultIPGateway, DNSServerSearchOrder, ServiceName, Index, MTU",
        )
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def link(self, alias: str, **kwargs) -> dict:
        command = Windows.get_cim_class(
            namespace="root/StandardCimv2",
            classname="MSFT_NetAdapter",
            property="Name, Status, LinkSpeed, PhysicalMediaType, MacAddress",
        )
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def route(self, alias: str, **kwargs) -> dict:
        command = Windows.get_cim_class(
            namespace="root/StandardCimv2",
            classname="MSFT_NetRoute",
            property="InterfaceAlias, NextHop, State, DestinationPrefix",
        )
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def resolve(self, alias: str, fqdn: str, **kwargs) -> dict:
        command = f"(Resolve-DnsName {fqdn}).IPAddress | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def ping(self, alias: str, host: str, **kwargs) -> dict:
        command = f"Test-Connection -ComputerName {host} -Count 1 -Quiet"
        return self.execute_command(alias, command, **kwargs)
