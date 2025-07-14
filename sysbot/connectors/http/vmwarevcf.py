import requests
import json
from ...utils import ConnectorInterface

class Vmwarevcf(ConnectorInterface):
    """Manages connections and operations for SDDC (Software-Defined Data Center) VCF components.
    Provides structured interaction with SDDCManager (VCF) through token-based management.
    """

    def open_session(self, host, port, login, password):
        """
        Establish connection to SDDC Manager API endpoint.
        """
        session = requests.Session()
        try:
            response = session.post(
                f"https://{host}/v1/tokens",
                verify=False,
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                timeout=10,
                json={
                    'username': login,
                    'password': password
                },
            )
        except Exception as e:
            raise TypeError(f"SDDCManager REST session error")
         
        response_json = response.json()
        if 'accessToken' not in response_json:
            raise Exception("No accessToken when connecting to SDDCManager : please check if credentials are valid")
        
        session_data = {'session': session, 'host': host, 'access_token': response_json['accessToken']}
        return session_data

    def execute_command(self, session, command, options):
        """
        Executes a command on a SddcManager API.
        """
        try:
            response = session['session'].get(f'https://{session['host']}{command}', 
                verify=False,
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f"Bearer {session['access_token']}"
                },
                timeout=10)
            return json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_all_sessions(self):
        pass

    