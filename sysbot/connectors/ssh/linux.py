import paramiko

class Linux(object):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell).
    It uses the Netmiko library to establish and manage SSH connections.
    """

    def open_session(self, host, port, login, password):
        """
        Opens an SSH session to a system.

        Args:
            host (str): Hostname or IP address of the system.
            port (int): Port of the SSH server.
            login (str): Username for the SSH session.
            password (str): Password for the SSH session.

        Returns:
            ConnectHandler: An SSH client session.

        Raises:
            Exception: If there is an error opening the SSH session.
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=login, password=password)
            return client
        except Exception as e:
            raise Exception(f"Failed to open SSH session: {str(e)}")

    def execute_command(self, session, command, options):
        """
        Executes a command on a system via SSH.

        Args:
            session (ConnectHandler): The SSH client session.
            command (str): The command to execute on the system.
            options (str): Additional options to pass to the command.

        Returns:
            str: The output of the command.

        Raises:
            Exception: If there is an error executing the command.
        """
        try:
            stdin, stdout, stderr = session.exec_command(command)
            return stdout.read().decode().strip()
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes an open SSH session.

        Args:
            session (ConnectHandler): The SSH client session to close.

        Raises:
            Exception: If there is an error closing the SSH session.
        """
        try:
            session.close()
        except Exception as e:
            raise Exception(f"Failed to close SSH session: {str(e)}")