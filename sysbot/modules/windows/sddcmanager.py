from sysbot.utils.engine import ComponentBase
import json


class Sddcmanager(ComponentBase):
    def get_hosts(self, alias: str, **kwargs) -> list:
        """Get all hosts managed by SDDC Manager."""
        command = "Get-VCFHost | Select-Object id, fqdn, esxiVersion, status, hardwareVendor, hardwareModel | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_host(self, alias: str, host_id: str, **kwargs) -> dict:
        """Get a specific host by ID."""
        command = f"Get-VCFHost -id '{host_id}' | Select-Object id, fqdn, esxiVersion, status, hardwareVendor, hardwareModel, ipAddresses, cpu, memory | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_domains(self, alias: str, **kwargs) -> list:
        """Get all workload domains."""
        command = "Get-VCFWorkloadDomain | Select-Object id, name, type, ssoId, isManagementDomain, status | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_domain(self, alias: str, domain_name: str, **kwargs) -> dict:
        """Get a specific workload domain by name."""
        command = f"Get-VCFWorkloadDomain -name '{domain_name}' | Select-Object id, name, type, ssoId, isManagementDomain, status, capacity | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_clusters(self, alias: str, **kwargs) -> list:
        """Get all clusters."""
        command = "Get-VCFCluster | Select-Object id, name, primaryDatastoreName, primaryDatastoreType, isDefault, isStretched | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_cluster(self, alias: str, cluster_id: str, **kwargs) -> dict:
        """Get a specific cluster by ID."""
        command = f"Get-VCFCluster -id '{cluster_id}' | Select-Object id, name, primaryDatastoreName, primaryDatastoreType, isDefault, isStretched, hosts | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_vcenters(self, alias: str, **kwargs) -> list:
        """Get all vCenter Server instances."""
        command = "Get-VCFvCenter | Select-Object id, fqdn, version, build | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_vcenter(self, alias: str, vcenter_id: str, **kwargs) -> dict:
        """Get a specific vCenter Server by ID."""
        command = f"Get-VCFvCenter -id '{vcenter_id}' | Select-Object id, fqdn, version, build, domain | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_nsxt_clusters(self, alias: str, **kwargs) -> list:
        """Get all NSX-T clusters."""
        command = "Get-VCFNsxtCluster | Select-Object id, vipFqdn, vip, nodes | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_nsxt_cluster(self, alias: str, cluster_id: str, **kwargs) -> dict:
        """Get a specific NSX-T cluster by ID."""
        command = f"Get-VCFNsxtCluster -id '{cluster_id}' | Select-Object id, vipFqdn, vip, nodes, domains | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_credentials(self, alias: str, **kwargs) -> list:
        """Get all credentials."""
        command = "Get-VCFCredential | Select-Object id, resource, resourceType, username, credentialType | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_sddc_manager(self, alias: str, **kwargs) -> dict:
        """Get SDDC Manager details."""
        command = "Get-VCFManager | Select-Object id, version, fqdn, status | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_tasks(self, alias: str, **kwargs) -> list:
        """Get all tasks."""
        command = "Get-VCFTask | Select-Object id, name, status, type, creationTimestamp | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_task(self, alias: str, task_id: str, **kwargs) -> dict:
        """Get a specific task by ID."""
        command = f"Get-VCFTask -id '{task_id}' | Select-Object id, name, status, type, creationTimestamp, completionTimestamp, errors | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result
