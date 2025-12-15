import socket
import ssl
import select
from sysbot.utils.engine import ConnectorInterface


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
            if port is None:
                return {
                    "StatusCode": 1,
                    "Session": None,
                    "Error": "Port is required for TCP connections"
                }

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
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Session" in session:
                sock = session["Session"]
            else:
                sock = session

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
                "Session": result_data,
                "Error": None
            }

        except socket.error as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Socket error during command execution: {str(e)}"
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
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
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Session" in session:
                sock = session["Session"]
            else:
                sock = session

            if sock:
                sock.close()

            return {
                "StatusCode": 0,
                "Session": "TCP session closed successfully",
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to close TCP session: {str(e)}"
            }


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
            if port is None:
                return {
                    "StatusCode": 1,
                    "Session": None,
                    "Error": "Port is required for UDP connections"
                }

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
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Session" in session:
                session_info = session["Session"]
            else:
                session_info = session

            if not session_info or "socket" not in session_info:
                return {
                    "StatusCode": 1,
                    "Session": None,
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
                "Session": result_data,
                "Error": None
            }

        except socket.error as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Socket error during command execution: {str(e)}"
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
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
        try:
            # Handle case where session is a dict from open_session
            if isinstance(session, dict) and "Session" in session:
                session_info = session["Session"]
            else:
                session_info = session

            if session_info and "socket" in session_info:
                session_info["socket"].close()

            return {
                "StatusCode": 0,
                "Session": "UDP session closed successfully",
                "Error": None
            }
        except Exception as e:
            return {
                "StatusCode": 1,
                "Session": None,
                "Error": f"Failed to close UDP session: {str(e)}"
            }
