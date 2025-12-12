from sysbot.utils.engine import ComponentBase
import json


class File(ComponentBase):
    def is_present(self, alias: str, path: str, **kwargs) -> bool:
        """Check if a file or directory exists."""
        command = f"""Test-Path -Path '{path}'"""
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def is_file(self, alias: str, path: str, **kwargs) -> bool:
        """Check if path is a file."""
        command = f"""Test-Path -Path '{path}' -PathType Leaf"""
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def is_directory(self, alias: str, path: str, **kwargs) -> bool:
        """Check if path is a directory."""
        command = f"""Test-Path -Path '{path}' -PathType Container"""
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def size(self, alias: str, path: str, **kwargs) -> str:
        """Get file size in bytes. Note: Only works with files, not directories."""
        command = f"""(Get-Item -Path '{path}').Length"""
        return self.execute_command(alias, command, **kwargs)

    def content(self, alias: str, path: str, **kwargs) -> str:
        """Get file content."""
        command = f"""Get-Content -Path '{path}' -Raw"""
        return self.execute_command(alias, command, **kwargs)

    def md5(self, alias: str, path: str, **kwargs) -> str:
        """Get MD5 hash of file."""
        command = f"""(Get-FileHash -Path '{path}' -Algorithm MD5).Hash"""
        return self.execute_command(alias, command, **kwargs)

    def attributes(self, alias: str, path: str, **kwargs) -> dict:
        """Get file/directory attributes."""
        command = f"""Get-Item -Path '{path}' | Select-Object Name, FullName, Length, CreationTime, LastWriteTime, LastAccessTime, Attributes, Extension | ConvertTo-Json -Compress"""
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def contains(self, alias: str, path: str, pattern: str, **kwargs) -> bool:
        """Check if file contains a pattern."""
        command = f"""Select-String -Path '{path}' -Pattern '{pattern}' -Quiet"""
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def owner(self, alias: str, path: str, **kwargs) -> str:
        """Get file/directory owner."""
        command = f"""(Get-Acl -Path '{path}').Owner"""
        return self.execute_command(alias, command, **kwargs)

    def permissions(self, alias: str, path: str, **kwargs) -> dict:
        """Get file/directory permissions (ACL information)."""
        command = f"""Get-Acl -Path '{path}' | Select-Object Owner, Group, AccessToString, @{{Name='Access';Expression={{$_.Access | Select-Object FileSystemRights, AccessControlType, IdentityReference, IsInherited, InheritanceFlags, PropagationFlags}}}} | ConvertTo-Json -Compress -Depth 3"""
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def list_directory(self, alias: str, path: str, **kwargs) -> list:
        """List contents of a directory. Returns empty list for empty directories."""
        command = f"""@(Get-ChildItem -Path '{path}' | Select-Object Name, Length, LastWriteTime, Attributes) | ConvertTo-Json -AsArray -Compress"""
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
