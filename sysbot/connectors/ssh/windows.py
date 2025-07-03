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
import logging
from typing import Any
from sysbot.connectors.utils import sftp

logger = logging.getLogger(__name__)

class Windows(object):
    """
    SSH connector for Windows systems using paramiko.
    """
    def open_session(self, host: str, port: int, login: str, password: str) -> paramiko.SSHClient:
        """Open an SSH session to a system."""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=login, password=password)
            logger.info(f"SSH session opened to {host}:{port}")
            return client
        except Exception as e:
            logger.error(f"Failed to open SSH session: {e}")
            raise

    def execute_command(self, session: paramiko.SSHClient, command: str) -> str:
        """Execute a command on a system via SSH."""
        try:
            stdin, stdout, stderr = session.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            if error:
                logger.error(f"PowerShell error: {error}")
                raise Exception(f"PowerShell error: {error}")
            logger.info(f"Command executed: {command}")
            return output
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            raise

    def execute_file(self, session: paramiko.SSHClient, script: str) -> Any:
        """Execute a file on a system via SSH and return the result as JSON or string."""
        try:
            file_uuid = uuid.uuid4()
            base_path = ".sysbot"
            script_path = f"{base_path}/{file_uuid}.ps1"
            result_path = f"{base_path}/{file_uuid}.txt"
            sftp_client = sftp()
            sftp_client.sftp_push_file(session, script_path, script)
            self.execute_command(session, f"powershell.exe -File {script_path} > {result_path}")
            result = sftp_client.sftp_read_file(session, result_path)
            logger.info(f"Script executed via SSH: {script_path}")
            return result
        except paramiko.SSHException as e:
            logger.error(f"SSH error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to execute file: {e}")
            raise

    def delete_file(self, session: paramiko.SSHClient, file_path: str) -> None:
        """Delete a file on the remote system via SFTP."""
        try:
            sftp_client = sftp()
            sftp_client.sftp_delete_file(session, file_path)
            logger.info(f"Deleted remote file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete remote file: {e}")
            raise

    def close_session(self, session: paramiko.SSHClient) -> None:
        """Close an open SSH session."""
        try:
            session.close()
            logger.info("SSH session closed.")
        except Exception as e:
            logger.error(f"Failed to close SSH session: {e}")
            raise