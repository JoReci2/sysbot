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
from abc import ABC, abstractmethod

class ConnectorInterface(ABC):
    """
    Abstract base class for protocol-specific connectors.
    """

    @abstractmethod
    def open_session(self, host: str, port: int, login: str = None, password: str = None) -> object:
        """
        Open a session to the target host.
        """
        pass

    @abstractmethod
    def execute_command(self, session: object, command: str, script: bool = False, runas: bool = False) -> any:
        """
        Execute a command on the specified session.
        """
        pass

    @abstractmethod
    def close_session(self, session: object) -> None:
        """
        Close the specified session.
        """
        pass

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
                print(f"Tunnel closed: {tunnel.ssh_address_or_host}")
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, alias: str, command: str) -> any:
        """
        Execute a command on the specified session.
        """
        try:
            connection = self._cache.switch(alias)
            if not connection or 'session' not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")

            result = self.protocol.execute_command(connection['session'], command)
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
