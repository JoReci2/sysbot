import requests
import urllib3
from sysbot.utils.engine import ComponentBase

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Vault(ComponentBase):
    """
    Plugin for interacting with HashiCorp Vault.
    Allows dumping all secrets from a Vault engine and storing them in Sysbot's secret manager.
    """

    def dump_engine(self, token: str, url: str, engine_name: str, key: str = None) -> dict:
        """
        Dump all secrets from a HashiCorp Vault engine.
        
        Args:
            token: Vault authentication token
            url: Vault server URL (e.g., 'https://vault.example.com:8200')
            engine_name: Name of the secrets engine to dump
            key: Optional key to store secrets in Sysbot's secret manager
            
        Returns:
            Dictionary containing all secrets from the engine if key is None,
            otherwise returns "Imported" after storing in secret manager
        """
        try:
            # Normalize URL - remove trailing slash if present
            vault_url = url.rstrip('/')
            
            # Headers for Vault API
            headers = {
                'X-Vault-Token': token
            }
            
            # First, determine the engine type (KV v1 or KV v2)
            engine_info = self._get_engine_info(vault_url, engine_name, headers)
            
            if engine_info.get('type') == 'kv' and engine_info.get('options', {}).get('version') == '2':
                # KV v2 engine
                secrets = self._dump_kv_v2_engine(vault_url, engine_name, headers)
            else:
                # KV v1 engine or other
                secrets = self._dump_kv_v1_engine(vault_url, engine_name, headers)
            
            # Store in secret manager if key is provided
            if key is not None:
                self._sysbot._cache.secrets.register(key, secrets)
                return "Imported"
            else:
                return secrets
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to connect to Vault: {e}")
        except Exception as e:
            raise RuntimeError(f"Error dumping Vault engine: {e}")
    
    def _get_engine_info(self, vault_url: str, engine_name: str, headers: dict) -> dict:
        """Get information about the secrets engine."""
        try:
            response = requests.get(
                f"{vault_url}/v1/sys/mounts/{engine_name}",
                headers=headers,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # If we can't get engine info, assume KV v2 as it's more common
                return {'type': 'kv', 'options': {'version': '2'}}
        except Exception:
            # Default to KV v2
            return {'type': 'kv', 'options': {'version': '2'}}
    
    def _dump_kv_v2_engine(self, vault_url: str, engine_name: str, headers: dict) -> dict:
        """Dump all secrets from a KV v2 engine."""
        all_secrets = {}
        
        # List all secrets recursively
        secret_paths = self._list_secrets_recursive(vault_url, engine_name, "", headers, is_v2=True)
        
        # Retrieve each secret
        for path in secret_paths:
            try:
                # For KV v2, use /data/ endpoint
                response = requests.get(
                    f"{vault_url}/v1/{engine_name}/data/{path}",
                    headers=headers,
                    verify=False,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'data' in data['data']:
                        all_secrets[path] = data['data']['data']
            except Exception as e:
                # Log error but continue with other secrets
                print(f"Warning: Failed to retrieve secret at {path}: {e}")
                continue
        
        return all_secrets
    
    def _dump_kv_v1_engine(self, vault_url: str, engine_name: str, headers: dict) -> dict:
        """Dump all secrets from a KV v1 engine."""
        all_secrets = {}
        
        # List all secrets recursively
        secret_paths = self._list_secrets_recursive(vault_url, engine_name, "", headers, is_v2=False)
        
        # Retrieve each secret
        for path in secret_paths:
            try:
                response = requests.get(
                    f"{vault_url}/v1/{engine_name}/{path}",
                    headers=headers,
                    verify=False,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        all_secrets[path] = data['data']
            except Exception as e:
                # Log error but continue with other secrets
                print(f"Warning: Failed to retrieve secret at {path}: {e}")
                continue
        
        return all_secrets
    
    def _list_secrets_recursive(self, vault_url: str, engine_name: str, path: str, headers: dict, is_v2: bool = True) -> list:
        """
        Recursively list all secret paths in the engine.
        
        Args:
            vault_url: Base Vault URL
            engine_name: Name of the secrets engine
            path: Current path to list (empty string for root)
            headers: Request headers with authentication
            is_v2: Whether this is a KV v2 engine
            
        Returns:
            List of all secret paths
        """
        secret_paths = []
        
        try:
            # For KV v2, use /metadata/ endpoint for listing
            if is_v2:
                list_url = f"{vault_url}/v1/{engine_name}/metadata/{path}"
            else:
                list_url = f"{vault_url}/v1/{engine_name}/{path}"
            
            response = requests.request(
                'LIST',
                list_url,
                headers=headers,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'keys' in data['data']:
                    for key in data['data']['keys']:
                        # If key ends with '/', it's a folder - recurse into it
                        if key.endswith('/'):
                            folder_path = f"{path}{key}" if path else key
                            secret_paths.extend(
                                self._list_secrets_recursive(vault_url, engine_name, folder_path, headers, is_v2)
                            )
                        else:
                            # It's a secret
                            secret_path = f"{path}{key}" if path else key
                            secret_paths.append(secret_path)
            
        except Exception as e:
            # If listing fails, just return empty list for this path
            print(f"Warning: Failed to list secrets at {path}: {e}")
        
        return secret_paths
