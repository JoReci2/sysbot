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

import base64
import os
import json
import importlib
from sshtunnel import SSHTunnelForwarder
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from cryptography.fernet import Fernet


class ConnectorInterface(ABC):
    def __init__(self):
        self._cache = None

    def set_cache(self, cache):
        self._cache = cache

    @abstractmethod
    def open_session(self, host, port, login, password):
        pass

    @abstractmethod
    def execute_command(self, session, command, **kwargs):
        pass

    @abstractmethod
    def close_session(self, session):
        pass


class ComponentMeta(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)


class ComponentGroup:
    def __init__(self, name):
        self.name = name


class ComponentBase:
    def __init__(self):
        self._sysbot = None

    def set_sysbot_instance(self, sysbot_instance):
        self._sysbot = sysbot_instance

    def execute_command(self, alias, command, **kwargs):
        if self._sysbot is None:
            raise RuntimeError("No Sysbot instance available")
        return self._sysbot.execute_command(alias, command, **kwargs)


class ComponentLoader:
    @staticmethod
    def discover_all_components(sysbot_file_path, component_type):
        components_dir = Path(sysbot_file_path).parent / component_type
        available_components = []

        def scan_directory(directory, prefix=""):
            if not directory.exists():
                return

            for item in directory.iterdir():
                if (
                    item.is_file()
                    and item.suffix == ".py"
                    and item.name != "__init__.py"
                ):
                    component_path = f"{prefix}.{item.stem}" if prefix else item.stem
                    available_components.append(component_path)
                elif item.is_dir() and not item.name.startswith("."):
                    new_prefix = f"{prefix}.{item.name}" if prefix else item.name
                    scan_directory(item, new_prefix)

        scan_directory(components_dir)
        return available_components

    @staticmethod
    def load_components(sysbot_instance, component_list):
        for component_full_path in component_list:
            try:
                parts = component_full_path.split(".", 1)
                if len(parts) != 2:
                    raise ValueError(
                        f"Invalid component path format: {component_full_path}"
                    )

                component_type, component_path = parts

                full_import_path = f"sysbot.{component_type}.{component_path}"
                component_module = importlib.import_module(full_import_path)

                component_name = component_path.split(".")[-1]
                class_name = component_name.capitalize()

                if hasattr(component_module, class_name):
                    component_class = getattr(component_module, class_name)
                    component_instance = component_class()
                    ComponentLoader.create_hierarchy(
                        sysbot_instance, component_full_path, component_instance
                    )
                else:
                    raise AttributeError(
                        f"Class '{class_name}' not found in {full_import_path}"
                    )

            except ImportError as e:
                raise Exception(f"Unable to load component {component_full_path}: {e}")

    @staticmethod
    def create_hierarchy(sysbot_instance, component_full_path, component_instance):
        if hasattr(component_instance, "set_sysbot_instance"):
            component_instance.set_sysbot_instance(sysbot_instance)

        parts = component_full_path.split(".")
        current_obj = sysbot_instance

        for i, part in enumerate(parts[:-1]):
            if not hasattr(current_obj, part):
                setattr(current_obj, part, ComponentGroup(part))
            current_obj = getattr(current_obj, part)

        final_name = parts[-1]
        setattr(current_obj, final_name, component_instance)


