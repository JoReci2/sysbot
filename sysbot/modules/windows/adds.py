"""
Active Directory Domain Services Module

This module provides methods for managing and querying Active Directory Domain
Services (AD DS) including domains, forests, domain controllers, users, groups,
computers, and organizational units using PowerShell AD cmdlets.
"""
from sysbot.utils.engine import ComponentBase
import json


class Adds(ComponentBase):
    def get_domain(self, alias: str, **kwargs) -> dict:
        """Get domain information."""
        command = "Get-ADDomain | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_forest(self, alias: str, **kwargs) -> dict:
        """Get forest information."""
        command = "Get-ADForest | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_domain_controller(self, alias: str, **kwargs) -> dict:
        """Get domain controller information."""
        command = "Get-ADDomainController | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_user(self, alias: str, identity: str, **kwargs) -> dict:
        """Get specific user by identity."""
        command = f"Get-ADUser -Identity '{identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_users(self, alias: str, filter: str = "*", **kwargs) -> list:
        """Get users matching filter."""
        command = f"Get-ADUser -Filter '{filter}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_group(self, alias: str, identity: str, **kwargs) -> dict:
        """Get specific group by identity."""
        command = f"Get-ADGroup -Identity '{identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_groups(self, alias: str, filter: str = "*", **kwargs) -> list:
        """Get groups matching filter."""
        command = f"Get-ADGroup -Filter '{filter}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_group_members(self, alias: str, identity: str, **kwargs) -> list:
        """Get members of a group."""
        command = f"Get-ADGroupMember -Identity '{identity}' | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_organizational_unit(self, alias: str, identity: str, **kwargs) -> dict:
        """Get specific organizational unit by identity."""
        command = f"Get-ADOrganizationalUnit -Identity '{identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_organizational_units(self, alias: str, filter: str = "*", **kwargs) -> list:
        """Get organizational units matching filter."""
        command = f"Get-ADOrganizationalUnit -Filter '{filter}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_computer(self, alias: str, identity: str, **kwargs) -> dict:
        """Get specific computer by identity."""
        command = f"Get-ADComputer -Identity '{identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_computers(self, alias: str, filter: str = "*", **kwargs) -> list:
        """Get computers matching filter."""
        command = f"Get-ADComputer -Filter '{filter}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_gpo(self, alias: str, **kwargs) -> list:
        """Get all Group Policy Objects."""
        command = "Get-GPO -All | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        result = json.loads(output)
        # Wrap single objects in a list
        if isinstance(result, dict):
            return [result]
        return result

    def get_gpos(self, alias: str, **kwargs) -> list:
        """Get all Group Policy Objects (alias for get_gpo)."""
        return self.get_gpo(alias, **kwargs)
