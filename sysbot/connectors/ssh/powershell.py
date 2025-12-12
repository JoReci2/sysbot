from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException
from sysbot.utils.engine import ConnectorInterface
from sysbot.connectors.config import DEFAULT_PORTS, create_response
import base64


class Powershell(ConnectorInterface):
    """
    Generic SSH connector for PowerShell using Netmiko.
    Supports PowerShell over SSH on Windows systems.
    """

    def open_session(self, host, port=None, login=None, password=None, **kwargs):
        """
        Opens an SSH session to a PowerShell-enabled system using Netmiko.
        
        Args:
            host (str): Hostname or IP address
            port (int): SSH port (default: 22)
            login (str): Username for authentication
            password (str): Password for authentication
            **kwargs: Additional Netmiko connection parameters
        
        Returns:
            dict: Session information including connection object
        """
        if port is None:
            port = DEFAULT_PORTS["ssh"]
            
        try:
            device_params = {
                "device_type": "terminal_server",  # Generic device type for PowerShell
                "host": host,
                "port": port,
                "username": login,
                "password": password,
                "timeout": kwargs.get("timeout", 30),
                "session_timeout": kwargs.get("session_timeout", 60),
            }
            
            # Add any additional parameters
            device_params.update({k: v for k, v in kwargs.items() 
                                if k not in ["timeout", "session_timeout"]})
            
            connection = ConnectHandler(**device_params)
            
            return {
                "connection": connection,
                "host": host,
                "port": port,
                "device_type": "powershell"
            }
        except NetMikoAuthenticationException as e:
            raise Exception(f"SSH authentication failed for {host}:{port}: {str(e)}")
        except NetMikoTimeoutException as e:
            raise Exception(f"SSH connection timeout for {host}:{port}: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to open SSH session to {host}:{port}: {str(e)}")

    def execute_command(self, session, command, runas=False, username=None, password=None, **kwargs):
        """
        Executes a PowerShell command via SSH using Netmiko.

        Args:
            session (dict): Session dictionary containing connection object
            command (str): The PowerShell command to execute
            runas (bool): Whether to run with elevated privileges
            username (str): Username for elevated execution (if different from session user)
            password (str): Password for elevated execution (if required)
            **kwargs: Additional execution parameters

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata
        """
        if not session or "connection" not in session:
            return create_response(
                status_code=1,
                result=None,
                error="Invalid session: connection not found"
            )
        
        connection = session["connection"]
        
        try:
            # Handle RunAs execution if requested
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

            # Encode command for PowerShell
            encoded_command = base64.b64encode(
                final_command.encode("utf_16_le")
            ).decode("ascii")
            
            # Execute through netmiko
            output = connection.send_command(
                f"powershell.exe -encodedcommand {encoded_command}",
                strip_prompt=kwargs.get("strip_prompt", True),
                strip_command=kwargs.get("strip_command", True)
            )
            
            return create_response(
                status_code=0,
                result=output,
                error=None,
                metadata={
                    "device_type": session.get("device_type"),
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
                    "device_type": session.get("device_type"),
                    "host": session.get("host"),
                    "command": command
                }
            )

    def close_session(self, session):
        """
        Closes the SSH session.
        
        Args:
            session (dict): Session dictionary containing connection object
        """
        if session and "connection" in session:
            try:
                session["connection"].disconnect()
            except Exception as e:
                raise Exception(f"Failed to close SSH session: {str(e)}")
