import socket
import select
from sysbot.utils.engine import ConnectorInterface


class Udp(ConnectorInterface):
    """
    UDP connector for connectionless communication.
    """

    def open_session(self, host, port, login=None, password=None):
        """
        Creates a UDP socket for communication.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port to communicate with.
            login (str): Username for authentication (not used in UDP).
            password (str): Password for authentication (not used in UDP).
            bind_port (int): Local port to bind to (optional).

        Returns:
            dict: Dictionary containing socket and target information.

        Raises:
            Exception: If there is an error creating the socket.
        """
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