class TunnelingManager:
    @staticmethod
    def get_protocol(protocol_name, product_name, cache=None):
        try:
            # Try new structure first: single file per protocol (e.g., sysbot.connectors.ssh)
            try:
                module_name = f"sysbot.connectors.{protocol_name.lower()}"
                connector = importlib.import_module(module_name)
                connector_class = getattr(connector, product_name.capitalize())
                instance = connector_class()

                if cache and hasattr(instance, "set_cache"):
                    instance.set_cache(cache)

                return instance
            except (ImportError, AttributeError):
                # Fall back to old structure: subdirectory per protocol (e.g., sysbot.connectors.ssh.bash)
                module_name = (
                    f"sysbot.connectors.{protocol_name.lower()}.{product_name.lower()}"
                )
                connector = importlib.import_module(module_name)
                connector_class = getattr(connector, product_name.capitalize())
                instance = connector_class()

                if cache and hasattr(instance, "set_cache"):
                    instance.set_cache(cache)

                return instance
        except ImportError as e:
            raise ImportError(f"Failed to import module '{module_name}': {str(e)}")
        except AttributeError as e:
            raise AttributeError(
                f"Module '{module_name}' does not have the attribute '{product_name.capitalize()}': {str(e)}"
            )
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while retrieving the protocol: {str(e)}"
            )

    @staticmethod
    def nested_tunnel(
        protocol, tunnel_config, target_config, index=0, previous_tunnels=None
    ):
        if previous_tunnels is None:
            previous_tunnels = []
        try:
            if index >= len(tunnel_config):
                session = protocol.open_session(
                    "localhost",
                    previous_tunnels[-1].local_bind_port,
                    target_config["username"],
                    target_config["password"],
                )
                return {"session": session, "tunnels": previous_tunnels}
            config = tunnel_config[index]
            ssh_address_or_host = (
                ("localhost", previous_tunnels[-1].local_bind_port)
                if previous_tunnels
                else (config["ip"], int(config["port"]))
            )
            remote_bind_address = (
                (target_config["ip"], int(target_config["port"]))
                if index == len(tunnel_config) - 1
                else (
                    tunnel_config[index + 1]["ip"],
                    int(tunnel_config[index + 1]["port"]),
                )
            )
            tunnel = SSHTunnelForwarder(
                ssh_address_or_host=ssh_address_or_host,
                remote_bind_address=remote_bind_address,
                ssh_username=config["username"],
                ssh_password=config["password"],
            )
            tunnel.start()
            previous_tunnels.append(tunnel)
            return TunnelingManager.nested_tunnel(
                protocol, tunnel_config, target_config, index + 1, previous_tunnels
            )
        except Exception as e:
            for tunnel in reversed(previous_tunnels):
                tunnel.stop()
            raise Exception(f"Failed to establish nested tunnels: {str(e)}")


class Cache:
    def __init__(self, no_current_error: str = "No current connection."):
        self.secrets = SecretsManager()
        self.connections = ConnectionsManager(no_current_error)

    def empty_cache(self) -> None:
        self.connections.clear_all()
        self.secrets.clear_all()

    def get_cache_stats(self) -> Dict[str, Any]:
        return {
            "connections": self.connections.get_stats(),
            "secrets": self.secrets.get_stats(),
        }

    def __len__(self) -> int:
        return len(self.connections) + len(self.secrets)


class ConnectionsManager:
    def __init__(self, no_current_error: str = "No current connection."):
        self._connections: Dict[int, Any] = {}
        self._aliases: Dict[str, int] = {}
        self._current_index: Optional[int] = None
        self._no_current_error = no_current_error

    def register(self, connection: Any, alias: Optional[str] = None) -> int:
        index = self._get_next_index()
        self._connections[index] = connection
        self._current_index = index

        if alias:
            self._aliases[alias] = index

        return index

    def switch(self, index_or_alias: Union[int, str]) -> Any:
        index = self._resolve_index(index_or_alias)
        if index not in self._connections:
            raise RuntimeError(f"Connection with index '{index}' does not exist.")

        self._current_index = index
        return self._connections[index]

    def get(self, index_or_alias: Union[int, str, None] = None) -> Any:
        if index_or_alias is None:
            if self._current_index is None:
                raise RuntimeError(self._no_current_error)
            return self._connections[self._current_index]

        index = self._resolve_index(index_or_alias)
        if index not in self._connections:
            raise RuntimeError(f"Connection with index '{index}' does not exist.")

        return self._connections[index]

    def get_all(self) -> Dict[int, Any]:
        return self._connections.copy()

    def clear(self, index_or_alias: Union[int, str]) -> None:
        index = self._resolve_index(index_or_alias)
        if index not in self._connections:
            raise RuntimeError(f"Connection with index '{index}' does not exist.")

        del self._connections[index]
        self._aliases = {
            alias: idx for alias, idx in self._aliases.items() if idx != index
        }

        if self._current_index == index:
            self._current_index = None

    def clear_all(self) -> None:
        self._connections.clear()
        self._aliases.clear()
        self._current_index = None

    def _get_next_index(self) -> int:
        if not self._connections:
            return 1
        return max(self._connections.keys()) + 1

    def _resolve_index(self, index_or_alias: Union[int, str]) -> int:
        if isinstance(index_or_alias, int):
            return index_or_alias

        if isinstance(index_or_alias, str):
            if index_or_alias in self._aliases:
                return self._aliases[index_or_alias]
            try:
                return int(index_or_alias)
            except ValueError:
                raise ValueError(f"Alias '{index_or_alias}' does not exist.")

        raise ValueError(f"Invalid index or alias type: {type(index_or_alias)}")

    def __len__(self) -> int:
        return len(self._connections)


