"""
Connectors Package

This package provides various protocol connectors for system automation,
enabling secure remote and local command execution across different platforms
and protocols. Supports shell-based, API-based, and socket-based communication
with multiple authentication methods.
"""

from . import ssh
from . import winrm
from . import http
from . import socket
from . import local

__all__ = ["ssh", "winrm", "http", "socket", "local"]
