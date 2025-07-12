import redfish as RedfishLibrary
import json
from ...utils.ConnectorInterface import ConnectorInterface

class Redfish(ConnectorInterface):
    """
    This class provides methods for interacting with systems using the Redfish API.
    It uses the redfish library to establish and manage sessions.
    """

    def open_session(self, host, port, login, password):
        """
        Opens a session to a system using the Redfish API.
        """
        try:
            client = RedfishLibrary.redfish_client(base_url=f"https://{host}:{port}", username=login, password=password, default_prefix='/redfish/v1/')
            client.login(auth="session")
            return client
        except Exception as e:
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, session, command, options):
        """
        Sends a GET request to a system using the Redfish API.
        """
        try:
            response = session.get(command)
            return json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes the session to the Redfish API.
        """
        try:
            session.logout()
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")