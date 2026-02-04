"""
Ansible Plugin Module

This module provides functionality for loading and parsing Ansible inventory files.
Supports both INI and YAML inventory formats with automatic format detection.
"""
import yaml
from pathlib import Path

from sysbot.utils.engine import ComponentBase


class Ansible(ComponentBase):
    """
    Ansible inventory loader plugin for managing Ansible inventory data.
    
    This class provides methods to load Ansible inventory files in both INI
    and YAML formats and optionally store them in the SysBot secrets cache.
    """
    
    def inventory(self, file: str, key: str = None) -> dict:
        """
        Load Ansible inventory file and optionally store in secrets cache.
        
        Supports both INI and YAML inventory formats. Automatically detects format
        based on file extension (.ini, .yml, .yaml). Files without extensions are
        treated as INI format.
        
        Args:
            file: Path to the Ansible inventory file to load.
            key: Optional key to store the data in secrets cache.
                If provided, returns "Imported", otherwise returns the data.
        
        Returns:
            Dictionary containing parsed Ansible inventory if key is None,
            otherwise returns "Imported" string after storing in cache.
            
            The returned dictionary has the following structure:
            {
                "groups": {
                    "group_name": {
                        "hosts": {
                            "host_name": {
                                "ansible_host": "...",
                                "ansible_user": "...",
                                ...
                            }
                        },
                        "vars": {...},
                        "children": [...]
                    }
                }
            }
        
        Raises:
            FileNotFoundError: If the inventory file does not exist.
            RuntimeError: If there's an error reading or parsing the inventory file.
        """
        file_path = Path(file)
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Ansible inventory file not found: {file_path}")
            
            # Detect format based on file extension
            if file_path.suffix in ['.yml', '.yaml']:
                result = self._parse_ansible_yaml(file_path)
            elif file_path.suffix == '.ini' or file_path.suffix == '':
                result = self._parse_ansible_ini(file_path)
            else:
                raise RuntimeError(f"Unsupported Ansible inventory format: {file_path.suffix}")
            
            if key is not None:
                self._sysbot._cache.secrets.register(key, result)
                return "Imported"
            else:
                return result
        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error loading Ansible inventory: {e}")

    def _parse_ansible_yaml(self, file_path: Path) -> dict:
        """Parse Ansible inventory in YAML format."""
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                inventory_data = yaml.safe_load(file)
            
            if not inventory_data:
                return {"groups": {}}
            
            groups = {}
            
            # Process the inventory structure
            def process_group(group_name, group_data):
                if group_name not in groups:
                    groups[group_name] = {
                        "hosts": {},
                        "vars": {},
                        "children": []
                    }
                
                if isinstance(group_data, dict):
                    # Process hosts
                    if "hosts" in group_data and isinstance(group_data["hosts"], dict):
                        for host_name, host_vars in group_data["hosts"].items():
                            if host_vars is None:
                                host_vars = {}
                            groups[group_name]["hosts"][host_name] = host_vars
                    
                    # Process group vars
                    if "vars" in group_data and isinstance(group_data["vars"], dict):
                        groups[group_name]["vars"] = group_data["vars"]
                    
                    # Process children groups
                    if "children" in group_data:
                        children = group_data["children"]
                        if isinstance(children, dict):
                            for child_name, child_data in children.items():
                                groups[group_name]["children"].append(child_name)
                                process_group(child_name, child_data)
                        elif isinstance(children, list):
                            groups[group_name]["children"].extend(children)
            
            # Start processing from 'all' or root level
            if "all" in inventory_data:
                process_group("all", inventory_data["all"])
                if "children" in inventory_data["all"] and isinstance(inventory_data["all"]["children"], dict):
                    for group_name, group_data in inventory_data["all"]["children"].items():
                        process_group(group_name, group_data)
            else:
                for group_name, group_data in inventory_data.items():
                    process_group(group_name, group_data)
            
            return {"groups": groups}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML inventory: {e}")
        except Exception as e:
            raise RuntimeError(f"Error processing YAML inventory: {e}")

    def _parse_ansible_ini(self, file_path: Path) -> dict:
        """Parse Ansible inventory in INI format."""
        try:
            groups = {}
            current_section = None
            
            with open(file_path, mode="r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#') or line.startswith(';'):
                        continue
                    
                    # Check for section headers
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        
                        # Check if this is a vars section
                        if current_section.endswith(':vars'):
                            group_name = current_section[:-5]
                            if group_name not in groups:
                                groups[group_name] = {"hosts": {}, "vars": {}, "children": []}
                        # Check if this is a children section
                        elif current_section.endswith(':children'):
                            group_name = current_section[:-9]
                            if group_name not in groups:
                                groups[group_name] = {"hosts": {}, "vars": {}, "children": []}
                        # Regular group section
                        else:
                            if current_section not in groups:
                                groups[current_section] = {"hosts": {}, "vars": {}, "children": []}
                        continue
                    
                    # Process section content
                    if current_section:
                        # Vars section - parse as key=value
                        if current_section.endswith(':vars'):
                            group_name = current_section[:-5]
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                # Try to convert to int (only if all digits)
                                if value.isdigit():
                                    groups[group_name]["vars"][key] = int(value)
                                else:
                                    groups[group_name]["vars"][key] = value
                        
                        # Children section - just list child group names
                        elif current_section.endswith(':children'):
                            group_name = current_section[:-9]
                            groups[group_name]["children"].append(line)
                        
                        # Regular host group
                        else:
                            # Parse host line: hostname [var=value var=value ...]
                            parts = line.split()
                            if parts:
                                hostname = parts[0]
                                host_vars = {}
                                
                                # Parse host variables (key=value format)
                                for part in parts[1:]:
                                    if '=' in part:
                                        key, value = part.split('=', 1)
                                        # Try to convert to int (only if all digits)
                                        if value.isdigit():
                                            host_vars[key] = int(value)
                                        else:
                                            host_vars[key] = value
                                
                                groups[current_section]["hosts"][hostname] = host_vars
            
            return {"groups": groups}
        except Exception as e:
            raise RuntimeError(f"Error processing INI inventory: {e}")
