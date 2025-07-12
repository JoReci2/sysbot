"""
Tests for privilege elevation functionality in SSH and WinRM connectors.
"""

import unittest
from unittest.mock import Mock, patch
from sysbot.connectors.ssh.bash import Bash
from sysbot.connectors.ssh.python import Python
from sysbot.connectors.winrm.powershell import Powershell


class TestSSHPrivilegeElevation(unittest.TestCase):
    """Test privilege elevation for SSH connectors"""

    def setUp(self):
        self.bash_connector = Bash()
        self.python_connector = Python()

    @patch("paramiko.SSHClient")
    def test_bash_execute_command_without_privilege_elevation(self, mock_ssh_client):
        """Test bash command execution without privilege elevation"""
        # Setup mock session
        mock_session = Mock()
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()

        mock_session.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        mock_stdout.read.return_value = b"test output"
        mock_stderr.read.return_value = b""

        # Execute command without privilege elevation
        result = self.bash_connector.execute_command(mock_session, "echo hello")

        # Verify correct command was executed
        mock_session.exec_command.assert_called_with("bash", get_pty=False)
        mock_stdin.write.assert_called_with("echo hello")
        self.assertEqual(result, "test output")

    @patch("paramiko.SSHClient")
    def test_bash_execute_command_with_privilege_elevation_no_password(
        self, mock_ssh_client
    ):
        """Test bash command execution with privilege elevation but no password"""
        # Setup mock session
        mock_session = Mock()
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()

        mock_session.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        mock_stdout.read.return_value = b"test output"
        mock_stderr.read.return_value = b""

        # Execute command with privilege elevation but no password
        result = self.bash_connector.execute_command(
            mock_session, "echo hello", runas=True
        )

        # Verify correct command was executed
        mock_session.exec_command.assert_called_with("sudo bash", get_pty=False)
        mock_stdin.write.assert_called_with("echo hello")
        self.assertEqual(result, "test output")

    @patch("paramiko.SSHClient")
    def test_bash_execute_command_with_privilege_elevation_and_password(
        self, mock_ssh_client
    ):
        """Test bash command execution with privilege elevation and password"""
        # Setup mock session
        mock_session = Mock()
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()

        mock_session.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        mock_stdout.read.return_value = b"test output"
        mock_stderr.read.return_value = b""

        # Execute command with privilege elevation and password
        result = self.bash_connector.execute_command(
            mock_session, "echo hello", runas=True, password="secret"
        )

        # Verify correct command was executed
        mock_session.exec_command.assert_called_with("sudo -S bash", get_pty=True)
        mock_stdin.write.assert_called_with("secret\necho hello")
        self.assertEqual(result, "test output")

    @patch("paramiko.SSHClient")
    def test_python_execute_command_without_privilege_elevation(self, mock_ssh_client):
        """Test python command execution without privilege elevation"""
        # Setup mock session
        mock_session = Mock()
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()

        mock_session.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        mock_stdout.read.return_value = b"test output"
        mock_stderr.read.return_value = b""

        # Execute command without privilege elevation
        result = self.python_connector.execute_command(mock_session, "print('hello')")

        # Verify correct command was executed
        mock_session.exec_command.assert_called_with("python3", get_pty=False)
        mock_stdin.write.assert_called_with("print('hello')")
        self.assertEqual(result, "test output")

    @patch("paramiko.SSHClient")
    def test_python_execute_command_with_privilege_elevation_and_password(
        self, mock_ssh_client
    ):
        """Test python command execution with privilege elevation and password"""
        # Setup mock session
        mock_session = Mock()
        mock_stdin = Mock()
        mock_stdout = Mock()
        mock_stderr = Mock()

        mock_session.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        mock_stdout.read.return_value = b"test output"
        mock_stderr.read.return_value = b""

        # Execute command with privilege elevation and password
        result = self.python_connector.execute_command(
            mock_session, "print('hello')", runas=True, password="secret"
        )

        # Verify correct command was executed
        mock_session.exec_command.assert_called_with("sudo -S python3", get_pty=True)
        mock_stdin.write.assert_called_with("secret\nprint('hello')")
        self.assertEqual(result, "test output")


