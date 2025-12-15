import requests
from requests.auth import HTTPBasicAuth
from pyVim.connect import SmartConnect, Disconnect
from sysbot.utils.engine import ConnectorInterface


class Basicauth(ConnectorInterface):
    """
    This class provides methods for interacting with an API using basic authentication.
    It uses the requests library to establish and manage sessions.
    """

    DEFAULT_PORT = 443

    def __init__(self):
        super().__init__()
        self.default_port = self.DEFAULT_PORT

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens a session to an API with basic auth.

        Args:
            host (str): Hostname or IP address of the API.
            port (int, optional): Port of the API. Defaults to 443.
            login (str): Username for authentication.
            password (str): Password for authentication.

        Returns:
            dict: Standardized response with StatusCode, Result, and Error.
        """
        try:
            if port is None:
                port = self.DEFAULT_PORT

            session_data = {
                "host": host,
                "port": port,
                "login": login,
                "password": password,
            }

            return {
                "StatusCode": 0,
                "Session": session_data,
                "Result": "Session opened successfully",
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Result": None,
                "Error": f"Failed to create basic auth session: {str(e)}"
            }

    def execute_command(self, session, command, options=None):
        """
        Executes a command (HTTP request) on an API with basic auth.

        Args:
            session: The session data (from Session field of open_session)
            command (str): The URL path/endpoint to request
            options (dict, optional): Request options like params, headers, etc.

        Returns:
            dict: Standardized response with StatusCode, Result, and Error.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Session" in session:
                session_data = session["Session"]
            else:
                session_data = session

            base_url = f"https://{session_data['host']}:{session_data['port']}{command}"
            basic = HTTPBasicAuth(session_data["login"], session_data["password"])

            if options and "params" in options:
                result = requests.get(
                    base_url, params=options["params"], verify=False, auth=basic
                )
            else:
                result = requests.get(base_url, verify=False, auth=basic)

            if result.status_code != 200:
                return {
                    "StatusCode": result.status_code,
                    "Result": result.content,
                    "Error": f"HTTP request failed with status code: {result.status_code}"
                }

            return {
                "StatusCode": 0,
                "Session": result.content,
                "Result": "Session opened successfully",
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Result": None,
                "Error": f"Failed to execute command: {str(e)}"
            }

    def close_session(self, session):
        """
        Closes the session to the API with basic auth.

        Args:
            session: The session data (from Session field of open_session)

        Returns:
            dict: Standardized response with StatusCode, Result, and Error.
        """
        return {
            "StatusCode": 0,
            "Session": "Basic auth session closed (no action needed)",
                "Result": "Session opened successfully",
            "Error": None
        }


class Vsphere(ConnectorInterface):
    """
    This class provides methods for interacting with VMware systems.
    It uses the pyVim library to establish and manage connections.
    """

    DEFAULT_PORT = 443

    def __init__(self):
        super().__init__()
        self.default_port = self.DEFAULT_PORT

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens a session to a VMware system.

        Args:
            host (str): Hostname or IP address of the VMware system.
            port (int, optional): Port of the VMware service. Defaults to 443.
            login (str): Username for the session.
            password (str): Password for the session.

        Returns:
            dict: Standardized response with StatusCode, Result, and Error.
        """
        try:
            if port is None:
                port = self.DEFAULT_PORT

            client = SmartConnect(
                host=host,
                port=port,
                user=login,
                pwd=password,
                disableSslCertValidation=True,
            )

            return {
                "StatusCode": 0,
                "Session": client,
                "Result": "Session opened successfully",
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Result": None,
                "Error": f"Failed to open VMware session: {str(e)}"
            }

    def execute_command(self, session, command, options=None):
        """
        Placeholder for executing a command on a VMware system.

        Args:
            session: The VMware client session (from Session field of open_session)
            command (str): The command to execute (currently a placeholder).
            options (dict, optional): Additional options for the command.

        Returns:
            dict: Standardized response with StatusCode, Result, and Error.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Session" in session:
                client = session["Session"]
            else:
                client = session

            # This function is a placeholder and returns the session
            return {
                "StatusCode": 0,
                "Session": client,
                "Result": "Session opened successfully",
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Result": None,
                "Error": f"Failed to execute command: {str(e)}"
            }

    def close_session(self, session):
        """
        Closes an open session to a VMware system.

        Args:
            session: The VMware client session (from Session field of open_session)

        Returns:
            dict: Standardized response with StatusCode, Result, and Error.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Session" in session:
                client = session["Session"]
            else:
                client = session

            Disconnect(client)

            return {
                "StatusCode": 0,
                "Session": "VMware session closed successfully",
                "Result": "Session opened successfully",
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Result": None,
                "Error": f"Failed to close VMware session: {str(e)}"
            }
