import socket, socks, paramiko, json, importlib
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
        self.client = None

    def __get_protocol__(self, protocol_name) -> object:
        """
        Retrieve and instantiate the protocol-specific connector.
        """
        try:
            module_name = f"sysbot.connectors.{protocol_name.lower()}"
            connector = importlib.import_module(module_name)
            self.protocol = getattr(connector, protocol_name.lower())()
        except ImportError as e:
            raise ImportError(f"Failed to import module '{module_name}': {str(e)}")
        except AttributeError as e:
            raise AttributeError(f"Module '{module_name}' does not have the attribute '{protocol_name.lower()}': {str(e)}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while retrieving the protocol: {str(e)}")

    def __ssh_tunnel__(self, tunnel_config, target_config, index=0, previous_tunnels=None) -> dict:
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

    def __socks5_proxy__(self, proxy_config, target_config, previous_proxies=None):
        """
        Establishes chained SOCKS5 proxies.
        """
        if previous_proxies is None:
            previous_proxies = []

        try:
            for index, config in enumerate(proxy_config):
                proxy_host, proxy_port = previous_proxies[-1] if previous_proxies else (None, None)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                if proxy_host and proxy_port:
                    sock = socks.socksocket()
                    sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
                    sock.connect((config['ip'], int(config['port'])))
                    ssh_client.connect(config['ip'], config['port'], config['username'], config['password'], sock=sock)
                else:
                    ssh_client.connect(config['ip'], config['port'], config['username'], config['password'])

                local_socks5_port = 1080 + index
                threading.Thread(target=self.__start_socks5_proxy__, args=(ssh_client, local_socks5_port), daemon=True).start()
                previous_proxies.append(("127.0.0.1", local_socks5_port))
            
            return previous_proxies
        except Exception as e:
            raise Exception(f"Failed to establish SOCKS5 proxies: {str(e)}")
    
    def open_session(self, alias: str, protocol: str, host: str, port: int, login: str, password: str, ssh_tunnel=None, socks5=None) -> None:
        """
        Open a session to the target host with optional nested SSH tunneling.
        """
        tunnels = []
        proxy_chain = []
        self.__get_protocol__(protocol)
        self.remote_port = int(port)
        try:
            if ssh_tunnel:
                if isinstance(ssh_tunnel, str):
                    ssh_tunnel = json.loads(ssh_tunnel)
                target_config = {'ip': host, 'port': int(self.remote_port), 'username': login, 'password': password}
                connection = self.__ssh_tunnel__(ssh_tunnel, target_config)
                tunnels = connection["tunnels"]
            
            elif socks5:
                if isinstance(socks5, str):
                    socks5 = json.loads(socks5)
                target_config = {'ip': host, 'port': int(self.remote_port), 'username': login, 'password': password}
                socks5_proxies = self.__socks5_proxy__(socks5, target_config)
                socks.set_default_proxy(socks.SOCKS5, socks5_proxies[-1][0], socks5_proxies[-1][1])
                socket.socket = socks.socksocket
                session = self.protocol.open_session(host, int(self.remote_port), login, password)
                connection = {"session": session, "socks5_proxies": socks5_proxies}

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

    def execute_command(self, alias: str, command: str, options: str = None) -> dict[str, str]:
        """
        Execute a command on the specified session.
        """
        try:
            connection = self._cache.switch(alias)
            if not connection or 'session' not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")

            result = self.protocol.execute_command(connection['session'], command, options)
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