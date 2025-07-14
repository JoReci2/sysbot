import paramiko
from ...utils import ConnectorInterface


class Bash(ConnectorInterface):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell).
    It uses the Netmiko library to establish and manage SSH connections.
    """

    def open_session(self, host, port, login, password):
        """
        Opens an SSH session to a system.
        """
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
            if runas and password is not None:
                # Use stdin to pass password securely to sudo
                stdin, stdout, stderr = session.exec_command(
                    "sudo -S bash", get_pty=True
                )
                stdin.write(f"{password}\n{command}")
            elif runas and password is None:
                stdin, stdout, stderr = session.exec_command("sudo bash", get_pty=False)
                stdin.write(command)
            else:
                stdin, stdout, stderr = session.exec_command("bash", get_pty=False)
                stdin.write(command)

            stdin.channel.shutdown_write()
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            if error:
                raise Exception(f"console error: {error}")
            return output
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes an open SSH session.
        """
        try:
            session.close()
        except Exception as e:
            raise Exception(f"Failed to close SSH session: {str(e)}")
