from winrm.protocol import Protocol
from base64 import b64encode
from sysbot.utils.engine import ConnectorInterface


class Powershell(ConnectorInterface):
    """
    This class provides methods for interacting with Windows systems using
    the Windows Remote Management (WinRM) protocol.
    It uses the pywinrm library to establish and manage sessions.
    """

    DEFAULT_PORT = 5986

    def __init__(self):
        super().__init__()
        self.default_port = self.DEFAULT_PORT

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens a WinRM session to a Windows system.

        Args:
            host (str): Hostname or IP address of the Windows system.
            port (int, optional): Port of the WinRM service. Defaults to 5986.
            login (str): Username for the session.
            password (str): Password for the session.

        Returns:
            dict: Standardized response with StatusCode and Error.
        """
        try:
            if port is None:
                port = self.DEFAULT_PORT

            p = Protocol(
                endpoint=f"https://{host}:{port}/wsman",
                transport="ntlm",
                username=login,
                password=password,
                server_cert_validation="ignore",
            )

            shell = p.open_shell()
            session = {"protocol": p, "shell": shell}

            return {
                "StatusCode": 0,
                "Session": session,
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to open WinRM session: {str(e)}"
            }

    def execute_command(
        self, session, command, runas=False, username=None, password=None
    ):
        """
        Executes a PowerShell command on a Windows system via WinRM.

        Args:
            session: The session dictionary (from Session field of open_session)
            command (str): The PowerShell command to execute on the Windows system.
            runas (bool): Whether to run with elevated privileges
            username (str): Username for elevated execution (if different from session user)
            password (str): Password for elevated execution (if required)

        Returns:
            dict: Standardized response with StatusCode and Error.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Session" in session:
                winrm_session = session["Session"]
            else:
                winrm_session = session

            if runas:
                if username and password:
                    # Create credentials for RunAs
                    ps_command = (
                        f"Start-Process PowerShell -Credential $credential "
                        f'-ArgumentList "-Command", "{command}" -Wait -NoNewWindow'
                    )
                    credential_command = f"""
$securePassword = ConvertTo-SecureString '{password}' -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential('{username}', $securePassword)
{ps_command}
"""
                    final_command = credential_command
                else:
                    # Run as administrator using current session
                    final_command = (
                        f"Start-Process PowerShell -Verb RunAs "
                        f'-ArgumentList "-Command", "{command}" -Wait'
                    )
            else:
                final_command = command

            encoded_command = b64encode(final_command.encode("utf_16_le")).decode(
                "ascii"
            )
            payload = winrm_session["protocol"].run_command(
                winrm_session["shell"],
                "powershell -encodedcommand {0}".format(encoded_command),
            )
            stdout, stderr, status_code = winrm_session["protocol"].get_command_output(
                winrm_session["shell"], payload
            )
            winrm_session["protocol"].cleanup_command(winrm_session["shell"], payload)

            if status_code != 0:
                return {
                    "StatusCode": status_code,
                    "Result": stdout,
                    "Error": stderr if stderr else None
                }

            return {
                "StatusCode": 0,
                "Session": stdout,
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to execute command: {str(e)}"
            }

    def close_session(self, session):
        """
        Closes the WinRM session to a Windows system.

        Args:
            session: The session dictionary (from Session field of open_session)

        Returns:
            dict: Standardized response with StatusCode and Error.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Session" in session:
                winrm_session = session["Session"]
            else:
                winrm_session = session

            winrm_session["protocol"].close_shell(winrm_session["shell"])

            return {
                "StatusCode": 0,
                "Session": "Session closed successfully",
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to close WinRM session: {str(e)}"
            }
