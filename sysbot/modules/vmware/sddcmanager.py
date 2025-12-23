from sysbot.utils.engine import ComponentBase
import json


class Sddcmanager(ComponentBase):
    """
    SDDC Manager module for VMware Cloud Foundation.
    
    This module uses the SDDC Manager REST API directly.
    Requires an HTTP session with Basic Auth or other authentication method.
    """
    
    def get_hosts(self, alias: str, **kwargs) -> list:
        """Get all hosts managed by SDDC Manager."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/hosts", options=options)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # API returns {"elements": [...]}
        if isinstance(result, dict) and "elements" in result:
            return result["elements"]
        return result if isinstance(result, list) else [result]

    def get_host(self, alias: str, host_id: str, **kwargs) -> dict:
        """Get a specific host by ID."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/hosts/{host_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_domains(self, alias: str, **kwargs) -> list:
        """Get all workload domains."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/domains", options=options)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # API returns {"elements": [...]}
        if isinstance(result, dict) and "elements" in result:
            return result["elements"]
        return result if isinstance(result, list) else [result]

    def get_domain(self, alias: str, domain_id: str, **kwargs) -> dict:
        """Get a specific workload domain by ID."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/domains/{domain_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_clusters(self, alias: str, **kwargs) -> list:
        """Get all clusters."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/clusters", options=options)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # API returns {"elements": [...]}
        if isinstance(result, dict) and "elements" in result:
            return result["elements"]
        return result if isinstance(result, list) else [result]

    def get_cluster(self, alias: str, cluster_id: str, **kwargs) -> dict:
        """Get a specific cluster by ID."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/clusters/{cluster_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_vcenters(self, alias: str, **kwargs) -> list:
        """Get all vCenter Server instances."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/vcenters", options=options)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # API returns {"elements": [...]}
        if isinstance(result, dict) and "elements" in result:
            return result["elements"]
        return result if isinstance(result, list) else [result]

    def get_vcenter(self, alias: str, vcenter_id: str, **kwargs) -> dict:
        """Get a specific vCenter Server by ID."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/vcenters/{vcenter_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_nsxt_clusters(self, alias: str, **kwargs) -> list:
        """Get all NSX-T clusters."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/nsxt-clusters", options=options)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # API returns {"elements": [...]}
        if isinstance(result, dict) and "elements" in result:
            return result["elements"]
        return result if isinstance(result, list) else [result]

    def get_nsxt_cluster(self, alias: str, cluster_id: str, **kwargs) -> dict:
        """Get a specific NSX-T cluster by ID."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/nsxt-clusters/{cluster_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_credentials(self, alias: str, **kwargs) -> list:
        """Get all credentials."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/credentials", options=options)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # API returns {"elements": [...]}
        if isinstance(result, dict) and "elements" in result:
            return result["elements"]
        return result if isinstance(result, list) else [result]

    def get_sddc_manager(self, alias: str, **kwargs) -> dict:
        """Get SDDC Manager details."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/sddc-managers", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        # If result has elements, return the first one
        if isinstance(result, dict) and "elements" in result:
            elements = result["elements"]
            return elements[0] if elements else {}
        return result

    def get_tasks(self, alias: str, **kwargs) -> list:
        """Get all tasks."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/tasks", options=options)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # API returns {"elements": [...]}
        if isinstance(result, dict) and "elements" in result:
            return result["elements"]
        return result if isinstance(result, list) else [result]

    def get_task(self, alias: str, task_id: str, **kwargs) -> dict:
        """Get a specific task by ID."""
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/tasks/{task_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result
