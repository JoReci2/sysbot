"""
VMware SDDC Manager Module

This module provides methods for managing VMware Cloud Foundation through SDDC
Manager, including hosts, clusters, domains, workload domains, and lifecycle
management using the SDDC Manager REST API.
"""
from sysbot.utils.engine import ComponentBase
import json


class Sddcmanager(ComponentBase):
    """
    SDDC Manager module for VMware Cloud Foundation.
    
    This module uses the SDDC Manager REST API directly.
    Requires an HTTP session with Basic Auth or other authentication method.
    """
    
    def get_hosts(self, alias: str, **kwargs) -> list:
        """
        Get all hosts managed by SDDC Manager.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing host information.
        """
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
        """
        Get a specific host by ID.

        Args:
            alias: Session alias for the connection.
            host_id: Host identifier.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing detailed host information.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/hosts/{host_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_domains(self, alias: str, **kwargs) -> list:
        """
        Get all workload domains.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing workload domain information.
        """
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
        """
        Get a specific workload domain by ID.

        Args:
            alias: Session alias for the connection.
            domain_id: Workload domain identifier.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing detailed workload domain information.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/domains/{domain_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_clusters(self, alias: str, **kwargs) -> list:
        """
        Get all clusters.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing cluster information.
        """
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
        """
        Get a specific cluster by ID.

        Args:
            alias: Session alias for the connection.
            cluster_id: Cluster identifier.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing detailed cluster information.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/clusters/{cluster_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_vcenters(self, alias: str, **kwargs) -> list:
        """
        Get all vCenter Server instances.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing vCenter Server information.
        """
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
        """
        Get a specific vCenter Server by ID.

        Args:
            alias: Session alias for the connection.
            vcenter_id: vCenter Server identifier.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing detailed vCenter Server information.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/vcenters/{vcenter_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_nsxt_clusters(self, alias: str, **kwargs) -> list:
        """
        Get all NSX-T clusters.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing NSX-T cluster information.
        """
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
        """
        Get a specific NSX-T cluster by ID.

        Args:
            alias: Session alias for the connection.
            cluster_id: NSX-T cluster identifier.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing detailed NSX-T cluster information.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/nsxt-clusters/{cluster_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_credentials(self, alias: str, **kwargs) -> list:
        """
        Get all credentials.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing credential information.
        """
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
        """
        Get SDDC Manager details.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing SDDC Manager information.
        """
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
        """
        Get all tasks.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing task information.
        """
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
        """
        Get a specific task by ID.

        Args:
            alias: Session alias for the connection.
            task_id: Task identifier.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing detailed task information.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, f"/v1/tasks/{task_id}", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_ntp(self, alias: str, **kwargs) -> dict:
        """
        Get NTP configuration.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing NTP configuration.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/system/ntp-configuration", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_dns(self, alias: str, **kwargs) -> dict:
        """
        Get DNS configuration.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing DNS configuration.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/system/dns-configuration", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_version(self, alias: str, **kwargs) -> dict:
        """
        Get SDDC Manager version information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing version information.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/system/version", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_vcf_services(self, alias: str, **kwargs) -> list:
        """
        Get VCF services status.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing VCF service status information.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/vcf-services", options=options)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # API returns {"elements": [...]}
        if isinstance(result, dict) and "elements" in result:
            return result["elements"]
        return result if isinstance(result, list) else [result]

    def get_ldap(self, alias: str, **kwargs) -> dict:
        """
        Get LDAP configuration.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing LDAP configuration.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/system/ldap-configuration", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result

    def get_syslog(self, alias: str, **kwargs) -> dict:
        """
        Get syslog configuration.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing syslog configuration.
        """
        options = {"method": "GET"}
        options.update(kwargs.get("options", {}))
        output = self.execute_command(alias, "/v1/system/syslog-configuration", options=options)
        if not output or output.strip() == "":
            return {}
        result = json.loads(output)
        return result
