from sysbot.utils.engine import ComponentBase


class Libvirt(ComponentBase):
    def list(self, alias: str, **kwargs) -> list:
        """List all domains (VMs) with their basic information.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments passed to execute_command

        Returns:
            List of domain dictionaries with UUID, name, and state
        """
        output = self.execute_command(alias, "virsh list --all --name", **kwargs)
        domains = [line.strip() for line in output.strip().split("\n") if line.strip()]
        return domains

    def dominfo(self, alias: str, domain: str, **kwargs) -> dict:
        """Get detailed information about a specific domain.

        Args:
            alias: Connection alias
            domain: Domain name or UUID
            **kwargs: Additional arguments passed to execute_command

        Returns:
            Dictionary containing domain information
        """
        output = self.execute_command(alias, f"virsh dominfo {domain}", **kwargs)
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def domstate(self, alias: str, domain: str, **kwargs) -> str:
        """Get the state of a domain.

        Args:
            alias: Connection alias
            domain: Domain name or UUID
            **kwargs: Additional arguments passed to execute_command

        Returns:
            Domain state as string
        """
        output = self.execute_command(alias, f"virsh domstate {domain}", **kwargs)
        return output.strip()

    def pool_list(self, alias: str, **kwargs) -> list:
        """List all storage pools.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments passed to execute_command

        Returns:
            List of storage pool names
        """
        output = self.execute_command(alias, "virsh pool-list --all --name", **kwargs)
        pools = [line.strip() for line in output.strip().split("\n") if line.strip()]
        return pools

    def pool_info(self, alias: str, pool: str, **kwargs) -> dict:
        """Get information about a specific storage pool.

        Args:
            alias: Connection alias
            pool: Pool name
            **kwargs: Additional arguments passed to execute_command

        Returns:
            Dictionary containing pool information
        """
        output = self.execute_command(alias, f"virsh pool-info {pool}", **kwargs)
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def net_list(self, alias: str, **kwargs) -> list:
        """List all virtual networks.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments passed to execute_command

        Returns:
            List of network names
        """
        output = self.execute_command(alias, "virsh net-list --all --name", **kwargs)
        networks = [
            line.strip() for line in output.strip().split("\n") if line.strip()
        ]
        return networks

    def net_info(self, alias: str, network: str, **kwargs) -> dict:
        """Get information about a specific virtual network.

        Args:
            alias: Connection alias
            network: Network name
            **kwargs: Additional arguments passed to execute_command

        Returns:
            Dictionary containing network information
        """
        output = self.execute_command(alias, f"virsh net-info {network}", **kwargs)
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def version(self, alias: str, **kwargs) -> dict:
        """Get libvirt and hypervisor version information.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments passed to execute_command

        Returns:
            Dictionary containing version information
        """
        output = self.execute_command(alias, "virsh version", **kwargs)
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info

    def nodeinfo(self, alias: str, **kwargs) -> dict:
        """Get information about the hypervisor node.

        Args:
            alias: Connection alias
            **kwargs: Additional arguments passed to execute_command

        Returns:
            Dictionary containing node information
        """
        output = self.execute_command(alias, "virsh nodeinfo", **kwargs)
        info = {}
        for line in output.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                info[key.strip()] = value.strip()
        return info
