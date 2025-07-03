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
import logging
from robot.utils import ConnectionCache
from robot.api.deco import keyword, library
from sshtunnel import SSHTunnelForwarder
from sysbot.connectors.utils import AbstractConnector
from sysbot.connectors.utils.tunnels import TunnelManager
from typing import Optional, cast

# Configuration du logger
logger = logging.getLogger(__name__)

# Utilitaire pour garantir un str non-None
def safe_str(val) -> str:
    return '' if val is None else str(val)

@library
class ConnectorHandler(object):
    """
    Interface for managing protocol-specific connections with optional SSH tunneling.
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def __init__(self) -> None:
        """
        Initialize the ConnectorHandler with a connection cache.
        """
        self._cache = ConnectionCache('No sessions created')
        self.tunnel_manager = TunnelManager()

    def _get_protocol(self, protocol_name: str, product_name: str) -> AbstractConnector:
        """
        Retrieve and instantiate the protocol-specific connector.
        """
        module_name = f"sysbot.connectors.{protocol_name.lower()}.{product_name.lower()}"
        class_name = product_name.capitalize()
        try:
            connector_module = importlib.import_module(module_name)
            connector_class = getattr(connector_module, class_name, None)
            if connector_class is None:
                raise ImportError(f"Class '{class_name}' not found in module '{module_name}'")
            if not isinstance(connector_class, type) or not issubclass(connector_class, AbstractConnector):
                raise TypeError(f"{class_name} does not inherit from AbstractConnector")
            return connector_class()
        except Exception as e:
            logger.error(f"Failed to import protocol '{protocol_name}' product '{product_name}': {e}")
            raise

    def _get_protocol_from_connection(self, connection: dict) -> AbstractConnector:
        """
        Retrieve the protocol instance from the connection dict.
        """
        protocol = connection.get("protocol")
        if protocol is None:
            raise RuntimeError("No protocol instance found in connection")
        return protocol

    @keyword
    def open_session(self, alias: str, protocol: str, product: str, host: str = '', port: int = 0, login: str = '', password: str = '', tunnel_config = None) -> None:
        """
        Open a session to the target host with optional nested SSH tunneling.
        """
        tunnels = []
        protocol_instance = self._get_protocol(protocol, product)
        remote_port = int(port)
        try:
            if tunnel_config:
                host = host or ''
                login = login or ''
                password = password or ''
                if isinstance(tunnel_config, str):
                    try:
                        tunnel_config = json.loads(tunnel_config)
                    except Exception as e:
                        raise Exception(f"Error during importing tunnel as json: {e}")
                target_config = {
                    'ip': host,
                    'port': remote_port,
                    'username': login,
                    'password': password
                }
                connection = self.tunnel_manager.open_nested_tunnel(
                    tunnel_config,
                    target_config,
                    protocol_instance.open_session
                )
                tunnels = connection["tunnels"]
            else:
                safe_login = login if login is not None else ''
                safe_password = password if password is not None else ''
                session = protocol_instance.open_session(host, remote_port, safe_login, safe_password)
                if not session:
                    raise Exception("Failed to open direct session")
                connection = {"session": session, "tunnels": None, "protocol": protocol_instance}
            self._cache.register(connection, alias)
        except Exception as e:
            self.tunnel_manager.close_tunnels(tunnels)
            logger.error(f"Failed to open session: {e}")
            raise

    @keyword
    def execute_command(self, alias: str, command: str) -> any:
        """
        Execute a command on the specified session.
        """
        try:
            connection = self._cache.switch(alias)
            if not isinstance(connection, dict) or 'session' not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")
            protocol_instance = self._get_protocol_from_connection(connection)
            result = protocol_instance.execute_command(connection['session'], command)
            return result
        except ValueError as ve:
            logger.error(f"Alias '{alias}' does not exist: {ve}")
            raise
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            raise

    @keyword
    def close_all_sessions(self) -> None:
        """
        Close all active sessions and stop any associated SSH tunnels.
        """
        try:
            for connection in self._cache._connections:
                protocol_instance = self._get_protocol_from_connection(connection)
                protocol_instance.close_session(connection['session'])
                if connection['tunnels'] is not None:
                    for tunnel in reversed(connection['tunnels']):
                        tunnel.stop()
            self._cache.empty_cache()
        except Exception as e:
            logger.error(f"Failed to close all sessions: {e}")
            raise
