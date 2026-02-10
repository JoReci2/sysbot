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

import json

from .utils.engine import ComponentMeta
from .utils.engine import TunnelingManager
from .utils.engine import ComponentLoader
from .utils.engine import Cache


class Sysbot(metaclass=ComponentMeta):
    """
    Main Sysbot class for managing system automation and remote connections.

    This class provides a unified interface for managing remote system connections,
    executing commands, and interacting with various system modules and plugins.
    It supports multiple protocols (SSH, WinRM, Socket, Local) and can manage
    tunneling configurations for complex network setups.

    Attributes:
        ROBOT_LIBRARY_SCOPE: Robot Framework library scope set to GLOBAL.
        ROBOT_LIBRARY_DOC_FORMAT: Documentation format set to reST.
    """
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_DOC_FORMAT = "reST"

    def __init__(self, components=None):
        """
        Initialize the Sysbot instance.

        Args:
            components: Optional list of component paths to load. If None,
                automatically discovers and loads all available modules and plugins.
                Component paths should be in the format 'modules.name' or 'plugins.name'.
        """
        if components is None:
            all_modules = ComponentLoader.discover_all_components(__file__, "modules")
            all_plugins = ComponentLoader.discover_all_components(__file__, "plugins")
            components = []
            components.extend([f"modules.{module}" for module in all_modules])
            components.extend([f"plugins.{plugin}" for plugin in all_plugins])
        ComponentLoader.load_components(self, components)
        self._cache = Cache("No sessions created")
        self._protocol = None

    def open_session(
        self,
        alias: str,
        protocol: str,
        product: str,
        host: str,
        port: int,
        login: str = None,
        password: str = None,
        tunnel_config=None,
        is_secret=False,
        **kwargs,
    ) -> None:
        """
        Open a new remote session with the specified connection parameters.

        This method establishes a connection to a remote system using the specified
        protocol and credentials. It supports direct connections and tunneling through
        intermediate hosts for complex network configurations.

        Args:
            alias: Unique identifier for the session.
            protocol: Connection protocol to use (e.g., 'ssh', 'winrm', 'socket', 'local').
            product: Product-specific implementation (e.g., 'bash', 'powershell').
            host: Target host IP address or hostname.
            port: Target port number.
            login: Username for authentication. Optional if is_secret is True.
            password: Password for authentication. Optional if is_secret is True.
            tunnel_config: Optional tunnel configuration as JSON string or dict for
                nested tunneling through intermediate hosts.
            is_secret: If True, treats host, login, and password as secret keys to
                retrieve actual values from the secret cache.
            **kwargs: Additional protocol-specific connection options.

        Raises:
            Exception: If the session fails to open or tunnel configuration is invalid.
        """
        tunnels = []
        self._protocol = TunnelingManager.get_protocol(protocol, product)
        self._remote_port = int(port)
        try:
            if tunnel_config:
                try:
                    if type(tunnel_config) is str:
                        tunnel_config = json.loads(
                            self._cache.secrets.get(tunnel_config)
                        )
                except Exception as e:
                    raise Exception(f"Error during importing tunnel as json: {e}")
                if is_secret:
                    target_config = {
                        "ip": self._cache.secrets.get(host),
                        "port": int(self._remote_port),
                        "username": self._cache.secrets.get(login),
                        "password": self._cache.secrets.get(password),
                    }
                else:
                    target_config = {
                        "ip": host,
                        "port": int(self._remote_port),
                        "username": login,
                        "password": password,
                    }
                TunnelingManager.nested_tunnel(
                    self._protocol, tunnel_config, target_config
                )
                connection = TunnelingManager.nested_tunnel(
                    self._protocol, tunnel_config, target_config
                )
                tunnels = connection["tunnels"]
            else:
                if is_secret:
                    session = self._protocol.open_session(
                        self._cache.secrets.get(host),
                        int(self._remote_port),
                        self._cache.secrets.get(login),
                        self._cache.secrets.get(password),
                        **kwargs
                    )
                else:
                    session = self._protocol.open_session(
                        host, int(self._remote_port), login, password, **kwargs
                    )
                if not session:
                    raise Exception("Failed to open direct session")
                connection = {"session": session, "tunnels": None}

            self._cache.connections.register(connection, alias)
        except Exception as e:
            for tunnel in reversed(tunnels):
                tunnel.stop()
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, alias: str, command: str, **kwargs) -> any:
        """
        Execute a command on a remote session.

        Args:
            alias: Session alias identifying the connection to use.
            command: Command string to execute on the remote system.
            **kwargs: Additional command execution options specific to the protocol.

        Returns:
            Command execution result. The format depends on the protocol used.

        Raises:
            ValueError: If the specified alias does not exist.
            RuntimeError: If no valid session is found for the alias.
            Exception: If command execution fails.
        """
        try:
            connection = self._cache.connections.switch(alias)
            if not connection or "session" not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")

            result = self._protocol.execute_command(
                connection["session"], command, **kwargs
            )
            return result
        except ValueError as ve:
            raise ValueError(f"Alias '{alias}' does not exist: {str(ve)}")
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_all_sessions(self) -> None:
        """
        Close all active sessions and clean up associated resources.

        This method closes all open connections, stops all active tunnels,
        and clears the connection cache.

        Raises:
            Exception: If any session fails to close properly.
        """
        try:
            for connection in self._cache.connections.get_all().values():
                self._protocol.close_session(connection["session"])
                if connection["tunnels"] is not None:
                    for tunnel in reversed(connection["tunnels"]):
                        tunnel.stop()
            self._cache.connections.clear_all()
        except Exception as e:
            raise Exception(f"Failed to close all sessions: {str(e)}")

    def close_session(self, alias: str) -> None:
        """
        Close a specific session identified by its alias.

        Args:
            alias: Session alias identifying the connection to close.

        Raises:
            RuntimeError: If no valid session is found for the alias.
            Exception: If the session fails to close properly.
        """
        try:
            connection = self._cache.connections.switch(alias)
            if not connection or "session" not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")
            self._protocol.close_session(connection["session"])
            self._cache.connections.clear(alias)
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")

    def call_components(self, function_path: str, *args, **kwargs) -> any:
        """
        Dynamically call a function from loaded components.

        This method allows calling any function from loaded modules or plugins
        using a dot-notation path (e.g., 'modules.linux.systemd.is_active').

        Args:
            function_path: Dot-separated path to the function (e.g., 'module.submodule.function').
                Must contain at least module.function.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            The result returned by the called function.

        Raises:
            ValueError: If the function path format is invalid.
            AttributeError: If the module or function is not found.
            TypeError: If the target is not a callable function.
            Exception: If the function call fails.
        """
        try:
            parts = function_path.split(".")
            if len(parts) < 2:
                raise ValueError(
                    f"Function path must contain at least module.function, got: '{function_path}'"
                )

            module_parts = parts[:-1]
            function_name = parts[-1]

            current_obj = self
            for part in module_parts:
                if hasattr(current_obj, part):
                    current_obj = getattr(current_obj, part)
                else:
                    raise AttributeError(
                        f"Module '{part}' not found in path '{'.'.join(module_parts)}'"
                    )

            if not hasattr(current_obj, function_name):
                raise AttributeError(
                    f"Function '{function_name}' not found in module '{'.'.join(module_parts)}'"
                )

            function = getattr(current_obj, function_name)

            if not callable(function):
                raise TypeError(f"'{function_name}' is not a callable function")

            result = function(*args, **kwargs)
            return result

        except Exception as e:
            raise Exception(f"Failed to call function '{function_path}': {str(e)}")

    def get_secret(self, secret_name: str) -> any:
        """
        Retrieve a secret value from the secret cache.

        Args:
            secret_name: Name of the secret to retrieve.

        Returns:
            The secret value associated with the given name.
        """
        return self._cache.secrets.get(secret_name)

    def add_secret(self, secret_name: str, value: any) -> None:
        """
        Add or update a secret in the secret cache.

        Args:
            secret_name: Name of the secret to store.
            value: Secret value to store (can be any type).
        """
        self._cache.secrets.register(secret_name, value)

    def remove_secret(self, secret_name: str) -> None:
        """
        Remove a secret from the secret cache.

        Args:
            secret_name: Name of the secret to remove.
        """
        self._cache.secrets.clear(secret_name)
