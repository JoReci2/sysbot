"""
Windows Server Update Services Module

This module provides methods for managing and querying Windows Server Update
Services (WSUS) including server configuration, update approvals, computer
groups, and synchronization using PowerShell WSUS cmdlets.
"""
from sysbot.utils.engine import ComponentBase
import json


class Wsus(ComponentBase):
    def get_server(self, alias: str, **kwargs) -> dict:
        """Get WSUS server information."""
        command = "Get-WsusServer | Select-Object Name, PortNumber, ServerProtocolVersion, UpdateServer | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        return json.loads(output)

    def get_update(self, alias: str, update_id: str = None, classification: str = None, approval: str = None, status: str = None, **kwargs) -> list:
        """Get WSUS updates with optional filters."""
        params = []
        if update_id:
            params.append(f"-UpdateId '{update_id}'")
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
        """Get computers registered with WSUS."""
        params = []
        if computer_name:
            params.append(f"-ComputerTargetName '{computer_name}'")
        
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
        if not output or output.strip() == "":
            return {}
        return json.loads(output)
