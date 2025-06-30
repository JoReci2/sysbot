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

from sysbot.connectors.ConnectorHandler import ConnectorInterface
from sysbot.connectors.ssh.utils import sftp

class Linux(ConnectorInterface):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell).
    It uses the Netmiko library to establish and manage SSH connections.
    """

    def __init__(self):
        self.file_execution_base_path   = ".sysbot"
        self.file_execution_uuid        = None
        self.file_execution_script_path = f"{self.file_execution_base_path}/{self.file_execution_uuid}.script"
        self.file_execution_result_path = f"{self.file_execution_base_path}/{self.file_execution_uuid}.result"

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

    def execute_command(self, session, command, script=False, runas=False):
        """
        Executes a command on a system via SSH.
        """
        try:
            stdin, stdout, stderr = session.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if error:
                raise Exception(f"console error: {error}")
            return stdout.read().decode().strip()
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def execute_file(self, session, script):
        """ 
        Execute a file on a system via SSH and return json as result
        """
        try:
            self.file_execution_uuid = uuid.uuid4()

            sftp.push_file(session, script)
            self.execute_command(session, f"{self.file_execution_script_path} > {self.file_execution_result_path}")
            
            return sftp.read_file(session)

        except paramiko.SSHException as e:
            raise Exception(f"SSH error occurred: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to execute file: {str(e)}")

    def close_session(self, session):
        """
        Closes an open SSH session.
        """
        try:
            session.close()
        except Exception as e:
            raise Exception(f"Failed to close SSH session: {str(e)}")