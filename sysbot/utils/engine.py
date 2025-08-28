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
from sshtunnel import SSHTunnelForwarder
from abc import ABC, abstractmethod


class ConnectorInterface(ABC):

    @abstractmethod
    def open_session(self, host, port, login, password):
        pass

    @abstractmethod
    def execute_command(self, session, command, **kwargs):
        pass

    @abstractmethod
    def close_session(self, session):
        pass

class MetaModules(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)

class ModuleGroup:
    def __init__(self, name):
        self.name = name

class BaseModule:
    def __init__(self):
        self._sysbot = None
    
    def set_sysbot_instance(self, sysbot_instance):
        self._sysbot = sysbot_instance
    
    def execute_command(self, alias, command, **kwargs):
        if self._sysbot is None:
            raise RuntimeError("No Sysbot instance available")
        return self._sysbot.execute_command(alias, command, **kwargs)

class TunnelingManager:
    @staticmethod
    def get_protocol(protocol_name, product_name):
        try:
            module_name = f"sysbot.connectors.{protocol_name.lower()}.{product_name.lower()}"
            connector = importlib.import_module(module_name)
            return getattr(connector, product_name.capitalize())()
        except ImportError as e:
            raise ImportError(f"Failed to import module '{module_name}': {str(e)}")
        except AttributeError as e:
            raise AttributeError(f"Module '{module_name}' does not have the attribute '{protocol_name.lower()}': {str(e)}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while retrieving the protocol: {str(e)}")

    @staticmethod
    def nested_tunnel(protocol, tunnel_config, target_config, index=0, previous_tunnels=None):
        if previous_tunnels is None:
            previous_tunnels = []
        try:
            if index >= len(tunnel_config):
                session = protocol.open_session(
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
            previous_tunnels.append(tunnel)
            return TunnelingManager.nested_tunnel(protocol, tunnel_config, target_config, index + 1, previous_tunnels)
        except Exception as e:
            for tunnel in reversed(previous_tunnels):
                tunnel.stop()
            raise Exception(f"Failed to establish nested tunnels: {str(e)}")
