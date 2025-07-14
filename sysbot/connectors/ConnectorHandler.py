import socket, paramiko, json
from robot.utils import ConnectionCache
from robot.api.deco import keyword, library
from sshtunnel import SSHTunnelForwarder

from ..utils import TunnelingManager


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


    def __get_protocol__(self, protocol_name, product_name):
        self.protocol = TunnelingManager.get_protocol(protocol_name, product_name)


    def __nested_tunnel__(self, tunnel_config, target_config):
        return TunnelingManager.nested_tunnel(self.protocol, tunnel_config, target_config)

    def open_session(self, alias: str, protocol: str, product: str, host: str, port: int, login: str=None, password: str=None, tunnel_config=None, **kwargs) -> None:
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