import requests
from requests.auth import HTTPBasicAuth
from sysbot.utils.engine import ConnectorInterface


class Basicauth(ConnectorInterface):
    """
    This class provides methods for interacting with an API using basic authentication.
    It uses the requests library to establish and manage sessions.
    """

    def open_session(self, host, port, login, password):
        """
        Opens a session to a API with basic auth.
        """
        session_data = {
            "host": host,
            "port": port,
            "login": login,
            "password": password,
        }
        return session_data

    def execute_command(self, session, command, options):
        """
        Executes a command on a API with basic auth.
        """
        base_url = f"https://{session['host']}:{session['port']}{command}"
        basic = HTTPBasicAuth(session["login"], session["password"])

        if options:
            try:
                result = requests.get(
                    base_url, params=options["params"], verify=False, auth=basic
                )
            except Exception as e:
                raise Exception(f"Failed to execute command: {str(e)}")
        else:
            try:
                result = requests.get(base_url, verify=False, auth=basic)
            except Exception as e:
                raise Exception(f"Failed to execute command: {str(e)}")

        if result.status_code != 200:
            raise Exception(f"Trellix status error: {result.status_code}")
        else:
            return result.content

    def close_session(self, session):
        """
        Closes the session to the API with basic auth.
        """
        try:
            pass
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")
