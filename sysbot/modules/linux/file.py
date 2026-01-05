"""
Linux File System Module

This module provides comprehensive file system operations for Linux systems,
including file type checking, attribute retrieval, content operations, and
permission management.
"""
from sysbot.utils.engine import ComponentBase


class File(ComponentBase):
    """File system operations class for Linux systems."""

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
        return self.execute_command(alias, f"test -e {path} ; echo $?", **kwargs) == "0"

    def is_file(self, alias: str, path: str, **kwargs) -> bool:
        """
        Check if path is a regular file.

        Args:
            alias: Session alias for the connection.
            path: Path to check.
            **kwargs: Additional command execution options.

        Returns:
            True if path is a regular file, False otherwise.
        """
        return self.execute_command(alias, f"test -f {path} ; echo $?", **kwargs) == "0"

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
        return self.execute_command(alias, f"test -d {path} ; echo $?", **kwargs) == "0"

    def is_executable(self, alias: str, path: str, **kwargs) -> bool:
        """
        Check if file is executable.

        Args:
            alias: Session alias for the connection.
            path: Path to check.
            **kwargs: Additional command execution options.

        Returns:
            True if file is executable, False otherwise.
        """
        return self.execute_command(alias, f"test -x {path} ; echo $?", **kwargs) == "0"

    def is_pipe(self, alias: str, path: str, **kwargs) -> bool:
        """
        Check if path is a named pipe (FIFO).

        Args:
            alias: Session alias for the connection.
            path: Path to check.
            **kwargs: Additional command execution options.

        Returns:
            True if path is a named pipe, False otherwise.
        """
        return self.execute_command(alias, f"test -p {path} ; echo $?", **kwargs) == "0"

    def is_socket(self, alias: str, path: str, **kwargs) -> bool:
        """
        Check if path is a socket.

        Args:
            alias: Session alias for the connection.
            path: Path to check.
            **kwargs: Additional command execution options.

        Returns:
            True if path is a socket, False otherwise.
        """
        return self.execute_command(alias, f"test -S {path} ; echo $?", **kwargs) == "0"

    def is_symlink(self, alias: str, path: str, **kwargs) -> bool:
        """
        Check if path is a symbolic link.

        Args:
            alias: Session alias for the connection.
            path: Path to check.
            **kwargs: Additional command execution options.

        Returns:
            True if path is a symbolic link, False otherwise.
        """
        return self.execute_command(alias, f"test -L {path} ; echo $?", **kwargs) == "0"

    def realpath(self, alias: str, path: str, **kwargs) -> str:
        """
        Get the canonical absolute path.

        Args:
            alias: Session alias for the connection.
            path: Path to resolve.
            **kwargs: Additional command execution options.

        Returns:
            Canonical absolute path.
        """
        return self.execute_command(alias, f"realpath {path}", **kwargs)

    def user(self, alias: str, path: str, **kwargs) -> str:
        """
        Get the owner user name of a file.

        Args:
            alias: Session alias for the connection.
            path: Path to query.
            **kwargs: Additional command execution options.

        Returns:
            Owner user name.
        """
        return self.execute_command(alias, f"stat -Lc %U {path}", **kwargs)

    def uid(self, alias: str, path: str, **kwargs) -> str:
        """
        Get the owner user ID of a file.

        Args:
            alias: Session alias for the connection.
            path: Path to query.
            **kwargs: Additional command execution options.

        Returns:
            Owner user ID.
        """
        return self.execute_command(alias, f"stat -Lc %u {path}", **kwargs)

    def group(self, alias: str, path: str, **kwargs) -> str:
        """
        Get the owner group name of a file.

        Args:
            alias: Session alias for the connection.
            path: Path to query.
            **kwargs: Additional command execution options.

        Returns:
            Owner group name.
        """
        return self.execute_command(alias, f"stat -Lc %G {path}", **kwargs)

    def gid(self, alias: str, path: str, **kwargs) -> str:
        """
        Get the owner group ID of a file.

        Args:
            alias: Session alias for the connection.
            path: Path to query.
            **kwargs: Additional command execution options.

        Returns:
            Owner group ID.
        """
        return self.execute_command(alias, f"stat -Lc %g {path}", **kwargs)

    def mode(self, alias: str, path: str, **kwargs) -> str:
        """
        Get the file permission mode in octal format.

        Args:
            alias: Session alias for the connection.
            path: Path to query.
            **kwargs: Additional command execution options.

        Returns:
            Permission mode in octal (e.g., '755', '644').
        """
        return self.execute_command(alias, f"stat -Lc %a {path}", **kwargs)

    def size(self, alias: str, path: str, **kwargs) -> str:
        """
        Get the file size in bytes.

        Args:
            alias: Session alias for the connection.
            path: Path to query.
            **kwargs: Additional command execution options.

        Returns:
            File size in bytes as a string.
        """
        return self.execute_command(alias, f"stat -Lc %s {path}", **kwargs)

    def md5sum(self, alias: str, path: str, **kwargs) -> str:
        """
        Calculate MD5 checksum of a file.

        Args:
            alias: Session alias for the connection.
            path: Path to the file.
            **kwargs: Additional command execution options.

        Returns:
            MD5 checksum hash string.
        """
        return self.execute_command(alias, f"md5sum {path} | cut -d' ' -f1", **kwargs)

    def content(self, alias: str, path: str, **kwargs) -> str:
        """
        Read the content of a file.

        Args:
            alias: Session alias for the connection.
            path: Path to the file.
            **kwargs: Additional command execution options.

        Returns:
            File content as a string.
        """
        return self.execute_command(alias, f"cat {path}", **kwargs)

    def contains(self, alias: str, path: str, pattern: str, **kwargs) -> bool:
        """
        Check if a file contains a specific pattern.

        Args:
            alias: Session alias for the connection.
            path: Path to the file.
            pattern: Pattern to search for.
            **kwargs: Additional command execution options.

        Returns:
            True if pattern is found in the file, False otherwise.
        """
        return (
            self.execute_command(
                alias, f"grep -qs -- {pattern} {path} ; echo $?", **kwargs
            )
            == "0"
        )
