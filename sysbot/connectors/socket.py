"""
Socket Connector Module

This module provides TCP and UDP socket connectors with support for SSL/TLS
encryption. It enables raw network communication for protocols not covered
by other specialized connectors.
"""
import socket
import ssl
import select
from sysbot.utils.engine import ConnectorInterface


class Tcp(ConnectorInterface):
    """
    TCP connector with optional SSL/TLS support for secure communication.
    """

    def __init__(self, port=80):
        """
        Initialize TCP connector with default port.

        Args:
            port (int): Default TCP port (default: 80).
        """
        super().__init__()
        self.default_port = port

    def open_session(self, host, port=None, login=None, password=None, use_ssl=True):
        """
        Opens a TCP socket connection with optional SSL/TLS encryption.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port to connect to. If None, uses default_port.
            login (str): Username for authentication (optional for raw TCP).
            password (str): Password for authentication (optional for raw TCP).
            use_ssl (bool): Whether to use SSL/TLS encryption (default: True).

        Returns:
            socket.socket or ssl.SSLSocket: Socket object for communication.

        Raises:
            Exception: If there is an error opening the connection.
        """
        if port is None:
            port = self.default_port
        try:
            conn = socket.create_connection((host, port))

            if use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(conn, server_hostname=host)
            else:
                sock = conn

            return sock

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
    ):
        """
        Send data through the TCP socket and optionally receive a response.

        Args:
            session (socket.socket or ssl.SSLSocket): The socket object.
            command (str or bytes): The data to send through the socket.
            expect_response (bool): Whether to wait for a response (default: True).
            timeout (int): Custom timeout for this operation (default: 30).
            buffer_size (int): Custom buffer size for receiving data (default: 4096).
            encoding (str): Encoding to use for string data (default: 'utf-8').

        Returns:
            dict: Dictionary containing:
                - 'sent': The data that was sent
                - 'bytes_sent': Number of bytes sent
                - 'received': The data received (if expect_response is True)
                - 'bytes_received': Number of bytes received
                - 'success': Boolean indicating if operation was successful
                - 'timeout': Boolean indicating if timeout occurred during receive

        Raises:
            Exception: If there is an error during communication.
        """
        if not session:
            raise Exception("Invalid session object. Session is None or closed.")

        try:
            original_timeout = session.gettimeout()
            session.settimeout(timeout)

            # Encode data if it's a string
            if isinstance(command, str):
                data_to_send = command.encode(encoding)
            else:
                data_to_send = command

            bytes_sent = session.send(data_to_send)

            result = {
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
                    received_data = session.recv(buffer_size)
                    if isinstance(command, str):
                        result["received"] = received_data.decode(
                            encoding, errors="ignore"
                        )
                    else:
                        result["received"] = received_data
                    result["bytes_received"] = len(received_data)
                except socket.timeout:
                    result["timeout"] = True

            # Restore original timeout
            session.settimeout(original_timeout)

            return result

        except socket.error as e:
            raise Exception(f"Socket error during command execution: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes the SSL/TCP socket connection.

        Args:
            session (ssl.SSLSocket): The SSL-wrapped TCP socket object to close.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            if session:
                session.close()
        except Exception as e:
            raise Exception(f"Failed to close TCP session: {str(e)}")


class Udp(ConnectorInterface):
    """
    UDP connector for connectionless communication.
    """

    def __init__(self, port=53):
        """
        Initialize UDP connector with default port.

        Args:
            port (int): Default UDP port (default: 53).
        """
        super().__init__()
        self.default_port = port

    def open_session(self, host, port=None, login=None, password=None):
        """
        Creates a UDP socket for communication.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port to communicate with. If None, uses default_port.
            login (str): Username for authentication (not used in UDP).
            password (str): Password for authentication (not used in UDP).

        Returns:
            dict: Dictionary containing socket and target information.

        Raises:
            Exception: If there is an error creating the socket.
        """
        if port is None:
            port = self.default_port
        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Store target information with socket
            session_info = {
                "socket": sock,
                "target_host": host,
                "target_port": int(port),
            }

            return session_info

        except socket.gaierror as e:
            raise Exception(f"Failed to resolve hostname {host}: {str(e)}")
        except OSError as e:
            raise Exception(f"Failed to create UDP socket: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to open UDP session to {host}:{port}: {str(e)}")

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
            session (dict): The session dictionary containing socket and target info.
            command (str or bytes): The data to send through the socket.
            expect_response (bool): Whether to wait for a response (default: True).
            timeout (int): Custom timeout for this operation (default: 30).
            buffer_size (int): Custom buffer size for receiving data (default: 4096).
            encoding (str): Encoding to use for string data (default: 'utf-8').

        Returns:
            dict: Dictionary containing:
                - 'sent': The data that was sent
                - 'bytes_sent': Number of bytes sent
                - 'received': The data received (if expect_response is True)
                - 'bytes_received': Number of bytes received
                - 'success': Boolean indicating if operation was successful
                - 'timeout': Boolean indicating if timeout occurred during receive
                - 'source_address': Address that sent the response (if received)

        Raises:
            Exception: If there is an error during communication.
        """
        if not session or "socket" not in session:
            raise Exception(
                "Invalid session object. Session is None or missing socket."
            )

        sock = session["socket"]
        target_host = session["target_host"]
        target_port = session["target_port"]

        try:
            original_timeout = sock.gettimeout()
            sock.settimeout(timeout)

            # Encode data if it's a string
            if isinstance(command, str):
                data_to_send = command.encode(encoding)
            else:
                data_to_send = command

            # Send UDP packet
            bytes_sent = sock.sendto(data_to_send, (target_host, target_port))

            result = {
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
                            result["received"] = received_data.decode(
                                encoding, errors="ignore"
                            )
                        else:
                            result["received"] = received_data
                        result["bytes_received"] = len(received_data)
                        result["source_address"] = source_address
                    else:
                        result["timeout"] = True
                except socket.timeout:
                    result["timeout"] = True

            # Restore original timeout
            sock.settimeout(original_timeout)

            return result

        except socket.error as e:
            raise Exception(f"Socket error during command execution: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes the UDP socket.

        Args:
            session (dict): The session dictionary containing the socket.

        Raises:
            Exception: If there is an error closing the session.
        """
        try:
            if session and "socket" in session:
                session["socket"].close()
        except Exception as e:
            raise Exception(f"Failed to close UDP session: {str(e)}")
