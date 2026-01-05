"""
WinRM Connector Module

This module provides Windows Remote Management (WinRM) connectors for remote
Windows system management. It supports PowerShell execution over WinRM using
the pywinrm library for establishing and managing sessions.
"""
from winrm.protocol import Protocol
from base64 import b64encode
from sysbot.utils.engine import ConnectorInterface


class Powershell(ConnectorInterface):
    """
    This class provides methods for interacting with Windows systems using
    the Windows Remote Management (WinRM) protocol.
    It uses the pywinrm library to establish and manage sessions.
    """

    def __init__(self, port=5986):
        """
        Initialize WinRM PowerShell connector with default port.

        Args:
            port (int): Default WinRM HTTPS port (default: 5986).
        """
        super().__init__()
        self.default_port = port

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens a WinRM session to a Windows system.

        Args:
            host (str): Hostname or IP address of the Windows system.
            port (int): Port of the WinRM service. If None, uses default_port.
            login (str): Username for the session.
            password (str): Password for the session.

        Returns:
            dict: A dictionary containing the protocol and shell objects.

        Raises:
            Exception: If there is an error opening the session.
        """
        if port is None:
            port = self.default_port
        try:
            p = Protocol(
                endpoint=f"https://{host}:{port}/wsman",
                transport="ntlm",
                username=login,
                password=password,
                server_cert_validation="ignore",
            )

            shell = p.open_shell()
            session = {"protocol": p, "shell": shell}

            return session
        except Exception as e:
            raise Exception(f"Failed to open WinRM session: {str(e)}")

    def execute_command(
        self, session, command, runas=False, username=None, password=None
    ):
        """
        Executes a PowerShell command on a Windows system via WinRM.

        Args:
            session (dict): The session dictionary containing the protocol and shell.
            command (str): The PowerShell command to execute on the Windows system.
            runas (bool): Whether to run with elevated privileges
            username (str): Username for elevated execution (if different from session user)
            password (str): Password for elevated execution (if required)

        Returns:
            str: The output of the command.

        Raises:
            Exception: If there is an error executing the command.
        """
        try:
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
            payload = session["protocol"].run_command(
                session["shell"],
                "powershell -encodedcommand {0}".format(encoded_command),
            )
            stdout, stderr, status_code = session["protocol"].get_command_output(
                session["shell"], payload
            )
            session["protocol"].cleanup_command(session["shell"], payload)
            return stdout
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes the WinRM session to a Windows system.

        Args:
            session (dict): The session dictionary containing the protocol and shell.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            session["protocol"].close_shell(session["shell"])
        except Exception as e:
            raise Exception(f"Failed to close WinRM session: {str(e)}")
