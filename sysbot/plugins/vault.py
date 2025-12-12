import requests
from typing import Union
from sysbot.utils.engine import ComponentBase


class Vault(ComponentBase):

    def dump_engine(self, token: str, url: str, engine_name: str, key: str = None, verify_ssl: bool = False) -> Union[dict, str]:
        try:
            # Normalize URL - remove trailing slash if present
            vault_url = url.rstrip('/')
            
            # Headers for Vault API
            headers = {
                'X-Vault-Token': token
            }
            
            # Try to detect engine version, attempting both KV v2 and KV v1
            secrets = self._dump_with_version_detection(vault_url, engine_name, headers, verify_ssl)
            
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
    
    def _dump_with_version_detection(self, vault_url: str, engine_name: str, headers: dict, verify_ssl: bool) -> dict:
        # First, try to get engine version from Vault's mount info
        engine_info = self._get_engine_info(vault_url, engine_name, headers, verify_ssl)
        
        # If we got version info, use it directly
        if engine_info and engine_info.get('type') == 'kv':
            version = engine_info.get('options', {}).get('version', '2')
            if version == '2':
                return self._dump_kv_v2_engine(vault_url, engine_name, headers, verify_ssl)
            else:
                return self._dump_kv_v1_engine(vault_url, engine_name, headers, verify_ssl)
        
        # If we couldn't determine version from API, try both versions
        # Try KV v2 first (most common)
        try:
            secrets = self._dump_kv_v2_engine(vault_url, engine_name, headers, verify_ssl)
            # KV v2 worked if we got a dict back (even if empty)
            return secrets
        except Exception:
            # KV v2 failed (wrong version, permission issue, etc.), try KV v1
            # Any exceptions are intentionally caught to allow fallback to v1
            pass
        
        # Try KV v1
        try:
            secrets = self._dump_kv_v1_engine(vault_url, engine_name, headers, verify_ssl)
            return secrets
        except Exception as e:
            raise RuntimeError(f"Failed to dump secrets from engine '{engine_name}'. Ensure the engine exists and token has proper permissions: {e}")
    
    def _get_engine_info(self, vault_url: str, engine_name: str, headers: dict, verify_ssl: bool) -> dict:
        try:
            response = requests.get(
                f"{vault_url}/v1/sys/mounts/{engine_name}",
                headers=headers,
                verify=verify_ssl,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception:
            return {}
    
    def _dump_kv_v2_engine(self, vault_url: str, engine_name: str, headers: dict, verify_ssl: bool) -> dict:
        all_secrets = {}
        
        # List all secrets recursively
        secret_paths = self._list_secrets_recursive(vault_url, engine_name, "", headers, is_v2=True, verify_ssl=verify_ssl)
        
        # Retrieve each secret
        for path in secret_paths:
            try:
                # For KV v2, use /data/ endpoint
                response = requests.get(
                    f"{vault_url}/v1/{engine_name}/data/{path}",
                    headers=headers,
                    verify=verify_ssl,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'data' in data['data']:
                        all_secrets[path] = data['data']['data']
            except Exception:
                # Skip secrets that fail to retrieve and continue with others
                continue
        
        return all_secrets
    
    def _dump_kv_v1_engine(self, vault_url: str, engine_name: str, headers: dict, verify_ssl: bool) -> dict:
        all_secrets = {}
        
        # List all secrets recursively
        secret_paths = self._list_secrets_recursive(vault_url, engine_name, "", headers, is_v2=False, verify_ssl=verify_ssl)
        
        # Retrieve each secret
        for path in secret_paths:
            try:
                response = requests.get(
                    f"{vault_url}/v1/{engine_name}/{path}",
                    headers=headers,
                    verify=verify_ssl,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        all_secrets[path] = data['data']
            except Exception:
                # Skip secrets that fail to retrieve and continue with others
                continue
        
        return all_secrets
    
    def _list_secrets_recursive(self, vault_url: str, engine_name: str, path: str, headers: dict, is_v2: bool = True, verify_ssl: bool = False) -> list:
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
                verify=verify_ssl,
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
                                self._list_secrets_recursive(vault_url, engine_name, folder_path, headers, is_v2, verify_ssl)
                            )
                        else:
                            # It's a secret
                            secret_path = f"{path}{key}" if path else key
                            secret_paths.append(secret_path)
            
        except Exception:
            # If listing fails, return empty list for this path
            pass
        
        return secret_paths
