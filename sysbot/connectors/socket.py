import socket
import ssl
import select
from sysbot.utils.engine import ConnectorInterface


class _SocketHelper:
    """
    Private helper class for common socket operations.
    """
    
    @staticmethod
    def validate_port(port, host):
        """
        Validates that a port is provided.
        
        Args:
            port: Port number or None.
            host: Hostname for error message.
            
        Returns:
            dict: Error response if port is None, None otherwise.
        """
        if port is None:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": "Port is required for socket connections"
            }
        return None
    
    @staticmethod
    def extract_session(session, session_key="Session"):
        """
        Extracts the actual session object from a response dict.
        
        Args:
            session: Session object or dict from open_session.
            session_key: Key to use when extracting from dict (default: "Session").
            
        Returns:
            The extracted session object.
        """
        if isinstance(session, dict) and session_key in session:
            return session[session_key]
        return session
    
    @staticmethod
    def close_socket(session, socket_key=None):
        """
        Closes a socket connection.
        
        Args:
            session: Socket object, dict, or session info containing socket.
            socket_key: Optional key to extract socket from session dict.
            
        Returns:
            dict: Standardized response with StatusCode and Error.
        """
        try:
            # Extract session if it's wrapped in a response dict
            actual_session = _SocketHelper.extract_session(session)
            
            # Close the socket
            if socket_key and isinstance(actual_session, dict) and socket_key in actual_session:
                # For UDP - session_info contains a "socket" key
                actual_session[socket_key].close()
            elif actual_session:
                # For TCP - session is the socket itself
                actual_session.close()
            
            return {
                "StatusCode": 0,
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Error": f"Failed to close socket: {str(e)}"
            }


class Tcp(ConnectorInterface):
    """
    TCP connector with optional SSL/TLS support for secure communication.
    """

    DEFAULT_PORT = None  # TCP can use any port

    def __init__(self):
        super().__init__()
        self.default_port = self.DEFAULT_PORT

    def open_session(self, host, port=None, login=None, password=None, use_ssl=True):
        """
        Opens a TCP socket connection with optional SSL/TLS encryption.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port to connect to.
            login (str): Username for authentication (optional for raw TCP).
            password (str): Password for authentication (optional for raw TCP).
            use_ssl (bool): Whether to use SSL/TLS encryption (default: True).

        Returns:
            dict: Standardized response with StatusCode and Error.
        """
        try:
            # Validate port
            port_error = _SocketHelper.validate_port(port, host)
            if port_error:
                return port_error

            conn = socket.create_connection((host, port))

            if use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(conn, server_hostname=host)
            else:
                sock = conn

            return {
                "StatusCode": 0,
                "Session": sock,
                "Error": None
            }

        except socket.timeout:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Connection to {host}:{port} timed out"
            }
        except socket.gaierror as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to resolve hostname {host}: {str(e)}"
            }
        except ConnectionRefusedError:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Connection refused to {host}:{port}"
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to open TCP session to {host}:{port}: {str(e)}"
            }

    def execute_command(
        self,
        session,
        command,
        expect_response=True,
        timeout=30,
        buffer_size=4096,
        encoding="utf-8",
    ):
        """
        Send data through the TCP socket and optionally receive a response.

        Args:
            session: The socket object (from Session field of open_session)
            command (str or bytes): The data to send through the socket.
            expect_response (bool): Whether to wait for a response (default: True).
            timeout (int): Custom timeout for this operation (default: 30).
            buffer_size (int): Custom buffer size for receiving data (default: 4096).
            encoding (str): Encoding to use for string data (default: 'utf-8').

        Returns:
            dict: Standardized response with StatusCode, Result (dict), and Error.
        """
        try:
            # Extract session using helper
            sock = _SocketHelper.extract_session(session)

            if not sock:
                return {
                    "StatusCode": 1,
                    "Session": None,
                    "Error": "Invalid session object. Session is None or closed."
                }

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
                "success": True,
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

            return {
                "StatusCode": 0,
                "Result": result_data,
                "Error": None
            }

        except socket.error as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Socket error during command execution: {str(e)}"
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to execute command: {str(e)}"
            }

    def close_session(self, session):
        """
        Closes the SSL/TCP socket connection.

        Args:
            session: The socket object (from Session field of open_session)

        Returns:
            dict: Standardized response with StatusCode and Error.
        """
        return _SocketHelper.close_socket(session)


