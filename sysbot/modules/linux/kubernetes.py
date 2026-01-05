from sysbot.utils.engine import ComponentBase
import json


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
            alias, f"kubectl get node {name} -o json", **kwargs
        )
        return json.loads(output)

    def get_pods(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get pods -n {namespace} -o json", **kwargs
        )
        return json.loads(output)

    def get_pod(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get pod {name} -n {namespace} -o json", **kwargs
        )
        return json.loads(output)

    def get_services(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get services -n {namespace} -o json", **kwargs
        )
        return json.loads(output)

    def get_service(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get service {name} -n {namespace} -o json", **kwargs
        )
        return json.loads(output)

    def get_deployments(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get deployments -n {namespace} -o json", **kwargs
        )
        return json.loads(output)

    def get_deployment(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get deployment {name} -n {namespace} -o json", **kwargs
        )
        return json.loads(output)

    def get_namespaces(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, "kubectl get namespaces -o json", **kwargs
        )
        return json.loads(output)

    def get_namespace(self, alias: str, name: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get namespace {name} -o json", **kwargs
        )
        return json.loads(output)

    def get_configmaps(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get configmaps -n {namespace} -o json", **kwargs
        )
        return json.loads(output)

    def get_configmap(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get configmap {name} -n {namespace} -o json", **kwargs
        )
        return json.loads(output)

    def get_secrets(self, alias: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get secrets -n {namespace} -o json", **kwargs
        )
        return json.loads(output)

    def get_secret(self, alias: str, name: str, namespace: str = "default", **kwargs) -> dict:
        output = self.execute_command(
            alias, f"kubectl get secret {name} -n {namespace} -o json", **kwargs
        )
        return json.loads(output)
