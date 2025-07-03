import paramiko
import time

class sftp(object):
    
    def sftp_read_file(self, session, filepath):
        try:
            with session.open_sftp() as sftp:
                with sftp.open(filepath, 'r') as file:
                    content = file.read().decode()
                    return content
        except Exception as e:
            raise Exception(f"Failed to read remote file: {str(e)}")


    def sftp_push_file(self, session, filepath, content):
        sftp = session.open_sftp()
        with sftp.file(filepath, "w") as f:
            f.write(content)
        sftp.chmod(filepath, 0o755)
        sftp.close()

    def sftp_delete_file(self, session, filepath):
        try:
            with session.open_sftp() as sftp:
                sftp.remove(filepath)
        except FileNotFoundError:
            raise Exception(f"File not found: {filepath}")
        except Exception as e:
            raise Exception(f"Failed to delete remote file: {str(e)}")

    def read_channel(self, channel, timeout=5):
        start_time = time.time()
        output = ""
        while True:
            if channel.recv_ready():
                output += channel.recv(4096).decode()
            if time.time() - start_time > timeout:
                break
            time.sleep(0.1)
        return output