import subprocess
import base64
import platform
from sysbot.utils.engine import ConnectorInterface


class Bash(ConnectorInterface):
    """
    This class provides methods for executing bash/shell commands locally
    without requiring SSH connection.
    """

    def __init__(self, port=None):
        """
        Initialize Local Bash connector.

        Args:
            port (int): Not used for local execution, kept for interface compatibility.
        """
        super().__init__()
        self.default_port = port

    def open_session(self, host=None, port=None, login=None, password=None):
        """
        Opens a local session (no actual connection needed).

        Args:
            host (str): Not used for local execution, kept for interface compatibility.
            port (int): Not used for local execution, kept for interface compatibility.
            login (str): Not used for local execution, kept for interface compatibility.
            password (str): Not used for local execution, kept for interface compatibility.

        Returns:
            dict: A session dictionary containing system information.

        Raises:
            Exception: If there is an error opening the session.
        """
        try:
            # Return a simple session object with system information
            session = {
                "type": "local_bash",
                "platform": platform.system(),
                "shell": "/bin/bash" if platform.system() != "Windows" else "bash"
            }
            return session
        except Exception as e:
            raise Exception(f"Failed to open local bash session: {str(e)}")

    def execute_command(self, session, command, runas=False, password=None):
        """
        Executes a command locally using bash.

        Args:
            session (dict): The local session object
            command (str): The command to execute
            runas (bool): Whether to run with elevated privileges using sudo
            password (str): Password for sudo authentication (if required)
                          Note: Password is passed via echo which may be visible in process lists

        Returns:
            str: The output of the command execution

        Raises:
            Exception: If there is an error executing the command
        """
        try:
            if runas:
                if password is not None:
                    # Use sudo with password via stdin
                    encoded_command = base64.b64encode(command.encode("utf-8")).decode("ascii")
                    payload = f"echo '{password}' | sudo -S bash -c 'echo {encoded_command} | base64 -d | bash'"
                else:
                    # Use sudo without password (assumes NOPASSWD in sudoers)
                    encoded_command = base64.b64encode(command.encode("utf-8")).decode("ascii")
                    payload = f"sudo bash -c 'echo {encoded_command} | base64 -d | bash'"
            else:
                payload = command

            # Execute the command locally
            result = subprocess.run(
                payload,
                shell=True,
                capture_output=True,
                text=True,
                executable="/bin/bash" if platform.system() != "Windows" else None
            )

            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Command failed"
                raise Exception(f"Command failed with exit code {result.returncode}: {error_msg}")

            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise Exception(f"Failed to execute command: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes a local session (no action needed for local execution).

        Args:
            session (dict): The local session object to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        # No actual cleanup needed for local execution
        pass


class Powershell(ConnectorInterface):
    """
    This class provides methods for executing PowerShell commands locally
    without requiring SSH or WinRM connection.
    """

    def __init__(self, port=None):
        """
        Initialize Local PowerShell connector.

        Args:
            port (int): Not used for local execution, kept for interface compatibility.
        """
        super().__init__()
        self.default_port = port

    def open_session(self, host=None, port=None, login=None, password=None):
        """
        Opens a local session (no actual connection needed).

        Args:
            host (str): Not used for local execution, kept for interface compatibility.
            port (int): Not used for local execution, kept for interface compatibility.
            login (str): Not used for local execution, kept for interface compatibility.
            password (str): Not used for local execution, kept for interface compatibility.

        Returns:
            dict: A session dictionary containing system information.

        Raises:
            Exception: If there is an error opening the session.
        """
        try:
            # Return a simple session object with system information
            session = {
                "type": "local_powershell",
                "platform": platform.system(),
                "shell": "powershell.exe" if platform.system() == "Windows" else "pwsh"
            }
            return session
        except Exception as e:
            raise Exception(f"Failed to open local PowerShell session: {str(e)}")

    def execute_command(self, session, command, runas=False, username=None, password=None):
        """
        Executes a PowerShell command locally.

        Args:
            session (dict): The local session object
            command (str): The PowerShell command to execute
            runas (bool): Whether to run with elevated privileges
            username (str): Username for elevated execution (if different from current user)
            password (str): Password for elevated execution (if required)
                          Note: Password is embedded in PowerShell script which may be visible

        Returns:
            str: The output of the command execution

        Raises:
            Exception: If there is an error executing the command
        """
        try:
            # Determine the PowerShell executable
            shell_exe = session.get("shell", "powershell.exe")
            
            if runas:
                # Encode the command to avoid escaping issues
                encoded_inner_command = base64.b64encode(
                    command.encode("utf-16-le")
                ).decode("ascii")
                
                # For local execution with runas, we need to use Start-Process with elevated privileges
                if username and password:
                    # Create credentials for RunAs with different user
                    ps_command = (
                        f"Start-Process {shell_exe} -Credential $credential "
                        f'-ArgumentList "-EncodedCommand", "{encoded_inner_command}" -Wait -NoNewWindow'
                    )
                    credential_command = f"""
$securePassword = ConvertTo-SecureString '{password}' -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential('{username}', $securePassword)
{ps_command}
"""
                    final_command = credential_command
                else:
                    # Run as administrator using current session (Windows only)
                    # Note: This will fail on non-Windows unless running as root
                    final_command = (
                        f"Start-Process {shell_exe} -Verb RunAs "
                        f'-ArgumentList "-EncodedCommand", "{encoded_inner_command}" -Wait'
                    )
            else:
                final_command = command

            # Encode command in base64 for PowerShell
            encoded_command = base64.b64encode(
                final_command.encode("utf-16-le")
            ).decode("ascii")

            # Execute the command locally
            result = subprocess.run(
                [shell_exe, "-encodedcommand", encoded_command],
                capture_output=True,
                text=True
            )

            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Command failed"
                raise Exception(f"Command failed with exit code {result.returncode}: {error_msg}")

            return result.stdout.strip()
        except subprocess.SubprocessError as e:
            raise Exception(f"Failed to execute PowerShell command: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to execute PowerShell command: {str(e)}")

    def close_session(self, session):
        """
        Closes a local session (no action needed for local execution).

        Args:
            session (dict): The local session object to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        # No actual cleanup needed for local execution
        pass
