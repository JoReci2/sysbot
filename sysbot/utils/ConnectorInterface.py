"""
MIT License

Copyright (c) 2024 Thibault SCIRE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from abc import ABC, abstractmethod
from typing import Optional
from .versionManager import version_manager


class ConnectorInterface(ABC):
    """
    Abstract base class defining the interface that all connectors must implement.
    This ensures that all connectors have the same structure and provide consistent methods.
    Supports versioning of connector methods for backward compatibility.
    """

    def __init__(self):
        """Initialize the connector with version manager support."""
        self.version_manager = version_manager
        self._connector_version = "1.0.0"  # Default version

    def set_connector_version(self, version: str) -> None:
        """
        Set the version for this connector instance.
        
        Args:
            version: Version string to set
        """
        self._connector_version = version

    def get_connector_version(self) -> str:
        """
        Get the current version of this connector.
        
        Returns:
            Current connector version
        """
        return self._connector_version

    def get_versioned_method(self, method_name: str, version: Optional[str] = None):
        """
        Get a versioned method from this connector.
        
        Args:
            method_name: Name of the method to retrieve
            version: Version to retrieve (optional, uses default if not specified)
            
        Returns:
            The versioned method
        """
        return self.version_manager.get_versioned_function(method_name, version)

    @abstractmethod
    def open_session(self, host, port, login, password):
        """
        Opens a session to the target system.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port to connect to.
            login (str): Username for authentication.
            password (str): Password for authentication.

        Returns:
            object: Session object that can be used for executing commands.

        Raises:
            Exception: If there is an error opening the session.
        """
        pass

    @abstractmethod
    def execute_command(self, session, command, **kwargs):
        """
        Executes a command on the target system.

        Args:
            session (object): The session object returned by open_session.
            command (str): The command to execute.
            **kwargs: Additional parameters specific to the connector.

        Returns:
            object: The result of the command execution.

        Raises:
            Exception: If there is an error executing the command.
        """
        pass

    @abstractmethod
    def close_session(self, session):
        """
        Closes an open session.

        Args:
            session (object): The session object to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        pass