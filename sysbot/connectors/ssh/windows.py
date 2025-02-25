import paramiko
import uuid

class Windows(object):
    """
    This class provides methods for interacting with systems using SSH (Secure Shell).
    It uses the Netmiko library to establish and manage SSH connections.
    """

    def __init__(self):
        self.file_execution_base_path   = ".sysbot"
        self.file_execution_uuid        = None
        self.file_execution_script_path = f"{self.file_execution_base_path}/{self.file_execution_uuid}.ps1"
        self.file_execution_result_path = f"{self.file_execution_base_path}/{self.file_execution_uuid}.txt"

    def __sftp_read_file__(self, session):
        
        try:
            with session.open_sftp() as sftp:
                with sftp.open(self.file_execution_result_path, 'r') as file:
                    content = file.read().decode()
                    return content
        except Exception as e:
            raise Exception(f"Failed to read remote file: {str(e)}")

    def __sftp_push_file__(self, session, content):
        
        sftp = session.open_sftp()
        try:
            sftp.stat(self.file_execution_base_path)
        except FileNotFoundError:
            sftp.mkdir(self.file_execution_base_path)

        with sftp.file(self.file_execution_script_path, "w") as f:
            f.write(content)
        sftp.chmod(self.file_execution_script_path, 0o755)
        sftp.close()

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

    def execute_command(self, session, command, options):
        """
        Executes a command on a system via SSH.
        """
        try:
            stdin, stdout, stderr = session.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if error:
                raise Exception(f"PowerShell error: {error}") 

            return stdout.read().decode().strip()
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def execute_file(self, session, content):
        """ 
        Execute a file on a system via SSH and return json as result
        """
        try:
            self.file_execution_uuid = uuid.uuid4()

            self.__sftp_push_file__(session, content)
            self.execute_command(session, f"powershell.exe -File {self.file_execution_script_path} > {self.file_execution_result_path}", options=None)
            
            return self.__sftp_read_file__(session)

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