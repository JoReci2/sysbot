import socket, paramiko, json, importlib
from robot.utils import ConnectionCache
from robot.api.deco import keyword, library
from sshtunnel import SSHTunnelForwarder


class ConnectorInterface(object):
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

    def __get_protocol__(self, protocol_name) -> object:
        """
        Retrieve and instantiate the protocol-specific connector.
        """
        try: 
            module_name = f"sysbot.connectors.{protocol_name.lower()}"
            connector = importlib.import_module(module_name)
            self.protocol = getattr(connector, protocol_name.lower())()
        except:
            raise ValueError("Protocol not found")

    def __nested_tunnel__(self, tunnel_config, target_config, index=0, previous_tunnels=None) -> dict:
        """
        Open nested SSH tunnels and establish the final connection.

        Args:
            tunnel_config (list): List of intermediate SSH tunnel configurations.
            target_config (dict): Final target connection configuration.
            index (int): Current index of the tunnel configuration (default: 0).
            previous_tunnels (list): List of previously opened tunnels (default: None).

        Returns:
            dict: Contains the final session and the list of opened tunnels.

        Raises:
            Exception: If any tunnel fails to open.
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

    def open_session(self, alias: str, protocol: str, host: str, port: int, login: str, password: str, tunnel_config=None) -> None:
        """
        Open a session to the target host with optional nested SSH tunneling.
        """
        tunnels = []
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
                self.__get_protocol__(protocol)
                self.remote_port = int(port)
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

    def execute_command(self, alias: str, command: str) -> str:
        """
        Execute a command on the specified session.
        """
        try:
            connection = self._cache.switch(alias)
            if not connection or 'session' not in connection:
                raise Exception(f"No valid session found for alias '{alias}'")

            result = self.protocol.execute_command(connection['session'], command)
            return result
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
