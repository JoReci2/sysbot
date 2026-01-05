"""
Linux Process Management Module

This module provides methods for querying and managing running processes on
Linux systems, including process information, thread details, and security contexts.
"""
from sysbot.utils.engine import ComponentBase


class Process(ComponentBase):
    """Process management and querying class for Linux systems."""

    def ps(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get process information by name using ps command.

        Args:
            alias: Session alias for the connection.
            name: Process name to search for.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing process information including
            user, pid, cpu, mem, vsz, rss, tty, stat, start, time, and command.
        """
        output = self.execute_command(
            alias, f"ps aux | grep {name} | grep -v grep", **kwargs
        )
        processes = []
        for line in output.splitlines():
            parts = line.split(maxsplit=10)
            if len(parts) >= 11:
                process = {
                    "user": parts[0],
                    "pid": int(parts[1]),
                    "cpu": float(parts[2]),
                    "mem": float(parts[3]),
                    "vsz": int(parts[4]),
                    "rss": int(parts[5]),
                    "tty": parts[6],
                    "stat": parts[7],
                    "start": parts[8],
                    "time": parts[9],
                    "command": parts[10],
                }
                processes.append(process)
        return processes

    def thread(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get thread information by process name.

        Args:
            alias: Session alias for the connection.
            name: Process name to search for.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing thread information including
            uid, pid, stack_ptr, tty, time, and command.
        """
        output = self.execute_command(
            alias, f"ps axms | grep {name} | grep -v grep", **kwargs
        )
        processes = []
        for line in output.splitlines():
            parts = line.split(maxsplit=10)
            if len(parts) >= 11:
                process = {
                    "uid": int(parts[0]),
                    "pid": int(parts[1]),
                    "stack_ptr": parts[2],
                    "tty": parts[9],
                    "time": parts[10],
                    "command": parts[11] if len(parts) > 11 else "",
                }
                processes.append(process)
        return processes

    def security(self, alias: str, name: str, **kwargs) -> dict:
        """
        Get security context information for processes by name.

        Args:
            alias: Session alias for the connection.
            name: Process name to search for.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing security information including
            euser, ruser, suser, fuser, f, comm, and label (SELinux context).
        """
        output = self.execute_command(
            alias,
            f"ps -eo euser,ruser,suser,fuser,f,comm,label | grep {name} | grep -v grep",
            **kwargs,
        )
        headers = ["euser", "ruser", "suser", "fuser", "f", "comm", "label"]
        processes = []
        for line in output.splitlines():
            line = line.strip()
            if not line or line.lower().startswith("euser"):
                continue
            parts = line.split(None, len(headers) - 1)
            if len(parts) < len(headers):
                continue
            processes.append(dict(zip(headers, parts)))
        return processes
