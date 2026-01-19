"""
SSH Connector Module

This module provides SSH (Secure Shell) connectors for remote system access.
It supports both Bash and PowerShell execution over SSH using the paramiko
library for establishing and managing secure connections, as well as hardware
network device connections using the netmiko library for non-standard SSH interfaces.
"""
import paramiko
import base64
from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect
from sysbot.utils.engine import ConnectorInterface


class Bash(ConnectorInterface):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell).
    It uses the paramiko library to establish and manage SSH connections.
    """

    def __init__(self, port=22):
        """
        Initialize SSH Bash connector with default port.

        Args:
            port (int): Default SSH port (default: 22).
        """
        super().__init__()
        self.default_port = port

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens an SSH session to a system.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port of the SSH service. If None, uses default_port.
            login (str): Username for the session.
            password (str): Password for the session.

        Returns:
            paramiko.SSHClient: An authenticated SSH client session.

        Raises:
            Exception: If there is an error opening the session.
        """
        if port is None:
            port = self.default_port
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=login, password=password)
            return client
        except Exception as e:
            raise Exception(f"Failed to open SSH session: {str(e)}")

    def execute_command(self, session, command, runas=False, password=None):
        """
        Executes a command on a system via SSH.

        Args:
            session: The SSH session object
            command (str): The command to execute
            runas (bool): Whether to run with elevated privileges using sudo
            password (str): Password for sudo authentication (if required)

        Returns:
            str: The output of the command execution

        Raises:
            Exception: If there is an error executing the command
        """
        try:
            encoded_command = base64.b64encode(command.encode("utf-8")).decode("ascii")

            if runas and password is not None:
                payload = f"echo '{password}' | sudo -S bash -c 'echo {encoded_command} | base64 -d | bash'"
            elif runas and password is None:
                payload = f"sudo bash -c 'echo {encoded_command} | base64 -d | bash'"
            else:
                payload = f"echo {encoded_command} | base64 -d | bash"

            stdin, stdout, stderr = session.exec_command(payload, get_pty=True)
            stdin.close()

            output = stdout.read().decode("utf-8").strip()
            error = stderr.read().decode("utf-8").strip()

            stdout.close()
            stderr.close()

            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0 and error:
                raise Exception(f"Command failed with exit code {exit_status}: {error}")
            return output
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes an open SSH session.

        Args:
            session (paramiko.SSHClient): The SSH client session to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            session.close()
        except Exception as e:
            raise Exception(f"Failed to close SSH session: {str(e)}")


class Powershell(ConnectorInterface):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell)
    with PowerShell commands.
    It uses the paramiko library to establish and manage SSH connections.
    """

    def __init__(self, port=22):
        """
        Initialize SSH PowerShell connector with default port.

        Args:
            port (int): Default SSH port (default: 22).
        """
        super().__init__()
        self.default_port = port

    def open_session(self, host, port=None, login=None, password=None):
        """
        Opens an SSH session to a system.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port of the SSH service. If None, uses default_port.
            login (str): Username for the session.
            password (str): Password for the session.

        Returns:
            paramiko.SSHClient: An authenticated SSH client session.

        Raises:
            Exception: If there is an error opening the session.
        """
        if port is None:
            port = self.default_port
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=login, password=password)
            return client
        except Exception as e:
            raise Exception(f"Failed to open SSH session: {str(e)}")

    def execute_command(self, session, command, runas=False, username=None, password=None):
        """
        Executes a command on a system via SSH.

        Args:
            session: The SSH session object
            command (str): The command to execute
            runas (bool): Whether to run with elevated privileges
            username (str): Username for elevated execution (if different from session user)
            password (str): Password for elevated execution (if required)

        Returns:
            str: The output of the command execution

        Raises:
            Exception: If there is an error executing the command
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

            encoded_command = base64.b64encode(
                final_command.encode("utf_16_le")
            ).decode("ascii")

            stdin, stdout, stderr = session.exec_command(
                "powershell.exe -encodedcommand {0}".format(encoded_command),
                get_pty=False,
            )
            stdin.close()

            output = stdout.read().decode("utf-8").strip()
            error = stderr.read().decode("utf-8").strip()

            stdout.close()
            stderr.close()

            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0 and error:
                raise Exception(f"Command failed with exit code {exit_status}: {error}")
            return output
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes an open SSH session.

        Args:
            session (paramiko.SSHClient): The SSH client session to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            session.close()
        except Exception as e:
            raise Exception(f"Failed to close SSH session: {str(e)}")


