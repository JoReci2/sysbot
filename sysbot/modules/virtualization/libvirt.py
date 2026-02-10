"""
Libvirt Virtualization Module

This module provides methods for managing virtual machines using libvirt on
Linux systems, including domain management, storage pool operations, and
network configuration.
"""
from sysbot.utils.engine import ComponentBase
import shlex


class Libvirt(ComponentBase):
    """Libvirt virtualization management class for Linux systems."""

    def list(self, alias: str, **kwargs) -> list:
        """
        List all libvirt domains (virtual machines).

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of domain names.
        """
        output = self.execute_command(alias, "virsh list --all --name", **kwargs)
        domains = [line.strip() for line in output.strip().split("\n") if line.strip()]
        return domains

    def dominfo(self, alias: str, domain: str, **kwargs) -> dict:
        """
        Get detailed information about a domain.

        Args:
            alias: Session alias for the connection.
            domain: Domain name or UUID.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing domain information.
        """
        output = self.execute_command(
            alias, f"virsh dominfo {shlex.quote(domain)}", **kwargs
        )
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def domstate(self, alias: str, domain: str, **kwargs) -> str:
        """
        Get the state of a domain.

        Args:
            alias: Session alias for the connection.
            domain: Domain name or UUID.
            **kwargs: Additional command execution options.

        Returns:
            Domain state (running, shut off, paused, etc.).
        """
        output = self.execute_command(
            alias, f"virsh domstate {shlex.quote(domain)}", **kwargs
        )
        return output.strip()

    def pool_list(self, alias: str, **kwargs) -> list:
        """
        List all storage pools.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of storage pool names.
        """
        output = self.execute_command(alias, "virsh pool-list --all --name", **kwargs)
        pools = [line.strip() for line in output.strip().split("\n") if line.strip()]
        return pools

    def pool_info(self, alias: str, pool: str, **kwargs) -> dict:
        """
        Get detailed information about a storage pool.

        Args:
            alias: Session alias for the connection.
            pool: Storage pool name.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing storage pool information.
        """
        output = self.execute_command(
            alias, f"virsh pool-info {shlex.quote(pool)}", **kwargs
        )
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def net_list(self, alias: str, **kwargs) -> list:
        """
        List all virtual networks.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of virtual network names.
        """
        output = self.execute_command(alias, "virsh net-list --all --name", **kwargs)
        networks = [
            line.strip() for line in output.strip().split("\n") if line.strip()
        ]
        return networks

    def net_info(self, alias: str, network: str, **kwargs) -> dict:
        """
        Get detailed information about a virtual network.

        Args:
            alias: Session alias for the connection.
            network: Virtual network name.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing virtual network information.
        """
        output = self.execute_command(
            alias, f"virsh net-info {shlex.quote(network)}", **kwargs
        )
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def version(self, alias: str, **kwargs) -> dict:
        """
        Get libvirt and hypervisor version information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing version information.
        """
        output = self.execute_command(alias, "virsh version", **kwargs)
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def nodeinfo(self, alias: str, **kwargs) -> dict:
        """
        Get information about the virtualization host node.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing node information (CPU, memory, etc.).
        """
        output = self.execute_command(alias, "virsh nodeinfo", **kwargs)
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info
