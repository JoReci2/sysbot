"""
Harvester Module

This module provides methods for interacting with Rancher Harvester HCI (Hyper-Converged Infrastructure)
via REST API. It supports operations such as virtual machine management, image management,
volume management, and cluster information retrieval.

Note: This module uses the HTTP connector with API Key or Basic authentication.
Sessions should be opened with protocol="http" and product="apikey" or "basicauth".
"""

import json
from sysbot.utils.engine import ComponentBase


class Harvester(ComponentBase):
    """
    Harvester module for hyper-converged infrastructure management.
    
    This class provides methods to interact with Rancher Harvester systems using REST API
    via the HTTP connector with API Key or Basic authentication.
    All methods require an alias to identify the established HTTP session.
    """

    def get_version(self, alias: str, **kwargs) -> dict:
        """
        Get Harvester version information.

        Args:
            alias (str): The session alias for the Harvester connection.

        Returns:
            dict: Version information.
        """
        response = self.execute_command(alias, "/v1/harvesterhci.io.settings/server-version", options={"method": "GET"}, **kwargs)
        return json.loads(response.decode())

    def list_virtual_machines(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        List all virtual machines in a namespace.

        Args:
            alias (str): The session alias for the Harvester connection.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: List of virtual machines.
        """
        response = self.execute_command(
            alias,
            f"/apis/kubevirt.io/v1/namespaces/{namespace}/virtualmachines",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_virtual_machine(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get details of a specific virtual machine.

        Args:
            alias (str): The session alias for the Harvester connection.
            name (str): Virtual machine name.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: Virtual machine details.
        """
        response = self.execute_command(
            alias,
            f"/apis/kubevirt.io/v1/namespaces/{namespace}/virtualmachines/{name}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def list_vm_instances(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        List all virtual machine instances in a namespace.

        Args:
            alias (str): The session alias for the Harvester connection.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: List of virtual machine instances.
        """
        response = self.execute_command(
            alias,
            f"/apis/kubevirt.io/v1/namespaces/{namespace}/virtualmachineinstances",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_vm_instance(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get details of a specific virtual machine instance.

        Args:
            alias (str): The session alias for the Harvester connection.
            name (str): Virtual machine instance name.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: Virtual machine instance details.
        """
        response = self.execute_command(
            alias,
            f"/apis/kubevirt.io/v1/namespaces/{namespace}/virtualmachineinstances/{name}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def list_images(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        List all VM images in a namespace.

        Args:
            alias (str): The session alias for the Harvester connection.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: List of VM images.
        """
        response = self.execute_command(
            alias,
            f"/apis/harvesterhci.io/v1beta1/namespaces/{namespace}/virtualmachineimages",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_image(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get details of a specific VM image.

        Args:
            alias (str): The session alias for the Harvester connection.
            name (str): Image name.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: Image details.
        """
        response = self.execute_command(
            alias,
            f"/apis/harvesterhci.io/v1beta1/namespaces/{namespace}/virtualmachineimages/{name}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def list_volumes(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        List all persistent volumes in a namespace.

        Args:
            alias (str): The session alias for the Harvester connection.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: List of persistent volumes.
        """
        response = self.execute_command(
            alias,
            f"/api/v1/namespaces/{namespace}/persistentvolumeclaims",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_volume(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get details of a specific persistent volume.

        Args:
            alias (str): The session alias for the Harvester connection.
            name (str): Volume name.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: Volume details.
        """
        response = self.execute_command(
            alias,
            f"/api/v1/namespaces/{namespace}/persistentvolumeclaims/{name}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def list_networks(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        List all networks in a namespace.

        Args:
            alias (str): The session alias for the Harvester connection.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: List of networks.
        """
        response = self.execute_command(
            alias,
            f"/apis/k8s.cni.cncf.io/v1/namespaces/{namespace}/network-attachment-definitions",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_network(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get details of a specific network.

        Args:
            alias (str): The session alias for the Harvester connection.
            name (str): Network name.
            namespace (str): Kubernetes namespace (default: "default").

        Returns:
            dict: Network details.
        """
        response = self.execute_command(
            alias,
            f"/apis/k8s.cni.cncf.io/v1/namespaces/{namespace}/network-attachment-definitions/{name}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def list_nodes(self, alias: str, **kwargs) -> dict:
        """
        List all cluster nodes.

        Args:
            alias (str): The session alias for the Harvester connection.

        Returns:
            dict: List of cluster nodes.
        """
        response = self.execute_command(
            alias,
            "/api/v1/nodes",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_node(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get details of a specific cluster node.

        Args:
            alias (str): The session alias for the Harvester connection.
            name (str): Node name.

        Returns:
            dict: Node details.
        """
        response = self.execute_command(
            alias,
            f"/api/v1/nodes/{name}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def list_namespaces(self, alias: str, **kwargs) -> dict:
        """
        List all namespaces in the cluster.

        Args:
            alias (str): The session alias for the Harvester connection.

        Returns:
            dict: List of namespaces.
        """
        response = self.execute_command(
            alias,
            "/api/v1/namespaces",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_cluster_info(self, alias: str, **kwargs) -> dict:
        """
        Get cluster information.

        Args:
            alias (str): The session alias for the Harvester connection.

        Returns:
            dict: Cluster information.
        """
        response = self.execute_command(
            alias,
            "/api/v1",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def list_settings(self, alias: str, **kwargs) -> dict:
        """
        List all Harvester settings.

        Args:
            alias (str): The session alias for the Harvester connection.

        Returns:
            dict: List of Harvester settings.
        """
        response = self.execute_command(
            alias,
            "/v1/harvesterhci.io.settings",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())

    def get_setting(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get a specific Harvester setting.

        Args:
            alias (str): The session alias for the Harvester connection.
            name (str): Setting name.

        Returns:
            dict: Setting details.
        """
        response = self.execute_command(
            alias,
            f"/v1/harvesterhci.io.settings/{name}",
            options={"method": "GET"},
            **kwargs
        )
        return json.loads(response.decode())
