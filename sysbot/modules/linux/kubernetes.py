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
    def version(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "kubectl version --output=json", **kwargs)
        return json.loads(output)

    def cluster_info(self, alias: str, **kwargs) -> str:
        output = self.execute_command(alias, "kubectl cluster-info", **kwargs)
        return output

    def get_nodes(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, "kubectl get nodes -o json", **kwargs
        )
        return json.loads(output)

    def get_node(self, alias: str, name: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get node {shlex.quote(name)} -o json", **kwargs
        )
        return json.loads(output)

    def get_pods(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get pods -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_pod(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get pod {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_services(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get services -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_service(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get service {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_deployments(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get deployments -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_deployment(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get deployment {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_namespaces(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, "kubectl get namespaces -o json", **kwargs
        )
        return json.loads(output)

    def get_namespace(self, alias: str, name: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get namespace {shlex.quote(name)} -o json", **kwargs
        )
        return json.loads(output)

    def get_configmaps(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get configmaps -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_configmap(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get configmap {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_secrets(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get secrets -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_secret(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get secret {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)
