import requests
import json

class neorest(object):
    """
    This class provides methods for interacting with a NEO REST API.
    It uses the requests library to establish and manage sessions.
    """

    def open_session(self, host, port, login, password):
        """
        Opens a session to a NEO REST API.

        Args:
            host (str): Hostname or IP address of the NEO REST API.
            port (int): Port of the NEO REST API.
            login (str): Username for the session.
            password (str): Password for the session.

        Returns:
            dict: A dictionary containing the session and host.

        Raises:
            Exception: If there is an error establishing the session or if the response status is 'ERROR'.
        """
        session = requests.Session()
        try:
            request = session.post(
                f"https://{host}:{port}/admin/launch?script=rh&template=json-request&action=json-login",
                verify=False,
                timeout=10,
                json={
                    'username': login,
                    'password': password
                },
            )
        except Exception as e:
            raise Exception(f"NEO REST session error: {str(e)}")
        
        response = json.loads(request.text)
        if response.get('status') == 'ERROR':
            raise Exception("NEO REST status error")
        
        session_data = {'session': session, 'host': host}
        return session_data

    def execute_command(self, session, command):
        """
        Executes a command on a NEO REST API.

        Args:
            session (dict): The session dictionary containing the session and host.
            command (str): The command to execute on the NEO REST API.

        Returns:
            dict: The response data of the command.

        Raises:
            Exception: If there is an error executing the command.
        """
        try:
            request = session['session'].post(
                f"https://{session['host']}/admin/launch?script=json",
                verify=False,
                timeout=10,
                json={'cmd': command}
            )
            result = json.loads(request.text)
            return result['data']
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes the session to the NEO REST API.

        Args:
            session (dict): The session dictionary containing the session and host.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            session['session'].close()
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")