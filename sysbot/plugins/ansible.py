"""
Ansible Plugin Module

This module provides functionality for loading and parsing Ansible inventory files.
Supports both INI and YAML inventory formats with automatic format detection.
Also provides functionality for executing Ansible playbooks.
"""
import yaml
import subprocess
import json
from pathlib import Path

from sysbot.utils.engine import ComponentBase


class Ansible(ComponentBase):
    """
    Ansible plugin for managing Ansible inventory data and executing playbooks.
    
    This class provides methods to load Ansible inventory files in both INI
    and YAML formats, execute Ansible playbooks, and optionally store results
    in the SysBot secrets cache.
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

    def playbook(
        self,
        playbook: str,
        inventory: str = None,
        limit: str = None,
        tags: str = None,
        skip_tags: str = None,
        extra_vars: dict = None,
        check: bool = False,
        diff: bool = False,
        verbose: int = 0,
        **kwargs
    ) -> dict:
        """
        Execute an Ansible playbook.
        
        Args:
            playbook: Path to the Ansible playbook file to execute.
            inventory: Path to the inventory file or comma-separated host list.
            limit: Limit execution to specific hosts or groups.
            tags: Only run plays and tasks tagged with these values.
            skip_tags: Skip plays and tasks tagged with these values.
            extra_vars: Dictionary of extra variables to pass to the playbook.
            check: Run in check mode (dry-run), don't make any changes.
            diff: Show differences when changing small files and templates.
            verbose: Increase verbosity level (0-4, where 0 is default).
            **kwargs: Additional ansible-playbook command-line options.
                     Supported options: become, become_user, forks, timeout
        
        Returns:
            Dictionary containing playbook execution results:
            {
                "success": bool,
                "return_code": int,
                "stdout": str,
                "stderr": str,
                "stats": dict (if parseable from output)
            }
        
        Raises:
            FileNotFoundError: If the playbook file does not exist.
            RuntimeError: If there's an error executing the playbook.
            ValueError: If invalid parameters are provided.
        
        Example:
            result = ansible.playbook(
                playbook="site.yml",
                inventory="inventory.ini",
                limit="webservers",
                extra_vars={"version": "1.2.3"},
                check=True
            )
        """
        playbook_path = Path(playbook)
        
        try:
            if not playbook_path.exists():
                raise FileNotFoundError(f"Ansible playbook file not found: {playbook_path}")
            
            # Allowlist of supported kwargs to prevent arbitrary command injection
            ALLOWED_KWARGS = {
                'become': bool,
                'become_user': str,
                'forks': int,
                'timeout': int
            }
            
            # Validate kwargs
            for key in kwargs:
                if key not in ALLOWED_KWARGS:
                    raise ValueError(f"Unsupported option: {key}. Allowed options: {', '.join(ALLOWED_KWARGS.keys())}")
            
            # Build the ansible-playbook command
            command = ["ansible-playbook"]
            
            # Add playbook file
            command.append(str(playbook_path))
            
            # Add inventory if specified (validate it's a path or valid host pattern)
            if inventory:
                inventory_path = Path(inventory)
                # Allow either existing file paths or comma-separated host lists
                if not (inventory_path.exists() or ',' in inventory):
                    raise ValueError(f"Inventory must be an existing file or comma-separated host list: {inventory}")
                command.extend(["-i", inventory])
            
            # Add limit if specified
            if limit:
                command.extend(["--limit", limit])
            
            # Add tags if specified
            if tags:
                command.extend(["--tags", tags])
            
            # Add skip-tags if specified
            if skip_tags:
                command.extend(["--skip-tags", skip_tags])
            
            # Add extra variables if specified
            # Use JSON format which is safer than direct string interpolation
            if extra_vars:
                if not isinstance(extra_vars, dict):
                    raise ValueError("extra_vars must be a dictionary")
                # Validate that extra_vars only contains safe types
                for key, value in extra_vars.items():
                    if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        raise ValueError(f"Unsupported type for extra_var '{key}': {type(value)}")
                command.extend(["--extra-vars", json.dumps(extra_vars)])
            
            # Add check mode if specified
            if check:
                command.append("--check")
            
            # Add diff mode if specified
            if diff:
                command.append("--diff")
            
            # Add verbosity if specified
            if verbose > 0:
                command.append("-" + "v" * min(verbose, 4))
            
            # Add validated kwargs as command-line options
            for key, value in kwargs.items():
                expected_type = ALLOWED_KWARGS[key]
                if not isinstance(value, expected_type):
                    raise ValueError(f"Option '{key}' expects type {expected_type.__name__}, got {type(value).__name__}")
                
                option_name = f"--{key.replace('_', '-')}"
                if isinstance(value, bool):
                    if value:
                        command.append(option_name)
                else:
                    command.extend([option_name, str(value)])
            
            # Execute the playbook
            result = subprocess.run(
                command,
                capture_output=True,
                text=True
            )
            
            # Prepare the result dictionary
            output = {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Try to extract stats from output if available
            try:
                # Look for the PLAY RECAP section in the output
                if "PLAY RECAP" in result.stdout:
                    recap_section = result.stdout.split("PLAY RECAP")[1].strip()
                    stats = {}
                    for line in recap_section.split('\n'):
                        line = line.strip()
                        if ':' in line and '=' in line:
                            # Parse lines like: "host : ok=2 changed=1 unreachable=0 failed=0"
                            parts = line.split(':')
                            if len(parts) >= 2:
                                host = parts[0].strip()
                                stat_parts = parts[1].strip().split()
                                host_stats = {}
                                for stat in stat_parts:
                                    if '=' in stat:
                                        key, value = stat.split('=')
                                        try:
                                            host_stats[key] = int(value)
                                        except ValueError:
                                            host_stats[key] = value
                                if host_stats:
                                    stats[host] = host_stats
                    if stats:
                        output["stats"] = stats
            except Exception:
                # If stats parsing fails, just skip it
                pass
            
            return output
            
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Error executing Ansible playbook: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error executing Ansible playbook: {e}")

