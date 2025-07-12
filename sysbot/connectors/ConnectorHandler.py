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

import socket, paramiko, json, importlib
from robot.utils import ConnectionCache
from robot.api.deco import keyword, library
from sshtunnel import SSHTunnelForwarder


class ConnectorHandler(object):
    """
    Interface for managing protocol-specific connections with optional SSH tunneling.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def __init__(self) -> None:
        """
        Initialize the ConnectorInterface with the specified protocol and optional tunneling parameters.
        """
        self._cache = ConnectionCache('No sessions created')
        self.protocol = None

    def __get_protocol__(self, protocol_name, product_name) -> object:
        """
        Retrieve and instantiate the protocol-specific connector.
        """
        try:
            module_name = f"sysbot.connectors.{protocol_name.lower()}.{product_name.lower()}"
            connector = importlib.import_module(module_name)
            self.protocol = getattr(connector, product_name.capitalize())()
        except ImportError as e:
            raise ImportError(f"Failed to import module '{module_name}': {str(e)}")
        except AttributeError as e:
            raise AttributeError(f"Module '{module_name}' does not have the attribute '{protocol_name.lower()}': {str(e)}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while retrieving the protocol: {str(e)}")

    def __nested_tunnel__(self, tunnel_config, target_config, index=0, previous_tunnels=None) -> dict:
        """
        Open nested SSH tunnels and establish the final connection.
        """
        if previous_tunnels is None:
            previous_tunnels = []

        try:
            if index >= len(tunnel_config):
                session = self.protocol.open_session(
                    'localhost',
                    previous_tunnels[-1].local_bind_port,
                    target_config['username'],
                    target_config['password']
                )
                return {"session": session, "tunnels": previous_tunnels}

            config = tunnel_config[index]
            ssh_address_or_host = (
                'localhost', previous_tunnels[-1].local_bind_port
            ) if previous_tunnels else (config['ip'], int(config['port']))
            remote_bind_address = (
                target_config['ip'], int(target_config['port'])
            ) if index == len(tunnel_config) - 1 else (
                tunnel_config[index + 1]['ip'], int(tunnel_config[index + 1]['port'])
            )

            tunnel = SSHTunnelForwarder(
                ssh_address_or_host=ssh_address_or_host,
                remote_bind_address=remote_bind_address,
                ssh_username=config['username'],
                ssh_password=config['password']
            )
            tunnel.start()
            print(f"Tunnel {index + 1} established: {ssh_address_or_host[0]}:{ssh_address_or_host[1]}")
            previous_tunnels.append(tunnel)

            return self.__nested_tunnel__(tunnel_config, target_config, index + 1, previous_tunnels)
        except Exception as e:
            for tunnel in reversed(previous_tunnels):
                tunnel.stop()
                try:
                    tunnel.ssh_address_or_host
                except:
                    print(f"Closed tunnel")
                else:
                    print(f"Closed tunnel to: {tunnel.ssh_address_or_host}")
            raise Exception(f"Failed to establish nested tunnels: {str(e)}")

    def open_session(self, alias: str, protocol: str, product: str, host: str, port: int, login: str=None, password: str=None, tunnel_config=None) -> None:
        """
        Open a session to the target host with optional nested SSH tunneling.
        """
        tunnels = []
        self.__get_protocol__(protocol, product)
        self.remote_port = int(port)
        try:
            if tunnel_config:
                try:
                    if type(tunnel_config) is str:
                        tunnel_config = json.loads(tunnel_config)
                except Exception as e:
                    raise Exception(f"Error during importing tunnel as json: {e}")
                target_config = {
                    'ip': host,
                    'port': int(self.remote_port),
                    'username': login,
                    'password': password
                }
                connection = self.__nested_tunnel__(tunnel_config, target_config)
                tunnels = connection["tunnels"]
            else:
                session = self.protocol.open_session(host, int(self.remote_port), login, password)
                if not session:
                    raise Exception("Failed to open direct session")
                connection = {"session": session, "tunnels": None}

            self._cache.register(connection, alias)
        except Exception as e:
            for tunnel in reversed(tunnels):
                tunnel.stop()
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, alias: str, command: str, **kwargs) -> any:
        """
        Execute a command on the specified session.
        """
        try:
            connection = self._cache.switch(alias)
            if not connection or 'session' not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")

            result = self.protocol.execute_command(connection['session'], command, **kwargs)
            return result
        except ValueError as ve:
            raise ValueError(f"Alias '{alias}' does not exist: {str(ve)}")
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_all_sessions(self) -> None:
        """
        Close all active sessions and stop any associated SSH tunnels.
        """
        try:
            for connection in self._cache._connections:
                self.protocol.close_session(connection['session'])
                if connection['tunnels'] is not None:
                    for tunnel in reversed(connection['tunnels']):
                        tunnel.stop()
            self._cache.empty_cache()
        except Exception as e:
            raise Exception(f"Failed to close all sessions: {str(e)}")

    def close_session(self, alias: str) -> None:
        try:
            connection = self._cache.switch(alias)
            if not connection or 'session' not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")
            self.protocol.close_session(connection)
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")

    def open_proxy_sock5(self, alias: str, listen_port: int, tunnel_config) -> dict:
        """
        Open a SOCKS5 proxy server that forwards connections through SSH tunnel chain.
        
        Args:
            alias (str): Unique identifier for this proxy session
            listen_port (int): Local port to listen for SOCKS5 connections  
            tunnel_config: SSH tunnel configuration (JSON string or list of dicts)
                Format: [{'ip': 'host1', 'port': 22, 'username': 'user1', 'password': 'pass1'}, ...]
                
        Returns:
            dict: Proxy server details and status
        """
        try:
            # Import the SOCKS5 proxy connector
            from .ssh.socks5_proxy import Socks5Proxy
            
            # Parse tunnel config if it's a JSON string
            if isinstance(tunnel_config, str):
                try:
                    tunnel_config = json.loads(tunnel_config)
                except Exception as e:
                    raise Exception(f"Error parsing tunnel config JSON: {e}")
            
            if not isinstance(tunnel_config, list) or not tunnel_config:
                raise Exception("tunnel_config must be a non-empty list of SSH hop configurations")
            
            # Create SOCKS5 proxy instance
            socks5_proxy = Socks5Proxy()
            
            # Open the SOCKS5 proxy
            result = socks5_proxy.open_proxy_sock5(alias, listen_port, tunnel_config)
            
            # Store the proxy instance in cache for later cleanup
            proxy_connection = {
                'proxy_instance': socks5_proxy,
                'type': 'socks5_proxy'
            }
            self._cache.register(proxy_connection, alias)
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to open SOCKS5 proxy: {str(e)}")

    def close_proxy_sock5(self, alias: str) -> dict:
        """
        Close a SOCKS5 proxy server and clean up all associated resources.
        
        Args:
            alias (str): The proxy session alias to close
            
        Returns:
            dict: Cleanup status
        """
        try:
            # Get the proxy connection from cache
            try:
                connection = self._cache.switch(alias)
                if not connection or 'proxy_instance' not in connection:
                    raise RuntimeError(f"No SOCKS5 proxy session found for alias '{alias}'")
            except ValueError:
                raise ValueError(f"No SOCKS5 proxy session found with alias '{alias}'")
            
            proxy_instance = connection['proxy_instance']
            
            # Close the SOCKS5 proxy
            result = proxy_instance.close_proxy_sock5(alias)
            
            # Remove from cache
            self._cache._connections = [conn for conn in self._cache._connections if conn != connection]
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to close SOCKS5 proxy: {str(e)}")