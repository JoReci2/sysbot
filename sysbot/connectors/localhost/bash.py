import subprocess
import platform
from sysbot.utils.engine import ConnectorInterface
from sysbot.connectors.config import create_response


class Bash(ConnectorInterface):
    """
    Localhost connector for executing commands on the local system.
    Automatically detects OS and executes appropriate shell commands.
    """

    def open_session(self, host=None, port=None, login=None, password=None, **kwargs):
        """
        Opens a localhost session (no actual connection needed).
        
        Args:
            host (str): Ignored for localhost (kept for interface compatibility)
            port (int): Ignored for localhost (kept for interface compatibility)
            login (str): Ignored for localhost (kept for interface compatibility)
            password (str): Ignored for localhost (kept for interface compatibility)
            **kwargs: Additional parameters
            
        Returns:
            dict: Session information for localhost
        """
        return {
            "type": "localhost",
            "os": platform.system(),
            "shell": self._get_default_shell()
        }
    
    def _get_default_shell(self):
        """Detect the default shell based on OS."""
        os_type = platform.system()
        if os_type == "Windows":
            return "cmd"  # or "powershell"
        else:
            return "bash"  # or "sh"
    
    def execute_command(self, session, command, shell=None, timeout=None, **kwargs):
        """
        Executes a command on the localhost.
        
        Args:
            session (dict): Session dictionary
            command (str): The command to execute
            shell (str): Shell to use (bash, sh, cmd, powershell, etc.)
            timeout (int): Command timeout in seconds
            **kwargs: Additional subprocess parameters
            
        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata
        """
        if not session:
            return create_response(
                status_code=1,
                result=None,
                error="Invalid session"
            )
        
        # Determine shell to use
        if shell is None:
            shell = session.get("shell", "bash")
        
        try:
            # Execute command based on OS and shell
            if platform.system() == "Windows":
                if shell.lower() in ["powershell", "pwsh"]:
                    cmd = ["powershell", "-Command", command]
                else:
                    cmd = ["cmd", "/c", command]
            else:
                if shell.lower() in ["bash", "sh"]:
                    cmd = [shell, "-c", command]
                else:
                    cmd = [shell, "-c", command]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                **kwargs
            )
            
            # Return structured response
            if result.returncode == 0:
                return create_response(
                    status_code=0,
                    result=result.stdout.strip(),
                    error=None,
                    metadata={
                        "os": session.get("os"),
                        "shell": shell,
                        "returncode": result.returncode,
                        "stderr": result.stderr.strip()
                    }
                )
            else:
                return create_response(
                    status_code=result.returncode,
                    result=result.stdout.strip(),
                    error=result.stderr.strip(),
                    metadata={
                        "os": session.get("os"),
                        "shell": shell,
                        "returncode": result.returncode
                    }
                )
                
        except subprocess.TimeoutExpired:
            return create_response(
                status_code=1,
                result=None,
                error=f"Command execution timeout after {timeout} seconds",
                metadata={
                    "os": session.get("os"),
                    "shell": shell,
                    "command": command
                }
            )
        except Exception as e:
            return create_response(
                status_code=1,
                result=None,
                error=f"Failed to execute command: {str(e)}",
                metadata={
                    "os": session.get("os"),
                    "shell": shell,
                    "command": command
                }
            )
    
    def close_session(self, session):
        """
        Closes the localhost session (no-op for localhost).
        
        Args:
            session (dict): Session dictionary
        """
        # No actual connection to close for localhost
        pass
