from sysbot.utils.engine import ComponentBase
import json


class Nsx(ComponentBase):
    """VMware NSX module for network virtualization and security management.
    
    This module provides methods to interact with VMware NSX Manager API.
    Requires an HTTP session with appropriate authentication to NSX Manager.
    """

    def get_logical_switches(self, alias: str, **kwargs) -> list:
        """Get all logical switches in NSX environment.
        
        Args:
            alias: Session identifier
            **kwargs: Additional command execution options
            
        Returns:
            List of logical switches with their details
        """
        command = "/api/2.0/vdn/virtualwires"
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return []
        
        try:
            result = json.loads(output)
            # NSX API returns data in different formats, handle accordingly
            if isinstance(result, dict):
                switches = result.get("virtualWires", {}).get("dataPage", {}).get("virtualWire", [])
                if isinstance(switches, dict):
                    return [switches]
                return switches if switches else []
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    def get_logical_routers(self, alias: str, **kwargs) -> list:
        """Get all logical routers in NSX environment.
        
        Args:
            alias: Session identifier
            **kwargs: Additional command execution options
            
        Returns:
            List of logical routers with their details
        """
        command = "/api/4.0/edges"
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return []
        
        try:
            result = json.loads(output)
            if isinstance(result, dict):
                edges = result.get("edgePage", {}).get("data", [])
                if isinstance(edges, dict):
                    return [edges]
                return edges if edges else []
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    def get_transport_zones(self, alias: str, **kwargs) -> list:
        """Get all transport zones in NSX environment.
        
        Args:
            alias: Session identifier
            **kwargs: Additional command execution options
            
        Returns:
            List of transport zones with their details
        """
        command = "/api/2.0/vdn/scopes"
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return []
        
        try:
            result = json.loads(output)
            if isinstance(result, dict):
                scopes = result.get("vdnScopes", {}).get("vdnScope", [])
                if isinstance(scopes, dict):
                    return [scopes]
                return scopes if scopes else []
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    def get_edge_clusters(self, alias: str, **kwargs) -> list:
        """Get all edge clusters in NSX environment.
        
        Args:
            alias: Session identifier
            **kwargs: Additional command execution options
            
        Returns:
            List of edge clusters with their details
        """
        command = "/api/v1/edge-clusters"
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return []
        
        try:
            result = json.loads(output)
            if isinstance(result, dict):
                clusters = result.get("results", [])
                return clusters if clusters else []
            elif isinstance(result, list):
                return result
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    def get_firewall_sections(self, alias: str, **kwargs) -> list:
        """Get all firewall sections in NSX environment.
        
        Args:
            alias: Session identifier
            **kwargs: Additional command execution options
            
        Returns:
            List of firewall sections with their details
        """
        command = "/api/4.0/firewall/globalroot-0/config"
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return []
        
        try:
            result = json.loads(output)
            if isinstance(result, dict):
                sections = result.get("layer3Sections", {}).get("section", [])
                if isinstance(sections, dict):
                    return [sections]
                return sections if sections else []
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    def get_firewall_rules(self, alias: str, section_id: str = None, **kwargs) -> list:
        """Get firewall rules from a specific section or all sections.
        
        Args:
            alias: Session identifier
            section_id: Optional specific section ID to get rules from
            **kwargs: Additional command execution options
            
        Returns:
            List of firewall rules with their details
        """
        if section_id:
            command = f"/api/4.0/firewall/globalroot-0/config/layer3sections/{section_id}"
        else:
            command = "/api/4.0/firewall/globalroot-0/config"
            
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return []
        
        try:
            result = json.loads(output)
            if isinstance(result, dict):
                if section_id:
                    rules = result.get("rule", [])
                else:
                    # Get all rules from all sections
                    sections = result.get("layer3Sections", {}).get("section", [])
                    if isinstance(sections, dict):
                        sections = [sections]
                    rules = []
                    for section in sections:
                        section_rules = section.get("rule", [])
                        if isinstance(section_rules, dict):
                            section_rules = [section_rules]
                        rules.extend(section_rules)
                    return rules
                    
                if isinstance(rules, dict):
                    return [rules]
                return rules if rules else []
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    def get_security_groups(self, alias: str, **kwargs) -> list:
        """Get all security groups in NSX environment.
        
        Args:
            alias: Session identifier
            **kwargs: Additional command execution options
            
        Returns:
            List of security groups with their details
        """
        command = "/api/2.0/services/securitygroup/scope/globalroot-0"
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return []
        
        try:
            result = json.loads(output)
            if isinstance(result, dict):
                groups = result.get("list", {}).get("securitygroup", [])
                if isinstance(groups, dict):
                    return [groups]
                return groups if groups else []
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    def get_ip_pools(self, alias: str, **kwargs) -> list:
        """Get all IP pools in NSX environment.
        
        Args:
            alias: Session identifier
            **kwargs: Additional command execution options
            
        Returns:
            List of IP pools with their details
        """
        command = "/api/2.0/services/ipam/pools/scope/globalroot-0"
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return []
        
        try:
            result = json.loads(output)
            if isinstance(result, dict):
                pools = result.get("ipamAddressPools", {}).get("ipamAddressPool", [])
                if isinstance(pools, dict):
                    return [pools]
                return pools if pools else []
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    def get_controllers(self, alias: str, **kwargs) -> list:
        """Get all NSX controllers in the environment.
        
        Args:
            alias: Session identifier
            **kwargs: Additional command execution options
            
        Returns:
            List of NSX controllers with their details
        """
        command = "/api/2.0/vdn/controller"
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return []
        
        try:
            result = json.loads(output)
            if isinstance(result, dict):
                controllers = result.get("controllers", {}).get("controller", [])
                if isinstance(controllers, dict):
                    return [controllers]
                return controllers if controllers else []
            return []
        except (json.JSONDecodeError, KeyError):
            return []

    def get_version(self, alias: str, **kwargs) -> dict:
        """Get NSX Manager version information.
        
        Args:
            alias: Session identifier
            **kwargs: Additional command execution options
            
        Returns:
            Dictionary containing version information
        """
        command = "/api/1.0/appliance-management/global/info"
        output = self.execute_command(alias, command, options={"method": "GET"}, **kwargs)
        
        if not output or output.strip() == "":
            return {}
        
        try:
            result = json.loads(output)
            if isinstance(result, dict):
                return result.get("versionInfo", {})
            return {}
        except (json.JSONDecodeError, KeyError):
            return {}
