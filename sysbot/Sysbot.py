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
    ROBOT_LIBRARY_SCOPE = "SUITE"
    ROBOT_LIBRARY_DOC_FORMAT = "reST"

    def __init__(self, components=None):
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
        tunnels = []
        self._protocol = TunnelingManager.get_protocol(protocol, product)
        self._remote_port = int(port) if port else None
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
                        "port": int(self._remote_port) if self._remote_port else None,
                        "username": self._cache.secrets.get(login),
                        "password": self._cache.secrets.get(password),
                    }
                else:
                    target_config = {
                        "ip": host,
                        "port": int(self._remote_port) if self._remote_port else None,
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
                    session_result = self._protocol.open_session(
                        self._cache.secrets.get(host),
                        int(self._remote_port) if self._remote_port else None,
                        self._cache.secrets.get(login),
                        self._cache.secrets.get(password),
                    )
                else:
                    session_result = self._protocol.open_session(
                        host, int(self._remote_port) if self._remote_port else None, login, password
                    )
                
                # Handle new dict response format with StatusCode, Session, Result, Error
                if isinstance(session_result, dict) and "StatusCode" in session_result:
                    if session_result["StatusCode"] != 0:
                        raise Exception(f"Failed to open session: {session_result.get('Error', 'Unknown error')}")
                    session = session_result["Session"]
                else:
                    # Old format: direct session object
                    session = session_result
                
                if not session:
                    raise Exception("Failed to open direct session")
                connection = {"session": session, "tunnels": None}

            self._cache.connections.register(connection, alias)
        except Exception as e:
            for tunnel in reversed(tunnels):
                tunnel.stop()
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, alias: str, command: str, **kwargs) -> any:
        try:
            connection = self._cache.connections.switch(alias)
            if not connection or "session" not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")

            result = self._protocol.execute_command(
                connection["session"], command, **kwargs
            )
            
            # Handle new dict response format with StatusCode, Result, Error, Metadata
            if isinstance(result, dict) and "StatusCode" in result:
                # For backward compatibility, if StatusCode is 0, return just the Result
                # Otherwise, return the full dict so users can see error details
                if result["StatusCode"] == 0 and result.get("Error") is None:
                    return result["Result"]
                else:
                    # Return full dict when there's an error or non-zero status
                    return result
            else:
                # Old format: direct result
                return result
        except ValueError as ve:
            raise ValueError(f"Alias '{alias}' does not exist: {str(ve)}")
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_all_sessions(self) -> None:
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
        try:
            connection = self._cache.connections.switch(alias)
            if not connection or "session" not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")
            self._protocol.close_session(connection["session"])
            self._cache.connections.clear(alias)
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")

    def call_components(self, function_path: str, *args, **kwargs) -> any:
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
        return self._cache.secrets.get(secret_name)

    def add_secret(self, secret_name: str, value: any) -> None:
        self._cache.secrets.register(secret_name, value)

    def remove_secret(self, secret_name: str) -> None:
        self._cache.secrets.clear(secret_name)
