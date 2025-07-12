import requests
import json
from ..ConnectorInterface import ConnectorInterface

class Vmwarensx(ConnectorInterface):
    """Manages connections and operations for SDDC (Software-Defined Data Center) VCF components.
    Provides structured interaction with SDDCManager (VCF) through token-based management.
    """

    def open_session(self, host, port, login, password) -> dict[requests.Session,str]:
        """Establish connection to NSX-T API endpoint.
        """
        session = requests.Session()
        try:
            response = session.post(
                f"https://{host}/api/session/create",
                verify=False,
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=10,
                data={
                    'j_username': login,
                    'j_password': password
                },
            )
            if response.status_code != 200:
                raise Exception(f'Unable to login on NSX: {response.status_code}')
        except Exception as e:
            raise TypeError(f"SDDCManager REST session error. Error: {e}")

        session_data = {'headers': session.headers,'session': session, 'host': host, 'x-xsrf-token': response.headers.get('x-xsrf-token', '')}
        return session_data

    
    def execute_command(self, session, command, options):
        """
        Executes a command on a NSX API.
        """
        try:
            response = session['session'].get(f'https://{session['host']}{command}', 
                headers={
                    'X-XSRF-TOKEN': session['x-xsrf-token']
                },
                verify=False,
                timeout=10)
            return response
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")


    def close_session(self, session):
        """
        Close NSX session
        """
        try:
            response = session['session'].post(f'https://{session['host']}/api/session/destroy', 
                headers={
                    'X-XSRF-TOKEN': session['x-xsrf-token']
                },
                verify=False,
                timeout=10)
            return response
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")