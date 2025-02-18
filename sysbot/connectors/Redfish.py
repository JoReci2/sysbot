import redfish
import json

class redfish(object):
    """
    This class provides methods for interacting with systems using the Redfish API.
    It uses the redfish library to establish and manage sessions.
    """

    def open_session(self, host, port, login, password):
        """
        Opens a session to a system using the Redfish API.

        Args:
            host (str): Hostname or IP address of the system.
            port (int): Port of the Redfish API.
            login (str): Username for the session.
            password (str): Password for the session.

        Returns:
            redfish.redfish_client: An authenticated Redfish client session.

        Raises:
            Exception: If there is an error opening the session.
        """
        try:
            client = redfish.redfish_client(base_url=f"https://{host}:{port}", username=login, password=password, default_prefix='/redfish/v1/')
            client.login(auth="session")
            return client
        except Exception as e:
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, session, command):
        """
        Sends a GET request to a system using the Redfish API.

        Args:
            session (redfish.redfish_client): The Redfish client session.
            command (str): The command (endpoint) to send to the system.

        Returns:
            dict: The response data of the GET request.

        Raises:
            Exception: If there is an error executing the command.
        """
        try:
            response = session.get(command)
            return json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes the session to the Redfish API.

        Args:
            session (redfish.redfish_client): The Redfish client session to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            session.logout()
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")