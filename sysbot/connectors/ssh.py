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
    Hardware SSH Connector for Network Devices

    This class provides methods for interacting with hardware network devices using SSH.
    It uses the netmiko library to establish and manage SSH connections to
    network equipment such as Cisco switches, routers, and other network devices.

    This connector is designed for devices with non-standard SSH interfaces that
    don't provide a traditional shell environment (bash/powershell).

    Features:
        - Automatic device type detection using netmiko's SSHDetect
        - Support for 100+ device types (Cisco, Arista, Juniper, HP, Dell, Palo Alto, etc.)
        - Direct CLI command execution without shell wrapping
        - Enable mode support for privileged commands
        - Configurable timeouts and connection parameters

    Supported Device Types:
        - Cisco: cisco_ios, cisco_nxos, cisco_asa, cisco_xe, cisco_xr
        - Arista: arista_eos
        - Juniper: juniper_junos
        - HP: hp_comware, hp_procurve
        - Dell: dell_force10, dell_os10
        - Palo Alto: paloalto_panos
        - And many more (see netmiko documentation)

    Usage Examples:
        Basic usage with automatic device detection:

        >>> from sysbot.Sysbot import Sysbot
        >>> bot = Sysbot()
        >>> bot.open_session(
        ...     alias='my_switch',
        ...     protocol='ssh',
        ...     product='hardware',
        ...     host='192.168.1.1',
        ...     port=22,
        ...     login='admin',
        ...     password='password'
        ... )
        >>> output = bot.execute_command('my_switch', 'show version')
        >>> print(output)
        >>> bot.close_all_sessions()

        With explicit device type (skips autodetection):

        >>> bot.open_session(
        ...     alias='my_switch',
        ...     protocol='ssh',
        ...     product='hardware',
        ...     host='192.168.1.1',
        ...     port=22,
        ...     login='admin',
        ...     password='password',
        ...     device_type='cisco_nxos'
        ... )

        With enable mode for privileged commands:

        >>> bot.open_session(
        ...     alias='my_switch',
        ...     protocol='ssh',
        ...     product='hardware',
        ...     host='192.168.1.1',
        ...     port=22,
        ...     login='admin',
        ...     password='password',
        ...     secret='enable_password',
        ...     device_type='cisco_ios'
        ... )

        With custom timeouts:

        >>> bot.open_session(
        ...     alias='my_switch',
        ...     protocol='ssh',
        ...     product='hardware',
        ...     host='192.168.1.1',
        ...     port=22,
        ...     login='admin',
        ...     password='password',
        ...     timeout=60,
        ...     session_timeout=60
        ... )

        Robot Framework example:

        >>> # Automatic detection
        >>> Open Session    my_switch    ssh    hardware    192.168.1.1    22    admin    password
        >>> ${output}=    Execute Command    my_switch    show version
        >>> Log    ${output}
        >>> Close All Sessions

        Robot Framework with explicit device type:

        >>> Open Session    my_switch    ssh    hardware    192.168.1.1    22    admin    password    device_type=cisco_ios
        >>> ${output}=    Execute Command    my_switch    show running-config
        >>> Close Session    my_switch

    Notes:
        - Autodetection adds a small overhead on first connection (creates temporary connection to detect type)
        - For production environments with known device types, consider specifying device_type explicitly
        - The connector automatically handles device-specific command formatting and output parsing
        - Some devices may require the 'secret' parameter for enable/privileged mode access

    See Also:
        - netmiko documentation: https://github.com/ktbyers/netmiko
        - Supported platforms: https://github.com/ktbyers/netmiko/blob/develop/PLATFORMS.md
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

        Examples:
            >>> # Default initialization with autodetect
            >>> connector = Hardware()

            >>> # Custom port
            >>> connector = Hardware(port=2222)

            >>> # Explicit device type (skips autodetection)
            >>> connector = Hardware(device_type='cisco_nxos')

            >>> # Custom port with explicit device type
            >>> connector = Hardware(port=2222, device_type='arista_eos')
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
            Exception: If there is an error opening the session or autodetection fails.

        Examples:
            >>> # Automatic device detection (default)
            >>> session = connector.open_session(
            ...     host='192.168.1.1',
            ...     port=22,
            ...     login='admin',
            ...     password='password'
            ... )

            >>> # Explicit device type
            >>> session = connector.open_session(
            ...     host='192.168.1.1',
            ...     port=22,
            ...     login='admin',
            ...     password='password',
            ...     device_type='cisco_ios'
            ... )

            >>> # With enable password for privileged mode
            >>> session = connector.open_session(
            ...     host='192.168.1.1',
            ...     port=22,
            ...     login='admin',
            ...     password='password',
            ...     secret='enable_password',
            ...     device_type='cisco_ios'
            ... )

            >>> # With custom timeouts
            >>> session = connector.open_session(
            ...     host='192.168.1.1',
            ...     port=22,
            ...     login='admin',
            ...     password='password',
            ...     timeout=120,
            ...     session_timeout=120
            ... )

        Notes:
            - When device_type is "autodetect", a temporary connection is created
              to detect the device type, then disconnected before establishing the
              final connection.
            - Autodetection may add 5-10 seconds to connection time.
            - If autodetection fails, specify device_type explicitly.
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
            session: The netmiko connection object returned by open_session.
            command (str): The command to execute on the device.
            **kwargs: Additional netmiko command options:
                - expect_string (str): Regular expression pattern to expect in output.
                - delay_factor (int): Multiplier for internal delays (default: 1).
                - max_loops (int): Maximum number of read loops (default: 500).
                - strip_prompt (bool): Remove trailing prompt from output (default: True).
                - strip_command (bool): Remove echoed command from output (default: True).

        Returns:
            str: The output of the command execution.

        Raises:
            Exception: If there is an error executing the command.

        Examples:
            >>> # Simple command execution
            >>> output = connector.execute_command(session, 'show version')
            >>> print(output)

            >>> # Command with delay factor for slow devices
            >>> output = connector.execute_command(
            ...     session,
            ...     'show tech-support',
            ...     delay_factor=2
            ... )

            >>> # Command with custom expect string
            >>> output = connector.execute_command(
            ...     session,
            ...     'show running-config',
            ...     expect_string=r'#'
            ... )

            >>> # Multiple commands
            >>> version = connector.execute_command(session, 'show version')
            >>> interfaces = connector.execute_command(session, 'show ip interface brief')
            >>> vlans = connector.execute_command(session, 'show vlan')

        Notes:
            - Commands are sent directly to the device CLI without shell wrapping.
            - The device's command prompt is automatically stripped from output.
            - For configuration commands, consider using netmiko's send_config_set method
              through the session object directly.
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

        Examples:
            >>> # Close a single session
            >>> connector.close_session(session)

            >>> # Using with context (recommended pattern)
            >>> session = None
            >>> try:
            ...     session = connector.open_session(
            ...         host='192.168.1.1',
            ...         port=22,
            ...         login='admin',
            ...         password='password'
            ...     )
            ...     output = connector.execute_command(session, 'show version')
            ...     print(output)
            ... finally:
            ...     if session:
            ...         connector.close_session(session)

        Notes:
            - Always close sessions when done to free resources.
            - The connection is gracefully disconnected.
            - Calling close on an already closed session may raise an exception.
        """
        try:
            session.disconnect()
        except Exception as e:
            raise Exception(f"Failed to close SSH hardware session: {str(e)}")
