"""
Module dédié à la gestion des tunnels SSH et à la récupération des protocoles pour ConnectorHandler.
"""

import importlib
from sshtunnel import SSHTunnelForwarder

class TunnelingManager:
    """
    Utility class for managing SSH tunnels and dynamic protocol retrieval.

    Provides static methods to dynamically instantiate connectors and establish nested SSH tunnels.
    """
    @staticmethod
    def get_protocol(protocol_name, product_name):
        """
        Dynamically instantiates the connector corresponding to the protocol and product.

        Args:
            protocol_name (str): Name of the protocol (e.g., 'ssh', 'http').
            product_name (str): Name of the product (e.g., 'bash', 'redfish').

        Returns:
            object: Instance of the corresponding connector.

        Raises:
            ImportError: If the module cannot be found.
            AttributeError: If the product class does not exist in the module.
            Exception: For any other unexpected error.
        """
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
        """
        Establishes nested SSH tunnels and opens the final session to the target.

        Args:
            protocol (ConnectorInterface): Instance of the connector to use for opening the final session.
            tunnel_config (list): List of dictionaries containing the configuration for each SSH hop.
            target_config (dict): Dictionary containing connection info for the final target.
            index (int, optional): Current hop index (used recursively).
            previous_tunnels (list, optional): List of already opened tunnels.

        Returns:
            dict: Dictionary with the opened session and the list of active tunnels.

        Raises:
            Exception: If tunnel establishment fails.
        """
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
            print(f"Tunnel {index + 1} established: {ssh_address_or_host[0]}:{ssh_address_or_host[1]}")
            previous_tunnels.append(tunnel)
            return TunnelingManager.nested_tunnel(protocol, tunnel_config, target_config, index + 1, previous_tunnels)
        except Exception as e:
            for tunnel in reversed(previous_tunnels):
                tunnel.stop()
                try:
                    tunnel.ssh_address_or_host
                except:
                    print(f"Closed tunnel")
                else:
                    print(f"Closed tunnel to: {tunnel.ssh_address_or_host}")
            raise Exception(f"Failed to establish nested tunnels: {str(e)}")
