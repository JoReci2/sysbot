"""
Active Directory Domain Services Module

This module provides methods for managing and querying Active Directory Domain
Services (AD DS) including domains, forests, domain controllers, users, groups,
computers, and organizational units using PowerShell AD cmdlets.
"""
from sysbot.utils.engine import ComponentBase
import json


class Adds(ComponentBase):
    """Active Directory Domain Services management class using PowerShell AD cmdlets."""

    def get_domain(self, alias: str, **kwargs) -> dict:
        """
        Get domain information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing Active Directory domain information.
        """
        command = "Get-ADDomain | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_forest(self, alias: str, **kwargs) -> dict:
        """
        Get forest information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing Active Directory forest information.
        """
        command = "Get-ADForest | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_domain_controller(self, alias: str, **kwargs) -> dict:
        """
        Get domain controller information.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing domain controller information.
        """
        command = "Get-ADDomainController | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_user(self, alias: str, identity: str, **kwargs) -> dict:
        """
        Get specific user by identity.

        Args:
            alias: Session alias for the connection.
            identity: User identity (username, DN, GUID, or SID).
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing user information with all properties.
        """
        command = f"Get-ADUser -Identity '{identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_users(self, alias: str, filter: str = "*", **kwargs) -> list:
        """
        Get users matching filter.

        Args:
            alias: Session alias for the connection.
            filter: LDAP filter string (default: "*" for all users).
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing user information.
        """
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
        """
        Get specific group by identity.

        Args:
            alias: Session alias for the connection.
            identity: Group identity (name, DN, GUID, or SID).
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing group information with all properties.
        """
        command = f"Get-ADGroup -Identity '{identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_groups(self, alias: str, filter: str = "*", **kwargs) -> list:
        """
        Get groups matching filter.

        Args:
            alias: Session alias for the connection.
            filter: LDAP filter string (default: "*" for all groups).
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing group information.
        """
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
        """
        Get members of a group.

        Args:
            alias: Session alias for the connection.
            identity: Group identity (name, DN, GUID, or SID).
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing group member information.
        """
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
        """
        Get specific organizational unit by identity.

        Args:
            alias: Session alias for the connection.
            identity: OU identity (name, DN, or GUID).
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing organizational unit information with all properties.
        """
        command = f"Get-ADOrganizationalUnit -Identity '{identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_organizational_units(self, alias: str, filter: str = "*", **kwargs) -> list:
        """
        Get organizational units matching filter.

        Args:
            alias: Session alias for the connection.
            filter: LDAP filter string (default: "*" for all OUs).
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing organizational unit information.
        """
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
        """
        Get specific computer by identity.

        Args:
            alias: Session alias for the connection.
            identity: Computer identity (name, DN, GUID, or SID).
            **kwargs: Additional command execution options.

        Returns:
            Dictionary containing computer information with all properties.
        """
        command = f"Get-ADComputer -Identity '{identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_computers(self, alias: str, filter: str = "*", **kwargs) -> list:
        """
        Get computers matching filter.

        Args:
            alias: Session alias for the connection.
            filter: LDAP filter string (default: "*" for all computers).
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing computer information.
        """
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
        """
        Get all Group Policy Objects.

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing GPO information.
        """
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
        """
        Get all Group Policy Objects (alias for get_gpo).

        Args:
            alias: Session alias for the connection.
            **kwargs: Additional command execution options.

        Returns:
            List of dictionaries containing GPO information.
        """
        return self.get_gpo(alias, **kwargs)
