from sysbot.utils.engine import ComponentBase
import json
import shlex


class Kubedashboard(ComponentBase):
    def get_dashboard_deployment(self, alias: str, namespace: str = "kubernetes-dashboard", **kwargs) -> dict:
        """Get the Kubernetes Dashboard deployment information."""
        output = self.execute_command(
            alias, f"kubectl get deployment kubernetes-dashboard -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_dashboard_service(self, alias: str, namespace: str = "kubernetes-dashboard", **kwargs) -> dict:
        """Get the Kubernetes Dashboard service information."""
        output = self.execute_command(
            alias, f"kubectl get service kubernetes-dashboard -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_dashboard_pods(self, alias: str, namespace: str = "kubernetes-dashboard", **kwargs) -> dict:
        """Get all pods in the Kubernetes Dashboard namespace."""
        output = self.execute_command(
            alias, f"kubectl get pods -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_dashboard_namespace(self, alias: str, namespace: str = "kubernetes-dashboard", **kwargs) -> dict:
        """Get the Kubernetes Dashboard namespace information."""
        output = self.execute_command(
            alias, f"kubectl get namespace {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_dashboard_serviceaccount(self, alias: str, name: str = "kubernetes-dashboard", namespace: str = "kubernetes-dashboard", **kwargs) -> dict:
        """Get the Kubernetes Dashboard service account information."""
        output = self.execute_command(
            alias, f"kubectl get serviceaccount {shlex.quote(name)} -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_dashboard_secrets(self, alias: str, namespace: str = "kubernetes-dashboard", **kwargs) -> dict:
        """Get secrets in the Kubernetes Dashboard namespace."""
        output = self.execute_command(
            alias, f"kubectl get secrets -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def get_dashboard_configmaps(self, alias: str, namespace: str = "kubernetes-dashboard", **kwargs) -> dict:
        """Get configmaps in the Kubernetes Dashboard namespace."""
        output = self.execute_command(
            alias, f"kubectl get configmaps -n {shlex.quote(namespace)} -o json", **kwargs
        )
        return json.loads(output)

    def check_dashboard_status(self, alias: str, namespace: str = "kubernetes-dashboard", **kwargs) -> dict:
        """Check if the Kubernetes Dashboard is running by getting deployment status."""
        deployment = self.get_dashboard_deployment(alias, namespace, **kwargs)
        return {
            "name": deployment.get("metadata", {}).get("name"),
            "namespace": deployment.get("metadata", {}).get("namespace"),
            "replicas": deployment.get("spec", {}).get("replicas"),
            "ready_replicas": deployment.get("status", {}).get("readyReplicas", 0),
            "available_replicas": deployment.get("status", {}).get("availableReplicas", 0),
            "conditions": deployment.get("status", {}).get("conditions", [])
        }