class Hardware(ConnectorInterface):
    """
    This class provides methods for interacting with hardware network devices using SSH.
    It uses the netmiko library to establish and manage SSH connections to
    network equipment such as Cisco switches, routers, and other network devices.
    
    This connector is designed for devices with non-standard SSH interfaces that
    don't provide a traditional shell environment (bash/powershell).
    
    The device type is automatically detected using netmiko's SSHDetect unless
    explicitly specified.
    """

    def __init__(self, port=22, device_type="autodetect"):
        """
        Initialize SSH Hardware connector with default port and device type.

        Args:
            port (int): Default SSH port (default: 22).
            device_type (str): Device type for netmiko (default: "autodetect").
                When set to "autodetect", the connector will automatically detect
                the device type. Can be explicitly set to: cisco_ios, cisco_nxos, 
                cisco_asa, arista_eos, juniper_junos, hp_comware, etc.
        """
        super().__init__()
        self.default_port = port
        self.default_device_type = device_type

    def open_session(self, host, port=None, login=None, password=None, **kwargs):
        """
        Opens an SSH session to a network device.

        Args:
            host (str): Hostname or IP address of the target device.
            port (int): Port of the SSH service. If None, uses default_port.
            login (str): Username for the session.
            password (str): Password for the session.
            **kwargs: Additional netmiko connection parameters:
                - device_type (str): Device type for netmiko. If not provided, uses default_device_type.
                  Set to "autodetect" to automatically detect the device type.
                - secret (str): Enable password for privileged mode.
                - timeout (int): Connection timeout in seconds.
                - session_timeout (int): Session timeout in seconds.
                - auth_timeout (int): Authentication timeout in seconds.
                - banner_timeout (int): Banner timeout in seconds.

        Returns:
            netmiko.ConnectHandler: An authenticated SSH connection to the network device.

        Raises:
            Exception: If there is an error opening the session.
        """
        if port is None:
            port = self.default_port
        
        # Extract device_type from kwargs or use default
        device_type = kwargs.pop('device_type', self.default_device_type)
        
        try:
            # Build netmiko connection parameters
            # Note: netmiko uses 'username' while the interface uses 'login'
            device = {
                'host': host,
                'port': port,
                'username': login,  # Map 'login' to netmiko's 'username'
                'password': password,
            }
            
            # Merge any additional kwargs (like secret, timeout, etc.)
            device.update(kwargs)
            
            # Auto-detect device type if requested
            if device_type == "autodetect":
                # Use SSHDetect to determine the device type
                device['device_type'] = 'autodetect'
                guesser = SSHDetect(**device)
                best_match = guesser.autodetect()
                
                # Safely disconnect if connection was established
                if hasattr(guesser, 'connection') and guesser.connection:
                    guesser.connection.disconnect()
                
                if best_match is None:
                    raise Exception(
                        f"Failed to autodetect device type for host {host}. "
                        f"Please specify device_type explicitly (e.g., device_type='cisco_ios')"
                    )
                
                device_type = best_match
            
            # Set the device type
            device['device_type'] = device_type
            
            connection = ConnectHandler(**device)
            return connection
        except Exception as e:
            raise Exception(f"Failed to open SSH hardware session: {str(e)}")

    def execute_command(self, session, command, **kwargs):
        """
        Executes a command on a network device via SSH.

        Args:
            session: The netmiko connection object
            command (str): The command to execute
            **kwargs: Additional netmiko command options (e.g., expect_string, delay_factor)

        Returns:
            str: The output of the command execution

        Raises:
            Exception: If there is an error executing the command
        """
        try:
            output = session.send_command(command, **kwargs)
            return output
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes an open SSH session to a network device.

        Args:
            session: The netmiko connection object to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            session.disconnect()
        except Exception as e:
            raise Exception(f"Failed to close SSH hardware session: {str(e)}")
