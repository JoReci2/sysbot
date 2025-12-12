from sysbot.utils.engine import ComponentBase
import json


class Veeam(ComponentBase):
    def get_server(self, alias: str, **kwargs) -> dict:
        """Get Veeam Backup & Replication server information."""
        command = "Get-VBRServer | Select-Object Name, Description, Type, Info | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        return json.loads(output)

    def get_backup_repository(self, alias: str, name: str = None, **kwargs) -> list:
        """Get backup repositories."""
        if name:
            # Escape single quotes to prevent injection
            name = name.replace("'", "''")
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

    def get_job(self, alias: str, name: str = None, **kwargs) -> list:
        """Get backup and replication jobs."""
        if name:
            # Escape single quotes to prevent injection
            name = name.replace("'", "''")
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

    def get_backup(self, alias: str, name: str = None, **kwargs) -> list:
        """Get backups."""
        if name:
            # Escape single quotes to prevent injection
            name = name.replace("'", "''")
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

    def get_restore_point(self, alias: str, backup_name: str = None, **kwargs) -> list:
        """Get restore points."""
        if backup_name:
            # Escape single quotes to prevent injection
            backup_name = backup_name.replace("'", "''")
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

    def get_backup_session(self, alias: str, job_name: str = None, **kwargs) -> list:
        """Get backup sessions."""
        if job_name:
            # Escape single quotes to prevent injection
            job_name = job_name.replace("'", "''")
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

    def get_vi_server(self, alias: str, name: str = None, **kwargs) -> list:
        """Get vSphere servers managed by Veeam."""
        if name:
            # Escape single quotes to prevent injection
            name = name.replace("'", "''")
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

    def get_server_session(self, alias: str, **kwargs) -> dict:
        """Get server session information."""
        command = "Get-VBRServerSession | Select-Object User, Server, Port | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return {}
        return json.loads(output)
