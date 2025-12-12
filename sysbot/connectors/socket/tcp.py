import socket
import ssl
from sysbot.utils.engine import ConnectorInterface
from sysbot.connectors.config import create_response


class Tcp(ConnectorInterface):
    """
    TCP socket connector with optional SSL/TLS support for secure communication.
    Supports both plain TCP and encrypted connections.
    """

    def open_session(self, host, port, login=None, password=None, use_ssl=True, **kwargs):
        """
        Opens a TCP socket connection with optional SSL/TLS encryption.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port to connect to.
            login (str): Username for authentication (optional, not used for raw TCP).
            password (str): Password for authentication (optional, not used for raw TCP).
            use_ssl (bool): Whether to use SSL/TLS encryption (default: True).
            **kwargs: Additional SSL/socket parameters

        Returns:
            dict: Session dictionary with socket and connection info

        Raises:
            Exception: If there is an error opening the connection.
        """
        try:
            timeout = kwargs.get("timeout", 30)
            conn = socket.create_connection((host, port), timeout=timeout)

            if use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = kwargs.get("check_hostname", False)
                context.verify_mode = ssl.CERT_NONE if kwargs.get("verify_mode") is None else kwargs.get("verify_mode")
                
                # Set minimum TLS version to 1.2 for security
                context.minimum_version = ssl.TLSVersion.TLSv1_2
                
                sock = context.wrap_socket(conn, server_hostname=host)
            else:
                sock = conn

            return {
                "socket": sock,
                "host": host,
                "port": port,
                "use_ssl": use_ssl
            }

        except socket.timeout:
            raise Exception(f"Connection to {host}:{port} timed out")
        except socket.gaierror as e:
            raise Exception(f"Failed to resolve hostname {host}: {str(e)}")
        except ConnectionRefusedError:
            raise Exception(f"Connection refused to {host}:{port}")
        except Exception as e:
            raise Exception(f"Failed to open TCP session to {host}:{port}: {str(e)}")

    def execute_command(
        self,
        session,
        command,
        expect_response=True,
        timeout=30,
        buffer_size=4096,
        encoding="utf-8",
        **kwargs
    ):
        """
        Send data through the TCP socket and optionally receive a response.

        Args:
            session (dict): The session dictionary containing socket and connection info.
            command (str or bytes): The data to send through the socket.
            expect_response (bool): Whether to wait for a response (default: True).
            timeout (int): Custom timeout for this operation (default: 30).
            buffer_size (int): Custom buffer size for receiving data (default: 4096).
            encoding (str): Encoding to use for string data (default: 'utf-8').
            **kwargs: Additional parameters

        Returns:
            dict: Standardized response with StatusCode, Result, Error, and Metadata
        """
        if not session or "socket" not in session:
            return create_response(
                status_code=1,
                result=None,
                error="Invalid session: socket not found"
            )

        sock = session["socket"]
        
        try:
            original_timeout = sock.gettimeout()
            sock.settimeout(timeout)

            # Encode data if it's a string
            if isinstance(command, str):
                data_to_send = command.encode(encoding)
            else:
                data_to_send = command

            bytes_sent = sock.send(data_to_send)

            result_data = {
                "sent": command,
                "bytes_sent": bytes_sent,
                "received": None,
                "bytes_received": 0,
                "timeout": False,
            }

            # Receive response if expected
            if expect_response:
                try:
                    received_data = sock.recv(buffer_size)
                    if isinstance(command, str):
                        result_data["received"] = received_data.decode(
                            encoding, errors="ignore"
                        )
                    else:
                        result_data["received"] = received_data
                    result_data["bytes_received"] = len(received_data)
                except socket.timeout:
                    result_data["timeout"] = True

            # Restore original timeout
            sock.settimeout(original_timeout)

            return create_response(
                status_code=0,
                result=result_data,
                error=None,
                metadata={
                    "host": session.get("host"),
                    "port": session.get("port"),
                    "use_ssl": session.get("use_ssl")
                }
            )

        except socket.error as e:
            return create_response(
                status_code=1,
                result=None,
                error=f"Socket error during command execution: {str(e)}",
                metadata={
                    "host": session.get("host"),
                    "port": session.get("port")
                }
            )
        except Exception as e:
            return create_response(
                status_code=1,
                result=None,
                error=f"Failed to execute command: {str(e)}",
                metadata={
                    "host": session.get("host"),
                    "port": session.get("port")
                }
            )

    def close_session(self, session):
        """
        Closes the SSL/TCP socket connection.

        Args:
            session (dict): The session dictionary containing the socket.

        Raises:
            Exception: If there is an error closing the session.
        """
        if session and "socket" in session:
            try:
                session["socket"].close()
            except Exception as e:
                raise Exception(f"Failed to close TCP session: {str(e)}")
