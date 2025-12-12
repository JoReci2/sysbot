from winrm.protocol import Protocol
from base64 import b64encode
from sysbot.utils.engine import ConnectorInterface
from sysbot.connectors.config import DEFAULT_PORTS, create_response


class Powershell(ConnectorInterface):
    """
    WinRM connector for Windows Remote Management using PowerShell.
    Supports remote command execution on Windows systems via WinRM protocol.
    """

    def open_session(self, host, port=None, login=None, password=None, **kwargs):
        """
        Opens a WinRM session to a Windows system.

        Args:
            host (str): Hostname or IP address of the Windows system.
            port (int): Port of the WinRM service (default: 5986 for HTTPS).
            login (str): Username for the session.
            password (str): Password for the session.
            **kwargs: Additional WinRM parameters (transport, server_cert_validation, etc.)

        Returns:
            dict: A dictionary containing the protocol, shell objects, and connection info.

        Raises:
            Exception: If there is an error opening the session.
        """
        if port is None:
            port = DEFAULT_PORTS["winrm"]
            
        try:
            # Default to HTTPS and NTLM transport
            transport = kwargs.get("transport", "ntlm")
            cert_validation = kwargs.get("server_cert_validation", "ignore")
            
            p = Protocol(
                endpoint=f"https://{host}:{port}/wsman",
                transport=transport,
                username=login,
                password=password,
                server_cert_validation=cert_validation,
            )

            shell = p.open_shell()
            session = {
                "protocol": p, 
                "shell": shell,
                "host": host,
                "port": port,
                "transport": transport
            }

            return session
        except Exception as e:
            raise Exception(f"Failed to open WinRM session to {host}:{port}: {str(e)}")

    def execute_command(
        self, session, command, runas=False, username=None, password=None, **kwargs
    ):
        """
        Executes a PowerShell command on a Windows system via WinRM.

        Args:
            session (dict): The session dictionary containing the protocol and shell.
            command (str): The PowerShell command to execute on the Windows system.
            runas (bool): Whether to run with elevated privileges
            username (str): Username for elevated execution (if different from session user)
            password (str): Password for elevated execution (if required)
            **kwargs: Additional execution parameters

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata
            
        Security Note:
            When using runas with credentials, passwords are passed as plain text in
            PowerShell scripts. Ensure WinRM is used over HTTPS and consider the
            security implications in environments with active logging or monitoring.

        Raises:
            Exception: If there is an error executing the command.
        """
        if not session or "protocol" not in session or "shell" not in session:
            return create_response(
                status_code=1,
                result=None,
                error="Invalid session: protocol or shell not found"
            )
            
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
            
            # For backward compatibility, return just stdout for status_code 0
            # But now we provide full structured response
            if status_code == 0:
                return create_response(
                    status_code=0,
                    result=stdout,
                    error=None,
                    metadata={
                        "host": session.get("host"),
                        "port": session.get("port"),
                        "stderr": stderr
                    }
                )
            else:
                return create_response(
                    status_code=status_code,
                    result=stdout,
                    error=stderr,
                    metadata={
                        "host": session.get("host"),
                        "port": session.get("port")
                    }
                )
        except Exception as e:
            return create_response(
                status_code=1,
                result=None,
                error=f"Failed to execute command: {str(e)}",
                metadata={
                    "host": session.get("host"),
                    "command": command
                }
            )

    def close_session(self, session):
        """
        Closes the WinRM session to a Windows system.

        Args:
            session (dict): The session dictionary containing the protocol and shell.

        Raises:
            Exception: If there is an error closing the session.
        """
        if session and "protocol" in session and "shell" in session:
            try:
                session["protocol"].close_shell(session["shell"])
            except Exception as e:
                raise Exception(f"Failed to close WinRM session: {str(e)}")
