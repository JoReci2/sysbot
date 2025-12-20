"""
Redfish Connector for BMC System Management

This module provides a Redfish connector for interacting with BMC (Baseboard Management
Controller) systems such as HPE iLO and Dell iDRAC. It uses the redfish library to
establish and manage Redfish API connections.
"""

import redfish
from sysbot.utils.engine import ConnectorInterface

# Default Redfish API prefix (standard for most BMC implementations)
DEFAULT_REDFISH_PREFIX = "/redfish/v1"

# Acceptable HTTP status codes for successful Redfish operations
REDFISH_SUCCESS_CODES = [200, 201, 202, 204]


class Redfish(ConnectorInterface):
    """
    This class provides methods for interacting with BMC systems using Redfish API.
    It uses the redfish library to establish and manage Redfish connections.
    """

    def __init__(self, port=443, redfish_prefix=DEFAULT_REDFISH_PREFIX):
        """
        Initialize Redfish connector with default port and API prefix.

        Args:
            port (int): Default HTTPS port for Redfish API (default: 443).
            redfish_prefix (str): Redfish API prefix (default: "/redfish/v1").
        """
        super().__init__()
        self.default_port = port
        self.redfish_prefix = redfish_prefix

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens a Redfish session to a BMC system.

        Args:
            host (str): Hostname or IP address of the BMC system.
            port (int): Port of the Redfish service. If None, uses default_port.
            login (str): Username for the session.
            password (str): Password for the session.

        Returns:
            redfish.rest.v1.RedfishClient: An authenticated Redfish client session.

        Raises:
            Exception: If there is an error opening the session.
        """
        if port is None:
            port = self.default_port
        try:
            # Build the base URL for Redfish
            base_url = f"https://{host}:{port}"
            
            # Create Redfish client and login
            client = redfish.redfish_client(
                base_url=base_url,
                username=login,
                password=password,
                default_prefix=self.redfish_prefix
            )
            client.login(auth="session")
            
            return client
        except Exception as e:
            raise Exception(f"Failed to open Redfish session: {str(e)}")

    def execute_command(self, session, command, method="GET", body=None):
        """
        Executes a Redfish API request.

        Args:
            session: The Redfish session object
            command (str): The Redfish API endpoint path (e.g., "/Systems/1")
            method (str): HTTP method (GET, POST, PATCH, DELETE, etc.) (default: GET)
            body (dict): Request body for POST/PATCH operations (optional)

        Returns:
            dict: The response from the Redfish API as a dictionary

        Raises:
            Exception: If there is an error executing the command
        """
        try:
            # Execute the request based on method
            if method.upper() == "GET":
                response = session.get(command)
            elif method.upper() == "POST":
                response = session.post(command, body=body)
            elif method.upper() == "PATCH":
                response = session.patch(command, body=body)
            elif method.upper() == "DELETE":
                response = session.delete(command)
            elif method.upper() == "PUT":
                response = session.put(command, body=body)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check response status
            if response.status not in REDFISH_SUCCESS_CODES:
                error_msg = f"Request failed with status {response.status}"
                if hasattr(response, 'dict') and response.dict:
                    error_msg += f": {response.dict}"
                raise Exception(error_msg)
            
            # Return the response data
            return response.dict if (hasattr(response, 'dict') and response.dict) else {}
            
        except Exception as e:
            raise Exception(f"Failed to execute Redfish command: {str(e)}")

    def close_session(self, session):
        """
        Closes an open Redfish session.

        Args:
            session (redfish.rest.v1.RedfishClient): The Redfish client session to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            session.logout()
        except Exception as e:
            raise Exception(f"Failed to close Redfish session: {str(e)}")
