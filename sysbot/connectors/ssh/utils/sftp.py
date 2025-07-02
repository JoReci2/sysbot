import paramiko
from typing import Optional

class sftp(object):
    """
    SFTP utility class for file operations over SSH connections.
    """
    
    def __init__(self, base_path: str = ".sysbot"):
        self.file_execution_base_path = base_path
        self.file_execution_script_path: Optional[str] = None
        self.file_execution_result_path: Optional[str] = None
    
    def read_file(self, session: paramiko.SSHClient, file_path: Optional[str] = None) -> str:
        """
        Read a file from the remote system.
        """
        if file_path is None:
            file_path = self.file_execution_result_path
            
        if file_path is None:
            raise ValueError("No file path specified for reading")
        
        try:
            with session.open_sftp() as sftp:
                with sftp.open(file_path, 'r') as file:
                    content = file.read().decode()
                    return content
        except Exception as e:
            raise Exception(f"Failed to read remote file: {str(e)}")

    def push_file(self, session: paramiko.SSHClient, content: str, file_path: Optional[str] = None) -> None:
        """
        Push a file to the remote system.
        """
        if file_path is None:
            file_path = self.file_execution_script_path
            
        if file_path is None:
            raise ValueError("No file path specified for writing")
        
        sftp_client = session.open_sftp()
        try:
            sftp_client.stat(self.file_execution_base_path)
        except FileNotFoundError:
            sftp_client.mkdir(self.file_execution_base_path)

        with sftp_client.file(file_path, "w") as f:
            f.write(content)
        sftp_client.chmod(file_path, 0o755)
        sftp_client.close()