class TestWinRMPrivilegeElevation(unittest.TestCase):
    """Test privilege elevation for WinRM PowerShell connector"""

    def setUp(self):
        self.powershell_connector = Powershell()

    @patch("winrm.protocol.Protocol")
    def test_powershell_execute_command_without_privilege_elevation(
        self, mock_protocol
    ):
        """Test PowerShell command execution without privilege elevation"""
        # Setup mock session
        mock_session = {"protocol": Mock(), "shell": Mock()}

        mock_session["protocol"].run_command.return_value = "command_id"
        mock_session["protocol"].get_command_output.return_value = (
            "test output",
            "",
            0,
        )

        # Execute command without privilege elevation
        result = self.powershell_connector.execute_command(mock_session, "Get-Process")

        # Verify the result
        self.assertEqual(result, "test output")
        mock_session["protocol"].run_command.assert_called_once()
        mock_session["protocol"].get_command_output.assert_called_once()
        mock_session["protocol"].cleanup_command.assert_called_once()

    @patch("winrm.protocol.Protocol")
    def test_powershell_execute_command_with_privilege_elevation_no_credentials(
        self, mock_protocol
    ):
        """Test PowerShell command execution with privilege elevation but no custom credentials"""
        # Setup mock session
        mock_session = {"protocol": Mock(), "shell": Mock()}

        mock_session["protocol"].run_command.return_value = "command_id"
        mock_session["protocol"].get_command_output.return_value = (
            "test output",
            "",
            0,
        )

        # Execute command with privilege elevation but no custom credentials
        result = self.powershell_connector.execute_command(
            mock_session, "Get-Process", runas=True
        )

        # Verify the result
        self.assertEqual(result, "test output")

        # Get the actual command that was run
        call_args = mock_session["protocol"].run_command.call_args
        executed_command = call_args[0][1]  # Second argument (first is shell)

        # Extract the base64 encoded command and decode it
        import base64
        import re

        # Extract the base64 part from the powershell command
        match = re.search(
            r"powershell -encodedcommand ([A-Za-z0-9+/=]+)", executed_command
        )
        if match:
            encoded_part = match.group(1)
            # Decode the base64 and convert from UTF-16LE
            decoded_command = base64.b64decode(encoded_part).decode("utf-16le")
        else:
            decoded_command = executed_command

        # Check that it contains the RunAs elevation
        self.assertIn("Start-Process PowerShell -Verb RunAs", decoded_command)
        self.assertIn("Get-Process", decoded_command)

    @patch("winrm.protocol.Protocol")
    def test_powershell_execute_command_with_privilege_elevation_and_credentials(
        self, mock_protocol
    ):
        """Test PowerShell command execution with privilege elevation and custom credentials"""
        # Setup mock session
        mock_session = {"protocol": Mock(), "shell": Mock()}

        mock_session["protocol"].run_command.return_value = "command_id"
        mock_session["protocol"].get_command_output.return_value = (
            "test output",
            "",
            0,
        )

        # Execute command with privilege elevation and custom credentials
        result = self.powershell_connector.execute_command(
            mock_session, "Get-Process", runas=True, username="admin", password="secret"
        )

        # Verify the result
        self.assertEqual(result, "test output")

        # Get the actual command that was run
        call_args = mock_session["protocol"].run_command.call_args
        executed_command = call_args[0][1]  # Second argument (first is shell)

        # Extract the base64 encoded command and decode it
        import base64
        import re

        # Extract the base64 part from the powershell command
        match = re.search(
            r"powershell -encodedcommand ([A-Za-z0-9+/=]+)", executed_command
        )
        if match:
            encoded_part = match.group(1)
            # Decode the base64 and convert from UTF-16LE
            decoded_command = base64.b64decode(encoded_part).decode("utf-16le")
        else:
            decoded_command = executed_command

        # Check that it contains the credential-based elevation
        self.assertIn("ConvertTo-SecureString", decoded_command)
        self.assertIn("PSCredential", decoded_command)
        self.assertIn("admin", decoded_command)
        self.assertIn("Get-Process", decoded_command)


class TestConnectorConsistency(unittest.TestCase):
    """Test that all connectors have consistent privilege elevation interfaces"""

    def test_ssh_connectors_support_runas_parameter(self):
        """Test that SSH connectors support runas parameter"""
        bash_connector = Bash()
        python_connector = Python()

        # Check that execute_command method supports runas parameter
        bash_method = bash_connector.execute_command
        python_method = python_connector.execute_command

        # These should not raise TypeError for the runas parameter
        try:
            # Mock session to avoid actual SSH connection
            mock_session = Mock()
            mock_stdin = Mock()
            mock_stdout = Mock()
            mock_stderr = Mock()

            mock_session.exec_command.return_value = (
                mock_stdin,
                mock_stdout,
                mock_stderr,
            )
            mock_stdout.read.return_value = b"test"
            mock_stderr.read.return_value = b""

            bash_method(mock_session, "test", runas=True, password="test")
            python_method(mock_session, "test", runas=True, password="test")

        except Exception as e:
            if "unexpected keyword argument" in str(e):
                self.fail(f"SSH connector doesn't support runas parameter: {e}")

    def test_winrm_connector_supports_runas_parameter(self):
        """Test that WinRM connector supports runas parameter"""
        powershell_connector = Powershell()

        # Check that execute_command method supports runas parameter
        powershell_method = powershell_connector.execute_command

        try:
            # Mock session to avoid actual WinRM connection
            mock_session = {"protocol": Mock(), "shell": Mock()}

            mock_session["protocol"].run_command.return_value = "command_id"
            mock_session["protocol"].get_command_output.return_value = ("test", "", 0)

            powershell_method(
                mock_session, "test", runas=True, username="admin", password="test"
            )

        except Exception as e:
            if "unexpected keyword argument" in str(e):
                self.fail(f"WinRM connector doesn't support runas parameter: {e}")


if __name__ == "__main__":
    unittest.main()
