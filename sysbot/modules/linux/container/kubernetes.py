"""
Kubernetes Module

This module provides methods for interacting with Kubernetes clusters using
kubectl, including cluster information, node management, pod operations, and
resource queries.
"""
from sysbot.utils.engine import ComponentBase
import json
import shlex


class Kubernetes(ComponentBase):
    """Kubernetes cluster management class using kubectl."""

    def version(self, alias: str, **kwargs) -> dict:
        """
        Get Kubernetes client and server version information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing version information in JSON format.
        """
        output = self.execute_command(alias, "kubectl version --output=json", **kwargs)
        return json.loads(output)

    def cluster_info(self, alias: str, **kwargs) -> str:
        """
        Get cluster information including control plane and services.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Cluster information as a string.
        """
        output = self.execute_command(alias, "kubectl cluster-info", **kwargs)
        return output

    def get_nodes(self, alias: str, **kwargs) -> dict:
        """
        Get all nodes in the cluster.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all nodes in JSON format.
        """
        output = self.execute_command(
            alias, "kubectl get nodes -o json", **kwargs
        )
        return json.loads(output)

    def get_node(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get a specific node by name.

        Args:
            alias: Session alias for the connection.
            name: Node name.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing node information in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get node {shlex.quote(name)} -o json", **kwargs
        )
        return json.loads(output)

    def get_pods(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get all pods in a namespace.

        Args:
            alias: Session alias for the connection.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all pods in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get pods -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_pod(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get a specific pod by name.

        Args:
            alias: Session alias for the connection.
            name: Pod name.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing pod information in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get pod {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_services(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get all services in a namespace.

        Args:
            alias: Session alias for the connection.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all services in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get services -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_service(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get a specific service by name.

        Args:
            alias: Session alias for the connection.
            name: Service name.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing service information in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get service {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_deployments(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get all deployments in a namespace.

        Args:
            alias: Session alias for the connection.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all deployments in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get deployments -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_deployment(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get a specific deployment by name.

        Args:
            alias: Session alias for the connection.
            name: Deployment name.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing deployment information in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get deployment {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_namespaces(self, alias: str, **kwargs) -> dict:
        """
        Get all namespaces in the cluster.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all namespaces in JSON format.
        """
        output = self.execute_command(
            alias, "kubectl get namespaces -o json", **kwargs
        )
        return json.loads(output)

    def get_namespace(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get a specific namespace by name.

        Args:
            alias: Session alias for the connection.
            name: Namespace name.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing namespace information in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get namespace {shlex.quote(name)} -o json", **kwargs
        )
        return json.loads(output)

    def get_configmaps(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get all ConfigMaps in a namespace.

        Args:
            alias: Session alias for the connection.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all ConfigMaps in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get configmaps -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_configmap(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get a specific ConfigMap by name.

        Args:
            alias: Session alias for the connection.
            name: ConfigMap name.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing ConfigMap information in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get configmap {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_secrets(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get all Secrets in a namespace.

        Args:
            alias: Session alias for the connection.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing all Secrets in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get secrets -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_secret(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        """
        Get a specific Secret by name.

        Args:
            alias: Session alias for the connection.
            name: Secret name.
            namespace: Kubernetes namespace (default: "default").
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing Secret information in JSON format.
        """
        output = self.execute_command(
            alias, f"kubectl get secret {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)
