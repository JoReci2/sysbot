"""
Connectors module for SysBot.

This module provides various protocol connectors for system automation:
- ssh: SSH connections with Bash and PowerShell support
- winrm: Windows Remote Management with PowerShell support
- http: HTTP/HTTPS connections with multiple authentication methods
- socket: Socket connections with TCP and UDP support
- local: Local execution with Bash and PowerShell support
"""

from . import ssh
from . import winrm
from . import http
from . import socket
from . import local

__all__ = ["ssh", "winrm", "http", "socket", "local"]
