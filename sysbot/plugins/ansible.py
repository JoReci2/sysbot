"""
Ansible Plugin Module

This module provides functionality for loading and parsing Ansible inventory files.
Supports both INI and YAML inventory formats with automatic format detection.
Also provides functionality for executing Ansible playbooks and roles using ansible-runner.
"""
import yaml
import tempfile
import shutil
import os
import re
from pathlib import Path

from sysbot.utils.engine import ComponentBase

# Try to import ansible_runner, but make it optional
# ansible_runner depends on fcntl which is Unix-only and will fail on Windows
try:
    import ansible_runner
    HAS_ANSIBLE_RUNNER = True
except ImportError:
    HAS_ANSIBLE_RUNNER = False
    ansible_runner = None


class Ansible(ComponentBase):
    """
    Ansible plugin for managing Ansible inventory data and executing playbooks and roles.
    
    This class provides methods to load Ansible inventory files in both INI
    and YAML formats, execute Ansible playbooks and roles using ansible-runner,
    and optionally store results in the SysBot secrets cache.
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
        forks: int = None,
        **kwargs
    ) -> dict:
        """
        Execute an Ansible playbook using ansible-runner.
        
        This method uses the official ansible-runner library to execute playbooks,
        providing better integration, event handling, and artifact management.
        
        Args:
            playbook: Path to the Ansible playbook file to execute.
            inventory: Path to the inventory file, comma-separated host list,
                      or dictionary/list representing inventory structure.
            limit: Limit execution to specific hosts or groups.
            tags: Only run plays and tasks tagged with these values (comma-separated).
            skip_tags: Skip plays and tasks tagged with these values (comma-separated).
            extra_vars: Dictionary of extra variables to pass to the playbook.
            check: Run in check mode (dry-run), don't make any changes.
            diff: Show differences when changing small files and templates.
            verbose: Increase verbosity level (0-4, where 0 is default).
            forks: Control Ansible parallel concurrency.
            **kwargs: Additional ansible-runner options (e.g., timeout, quiet).
        
        Returns:
            Dictionary containing playbook execution results:
            {
                "success": bool,
                "status": str (one of: successful, failed, timeout, canceled),
                "rc": int (return code),
                "stats": dict (playbook statistics per host),
                "stdout": str (captured output)
            }
        
        Raises:
            FileNotFoundError: If the playbook file does not exist.
            ValueError: If invalid parameters are provided.
            RuntimeError: If there's an error executing the playbook.
        
        Example:
            result = ansible.playbook(
                playbook="site.yml",
                inventory="inventory.ini",
                limit="webservers",
                extra_vars={"version": "1.2.3"},
                check=True
            )
        """
        if not HAS_ANSIBLE_RUNNER:
            raise RuntimeError(
                "ansible-runner is not available. This functionality requires ansible-runner "
                "which is not supported on Windows. Please use this feature on a Unix-like system."
            )
        
        playbook_path = Path(playbook)
        
        try:
            if not playbook_path.exists():
                raise FileNotFoundError(f"Ansible playbook file not found: {playbook_path}")
            
            # Validate verbosity range (Ansible supports 0-4, i.e., -v, -vv, -vvv, -vvvv)
            if verbose < 0 or verbose > 4:
                raise ValueError("Verbosity level must be between 0 and 4")
            
            # Validate extra_vars if provided
            if extra_vars is not None:
                if not isinstance(extra_vars, dict):
                    raise ValueError("extra_vars must be a dictionary")
                # Validate that extra_vars only contains safe types
                for key, value in extra_vars.items():
                    if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        raise ValueError(f"Unsupported type for extra_var '{key}': {type(value)}")
            
            # Validate tags and skip_tags to prevent command injection
            tag_pattern = re.compile(r'^[a-zA-Z0-9_,\-]+$')
            if tags and not tag_pattern.match(tags):
                raise ValueError("tags parameter contains invalid characters. Only alphanumeric, underscore, hyphen, and comma are allowed.")
            if skip_tags and not tag_pattern.match(skip_tags):
                raise ValueError("skip_tags parameter contains invalid characters. Only alphanumeric, underscore, hyphen, and comma are allowed.")
            
            # Create a temporary directory for ansible-runner
            with tempfile.TemporaryDirectory() as tmpdir:
                # Set up the project directory structure
                project_dir = os.path.join(tmpdir, 'project')
                os.makedirs(project_dir)
                
                # Copy the playbook to the project directory
                playbook_name = playbook_path.name
                shutil.copy(str(playbook_path), os.path.join(project_dir, playbook_name))
                
                # If playbook references other files in the same directory, copy them too
                playbook_dir = playbook_path.parent
                if playbook_dir != Path('.'):
                    for item in playbook_dir.iterdir():
                        if item.is_file() and item != playbook_path:
                            try:
                                shutil.copy(str(item), project_dir)
                            except Exception:
                                # Skip files that can't be copied
                                pass
                
                # Prepare runner arguments
                runner_args = {
                    'private_data_dir': tmpdir,
                    'playbook': playbook_name,
                    'quiet': False,
                }
                
                # Add verbosity only if greater than 0
                if verbose > 0:
                    runner_args['verbosity'] = verbose
                
                # Add inventory if specified
                if inventory:
                    # Check if inventory is a path
                    inventory_path = Path(inventory)
                    if inventory_path.exists():
                        # Copy inventory file to the private_data_dir
                        inventory_dir = os.path.join(tmpdir, 'inventory')
                        os.makedirs(inventory_dir)
                        shutil.copy(str(inventory_path), os.path.join(inventory_dir, inventory_path.name))
                        runner_args['inventory'] = inventory_path.name
                    else:
                        # Assume it's a comma-separated host list or inline inventory
                        runner_args['inventory'] = inventory
                
                # Add limit if specified
                if limit:
                    runner_args['limit'] = limit
                
                # Add extra variables
                if extra_vars:
                    runner_args['extravars'] = extra_vars
                
                # Add forks if specified
                if forks is not None:
                    if not isinstance(forks, int) or forks < 1:
                        raise ValueError("forks must be a positive integer")
                    runner_args['forks'] = forks
                
                # Build cmdline options for tags, skip-tags, check, diff
                cmdline_parts = []
                if tags:
                    cmdline_parts.append(f"--tags {tags}")
                if skip_tags:
                    cmdline_parts.append(f"--skip-tags {skip_tags}")
                if check:
                    cmdline_parts.append("--check")
                if diff:
                    cmdline_parts.append("--diff")
                
                if cmdline_parts:
                    runner_args['cmdline'] = ' '.join(cmdline_parts)
                
                # Add any additional kwargs (e.g., timeout, quiet)
                allowed_kwargs = {'timeout', 'quiet', 'suppress_env_files', 
                                 'process_isolation', 'container_image'}
                for key, value in kwargs.items():
                    if key in allowed_kwargs:
                        runner_args[key] = value
                
                # Run the playbook
                r = ansible_runner.run(**runner_args)
                
                # Collect stdout from events
                stdout_lines = []
                if hasattr(r, 'events'):
                    for event in r.events:
                        if 'stdout' in event and event['stdout']:
                            stdout_lines.append(event['stdout'])
                
                stdout = '\n'.join(stdout_lines) if stdout_lines else ''
                
                # Prepare the result dictionary
                # ansible-runner always provides rc and status attributes
                output = {
                    "success": r.status == 'successful',
                    "status": r.status,
                    "rc": r.rc,
                    "stats": r.stats,
                    "stdout": stdout
                }
                
                return output
                
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error executing Ansible playbook: {e}")

    def role(
        self,
        role: str,
        hosts: str,
        inventory: str = None,
        extra_vars: dict = None,
        check: bool = False,
        diff: bool = False,
        verbose: int = 0,
        forks: int = None,
        **kwargs
    ) -> dict:
        """
        Execute an Ansible role on specific hosts using ansible-runner.
        
        This method dynamically creates a playbook that applies the specified role
        to the given hosts, then executes it using ansible-runner.
        
        Args:
            role: Name of the Ansible role to execute. Can be a role name from
                  roles directory or a fully qualified role name (e.g., namespace.rolename).
            hosts: Target hosts or groups to execute the role on. Can be a specific
                   host, a group name, or a pattern (e.g., "webservers", "web*.example.com").
            inventory: Path to the inventory file, comma-separated host list,
                      or dictionary/list representing inventory structure.
            extra_vars: Dictionary of extra variables to pass to the role.
            check: Run in check mode (dry-run), don't make any changes.
            diff: Show differences when changing small files and templates.
            verbose: Increase verbosity level (0-4, where 0 is default).
            forks: Control Ansible parallel concurrency.
            **kwargs: Additional ansible-runner options (e.g., timeout, quiet).
        
        Returns:
            Dictionary containing role execution results:
            {
                "success": bool,
                "status": str (one of: successful, failed, timeout, canceled),
                "rc": int (return code),
                "stats": dict (playbook statistics per host),
                "stdout": str (captured output)
            }
        
        Raises:
            ValueError: If invalid parameters are provided.
            RuntimeError: If there's an error executing the role.
        
        Example:
            result = ansible.role(
                role="common",
                hosts="webservers",
                inventory="inventory.ini",
                extra_vars={"ntp_server": "ntp.example.com"},
                check=True
            )
        """
        if not HAS_ANSIBLE_RUNNER:
            raise RuntimeError(
                "ansible-runner is not available. This functionality requires ansible-runner "
                "which is not supported on Windows. Please use this feature on a Unix-like system."
            )
        
        try:
            # Validate role name to prevent path traversal or injection
            role_pattern = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
            if not role_pattern.match(role):
                raise ValueError("role parameter contains invalid characters. Only alphanumeric, underscore, hyphen, and dot are allowed.")
            
            # Validate hosts parameter
            if not hosts or not isinstance(hosts, str):
                raise ValueError("hosts parameter must be a non-empty string")
            
            # Validate extra_vars if provided
            if extra_vars is not None:
                if not isinstance(extra_vars, dict):
                    raise ValueError("extra_vars must be a dictionary")
                # Validate that extra_vars only contains safe types
                for key, value in extra_vars.items():
                    if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        raise ValueError(f"Unsupported type for extra_var '{key}': {type(value)}")
            
            # Validate verbosity range
            if verbose < 0 or verbose > 4:
                raise ValueError("Verbosity level must be between 0 and 4")
            
            # Create a temporary directory for ansible-runner
            with tempfile.TemporaryDirectory() as tmpdir:
                # Set up the project directory structure
                project_dir = os.path.join(tmpdir, 'project')
                os.makedirs(project_dir)
                
                # Handle roles_path - copy roles to project directory
                roles_path = kwargs.pop('roles_path', None)
                if roles_path:
                    roles_path_obj = Path(roles_path)
                    if roles_path_obj.exists() and roles_path_obj.is_dir():
                        # Copy the roles directory to the project directory
                        dest_roles_dir = os.path.join(project_dir, 'roles')
                        shutil.copytree(str(roles_path_obj), dest_roles_dir)
                    elif roles_path_obj.exists():
                        # If it's a file, assume it's a role tarball or similar - not handled
                        raise ValueError(f"roles_path must be a directory: {roles_path}")
                
                # Create a dynamic playbook for the role
                playbook_name = 'role_execution.yml'
                playbook_content = [
                    {
                        'name': f'Execute role {role} on {hosts}',
                        'hosts': hosts,
                        'roles': [role]
                    }
                ]
                
                playbook_path = os.path.join(project_dir, playbook_name)
                with open(playbook_path, 'w', encoding='utf-8') as f:
                    yaml.dump(playbook_content, f, default_flow_style=False)
                
                # Prepare runner arguments
                runner_args = {
                    'private_data_dir': tmpdir,
                    'playbook': playbook_name,
                    'quiet': False,
                }
                
                # Add verbosity only if greater than 0
                if verbose > 0:
                    runner_args['verbosity'] = verbose
                
                # Add inventory if specified
                if inventory:
                    # Check if inventory is a path
                    inventory_path = Path(inventory)
                    if inventory_path.exists():
                        # Copy inventory file to the private_data_dir
                        inventory_dir = os.path.join(tmpdir, 'inventory')
                        os.makedirs(inventory_dir)
                        shutil.copy(str(inventory_path), os.path.join(inventory_dir, inventory_path.name))
                        runner_args['inventory'] = inventory_path.name
                    else:
                        # Assume it's a comma-separated host list or inline inventory
                        runner_args['inventory'] = inventory
                
                # Add extra variables
                if extra_vars:
                    runner_args['extravars'] = extra_vars
                
                # Add forks if specified
                if forks is not None:
                    if not isinstance(forks, int) or forks < 1:
                        raise ValueError("forks must be a positive integer")
                    runner_args['forks'] = forks
                
                # Build cmdline options for check and diff
                cmdline_parts = []
                if check:
                    cmdline_parts.append("--check")
                if diff:
                    cmdline_parts.append("--diff")
                
                if cmdline_parts:
                    runner_args['cmdline'] = ' '.join(cmdline_parts)
                
                # Add any additional kwargs (e.g., timeout, quiet)
                allowed_kwargs = {'timeout', 'quiet', 'suppress_env_files', 
                                 'process_isolation', 'container_image'}
                for key, value in kwargs.items():
                    if key in allowed_kwargs:
                        runner_args[key] = value
                
                # Run the role via the generated playbook
                r = ansible_runner.run(**runner_args)
                
                # Collect stdout from events
                stdout_lines = []
                if hasattr(r, 'events'):
                    for event in r.events:
                        if 'stdout' in event and event['stdout']:
                            stdout_lines.append(event['stdout'])
                
                stdout = '\n'.join(stdout_lines) if stdout_lines else ''
                
                # Prepare the result dictionary
                output = {
                    "success": r.status == 'successful',
                    "status": r.status,
                    "rc": r.rc,
                    "stats": r.stats,
                    "stdout": stdout
                }
                
                return output
                
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error executing Ansible role: {e}")
