import logging
from typing import List, Dict, Any, Optional
from sshtunnel import SSHTunnelForwarder

logger = logging.getLogger(__name__)

class TunnelManager:
    """
    Gère la création et la fermeture de tunnels SSH imbriqués.
    """
    def __init__(self):
        self.tunnels: List[SSHTunnelForwarder] = []

    def open_nested_tunnel(
        self,
        tunnel_config: List[Dict[str, Any]],
        target_config: Dict[str, Any],
        protocol_open_session,
        index: int = 0,
        previous_tunnels: Optional[List[SSHTunnelForwarder]] = None
    ) -> Dict[str, Any]:
        """
        Ouvre des tunnels SSH imbriqués et retourne la session finale et la liste des tunnels ouverts.
        """
        if previous_tunnels is None:
            previous_tunnels = []
        try:
            if index >= len(tunnel_config):
                username = target_config.get('username') or ''
                password = target_config.get('password') or ''
                session = protocol_open_session(
                    'localhost',
                    previous_tunnels[-1].local_bind_port,
                    username,
                    password
                )
                return {"session": session, "tunnels": previous_tunnels}
            config = tunnel_config[index]
            if previous_tunnels:
                ssh_host = 'localhost'
                ssh_port = int(previous_tunnels[-1].local_bind_port)
            else:
                ip_val = config.get('ip')
                port_val = config.get('port')
                ssh_host = '' if ip_val is None else str(ip_val)
                ssh_port = 0 if port_val is None else int(port_val)
            ssh_address_or_host = (ssh_host, ssh_port)
            target_ip_val = target_config.get('ip')
            target_port_val = target_config.get('port')
            target_ip = '' if target_ip_val is None else str(target_ip_val)
            target_port = 0 if target_port_val is None else int(target_port_val)
            if index == len(tunnel_config) - 1:
                remote_bind_address = (target_ip, target_port)
            else:
                next_ip_val = tunnel_config[index + 1].get('ip')
                next_port_val = tunnel_config[index + 1].get('port')
                next_ip = '' if next_ip_val is None else str(next_ip_val)
                next_port = 0 if next_port_val is None else int(next_port_val)
                remote_bind_address = (next_ip, next_port)
            ssh_username_val = config.get('username')
            ssh_password_val = config.get('password')
            ssh_username = '' if ssh_username_val is None else str(ssh_username_val)
            ssh_password = '' if ssh_password_val is None else str(ssh_password_val)
            tunnel = SSHTunnelForwarder(
                ssh_address_or_host=ssh_address_or_host,
                remote_bind_address=remote_bind_address,
                ssh_username=ssh_username,
                ssh_password=ssh_password
            )
            tunnel.start()
            logger.info(f"Tunnel {index + 1} established: {ssh_address_or_host[0]}:{ssh_address_or_host[1]}")
            previous_tunnels.append(tunnel)
            return self.open_nested_tunnel(
                tunnel_config,
                target_config,
                protocol_open_session,
                index + 1,
                previous_tunnels
            )
        except Exception as e:
            self.close_tunnels(previous_tunnels)
            logger.error(f"Failed to establish nested tunnels: {e}")
            raise

    def close_tunnels(self, tunnels: Optional[List[SSHTunnelForwarder]] = None) -> None:
        """
        Ferme proprement tous les tunnels passés en argument (ou ceux de l'instance si non précisé).
        """
        if tunnels is None:
            tunnels = self.tunnels
        for tunnel in reversed(tunnels):
            try:
                tunnel.stop()
                # L'attribut ssh_address_or_host n'est pas garanti par la lib, on log le tunnel lui-même
                logger.info(f"Closed tunnel: {tunnel}")
            except Exception as e:
                logger.warning(f"Error closing tunnel: {e}") 