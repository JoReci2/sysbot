import paramiko
import base64
from sysbot.utils.engine import ConnectorInterface


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
        """
        try:
            session.close()
        except Exception as e:
            raise Exception(f"Failed to close SSH session: {str(e)}")
