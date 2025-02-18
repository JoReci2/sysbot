from netmiko import ConnectHandler

class ios(object):
    """
    This is a class for interacting with Cisco IOS devices.
    It uses the Netmiko library to establish and manage SSH connections.
    """

    def open_session(self, host, port, login, password):
        """
        Opens an SSH session to a Cisco IOS device.

        Args:
            host (str): Hostname or IP address of the Cisco IOS device.
            port (int): Port of the SSH server client.
            login (str): Username for the SSH session.
            password (str): Password for the SSH session.

        Returns:
            ConnectHandler: An SSH client session.

        Raises:
            NetmikoAuthenticationException: If authentication fails.
            NetmikoTimeoutException: If the connection times out.
            Exception: For any other exceptions.
        """
        try:
            client = ConnectHandler(device_type='cisco_ios', ip=host, port=port, username=login, password=password)
            return client
        except Exception as e:
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, session, command, options):
        """
        Executes a command on a Cisco IOS device via SSH.

        Args:
            session (ConnectHandler): SSH session.
            command (str): The command to execute on the Cisco IOS device.

        Returns:
            str: The output of the command.

        Raises:
            NetmikoTimeoutException: If the command execution times out.
            Exception: For any other exceptions.
        """
        try:
            output = session.send_command(command)
            return output
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes an active SSH session to a Cisco IOS device.

        Args:
            session (ConnectHandler): SSH session to close.

        Raises:
            Exception: If the session fails to close properly.
        """
        try:
            session.disconnect()
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")