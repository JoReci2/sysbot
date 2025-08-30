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

import importlib
import json
#from robot.utils import ConnectionCache

from .utils.engine import ComponentMeta
from .utils.engine import TunnelingManager
from .utils.engine import ComponentLoader
from .utils.cache import Cache as ConnectionCache


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
        self._cache = ConnectionCache("No sessions created")
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
        **kwargs,
    ) -> None:
        tunnels = []
        self._protocol = TunnelingManager.get_protocol(protocol, product)
        self._remote_port = int(port)
        try:
            if tunnel_config:
                try:
                    if type(tunnel_config) is str:
                        tunnel_config = json.loads(tunnel_config)
                except Exception as e:
                    raise Exception(f"Error during importing tunnel as json: {e}")
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
                session = self._protocol.open_session(
                    host, int(self._remote_port), login, password
                )
                if not session:
                    raise Exception("Failed to open direct session")
                connection = {"session": session, "tunnels": None}

            self._cache.register(connection, alias)
        except Exception as e:
            for tunnel in reversed(tunnels):
                tunnel.stop()
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, alias: str, command: str, **kwargs) -> any:
        try:
            connection = self._cache.switch(alias)
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
        try:
            for connection in self._cache.get_all_connections().values():
                self._protocol.close_session(connection["session"])
                if connection["tunnels"] is not None:
                    for tunnel in reversed(connection["tunnels"]):
                        tunnel.stop()
            self._cache.empty_cache()
        except Exception as e:
            raise Exception(f"Failed to close all sessions: {str(e)}")

    def close_session(self, alias: str) -> None:
        try:
            connection = self._cache.switch(alias)
            if not connection or "session" not in connection:
                raise RuntimeError(f"No valid session found for alias '{alias}'")
            self._protocol.close_session(connection)
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

    def import_data_from(self, module: str, **kwargs) -> any:
        module = module.lower()

        try:
            module_name = f"sysbot.dataloaders.{module}"
            loader_module = importlib.import_module(module_name)
            result = loader_module.load(**kwargs)
            return result

        except ModuleNotFoundError:
            raise ValueError(f"No loader available for module: {module}")

        except Exception as e:
            raise RuntimeError(f"An error occurred while processing the module: {e}")
