import paramiko

class sftp(object):
    
    def read_file(self, session):
        
        try:
            with session.open_sftp() as sftp:
                with sftp.open(self.file_execution_result_path, 'r') as file:
                    content = file.read().decode()
                    return content
        except Exception as e:
            raise Exception(f"Failed to read remote file: {str(e)}")

    def push_file(self, session, content):
        
        sftp = session.open_sftp()
        try:
            sftp.stat(self.file_execution_base_path)
        except FileNotFoundError:
            sftp.mkdir(self.file_execution_base_path)

        with sftp.file(self.file_execution_script_path, "w") as f:
            f.write(content)
        sftp.chmod(self.file_execution_script_path, 0o755)
        sftp.close()
