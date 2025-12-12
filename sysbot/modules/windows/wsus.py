from sysbot.utils.engine import ComponentBase
import json


class Wsus(ComponentBase):
    def get_server(self, alias: str, **kwargs) -> dict:
        """Get WSUS server information."""
        command = "Get-WsusServer | Select-Object Name, PortNumber, ServerProtocolVersion, UpdateServer | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_update(self, alias: str, update_id: str = None, classification: str = None, approval: str = None, status: str = None, **kwargs) -> list:
        """Get WSUS updates with optional filters.
        
        Args:
            alias: The connection alias
            update_id: Specific update GUID (optional)
            classification: Filter by classification (e.g., Critical, Security, All) (optional)
            approval: Filter by approval status (Approved, Unapproved, Declined, Any) (optional)
            status: Filter by status (Any, Installed, FailedOrNeeded) (optional)
        
        Returns:
            List of update objects
        """
        params = []
        if update_id:
            # Escape single quotes to prevent injection
            escaped_id = update_id.replace("'", "''")
            params.append(f"-UpdateId '{escaped_id}'")
        if classification:
            params.append(f"-Classification {classification}")
        if approval:
            params.append(f"-Approval {approval}")
        if status:
            params.append(f"-Status {status}")
        
        param_str = " ".join(params) if params else ""
        command = f"Get-WsusUpdate {param_str} | Select-Object Title, UpdateId, Classification, Approval, ComputersNeedingThisUpdate, ComputersInstalledThisUpdate | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_computer(self, alias: str, computer_name: str = None, **kwargs) -> list:
        """Get computers registered with WSUS.
        
        Args:
            alias: The connection alias
            computer_name: Filter by computer name (optional)
        
        Returns:
            List of computer objects
        """
        params = []
        if computer_name:
            # Escape single quotes to prevent injection
            escaped_name = computer_name.replace("'", "''")
            params.append(f"-ComputerTargetName '{escaped_name}'")
        
        param_str = " ".join(params) if params else ""
        command = f"Get-WsusComputer {param_str} | Select-Object FullDomainName, IPAddress, LastReportedStatusTime, LastSyncTime, OSDescription | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_classification(self, alias: str, **kwargs) -> list:
        """Get available update classifications."""
        command = "Get-WsusClassification | Select-Object Classification, Id | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_product(self, alias: str, **kwargs) -> list:
        """Get available products for updates."""
        command = "Get-WsusProduct | Select-Object Product, Id | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_status(self, alias: str, **kwargs) -> dict:
        """Get WSUS server status and statistics."""
        command = "Get-WsusServer | Get-WsusServerStatistics | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
