"""
MIT License

Copyright (c) 2024 Thibault SCIRE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import paramiko
import uuid
import json
import time
from ...utils.ConnectorInterface import ConnectorInterface
from ...utils.versionManager import version_manager


class Bash(ConnectorInterface):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell).
    It uses the Paramiko library to establish and manage SSH connections.
    Supports versioned methods for backward compatibility.
    """

    def __init__(self):
        """Initialize the Bash connector with version management."""
        super().__init__()
        self.set_connector_version("1.0.0")

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

    @version_manager.versioned("1.0.0", default="1.0.0")
    def execute_command(self, session, command, runas=False, password=None):
        """
        Executes a command on a system via SSH (version 1.0.0).
        """
        try:
            if runas == True and password != None:
                stdin, stdout, stderr = session.exec_command(f"echo {password} | sudo -S bash", get_pty=True)
            elif runas == True and password == None:
                stdin, stdout, stderr = session.exec_command("sudo bash", get_pty=False)
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

    @version_manager.versioned("1.1.0")
    def execute_command(self, session, command, runas=False, password=None, timeout=30):
        """
        Executes a command on a system via SSH (version 1.1.0 with timeout support).
        """
        try:
            if runas == True and password != None:
                stdin, stdout, stderr = session.exec_command(f"echo {password} | sudo -S bash", get_pty=True, timeout=timeout)
            elif runas == True and password == None:
                stdin, stdout, stderr = session.exec_command("sudo bash", get_pty=False, timeout=timeout)
            else:
                stdin, stdout, stderr = session.exec_command("bash", get_pty=False, timeout=timeout)
            
            stdin.write(command)
            stdin.channel.shutdown_write()
            
            # Wait for command completion with timeout
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            result = {
                "output": output,
                "error": error,
                "exit_status": exit_status,
                "timeout": timeout
            }
            
            if error and exit_status != 0:
                raise Exception(f"Command failed with exit status {exit_status}: {error}")
            
            return result
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    @version_manager.versioned("2.0.0")  
    def execute_command(self, session, command, runas=False, password=None, timeout=30, return_format="string"):
        """
        Executes a command on a system via SSH (version 2.0.0 with flexible return formats).
        
        Args:
            session: SSH session object
            command: Command to execute
            runas: Execute with sudo privileges
            password: Password for sudo
            timeout: Command timeout in seconds
            return_format: "string" for backward compatibility, "dict" for detailed info
        """
        try:
            if runas == True and password != None:
                stdin, stdout, stderr = session.exec_command(f"echo {password} | sudo -S bash", get_pty=True, timeout=timeout)
            elif runas == True and password == None:
                stdin, stdout, stderr = session.exec_command("sudo bash", get_pty=False, timeout=timeout)
            else:
                stdin, stdout, stderr = session.exec_command("bash", get_pty=False, timeout=timeout)
            
            stdin.write(command)
            stdin.channel.shutdown_write()
            
            # Wait for command completion with timeout
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            if return_format == "string":
                # Backward compatibility mode
                if error and exit_status != 0:
                    raise Exception(f"console error: {error}")
                return output
            else:
                # Enhanced mode with full details
                return {
                    "output": output,
                    "error": error,
                    "exit_status": exit_status,
                    "timeout": timeout,
                    "command": command,
                    "success": exit_status == 0
                }
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