"""
MIT License

Copyright (c) 2024 Thibault SCIRE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import socket
import struct
import threading
import paramiko
from typing import Dict, List, Optional, Tuple, Any
from sshtunnel import SSHTunnelForwarder
from ...utils.ConnectorInterface import ConnectorInterface


class Socks5Proxy(ConnectorInterface):
    """
    This class provides SOCKS5 proxy functionality that can be used through SSH tunnel chains.
    It implements a SOCKS5 server that forwards traffic through SSH connections using sshtunnel.
    """

    def __init__(self):
        """Initialize the SOCKS5 proxy connector."""
        self.proxy_sessions: Dict[str, Dict[str, Any]] = {}

    def open_session(self, host: str, port: int, login: str, password: str) -> Dict[str, Any]:
        """
        Opens an SSH session for SOCKS5 proxy use.
        This is a basic SSH connection that will be used for the proxy.
        
        Args:
            host (str): SSH server hostname or IP
            port (int): SSH server port
            login (str): SSH username
            password (str): SSH password
            
        Returns:
            Dict containing SSH client and connection details
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=login, password=password)
            
            return {
                'ssh_client': client,
                'host': host,
                'port': port,
                'login': login,
                'password': password
            }
        except Exception as e:
            raise Exception(f"Failed to open SSH session for SOCKS5 proxy: {str(e)}")

    def execute_command(self, session: Dict[str, Any], command: str, **kwargs) -> str:
        """
        Execute command on the SSH session.
        For SOCKS5 proxy, this is mainly used for testing connectivity.
        
        Args:
            session: The SSH session dictionary
            command: Command to execute
            
        Returns:
            Command output
        """
        try:
            ssh_client = session['ssh_client']
            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if error:
                raise Exception(f"Command error: {error}")
            return output
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session: Dict[str, Any]) -> None:
        """
        Close the SSH session.
        
        Args:
            session: The SSH session dictionary to close
        """
        try:
            if 'ssh_client' in session:
                session['ssh_client'].close()
        except Exception as e:
            raise Exception(f"Failed to close SSH session: {str(e)}")

    def open_proxy_sock5(self, session_alias: str, listen_port: int, 
                         tunnel_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Open a SOCKS5 proxy server that forwards connections through SSH tunnel chain.
        
        Args:
            session_alias (str): Unique identifier for this proxy session
            listen_port (int): Local port to listen for SOCKS5 connections
            tunnel_config (List[Dict]): List of SSH tunnel hops configuration
                Format: [{'ip': 'host1', 'port': 22, 'username': 'user1', 'password': 'pass1'}, ...]
                
        Returns:
            Dict containing proxy server details and active tunnels
        """
        try:
            if not tunnel_config or not isinstance(tunnel_config, list):
                raise Exception("tunnel_config must be a non-empty list of SSH hop configurations")
            
            # Create nested SSH tunnels using sshtunnel
            tunnels = self._create_nested_tunnels(tunnel_config)
            
            # Get the final tunnel endpoint
            final_tunnel = tunnels[-1] if tunnels else None
            final_host = '127.0.0.1'
            final_port = final_tunnel.local_bind_port if final_tunnel else tunnel_config[0]['port']
            
            # Create SSH client to the final endpoint
            final_ssh_client = paramiko.SSHClient()
            final_ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if tunnels:
                # Connect through the tunnel
                final_ssh_client.connect(
                    final_host,
                    port=final_port,
                    username=tunnel_config[-1]['username'],
                    password=tunnel_config[-1]['password']
                )
            else:
                # Direct connection
                final_ssh_client.connect(
                    tunnel_config[0]['ip'],
                    port=tunnel_config[0]['port'],
                    username=tunnel_config[0]['username'],
                    password=tunnel_config[0]['password']
                )
            
            # Start SOCKS5 server
            server_socket = self._start_socks5_server(listen_port, final_ssh_client)
            
            proxy_session = {
                'listen_port': listen_port,
                'server_socket': server_socket,
                'ssh_client': final_ssh_client,
                'tunnels': tunnels,
                'running': True,
                'accept_thread': None
            }
            
            # Start accepting connections
            accept_thread = threading.Thread(
                target=self._accept_connections,
                args=(server_socket, final_ssh_client)
            )
            accept_thread.daemon = True
            accept_thread.start()
            proxy_session['accept_thread'] = accept_thread
            
            self.proxy_sessions[session_alias] = proxy_session
            
            return {
                'status': 'started',
                'listen_port': listen_port,
                'session_alias': session_alias,
                'tunnel_count': len(tunnels)
            }
            
        except Exception as e:
            # Clean up on failure
            if 'tunnels' in locals():
                self._cleanup_tunnels(tunnels)
            raise Exception(f"Failed to open SOCKS5 proxy: {str(e)}")

    def close_proxy_sock5(self, session_alias: str) -> Dict[str, Any]:
        """
        Close a SOCKS5 proxy server and clean up all associated resources.
        
        Args:
            session_alias (str): The session alias to close
            
        Returns:
            Dict containing cleanup status
        """
        try:
            if session_alias not in self.proxy_sessions:
                raise Exception(f"No SOCKS5 proxy session found with alias: {session_alias}")
            
            proxy_session = self.proxy_sessions[session_alias]
            
            # Stop SOCKS5 server
            if 'server_socket' in proxy_session:
                proxy_session['server_socket'].close()
            
            # Close SSH client
            if 'ssh_client' in proxy_session:
                proxy_session['ssh_client'].close()
            
            # Clean up tunnels
            if 'tunnels' in proxy_session:
                self._cleanup_tunnels(proxy_session['tunnels'])
            
            # Mark as not running and remove from sessions
            proxy_session['running'] = False
            del self.proxy_sessions[session_alias]
            
            return {
                'status': 'closed',
                'session_alias': session_alias
            }
            
        except Exception as e:
            raise Exception(f"Failed to close SOCKS5 proxy: {str(e)}")

    def _create_nested_tunnels(self, tunnel_config: List[Dict[str, Any]]) -> List[SSHTunnelForwarder]:
        """
        Create a chain of SSH tunnels using sshtunnel.
        
        Args:
            tunnel_config: List of SSH hop configurations
            
        Returns:
            List of SSHTunnelForwarder objects
        """
        tunnels = []
        
        try:
            # If only one hop, no intermediate tunnels needed
            if len(tunnel_config) == 1:
                return tunnels
            
            # Create tunnels for each hop
            for i in range(len(tunnel_config) - 1):
                current_hop = tunnel_config[i]
                next_hop = tunnel_config[i + 1]
                
                # Determine the SSH address for this tunnel
                if i == 0:
                    # First tunnel connects directly to first hop
                    ssh_address_or_host = (current_hop['ip'], current_hop['port'])
                else:
                    # Subsequent tunnels connect through previous tunnel
                    prev_tunnel = tunnels[i - 1]
                    ssh_address_or_host = ('127.0.0.1', prev_tunnel.local_bind_port)
                
                # Create tunnel to next hop
                tunnel = SSHTunnelForwarder(
                    ssh_address_or_host=ssh_address_or_host,
                    ssh_username=current_hop['username'],
                    ssh_password=current_hop['password'],
                    remote_bind_address=(next_hop['ip'], next_hop['port']),
                    local_bind_address=('127.0.0.1', 0)  # 0 = auto-assign port
                )
                
                tunnel.start()
                tunnels.append(tunnel)
                print(f"Tunnel {i + 1} established: localhost:{tunnel.local_bind_port} -> {next_hop['ip']}:{next_hop['port']}")
            
            return tunnels
            
        except Exception as e:
            self._cleanup_tunnels(tunnels)
            raise Exception(f"Failed to create tunnel chain: {str(e)}")

    def _start_socks5_server(self, listen_port: int, ssh_client: paramiko.SSHClient) -> socket.socket:
        """
        Start a SOCKS5 server socket.
        
        Args:
            listen_port: Port to listen on
            ssh_client: SSH client to forward connections through
            
        Returns:
            Server socket object
        """
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('127.0.0.1', listen_port))
            server_socket.listen(10)
            
            return server_socket
            
        except Exception as e:
            raise Exception(f"Failed to start SOCKS5 server: {str(e)}")

    def _accept_connections(self, server_socket: socket.socket, ssh_client: paramiko.SSHClient) -> None:
        """
        Accept and handle SOCKS5 connections.
        
        Args:
            server_socket: Server socket to accept connections on
            ssh_client: SSH client to forward connections through
        """
        while True:
            try:
                client_socket, addr = server_socket.accept()
                # Handle each SOCKS5 connection in a separate thread
                thread = threading.Thread(
                    target=self._handle_socks5_connection,
                    args=(client_socket, ssh_client)
                )
                thread.daemon = True
                thread.start()
            except socket.error:
                # Server socket closed
                break
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def _handle_socks5_connection(self, client_socket: socket.socket, ssh_client: paramiko.SSHClient) -> None:
        """
        Handle a single SOCKS5 connection.
        
        Args:
            client_socket: Client socket connection
            ssh_client: SSH client to forward through
        """
        try:
            # SOCKS5 greeting
            data = client_socket.recv(1024)
            if len(data) < 3 or data[0] != 0x05:
                client_socket.close()
                return
            
            # Reply with no authentication required
            client_socket.send(b'\x05\x00')
            
            # SOCKS5 connection request
            data = client_socket.recv(1024)
            if len(data) < 8 or data[0] != 0x05 or data[1] != 0x01:
                client_socket.close()
                return
            
            # Parse target address
            addr_type = data[3]
            if addr_type == 0x01:  # IPv4
                target_host = socket.inet_ntoa(data[4:8])
                target_port = struct.unpack('>H', data[8:10])[0]
            elif addr_type == 0x03:  # Domain name
                domain_len = data[4]
                target_host = data[5:5+domain_len].decode('utf-8')
                target_port = struct.unpack('>H', data[5+domain_len:7+domain_len])[0]
            else:
                # Unsupported address type
                client_socket.send(b'\x05\x08\x00\x01\x00\x00\x00\x00\x00\x00')
                client_socket.close()
                return
            
            # Create SSH tunnel to target
            try:
                transport = ssh_client.get_transport()
                channel = transport.open_channel(
                    'direct-tcpip',
                    (target_host, target_port),
                    ('127.0.0.1', 0)
                )
                
                # Send success response
                client_socket.send(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00')
                
                # Start relaying data
                self._relay_data(client_socket, channel)
                
            except Exception as e:
                # Connection failed
                client_socket.send(b'\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00')
                client_socket.close()
                
        except Exception:
            client_socket.close()

    def _relay_data(self, socket1: socket.socket, socket2: paramiko.Channel) -> None:
        """
        Relay data between client socket and SSH channel.
        
        Args:
            socket1: Client socket
            socket2: SSH channel
        """
        def forward_data(source, destination, is_socket_to_channel=True):
            try:
                while True:
                    if is_socket_to_channel:
                        data = source.recv(4096)
                        if not data:
                            break
                        destination.send(data)
                    else:
                        data = source.recv(4096)
                        if not data:
                            break
                        destination.send(data)
            except:
                pass
            finally:
                try:
                    source.close()
                except:
                    pass
                try:
                    destination.close()
                except:
                    pass
        
        # Start forwarding in both directions
        thread1 = threading.Thread(target=forward_data, args=(socket1, socket2, True))
        thread2 = threading.Thread(target=forward_data, args=(socket2, socket1, False))
        
        thread1.daemon = True
        thread2.daemon = True
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()

    def _cleanup_tunnels(self, tunnels: List[SSHTunnelForwarder]) -> None:
        """
        Clean up a list of SSH tunnels.
        
        Args:
            tunnels: List of SSHTunnelForwarder objects to clean up
        """
        for tunnel in reversed(tunnels):
            try:
                tunnel.stop()
                print(f"Closed tunnel to: {tunnel.ssh_address_or_host}")
            except Exception as e:
                print(f"Error closing tunnel: {e}")