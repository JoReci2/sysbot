import socket
import select
from sysbot.utils.engine import ConnectorInterface
from sysbot.connectors.config import create_response


class Udp(ConnectorInterface):
    """
    UDP socket connector for connectionless communication.
    Supports datagram-based communication with optional response handling.
    """

    def open_session(self, host, port, login=None, password=None, **kwargs):
        """
        Creates a UDP socket for communication.

        Args:
            host (str): Hostname or IP address of the target system.
            port (int): Port to communicate with.
            login (str): Username for authentication (not used in UDP).
            password (str): Password for authentication (not used in UDP).
            **kwargs: Additional socket parameters

        Returns:
            dict: Dictionary containing socket and target information.

        Raises:
            Exception: If there is an error creating the socket.
        """
        try:
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Set socket options if provided
            if kwargs.get("broadcast"):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

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
        **kwargs
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

            result_data = {
                "sent": command,
                "bytes_sent": bytes_sent,
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

            return create_response(
                status_code=0,
                result=result_data,
                error=None,
                metadata={
                    "target_host": target_host,
                    "target_port": target_port
                }
            )

        except socket.error as e:
            return create_response(
                status_code=1,
                result=None,
                error=f"Socket error during command execution: {str(e)}",
                metadata={
                    "target_host": target_host,
                    "target_port": target_port
                }
            )
        except Exception as e:
            return create_response(
                status_code=1,
                result=None,
                error=f"Failed to execute command: {str(e)}",
                metadata={
                    "target_host": target_host,
                    "target_port": target_port
                }
            )

    def close_session(self, session):
        """
        Closes the UDP socket.

        Args:
            session (dict): The session dictionary containing the socket.

        Raises:
            Exception: If there is an error closing the session.
        """
        if session and "socket" in session:
            try:
                session["socket"].close()
            except Exception as e:
                raise Exception(f"Failed to close UDP session: {str(e)}")
