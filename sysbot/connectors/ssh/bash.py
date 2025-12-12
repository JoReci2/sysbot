from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException
from sysbot.utils.engine import ConnectorInterface
from sysbot.connectors.config import DEFAULT_PORTS, create_response


class Bash(ConnectorInterface):
    """
    Generic SSH connector using Netmiko with automatic device type detection.
    Supports bash shells on Linux, Unix, network devices, and other SSH-enabled systems.
    """

    def open_session(self, host, port=None, login=None, password=None, device_type="autodetect", **kwargs):
        """
        Opens an SSH session using Netmiko with automatic device detection.
        
        Args:
            host (str): Hostname or IP address
            port (int): SSH port (default: 22)
            login (str): Username for authentication
            password (str): Password for authentication
            device_type (str): Device type for Netmiko (default: 'autodetect')
            **kwargs: Additional Netmiko connection parameters
        
        Returns:
            dict: Session information including connection object
        """
        if port is None:
            port = DEFAULT_PORTS["ssh"]
            
        try:
            device_params = {
                "device_type": device_type,
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
                "device_type": connection.device_type if hasattr(connection, "device_type") else device_type
            }
        except NetMikoAuthenticationException as e:
            raise Exception(f"SSH authentication failed for {host}:{port}: {str(e)}")
        except NetMikoTimeoutException as e:
            raise Exception(f"SSH connection timeout for {host}:{port}: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to open SSH session to {host}:{port}: {str(e)}")

    def execute_command(self, session, command, runas=False, password=None, **kwargs):
        """
        Executes a command via SSH using Netmiko.

        Args:
            session (dict): Session dictionary containing connection object
            command (str): The command to execute
            runas (bool): Whether to run with elevated privileges using sudo
            password (str): Password for sudo authentication (if required)
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
            # Handle sudo execution if requested
            if runas:
                if password:
                    # Send sudo command with password
                    output = connection.send_command(
                        f"echo '{password}' | sudo -S {command}",
                        expect_string=r"#|\$",
                        strip_prompt=True,
                        strip_command=True
                    )
                else:
                    # Assume passwordless sudo or already privileged
                    output = connection.send_command(
                        f"sudo {command}",
                        expect_string=r"#|\$",
                        strip_prompt=True,
                        strip_command=True
                    )
            else:
                output = connection.send_command(
                    command,
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
