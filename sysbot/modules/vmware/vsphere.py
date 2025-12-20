from sysbot.utils.engine import ComponentBase
import json


class Vsphere(ComponentBase):
    """
    VMware vSphere module for managing virtual machines, hosts, and datastores.
    Requires a session opened with protocol="http", product="vsphere".
    """

    def list_vms(self, alias: str, **kwargs) -> list:
        """
        List all virtual machines in vCenter.

        Args:
            alias (str): Session alias.

        Returns:
            list: List of VM objects with basic information.
        """
        output = self.execute_command(
            alias, "/rest/vcenter/vm", options={"method": "GET"}, **kwargs
        )
        result = json.loads(output)
        return result.get("value", [])

    def get_vm(self, alias: str, vm_id: str, **kwargs) -> dict:
        """
        Get detailed information about a specific virtual machine.

        Args:
            alias (str): Session alias.
            vm_id (str): Virtual machine identifier.

        Returns:
            dict: VM detailed information.
        """
        output = self.execute_command(
            alias, f"/rest/vcenter/vm/{vm_id}", options={"method": "GET"}, **kwargs
        )
        result = json.loads(output)
        return result.get("value", {})

    def get_vm_power_state(self, alias: str, vm_id: str, **kwargs) -> str:
        """
        Get the power state of a virtual machine.

        Args:
            alias (str): Session alias.
            vm_id (str): Virtual machine identifier.

        Returns:
            str: Power state (POWERED_ON, POWERED_OFF, SUSPENDED).
        """
        output = self.execute_command(
            alias,
            f"/rest/vcenter/vm/{vm_id}/power",
            options={"method": "GET"},
            **kwargs,
        )
        result = json.loads(output)
        return result.get("value", {}).get("state", "")

    def power_on_vm(self, alias: str, vm_id: str, **kwargs) -> dict:
        """
        Power on a virtual machine.

        Args:
            alias (str): Session alias.
            vm_id (str): Virtual machine identifier.

        Returns:
            dict: Operation result.
        """
        output = self.execute_command(
            alias,
            f"/rest/vcenter/vm/{vm_id}/power/start",
            options={"method": "POST"},
            **kwargs,
        )
        if output:
            return json.loads(output)
        return {}

    def power_off_vm(self, alias: str, vm_id: str, **kwargs) -> dict:
        """
        Power off a virtual machine.

        Args:
            alias (str): Session alias.
            vm_id (str): Virtual machine identifier.

        Returns:
            dict: Operation result.
        """
        output = self.execute_command(
            alias,
            f"/rest/vcenter/vm/{vm_id}/power/stop",
            options={"method": "POST"},
            **kwargs,
        )
        if output:
            return json.loads(output)
        return {}

    def reset_vm(self, alias: str, vm_id: str, **kwargs) -> dict:
        """
        Reset a virtual machine.

        Args:
            alias (str): Session alias.
            vm_id (str): Virtual machine identifier.

        Returns:
            dict: Operation result.
        """
        output = self.execute_command(
            alias,
            f"/rest/vcenter/vm/{vm_id}/power/reset",
            options={"method": "POST"},
            **kwargs,
        )
        if output:
            return json.loads(output)
        return {}

    def suspend_vm(self, alias: str, vm_id: str, **kwargs) -> dict:
        """
        Suspend a virtual machine.

        Args:
            alias (str): Session alias.
            vm_id (str): Virtual machine identifier.

        Returns:
            dict: Operation result.
        """
        output = self.execute_command(
            alias,
            f"/rest/vcenter/vm/{vm_id}/power/suspend",
            options={"method": "POST"},
            **kwargs,
        )
        if output:
            return json.loads(output)
        return {}

    def list_hosts(self, alias: str, **kwargs) -> list:
        """
        List all ESXi hosts in vCenter.

        Args:
            alias (str): Session alias.

        Returns:
            list: List of host objects.
        """
        output = self.execute_command(
            alias, "/rest/vcenter/host", options={"method": "GET"}, **kwargs
        )
        result = json.loads(output)
        return result.get("value", [])

    def get_host(self, alias: str, host_id: str, **kwargs) -> dict:
        """
        Get detailed information about a specific host.

        Args:
            alias (str): Session alias.
            host_id (str): Host identifier.

        Returns:
            dict: Host detailed information.
        """
        output = self.execute_command(
            alias, f"/rest/vcenter/host/{host_id}", options={"method": "GET"}, **kwargs
        )
        result = json.loads(output)
        return result.get("value", {})

    def list_datastores(self, alias: str, **kwargs) -> list:
        """
        List all datastores in vCenter.

        Args:
            alias (str): Session alias.

        Returns:
            list: List of datastore objects.
        """
        output = self.execute_command(
            alias, "/rest/vcenter/datastore", options={"method": "GET"}, **kwargs
        )
        result = json.loads(output)
        return result.get("value", [])

    def get_datastore(self, alias: str, datastore_id: str, **kwargs) -> dict:
        """
        Get detailed information about a specific datastore.

        Args:
            alias (str): Session alias.
            datastore_id (str): Datastore identifier.

        Returns:
            dict: Datastore detailed information.
        """
        output = self.execute_command(
            alias,
            f"/rest/vcenter/datastore/{datastore_id}",
            options={"method": "GET"},
            **kwargs,
        )
        result = json.loads(output)
        return result.get("value", {})

    def list_clusters(self, alias: str, **kwargs) -> list:
        """
        List all clusters in vCenter.

        Args:
            alias (str): Session alias.

        Returns:
            list: List of cluster objects.
        """
        output = self.execute_command(
            alias, "/rest/vcenter/cluster", options={"method": "GET"}, **kwargs
        )
        result = json.loads(output)
        return result.get("value", [])

    def get_cluster(self, alias: str, cluster_id: str, **kwargs) -> dict:
        """
        Get detailed information about a specific cluster.

        Args:
            alias (str): Session alias.
            cluster_id (str): Cluster identifier.

        Returns:
            dict: Cluster detailed information.
        """
        output = self.execute_command(
            alias,
            f"/rest/vcenter/cluster/{cluster_id}",
            options={"method": "GET"},
            **kwargs,
        )
        result = json.loads(output)
        return result.get("value", {})

    def list_networks(self, alias: str, **kwargs) -> list:
        """
        List all networks in vCenter.

        Args:
            alias (str): Session alias.

        Returns:
            list: List of network objects.
        """
        output = self.execute_command(
            alias, "/rest/vcenter/network", options={"method": "GET"}, **kwargs
        )
        result = json.loads(output)
        return result.get("value", [])

    def get_network(self, alias: str, network_id: str, **kwargs) -> dict:
        """
        Get detailed information about a specific network.

        Args:
            alias (str): Session alias.
            network_id (str): Network identifier.

        Returns:
            dict: Network detailed information.
        """
        output = self.execute_command(
            alias,
            f"/rest/vcenter/network/{network_id}",
            options={"method": "GET"},
            **kwargs,
        )
        result = json.loads(output)
        return result.get("value", {})

    def list_datacenters(self, alias: str, **kwargs) -> list:
        """
        List all datacenters in vCenter.

        Args:
            alias (str): Session alias.

        Returns:
            list: List of datacenter objects.
        """
        output = self.execute_command(
            alias, "/rest/vcenter/datacenter", options={"method": "GET"}, **kwargs
        )
        result = json.loads(output)
        return result.get("value", [])

    def get_datacenter(self, alias: str, datacenter_id: str, **kwargs) -> dict:
        """
        Get detailed information about a specific datacenter.

        Args:
            alias (str): Session alias.
            datacenter_id (str): Datacenter identifier.

        Returns:
            dict: Datacenter detailed information.
        """
        output = self.execute_command(
            alias,
            f"/rest/vcenter/datacenter/{datacenter_id}",
            options={"method": "GET"},
            **kwargs,
        )
        result = json.loads(output)
        return result.get("value", {})
