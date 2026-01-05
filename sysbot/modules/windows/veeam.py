"""
Veeam Backup & Replication Module

This module provides methods for managing and querying Veeam Backup & Replication,
including backup jobs, repositories, managed servers, backup sessions, and restore
operations using PowerShell Veeam cmdlets.
"""
from sysbot.utils.engine import ComponentBase
import json


class Veeam(ComponentBase):
    """Veeam Backup & Replication management class using PowerShell Veeam cmdlets."""

    def get_servers(self, alias: str, **kwargs) -> list:
        """
        Get managed servers in Veeam Backup & Replication.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing server information including Name, Description, Type, and Info.
        """
        command = "Get-VBRServer | Select-Object Name, Description, Type, Info | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_backup_repositories(self, alias: str, name: str = None, **kwargs) -> list:
        """Get backup repositories."""
        if name:
            command = f"Get-VBRBackupRepository -Name '{name}' | Select-Object Name, Description, Path, Type, Extent | ConvertTo-Json"
        else:
            command = "Get-VBRBackupRepository | Select-Object Name, Description, Path, Type, Extent | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_jobs(self, alias: str, name: str = None, **kwargs) -> list:
        """Get backup and replication jobs."""
        if name:
            command = f"Get-VBRJob -Name '{name}' | Select-Object Name, Description, JobType, IsScheduleEnabled, IsRunning, LastResult | ConvertTo-Json"
        else:
            command = "Get-VBRJob | Select-Object Name, Description, JobType, IsScheduleEnabled, IsRunning, LastResult | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_backups(self, alias: str, name: str = None, **kwargs) -> list:
        """Get backups."""
        if name:
            command = f"Get-VBRBackup -Name '{name}' | Select-Object Name, Description, JobName, CreationTime, JobType | ConvertTo-Json"
        else:
            command = "Get-VBRBackup | Select-Object Name, Description, JobName, CreationTime, JobType | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_restore_points(self, alias: str, backup_name: str = None, **kwargs) -> list:
        """Get restore points."""
        if backup_name:
            command = f"Get-VBRBackup -Name '{backup_name}' | Get-VBRRestorePoint | Select-Object Name, CreationTime, Type, VmName | ConvertTo-Json"
        else:
            command = "Get-VBRBackup | Get-VBRRestorePoint | Select-Object Name, CreationTime, Type, VmName | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_backup_sessions(self, alias: str, job_name: str = None, **kwargs) -> list:
        """Get backup sessions."""
        if job_name:
            command = f"Get-VBRJob -Name '{job_name}' | Get-VBRBackupSession | Select-Object Name, JobName, State, Result, CreationTime, EndTime | ConvertTo-Json"
        else:
            command = "Get-VBRBackupSession | Select-Object Name, JobName, State, Result, CreationTime, EndTime | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_vi_servers(self, alias: str, name: str = None, **kwargs) -> list:
        """Get vSphere servers managed by Veeam."""
        if name:
            command = f"Get-VBRViServer -Name '{name}' | Select-Object Name, Description, Type, ApiVersion, IsUnavailable | ConvertTo-Json"
        else:
            command = "Get-VBRViServer | Select-Object Name, Description, Type, ApiVersion, IsUnavailable | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_server_sessions(self, alias: str, **kwargs) -> list:
        """Get server session information."""
        command = "Get-VBRServerSession | Select-Object User, Server, Port | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result
