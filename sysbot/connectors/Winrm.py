from winrm.protocol import Protocol

class winrm(object):
    """
    This class provides methods for interacting with Windows systems using the Windows Remote Management (WinRM) protocol.
    It uses the pywinrm library to establish and manage sessions.
    """

    def open_session(self, host, port, login, password):
        """
        Opens a WinRM session to a Windows system.

        Args:
            host (str): Hostname or IP address of the Windows system.
            port (int): Port of the WinRM service.
            login (str): Username for the session.
            password (str): Password for the session.

        Returns:
            dict: A dictionary containing the protocol and shell objects.

        Raises:
            Exception: If there is an error opening the session.
        """
        try:
            p = Protocol(
                endpoint=f'http://{host}:{port}/wsman',
                transport='ntlm',
                username=login,
                password=password,
                server_cert_validation='ignore'
            )

            shell = p.open_shell()
            session = {
                'protocol': p,
                'shell': shell
            }
            return session
        except Exception as e:
            raise Exception(f"Failed to open WinRM session: {str(e)}")

    def execute_command(self, session, command):
        """
        Executes a PowerShell command on a Windows system via WinRM.

        Args:
            session (dict): The session dictionary containing the protocol and shell.
            command (str): The PowerShell command to execute on the Windows system.

        Returns:
            str: The output of the command.

        Raises:
            Exception: If there is an error executing the command.
        """
        try:
            payload = session['protocol'].run_command(session['shell'], 'powershell', ['-Command', command])
            response = session['protocol'].get_command_output(session['shell'], payload)
            output = response[0].decode().strip()
            session['protocol'].cleanup_command(session['shell'], payload)
            return output
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes the WinRM session to a Windows system.

        Args:
            session (dict): The session dictionary containing the protocol and shell.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            session['protocol'].close_shell(session['shell'])
        except Exception as e:
            raise Exception(f"Failed to close WinRM session: {str(e)}")