"""
Data Plugin Module

This module provides functionality for loading and managing data from various
file formats (CSV, JSON, YAML, Ansible Inventory) and storing them as secrets in the SysBot cache.
Useful for managing test data and configuration files.
"""
import csv
import json
import yaml
from pathlib import Path

from sysbot.utils.engine import ComponentBase


class Data(ComponentBase):
    """
    Data loader plugin for managing test data from various file formats.
    
    This class provides methods to load data from CSV, JSON, YAML, and Ansible inventory files
    and optionally store them in the SysBot secrets cache.
    """
    
    def csv(self, file: str, key: str = None) -> list[dict]:
        """
        Load CSV file and optionally store in secrets cache.
        
        Args:
            file: Path to the CSV file to load.
            key: Optional key to store the data in secrets cache.
                If provided, returns "Imported", otherwise returns the data.
        
        Returns:
            List of dictionaries representing CSV rows if key is None,
            otherwise returns "Imported" string after storing in cache.
        
        Raises:
            FileNotFoundError: If the CSV file does not exist.
            RuntimeError: If there's an error reading or parsing the CSV file.
        """
        file_path = file
        try:
            result = []
            with open(file_path, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    result.append(row)
            if key is not None:
                self._sysbot._cache.secrets.register(key, result)
                return "Imported"
            else:
                return result
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        except csv.Error as e:
            raise RuntimeError(f"Error reading CSV file: {file_path} - {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred while loading CSV: {e}")

    def json(self, file: str, key: str = None) -> dict:
        """
        Load JSON file and optionally store in secrets cache.
        
        Args:
            file: Path to the JSON file to load.
            key: Optional key to store the data in secrets cache.
                If provided, returns "Imported", otherwise returns the data.
        
        Returns:
            Dictionary containing JSON data if key is None,
            otherwise returns "Imported" string after storing in cache.
        
        Raises:
            FileNotFoundError: If the JSON file does not exist.
            RuntimeError: If there's an error reading or parsing the JSON file.
        """
        file_path = file
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                result = json.load(file)
            if key is not None:
                self._sysbot._cache.secrets.register(key, result)
                return "Imported"
            else:
                return result
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error decoding JSON file: {file_path} - {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred while loading JSON: {e}")

    def yaml(self, file: str, key: str = None) -> dict:
        """
        Load YAML file and optionally store in secrets cache.
        
        Args:
            file: Path to the YAML file to load.
            key: Optional key to store the data in secrets cache.
                If provided, returns "Imported", otherwise returns the data.
        
        Returns:
            Dictionary containing YAML data if key is None,
            otherwise returns "Imported" string after storing in cache.
        
        Raises:
            FileNotFoundError: If the YAML file does not exist.
            RuntimeError: If there's an error reading or parsing the YAML file.
        """
        file_path = file
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                result = yaml.safe_load(file)
            if key is not None:
                self._sysbot._cache.secrets.register(key, result)
                return "Imported"
            else:
                return result
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML file not found: {file_path}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML file: {file_path} - {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred while loading YAML: {e}")

    def ansible(self, file: str, key: str = None) -> dict:
        """
        Load Ansible inventory file and optionally store in secrets cache.
        
        Supports both INI and YAML inventory formats. Automatically detects format
        based on file extension (.ini, .yml, .yaml).
        
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
                                # Try to convert numeric values
                                try:
                                    if '.' in value:
                                        groups[group_name]["vars"][key.strip()] = float(value.strip())
                                    else:
                                        groups[group_name]["vars"][key.strip()] = int(value.strip())
                                except ValueError:
                                    groups[group_name]["vars"][key.strip()] = value.strip()
                        
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
                                        # Try to convert numeric values
                                        try:
                                            if '.' in value:
                                                host_vars[key] = float(value)
                                            else:
                                                host_vars[key] = int(value)
                                        except ValueError:
                                            host_vars[key] = value
                                
                                groups[current_section]["hosts"][hostname] = host_vars
            
            return {"groups": groups}
        except Exception as e:
            raise RuntimeError(f"Error processing INI inventory: {e}")

