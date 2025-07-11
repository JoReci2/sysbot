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

class Python(object):
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
        """
        try:
            if runas == True and password != None:
                stdin, stdout, stderr = session.exec_command(f"echo {password} | sudo -S python3", get_pty=True)
            elif runas == True and password == None:
                stdin, stdout, stderr = session.exec_command("sudo python3", get_pty=True)
            else:
                stdin, stdout, stderr = session.exec_command("python3", get_pty=False)
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