class Udp(ConnectorInterface):
    """
    UDP connector for connectionless communication.
    """

    DEFAULT_PORT = None  # UDP can use any port

    def __init__(self):
        super().__init__()
        self.default_port = self.DEFAULT_PORT

    def open_session(self, host, port=None, login=None, password=None):
        """
        Creates a UDP socket for communication.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port to communicate with.
            login (str): Username for authentication (not used in UDP).
            password (str): Password for authentication (not used in UDP).

        Returns:
            dict: Standardized response with StatusCode and Error.
        """
        try:
            # Validate port using helper
            port_error = _SocketHelper.validate_port(port, host)
            if port_error:
                return port_error

            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Store target information with socket
            session_info = {
                "socket": sock,
                "target_host": host,
                "target_port": int(port),
            }

            return {
                "StatusCode": 0,
                "Session": session_info,
                "Error": None
            }

        except socket.gaierror as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to resolve hostname {host}: {str(e)}"
            }
        except OSError as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to create UDP socket: {str(e)}"
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to open UDP session to {host}:{port}: {str(e)}"
            }

    def execute_command(
        self,
        session,
        command,
        expect_response=True,
        timeout=30,
        buffer_size=4096,
        encoding="utf-8",
    ):
        """
        Send data through the UDP socket and optionally receive a response.

        Args:
            session: The session dictionary (from Session field of open_session)
            command (str or bytes): The data to send through the socket.
            expect_response (bool): Whether to wait for a response (default: True).
            timeout (int): Custom timeout for this operation (default: 30).
            buffer_size (int): Custom buffer size for receiving data (default: 4096).
            encoding (str): Encoding to use for string data (default: 'utf-8').

        Returns:
            dict: Standardized response with StatusCode, Result (dict), and Error.
        """
        try:
            # Extract session info using helper
            session_info = _SocketHelper.extract_session(session)

            if not session_info or "socket" not in session_info:
                return {
                    "StatusCode": 1,
                    "Result": None,
                    "Error": "Invalid session object. Session is None or missing socket."
                }

            sock = session_info["socket"]
            target_host = session_info["target_host"]
            target_port = session_info["target_port"]

            original_timeout = sock.gettimeout()
            sock.settimeout(timeout)

            # Encode data if it's a string
            if isinstance(command, str):
                data_to_send = command.encode(encoding)
            else:
                data_to_send = command

            # Send UDP packet
            bytes_sent = sock.sendto(data_to_send, (target_host, target_port))

            result_data = {
                "sent": command,
                "bytes_sent": bytes_sent,
                "success": True,
                "received": None,
                "bytes_received": 0,
                "timeout": False,
                "source_address": None,
            }

            # Receive response if expected
            if expect_response:
                try:
                    # Use select to check if data is available
                    ready, _, _ = select.select([sock], [], [], timeout)
                    if ready:
                        received_data, source_address = sock.recvfrom(buffer_size)
                        if isinstance(command, str):
                            result_data["received"] = received_data.decode(
                                encoding, errors="ignore"
                            )
                        else:
                            result_data["received"] = received_data
                        result_data["bytes_received"] = len(received_data)
                        result_data["source_address"] = source_address
                    else:
                        result_data["timeout"] = True
                except socket.timeout:
                    result_data["timeout"] = True

            # Restore original timeout
            sock.settimeout(original_timeout)

            return {
                "StatusCode": 0,
                "Result": result_data,
                "Error": None
            }

        except socket.error as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Socket error during command execution: {str(e)}"
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Result": None,
                "Error": f"Failed to execute command: {str(e)}"
            }

    def close_session(self, session):
        """
        Closes the UDP socket.

        Args:
            session: The session dictionary (from Session field of open_session)

        Returns:
            dict: Standardized response with StatusCode and Error.
        """
        return _SocketHelper.close_socket(session, socket_key="socket")
