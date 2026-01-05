"""
Windows File System Module

This module provides comprehensive file system operations for Windows systems,
including file type checking, attribute retrieval, content operations, and
ACL (Access Control List) management using PowerShell.
"""
from sysbot.utils.engine import ComponentBase
import json


class File(ComponentBase):
    """Windows file system operations class using PowerShell."""

    def is_present(self, alias: str, path: str, **kwargs) -> bool:
        """
        Check if a file or directory exists.

        Args:
            alias: Session alias for the connection.
            path: Path to check.
            **kwargs: Additional command execution options.

        Returns:
            True if path exists, False otherwise.
        """
        command = f"""Test-Path -Path '{path}'"""
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def is_file(self, alias: str, path: str, **kwargs) -> bool:
        """
        Check if path is a file.

        Args:
            alias: Session alias for the connection.
            path: Path to check.
            **kwargs: Additional command execution options.

        Returns:
            True if path is a file, False otherwise.
        """
        command = f"""Test-Path -Path '{path}' -PathType Leaf"""
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def is_directory(self, alias: str, path: str, **kwargs) -> bool:
        """
        Check if path is a directory.

        Args:
            alias: Session alias for the connection.
            path: Path to check.
            **kwargs: Additional command execution options.

        Returns:
            True if path is a directory, False otherwise.
        """
        command = f"""Test-Path -Path '{path}' -PathType Container"""
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def size(self, alias: str, path: str, **kwargs) -> str:
        """
        Get file size in bytes.

        Args:
            alias: Session alias for the connection.
            path: Path to the file.
            **kwargs: Additional command execution options.

        Returns:
            File size in bytes as a string. Note: Only works with files, not directories.
        """
        command = f"""(Get-Item -Path '{path}').Length"""
        return self.execute_command(alias, command, **kwargs)

    def content(self, alias: str, path: str, **kwargs) -> str:
        """
        Get file content.

        Args:
            alias: Session alias for the connection.
            path: Path to the file.
            **kwargs: Additional command execution options.

        Returns:
            File content as a string.
        """
        command = f"""Get-Content -Path '{path}' -Raw"""
        return self.execute_command(alias, command, **kwargs)

    def md5(self, alias: str, path: str, **kwargs) -> str:
        """
        Get MD5 hash of file.

        Args:
            alias: Session alias for the connection.
            path: Path to the file.
            **kwargs: Additional command execution options.

        Returns:
            MD5 hash string.
        """
        command = f"""(Get-FileHash -Path '{path}' -Algorithm MD5).Hash"""
        return self.execute_command(alias, command, **kwargs)

    def attributes(self, alias: str, path: str, **kwargs) -> dict:
        """
        Get file or directory attributes.

        Args:
            alias: Session alias for the connection.
            path: Path to query.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing file/directory attributes including Name, FullName, Length,
            CreationTime, LastWriteTime, LastAccessTime, Attributes, and Extension.
        """
        command = f"""Get-Item -Path '{path}' | Select-Object Name, FullName, Length, CreationTime, LastWriteTime, LastAccessTime, Attributes, Extension | ConvertTo-Json -Compress"""
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def contains(self, alias: str, path: str, pattern: str, **kwargs) -> bool:
        """
        Check if file contains a pattern.

        Args:
            alias: Session alias for the connection.
            path: Path to the file.
            pattern: Pattern to search for.
            **kwargs: Additional command execution options.

        Returns:
            True if pattern is found in the file, False otherwise.
        """
        command = f"""Select-String -Path '{path}' -Pattern '{pattern}' -Quiet"""
        output = self.execute_command(alias, command, **kwargs)
        return output.strip().lower() == "true"

    def owner(self, alias: str, path: str, **kwargs) -> str:
        """
        Get file or directory owner.

        Args:
            alias: Session alias for the connection.
            path: Path to query.
            **kwargs: Additional command execution options.

        Returns:
            Owner name as a string.
        """
        command = f"""(Get-Acl -Path '{path}').Owner"""
        return self.execute_command(alias, command, **kwargs)

    def permissions(self, alias: str, path: str, **kwargs) -> dict:
        """
        Get file or directory permissions (ACL information).

        Args:
            alias: Session alias for the connection.
            path: Path to query.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing ACL information including Owner, Group, AccessToString,
            and detailed Access information with FileSystemRights, AccessControlType,
            IdentityReference, IsInherited, InheritanceFlags, and PropagationFlags.
        """
        command = f"""
Get-Acl -Path '{path}' | Select-Object Owner, Group, AccessToString, @{{
    Name='Access';
    Expression={{
        $_.Access | Select-Object FileSystemRights, AccessControlType, IdentityReference, IsInherited, InheritanceFlags, PropagationFlags
    }}
}} | ConvertTo-Json -Compress -Depth 3
""".strip()
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def list_directory(self, alias: str, path: str, **kwargs) -> list:
        """
        List contents of a directory.

        Args:
            alias: Session alias for the connection.
            path: Path to the directory.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing Name, Length, LastWriteTime, and Attributes
            for each item in the directory. Returns empty list for empty directories.
        """
        command = f"""@(Get-ChildItem -Path '{path}' | Select-Object Name, Length, LastWriteTime, Attributes) | ConvertTo-Json -AsArray -Compress"""
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