class SecretsManager:
    def __init__(self):
        self._secrets: Dict[str, bytes] = {}  # Stockage des secrets chiffrés
        self._fernet_key = self._get_or_generate_key()
        self._cipher = Fernet(self._fernet_key)

    def _get_or_generate_key(self) -> bytes:
        key_env = os.getenv("SYSBOT_ENCRYPTION_KEY")
        if key_env:
            try:
                return base64.urlsafe_b64decode(key_env.encode())
            except Exception:
                pass

        key = Fernet.generate_key()

        os.environ["SYSBOT_ENCRYPTION_KEY"] = base64.urlsafe_b64encode(key).decode()

        return key

    def register(
        self, secret_name: str, secret_value: Union[str, Dict[str, Any], List[Any]]
    ) -> None:
        if isinstance(secret_value, str):
            encrypted_secret = self._cipher.encrypt(secret_value.encode())
            self._secrets[secret_name] = encrypted_secret
        elif isinstance(secret_value, (dict, list)):
            json_string = json.dumps(secret_value, indent=None, separators=(",", ":"))
            encrypted_secret = self._cipher.encrypt(json_string.encode())
            self._secrets[secret_name] = encrypted_secret
        else:
            raise ValueError("Secret value must be a string, dictionary, or list")

    def switch(self, secret_name: str) -> Union[str, Dict[str, Any], List[Any]]:
        return self.get(secret_name)

    def get(self, secret_reference: str) -> Union[str, Dict[str, Any], List[Any]]:
        if "." in secret_reference:
            secret_name, field_path = secret_reference.split(".", 1)
            secret_value = self._get_secret(secret_name)

            current_value = secret_value
            for field in field_path.split("."):
                if isinstance(current_value, dict) and field in current_value:
                    current_value = current_value[field]
                elif isinstance(current_value, list):
                    try:
                        index = int(field)
                        current_value = current_value[index]
                    except (ValueError, IndexError):
                        raise KeyError(
                            f"Field '{field}' not found in secret '{secret_name}'"
                        )
                else:
                    raise KeyError(
                        f"Field '{field}' not found in secret '{secret_name}'"
                    )

            return current_value
        else:
            return self._get_secret(secret_reference)

    def get_all(self) -> Dict[str, Union[str, Dict[str, Any], List[Any]]]:
        all_secrets = {}
        for secret_name in self._secrets.keys():
            try:
                all_secrets[secret_name] = self._get_secret(secret_name)
            except Exception:
                continue
        return all_secrets

    def clear(self, secret_name: str) -> None:
        if secret_name not in self._secrets:
            raise KeyError(f"Secret '{secret_name}' not found")

        del self._secrets[secret_name]

    def clear_all(self) -> None:
        self._secrets.clear()

    def _get_secret(self, secret_name: str) -> Union[str, Dict[str, Any], List[Any]]:
        if secret_name not in self._secrets:
            raise KeyError(f"Secret '{secret_name}' not found")

        try:
            encrypted_secret = self._secrets[secret_name]
            decrypted_value = self._cipher.decrypt(encrypted_secret).decode()

            try:
                return json.loads(decrypted_value)
            except json.JSONDecodeError:
                return decrypted_value

        except Exception as e:
            raise Exception(f"Failed to decrypt secret '{secret_name}': {str(e)}")

    def _get_secret_dict(self, secret_name: str) -> Dict[str, Any]:
        secret_value = self._get_secret(secret_name)
        if not isinstance(secret_value, dict):
            raise ValueError(f"Secret '{secret_name}' is not a dictionary")
        return secret_value

    def get_stats(self) -> Dict[str, int]:
        return {
            "total_secrets": len(self._secrets),
            "total_size_bytes": sum(len(secret) for secret in self._secrets.values()),
        }

    def __len__(self) -> int:
        return len(self._secrets)

    def __contains__(self, secret_name: str) -> bool:
        return secret_name in self._secrets
