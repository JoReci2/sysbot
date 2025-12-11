from sysbot.utils.engine import ComponentBase
import json


class File(ComponentBase):
    def is_present(self, alias: str, path: str, **kwargs) -> bool:
        """Check if a file or directory exists."""
        # Escape single quotes by doubling them for PowerShell
        escaped_path = path.replace("'", "''")
        command = f"Test-Path -Path '{escaped_path}'"
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def is_file(self, alias: str, path: str, **kwargs) -> bool:
        """Check if path is a file."""
        escaped_path = path.replace("'", "''")
        command = f"Test-Path -Path '{escaped_path}' -PathType Leaf"
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def is_directory(self, alias: str, path: str, **kwargs) -> bool:
        """Check if path is a directory."""
        escaped_path = path.replace("'", "''")
        command = f"Test-Path -Path '{escaped_path}' -PathType Container"
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def size(self, alias: str, path: str, **kwargs) -> str:
        """Get file size in bytes. Note: Only works with files, not directories."""
        escaped_path = path.replace("'", "''")
        command = f"(Get-Item -Path '{escaped_path}').Length"
        return self.execute_command(alias, command, **kwargs)

    def content(self, alias: str, path: str, **kwargs) -> str:
        """Get file content."""
        escaped_path = path.replace("'", "''")
        command = f"Get-Content -Path '{escaped_path}' -Raw"
        return self.execute_command(alias, command, **kwargs)

    def md5(self, alias: str, path: str, **kwargs) -> str:
        """Get MD5 hash of file."""
        escaped_path = path.replace("'", "''")
        command = f"(Get-FileHash -Path '{escaped_path}' -Algorithm MD5).Hash"
        return self.execute_command(alias, command, **kwargs)

    def attributes(self, alias: str, path: str, **kwargs) -> dict:
        """Get file/directory attributes."""
        escaped_path = path.replace("'", "''")
        command = f"Get-Item -Path '{escaped_path}' | Select-Object Name, FullName, Length, CreationTime, LastWriteTime, LastAccessTime, Attributes, Extension | ConvertTo-Json -Compress"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def contains(self, alias: str, path: str, pattern: str, **kwargs) -> bool:
        """Check if file contains a pattern."""
        escaped_path = path.replace("'", "''")
        escaped_pattern = pattern.replace("'", "''")
        command = f"Select-String -Path '{escaped_path}' -Pattern '{escaped_pattern}' -Quiet"
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def owner(self, alias: str, path: str, **kwargs) -> str:
        """Get file/directory owner."""
        escaped_path = path.replace("'", "''")
        command = f"(Get-Acl -Path '{escaped_path}').Owner"
        return self.execute_command(alias, command, **kwargs)

    def list_directory(self, alias: str, path: str, **kwargs) -> list:
        """List contents of a directory. Returns empty list for empty directories."""
        escaped_path = path.replace("'", "''")
        command = f"@(Get-ChildItem -Path '{escaped_path}' | Select-Object Name, Length, LastWriteTime, Attributes) | ConvertTo-Json -AsArray -Compress"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
