"""
Vault Plugin Module

This module provides integration with HashiCorp Vault for secure secret management.
It supports dumping secrets from Vault KV (Key-Value) engines and storing them
in the SysBot secret cache for use in test automation.
"""
import hvac
from typing import Union
from sysbot.utils.engine import ComponentBase


class Vault(ComponentBase):
    """
    HashiCorp Vault integration plugin for secure secret management.
    
    This class provides functionality to dump secrets from Vault KV engines
    and store them in the SysBot secrets cache for use in test automation.
    Supports both KV v1 and KV v2 engines with automatic version detection.
    """

    def dump_engine(self, token: str, url: str, engine_name: str, key: str = None, verify_ssl: bool = False) -> Union[dict, str]:
        """
        Dump all secrets from a Vault KV engine.
        
        Automatically detects KV engine version (v1 or v2) and recursively
        retrieves all secrets from the specified engine.
        
        Args:
            token: Vault authentication token.
            url: Vault server URL (e.g., http://localhost:8200).
            engine_name: Name of the KV engine to dump.
            key: Optional key to store secrets in cache. If provided,
                returns "Imported", otherwise returns the secrets dict.
            verify_ssl: Whether to verify SSL certificates (default: False).
        
        Returns:
            Dictionary of all secrets if key is None,
            otherwise returns "Imported" string after storing in cache.
        
        Raises:
            RuntimeError: If there's an error connecting to Vault or
                dumping secrets from the engine.
        """
        try:
            client = hvac.Client(url=url, token=token, verify=verify_ssl)
            
            secrets = self._dump_with_version_detection(client, engine_name)
            
            if key is not None:
                self._sysbot._cache.secrets.register(key, secrets)
                return "Imported"
            else:
                return secrets
                
        except Exception as e:
            raise RuntimeError(f"Error dumping Vault engine: {e}")
    
    def _dump_with_version_detection(self, client: hvac.Client, engine_name: str) -> dict:
        """
        Attempt to dump secrets with automatic KV version detection.
        
        Tries KV v2 first, then falls back to KV v1 if v2 fails.
        
        Args:
            client: Authenticated HVAC client instance.
            engine_name: Name of the KV engine to dump.
        
        Returns:
            Dictionary containing all secrets from the engine.
        
        Raises:
            RuntimeError: If both v1 and v2 dump attempts fail.
        """
        try:
            secrets = self._dump_kv_v2_engine(client, engine_name)
            return secrets
        except Exception:
            pass
        
        try:
            secrets = self._dump_kv_v1_engine(client, engine_name)
            return secrets
        except Exception as e:
            raise RuntimeError(f"Failed to dump secrets from engine '{engine_name}'. Ensure the engine exists and token has proper permissions: {e}")
    
    def _dump_kv_v2_engine(self, client: hvac.Client, engine_name: str) -> dict:
        """
        Dump all secrets from a KV v2 engine.
        
        Args:
            client: Authenticated HVAC client instance.
            engine_name: Name of the KV v2 engine to dump.
        
        Returns:
            Dictionary mapping secret paths to their data.
        """
        all_secrets = {}
        secret_paths = self._list_secrets_recursive(client, engine_name, "", is_v2=True)
        
        for path in secret_paths:
            try:
                response = client.secrets.kv.v2.read_secret(path=path, mount_point=engine_name)
                if response and 'data' in response and 'data' in response['data']:
                    all_secrets[path] = response['data']['data']
            except Exception:
                continue
        
        return all_secrets
    
    def _dump_kv_v1_engine(self, client: hvac.Client, engine_name: str) -> dict:
        """
        Dump all secrets from a KV v1 engine.
        
        Args:
            client: Authenticated HVAC client instance.
            engine_name: Name of the KV v1 engine to dump.
        
        Returns:
            Dictionary mapping secret paths to their data.
        """
        all_secrets = {}
        secret_paths = self._list_secrets_recursive(client, engine_name, "", is_v2=False)
        
        for path in secret_paths:
            try:
                response = client.secrets.kv.v1.read_secret(path=path, mount_point=engine_name)
                if response and 'data' in response:
                    all_secrets[path] = response['data']
            except Exception:
                continue
        
        return all_secrets
    
    def _list_secrets_recursive(self, client: hvac.Client, engine_name: str, path: str, is_v2: bool = True) -> list:
        """
        Recursively list all secret paths in a KV engine.
        
        Args:
            client: Authenticated HVAC client instance.
            engine_name: Name of the KV engine.
            path: Current path to list (empty string for root).
            is_v2: Whether the engine is KV v2 (True) or v1 (False).
        
        Returns:
            List of all secret paths found recursively.
        """
        secret_paths = []
        
        try:
            if is_v2:
                response = client.secrets.kv.v2.list_secrets(path=path, mount_point=engine_name)
            else:
                response = client.secrets.kv.v1.list_secrets(path=path, mount_point=engine_name)
            
            if response and 'data' in response and 'keys' in response['data']:
                for item in response['data']['keys']:
                    if item.endswith('/'):
                        folder_path = f"{path}{item}" if path else item
                        secret_paths.extend(
                            self._list_secrets_recursive(client, engine_name, folder_path, is_v2)
                        )
                    else:
                        secret_path = f"{path}{item}" if path else item
                        secret_paths.append(secret_path)
        except Exception:
            pass
        
        return secret_paths
