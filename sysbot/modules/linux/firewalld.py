"""
Firewalld Module

This module provides methods for managing and querying the firewalld firewall
service on RHEL/Fedora-based Linux systems, including zone management and
rule configuration.
"""
from sysbot.utils.engine import ComponentBase
from typing import Dict, List


class Firewalld(ComponentBase):
    """Firewalld firewall management class for RHEL/Fedora-based Linux systems."""

    def getZones(self, alias: str, **kwargs) -> List[str]:
        """
        Get list of all available firewalld zones.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of zone names.
        """
        output = self.execute_command(alias, "firewall-cmd --get-zones", **kwargs)
        return output.strip().split()

    def getActiveZones(self, alias: str, **kwargs) -> Dict[str, List[str]]:
        """
        Get active firewalld zones with their associated interfaces.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary mapping zone names to lists of network interfaces.
        """
        output = self.execute_command(
            alias, "firewall-cmd --get-active-zones", **kwargs
        )
        zones: Dict[str, List[str]] = {}
        current = None
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            if not line.startswith("interfaces:"):
                current = line
                zones[current] = []
            elif current and line.startswith("interfaces:"):
                ifaces = line.split("interfaces:", 1)[1].strip().split()
                zones[current].extend(ifaces)
        return zones

    def getDefaultZone(self, alias: str, **kwargs) -> str:
        """
        Get the default firewalld zone.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Name of the default zone.
        """
        output = self.execute_command(
            alias, "firewall-cmd --get-default-zone", **kwargs
        )
        return output.strip()

    def getForwardPorts(self, alias: str, zone: str, **kwargs) -> List[str]:
        """
        Get list of forward ports in a zone.

        Args:
            alias: Session alias for the connection.
            zone: Zone name to query.
            **kwargs: Additional command execution options.

        Returns:
            List of forward port rules.
        """
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-forward-ports", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getPorts(self, alias: str, zone: str, **kwargs) -> List[str]:
        """
        Get list of open ports in a zone.

        Args:
            alias: Session alias for the connection.
            zone: Zone name to query.
            **kwargs: Additional command execution options.

        Returns:
            List of open ports (e.g., ['80/tcp', '443/tcp']).
        """
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-ports", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getInterface(self, alias: str, zone: str, **kwargs) -> List[str]:
        """
        Get list of interfaces bound to a zone.

        Args:
            alias: Session alias for the connection.
            zone: Zone name to query.
            **kwargs: Additional command execution options.

        Returns:
            List of network interface names.
        """
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-interfaces", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getServices(self, alias: str, zone: str, **kwargs) -> List[str]:
        """
        Get list of services allowed in a zone.

        Args:
            alias: Session alias for the connection.
            zone: Zone name to query.
            **kwargs: Additional command execution options.

        Returns:
            List of service names (e.g., ['ssh', 'http', 'https']).
        """
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-services", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getProtocols(self, alias: str, zone: str, **kwargs) -> List[str]:
        """
        Get list of protocols allowed in a zone.

        Args:
            alias: Session alias for the connection.
            zone: Zone name to query.
            **kwargs: Additional command execution options.

        Returns:
            List of protocol names.
        """
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-protocols", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getSourcePorts(self, alias: str, zone: str, **kwargs) -> List[str]:
        """
        Get list of source ports in a zone.

        Args:
            alias: Session alias for the connection.
            zone: Zone name to query.
            **kwargs: Additional command execution options.

        Returns:
            List of source port rules.
        """
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-source-ports", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getSources(self, alias: str, zone: str, **kwargs) -> List[str]:
        """
        Get list of source addresses/networks in a zone.

        Args:
            alias: Session alias for the connection.
            zone: Zone name to query.
            **kwargs: Additional command execution options.

        Returns:
            List of source addresses or network ranges.
        """
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-sources", **kwargs
        )
        return output.strip().split() if output.strip() else []
