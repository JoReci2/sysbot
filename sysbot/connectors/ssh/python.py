import paramiko
import os
from ...utils import ConnectorInterface


class Python(ConnectorInterface):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell).
    It uses the paramiko library to establish and manage SSH connections with support
    for both password and SSH key authentication.
    """

    def _load_private_key(self, private_key_path, private_key_passphrase=None):
        """
        Load a private key from file, trying different key types.
        
        Args:
            private_key_path (str): Path to the private key file
            private_key_passphrase (str): Passphrase for the private key (optional)
            
        Returns:
            paramiko.PKey: The loaded private key object
            
        Raises:
            Exception: If the key cannot be loaded
        """
        if not os.path.exists(private_key_path):
            raise Exception(f"Private key file not found: {private_key_path}")
        
        # Try different key types
        key_types = [
            paramiko.RSAKey,
            paramiko.DSSKey,
            paramiko.ECDSAKey,
            paramiko.Ed25519Key
        ]
        
        for key_type in key_types:
            try:
                return key_type.from_private_key_file(private_key_path, password=private_key_passphrase)
            except (paramiko.PasswordRequiredException, paramiko.SSHException):
                continue
        
        raise Exception(f"Unable to load private key from {private_key_path}. "
                       "Key may be in an unsupported format or passphrase is incorrect.")

    def open_session(self, host, port, login, password, **kwargs):
        """
        Opens an SSH session to a system with support for password and SSH key authentication.
        
        Args:
            host (str): Hostname or IP address
            port (int): SSH port
            login (str): Username
            password (str): Password (used as fallback if key auth fails)
            **kwargs: Additional parameters including:
                - private_key_path (str): Path to private key file
                - private_key_passphrase (str): Passphrase for private key
                - public_key_path (str): Path to public key file (optional)
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Extract SSH key parameters
            private_key_path = kwargs.get('private_key_path')
            private_key_passphrase = kwargs.get('private_key_passphrase')
            
            # Try SSH key authentication first if private key is provided
            if private_key_path:
                try:
                    private_key = self._load_private_key(private_key_path, private_key_passphrase)
                    client.connect(host, port=port, username=login, pkey=private_key)
                    return client
                except Exception as key_error:
                    # If key authentication fails and no password, raise the key error
                    if not password:
                        raise Exception(f"SSH key authentication failed: {str(key_error)}")
                    # Otherwise, continue to try password authentication
                    client.close()
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Use password authentication if key auth failed or no key provided
            if password:
                client.connect(host, port=port, username=login, password=password)
                return client
            else:
                raise Exception("No valid authentication method provided")
                
        except Exception as e:
            raise Exception(f"Failed to open SSH session: {str(e)}")

    def execute_command(self, session, command, runas=False, password=None):
        """
        Executes a Python command on a system via SSH.

        Args:
            session: The SSH session object
            command (str): The Python command to execute
            runas (bool): Whether to run with elevated privileges using sudo
            password (str): Password for sudo authentication (if required)

        Returns:
            str: The output of the command execution

        Raises:
            Exception: If there is an error executing the command
        """
        try:
            if runas and password is not None:
                # Use stdin to pass password securely to sudo
                stdin, stdout, stderr = session.exec_command(
                    "sudo -S python3", get_pty=True
                )
                stdin.write(f"{password}\n{command}")
            elif runas and password is None:
                stdin, stdout, stderr = session.exec_command(
                    "sudo python3", get_pty=False
                )
                stdin.write(command)
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
