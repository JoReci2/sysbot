"""
Linux Network Interface Module

This module provides methods for managing and querying network interfaces,
IP addresses, routes, and network connectivity on Linux systems using the
iproute2 (ip) command suite.
"""
from sysbot.utils.engine import ComponentBase
import json


class Ip(ComponentBase):
    """Network interface and routing management class for Linux systems."""

    def addr(self, alias: str, interface: str, **kwargs) -> dict:
        """
        Get IP address information for a network interface.

        Args:
            alias: Session alias for the connection.
            interface: Network interface name (e.g., eth0, ens33).
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing IP address configuration in JSON format.
        """
        output = self.execute_command(
            alias, f"ip --json addr show {interface}", **kwargs
        )
        return json.loads(output)

    def route(self, alias: str, **kwargs) -> dict:
        """
        Get routing table information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing routing table in JSON format.
        """
        output = self.execute_command(alias, "ip --json route", **kwargs)
        return json.loads(output)

    def speed(self, alias: str, interface: str, **kwargs) -> str:
        """
        Get the link speed of a network interface.

        Args:
            alias: Session alias for the connection.
            interface: Network interface name (e.g., eth0, ens33).
            **kwargs: Additional command execution options.

        Returns:
            Link speed in Mbps as a string.
        """
        return self.execute_command(
            alias, f"cat /sys/class/net/{interface}/speed", **kwargs
        )

    def link(self, alias: str, interface: str, **kwargs) -> dict:
        """
        Get link layer information for a network interface.

        Args:
            alias: Session alias for the connection.
            interface: Network interface name (e.g., eth0, ens33).
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing link layer information in JSON format.
        """
        output = self.execute_command(
            alias, f"ip --json link show {interface}", **kwargs
        )
        return json.loads(output)

    def resolve(self, alias: str, fqdn: str, **kwargs) -> dict:
        """
        Resolve a fully qualified domain name to an IP address.

        Args:
            alias: Session alias for the connection.
            fqdn: Fully qualified domain name to resolve.
            **kwargs: Additional command execution options.

        Returns:
            Resolved IP address as a string.
        """
        return self.execute_command(
            alias, f"getent hosts {fqdn} | awk '{{print $1}}'", **kwargs
        )

    def ping(self, alias: str, host: str, **kwargs) -> bool:
        """
        Test network connectivity to a host using ping.

        Args:
            alias: Session alias for the connection.
            host: Hostname or IP address to ping.
            **kwargs: Additional command execution options.

        Returns:
            True if host is reachable, False otherwise.
        """
        return (
            self.execute_command(
                alias, f"ping -W 1 -c 1 {host} > /dev/null 2>&1 ; echo $?", **kwargs
            )
            == "0"
        )
