import paramiko
import base64
from sysbot.utils.engine import ConnectorInterface


class Bash(ConnectorInterface):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell).
    It uses the Paramiko library to establish and manage SSH connections for Bash shells.
    """

    DEFAULT_PORT = 22

    def __init__(self):
        super().__init__()
        self.default_port = self.DEFAULT_PORT

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens an SSH session to a system.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int, optional): SSH port. Defaults to 22.
            login (str): Username for authentication.
            password (str): Password for authentication.

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            if port is None:
                port = self.DEFAULT_PORT

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=login, password=password)

            return {
                "StatusCode": 0,
                "Result": client,
                "Error": None,
                "Metadata": {
                    "host": host,
                    "port": port,
                    "protocol": "ssh",
                    "shell": "bash"
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to open SSH session: {str(e)}",
                "Metadata": {
                    "host": host,
                    "port": port or self.DEFAULT_PORT,
                    "protocol": "ssh",
                    "shell": "bash"
                }
            }

    def execute_command(self, session, command, runas=False, password=None):
        """
        Executes a command on a system via SSH.

        Args:
            session: The SSH session object (from Result field of open_session)
            command (str): The command to execute
            runas (bool): Whether to run with elevated privileges using sudo
            password (str): Password for sudo authentication (if required)

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Result" in session:
                client = session["Result"]
            else:
                client = session

            encoded_command = base64.b64encode(command.encode("utf-8")).decode("ascii")

            if runas and password is not None:
                payload = f"echo '{password}' | sudo -S bash -c 'echo {encoded_command} | base64 -d | bash'"
            elif runas and password is None:
                payload = f"sudo bash -c 'echo {encoded_command} | base64 -d | bash'"
            else:
                payload = f"echo {encoded_command} | base64 -d | bash"

            stdin, stdout, stderr = client.exec_command(payload, get_pty=True)
            stdin.close()

            output = stdout.read().decode("utf-8").strip()
            error = stderr.read().decode("utf-8").strip()

            stdout.close()
            stderr.close()

            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0:
                return {
                    "StatusCode": exit_status,
                    "Result": output,
                    "Error": error if error else None,
                    "Metadata": {
                        "command": command,
                        "runas": runas,
                        "shell": "bash"
                    }
                }

            return {
                "StatusCode": 0,
                "Result": output,
                "Error": None,
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "bash"
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to execute command: {str(e)}",
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "bash"
                }
            }

    def close_session(self, session):
        """
        Closes an open SSH session.

        Args:
            session: The SSH session object (from Result field of open_session)

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Result" in session:
                client = session["Result"]
            else:
                client = session

            client.close()

            return {
                "StatusCode": 0,
                "Result": "Session closed successfully",
                "Error": None,
                "Metadata": {
                    "shell": "bash"
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to close SSH session: {str(e)}",
                "Metadata": {
                    "shell": "bash"
                }
            }


class Powershell(ConnectorInterface):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell).
    It uses the Paramiko library to establish and manage SSH connections for PowerShell.
    """

    DEFAULT_PORT = 22

    def __init__(self):
        super().__init__()
        self.default_port = self.DEFAULT_PORT

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens an SSH session to a system.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int, optional): SSH port. Defaults to 22.
            login (str): Username for authentication.
            password (str): Password for authentication.

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            if port is None:
                port = self.DEFAULT_PORT

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=login, password=password)

            return {
                "StatusCode": 0,
                "Result": client,
                "Error": None,
                "Metadata": {
                    "host": host,
                    "port": port,
                    "protocol": "ssh",
                    "shell": "powershell"
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to open SSH session: {str(e)}",
                "Metadata": {
                    "host": host,
                    "port": port or self.DEFAULT_PORT,
                    "protocol": "ssh",
                    "shell": "powershell"
                }
            }

    def execute_command(self, session, command, runas=False, username=None, password=None):
        """
        Executes a PowerShell command on a system via SSH.

        Args:
            session: The SSH session object (from Result field of open_session)
            command (str): The PowerShell command to execute
            runas (bool): Whether to run with elevated privileges
            username (str): Username for elevated authentication (if required)
            password (str): Password for elevated authentication (if required)

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Result" in session:
                client = session["Result"]
            else:
                client = session

            if runas and username and password:
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
            elif runas:
                final_command = (
                    f"Start-Process PowerShell -Verb RunAs "
                    f'-ArgumentList "-Command", "{command}" -Wait'
                )
            else:
                final_command = command

            encoded_command = base64.b64encode(
                final_command.encode("utf_16_le")
            ).decode("ascii")

            stdin, stdout, stderr = client.exec_command(
                "powershell.exe -encodedcommand {0}".format(encoded_command),
                get_pty=False,
            )
            stdin.close()

            output = stdout.read().decode("utf-8").strip()
            error = stderr.read().decode("utf-8").strip()

            stdout.close()
            stderr.close()

            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0:
                return {
                    "StatusCode": exit_status,
                    "Result": output,
                    "Error": error if error else None,
                    "Metadata": {
                        "command": command,
                        "runas": runas,
                        "shell": "powershell"
                    }
                }

            return {
                "StatusCode": 0,
                "Result": output,
                "Error": None,
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "powershell"
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to execute command: {str(e)}",
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "powershell"
                }
            }

    def close_session(self, session):
        """
        Closes an open SSH session.

        Args:
            session: The SSH session object (from Result field of open_session)

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Result" in session:
                client = session["Result"]
            else:
                client = session

            client.close()

            return {
                "StatusCode": 0,
                "Result": "Session closed successfully",
                "Error": None,
                "Metadata": {
                    "shell": "powershell"
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to close SSH session: {str(e)}",
                "Metadata": {
                    "shell": "powershell"
                }
            }
