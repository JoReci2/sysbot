import subprocess
import platform
import base64
from sysbot.utils.engine import ConnectorInterface


class Bash(ConnectorInterface):
    """
    This class provides methods for executing commands locally on the system using Bash.
    No network connection or credentials are required.
    """

    DEFAULT_PORT = None  # Localhost doesn't use ports

    def __init__(self):
        super().__init__()
        self.default_port = self.DEFAULT_PORT

    def open_session(self, host=None, port=None, login=None, password=None):
        """
        Opens a local session. No actual session is created for localhost.

        Args:
            host (str, optional): Ignored for localhost.
            port (int, optional): Ignored for localhost.
            login (str, optional): Ignored for localhost.
            password (str, optional): Ignored for localhost.

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            # Check if bash is available
            system = platform.system()
            if system == "Windows":
                # Check if Git Bash or WSL is available
                try:
                    subprocess.run(["bash", "--version"], capture_output=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return {
                        "StatusCode": 1,
                        "Result": None,
                        "Error": "Bash not available on this Windows system",
                        "Metadata": {
                            "host": "localhost",
                            "protocol": "localhost",
                            "shell": "bash",
                            "system": system
                        }
                    }

            return {
                "StatusCode": 0,
                "Result": {"type": "localhost", "shell": "bash"},
                "Error": None,
                "Metadata": {
                    "host": "localhost",
                    "protocol": "localhost",
                    "shell": "bash",
                    "system": system
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to initialize localhost session: {str(e)}",
                "Metadata": {
                    "host": "localhost",
                    "protocol": "localhost",
                    "shell": "bash",
                    "system": platform.system()
                }
            }

    def execute_command(self, session, command, runas=False, password=None):
        """
        Executes a command locally using Bash.

        Args:
            session: The session object (from Result field of open_session)
            command (str): The command to execute
            runas (bool): Whether to run with elevated privileges (sudo on Linux/Mac)
            password (str): Password for sudo authentication (if required)

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            encoded_command = base64.b64encode(command.encode("utf-8")).decode("ascii")

            if runas and password is not None:
                payload = f"echo '{password}' | sudo -S bash -c 'echo {encoded_command} | base64 -d | bash'"
            elif runas and password is None:
                payload = f"sudo bash -c 'echo {encoded_command} | base64 -d | bash'"
            else:
                payload = f"echo {encoded_command} | base64 -d | bash"

            result = subprocess.run(
                ["bash", "-c", payload],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                return {
                    "StatusCode": result.returncode,
                    "Result": result.stdout.strip(),
                    "Error": result.stderr.strip() if result.stderr else None,
                    "Metadata": {
                        "command": command,
                        "runas": runas,
                        "shell": "bash"
                    }
                }

            return {
                "StatusCode": 0,
                "Result": result.stdout.strip(),
                "Error": None,
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "bash"
                }
            }
        except subprocess.TimeoutExpired:
            return {
                "StatusCode": 124,
                "Result": None,
                "Error": "Command execution timed out after 300 seconds",
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "bash"
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to execute command: {str(e)}",
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "bash"
                }
            }

    def close_session(self, session):
        """
        Closes the localhost session. This is a no-op for localhost.

        Args:
            session: The session object (from Result field of open_session)

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        return {
            "StatusCode": 0,
            "Result": "Localhost session closed (no action needed)",
            "Error": None,
            "Metadata": {
                "shell": "bash"
            }
        }


class Powershell(ConnectorInterface):
    """
    This class provides methods for executing PowerShell commands locally on the system.
    No network connection or credentials are required.
    """

    DEFAULT_PORT = None  # Localhost doesn't use ports

    def __init__(self):
        super().__init__()
        self.default_port = self.DEFAULT_PORT

    def open_session(self, host=None, port=None, login=None, password=None):
        """
        Opens a local PowerShell session. No actual session is created for localhost.

        Args:
            host (str, optional): Ignored for localhost.
            port (int, optional): Ignored for localhost.
            login (str, optional): Ignored for localhost.
            password (str, optional): Ignored for localhost.

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            # Check if PowerShell is available
            system = platform.system()
            powershell_cmd = "pwsh" if system != "Windows" else "powershell"

            # Try pwsh first (PowerShell Core), fall back to powershell on Windows
            try:
                subprocess.run([powershell_cmd, "-Version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                if system == "Windows":
                    powershell_cmd = "powershell"
                    subprocess.run([powershell_cmd, "-Version"], capture_output=True, check=True)
                else:
                    return {
                        "StatusCode": 1,
                        "Result": None,
                        "Error": "PowerShell not available on this system",
                        "Metadata": {
                            "host": "localhost",
                            "protocol": "localhost",
                            "shell": "powershell",
                            "system": system
                        }
                    }

            return {
                "StatusCode": 0,
                "Result": {"type": "localhost", "shell": "powershell", "command": powershell_cmd},
                "Error": None,
                "Metadata": {
                    "host": "localhost",
                    "protocol": "localhost",
                    "shell": "powershell",
                    "system": system,
                    "powershell_command": powershell_cmd
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to initialize localhost PowerShell session: {str(e)}",
                "Metadata": {
                    "host": "localhost",
                    "protocol": "localhost",
                    "shell": "powershell",
                    "system": platform.system()
                }
            }

    def execute_command(self, session, command, runas=False, username=None, password=None):
        """
        Executes a PowerShell command locally.

        Args:
            session: The session object (from Result field of open_session)
            command (str): The PowerShell command to execute
            runas (bool): Whether to run with elevated privileges
            username (str): Username for elevated execution (if different from current user)
            password (str): Password for elevated execution (if required)

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Result" in session:
                ps_session = session["Result"]
            else:
                ps_session = session

            powershell_cmd = ps_session.get("command", "powershell") if isinstance(ps_session, dict) else "powershell"

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

            result = subprocess.run(
                [powershell_cmd, "-EncodedCommand", encoded_command],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                return {
                    "StatusCode": result.returncode,
                    "Result": result.stdout.strip(),
                    "Error": result.stderr.strip() if result.stderr else None,
                    "Metadata": {
                        "command": command,
                        "runas": runas,
                        "shell": "powershell"
                    }
                }

            return {
                "StatusCode": 0,
                "Result": result.stdout.strip(),
                "Error": None,
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "powershell"
                }
            }
        except subprocess.TimeoutExpired:
            return {
                "StatusCode": 124,
                "Result": None,
                "Error": "Command execution timed out after 300 seconds",
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "powershell"
                }
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to execute command: {str(e)}",
                "Metadata": {
                    "command": command,
                    "runas": runas,
                    "shell": "powershell"
                }
            }

    def close_session(self, session):
        """
        Closes the localhost PowerShell session. This is a no-op for localhost.

        Args:
            session: The session object (from Result field of open_session)

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata.
        """
        return {
            "StatusCode": 0,
            "Result": "Localhost PowerShell session closed (no action needed)",
            "Error": None,
            "Metadata": {
                "shell": "powershell"
            }
        }
