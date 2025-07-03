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

import logging
from typing import Any, Dict, Optional
from winrm.protocol import Protocol
from sysbot.connectors.utils import AbstractConnector

logger = logging.getLogger(__name__)

class Windows(AbstractConnector):
    """
    WinRM connector for Windows systems using pywinrm.
    """
    def open_session(self, host: str, port: int, login: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        """Open a WinRM session to a Windows system."""
        try:
            p = Protocol(
                endpoint=f'http://{host}:{port}/wsman',
                transport='ntlm',
                username=login,
                password=password,
                server_cert_validation='ignore'
            )
            shell = p.open_shell()
            session = {'protocol': p, 'shell': shell}
            logger.info(f"WinRM session opened to {host}:{port}")
            return session
        except Exception as e:
            logger.error(f"Failed to open WinRM session: {e}")
            raise

    def execute_command(self, session: Dict[str, Any], command: str, script: bool = False, runas: bool = False) -> str:
        """Execute a PowerShell command on a Windows system via WinRM."""
        try:
            # If script=True, treat command as a script block
            ps_command = command if not script else f"& {{ {command} }}"
            payload = session['protocol'].run_command(session['shell'], 'powershell', ['-Command', ps_command])
            response = session['protocol'].get_command_output(session['shell'], payload)
            output = response[0].decode().strip()
            error = response[1].decode().strip()
            session['protocol'].cleanup_command(session['shell'], payload)
            if error:
                logger.error(f"PowerShell error: {error}")
                raise Exception(f"PowerShell error: {error}")
            logger.info(f"Command executed via WinRM: {command}")
            return output
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            raise

    def close_session(self, session: Dict[str, Any]) -> None:
        """Close the WinRM session to a Windows system."""
        try:
            session['protocol'].close_shell(session['shell'])
            logger.info("WinRM session closed.")
        except Exception as e:
            logger.error(f"Failed to close WinRM session: {e}")
            raise