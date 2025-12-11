from sysbot.utils.engine import ComponentBase
import json


class Adds(ComponentBase):
    def get_domain(self, alias: str, **kwargs) -> dict:
        """Get information about the Active Directory domain."""
        command = "Get-ADDomain | Select-Object Name, DNSRoot, NetBIOSName, DomainMode, Forest, PDCEmulator | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_forest(self, alias: str, **kwargs) -> dict:
        """Get information about the Active Directory forest."""
        command = "Get-ADForest | Select-Object Name, ForestMode, RootDomain, DomainNamingMaster, SchemaMaster | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_domain_controller(self, alias: str, **kwargs) -> dict:
        """Get information about domain controllers."""
        command = "Get-ADDomainController | Select-Object Name, Domain, Forest, OperatingSystem, IPv4Address, IsGlobalCatalog, IsReadOnly, Site | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_user(self, alias: str, identity: str, **kwargs) -> dict:
        """Get information about an Active Directory user."""
        # Escape single quotes in identity to prevent injection
        identity_escaped = identity.replace("'", "''")
        command = f"Get-ADUser -Identity '{identity_escaped}' -Properties * | Select-Object Name, SamAccountName, UserPrincipalName, DistinguishedName, Enabled, EmailAddress, Department, Title | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_users(self, alias: str, filter: str = "*", **kwargs) -> dict:
        """Get a list of Active Directory users."""
        # Escape single quotes in filter to prevent injection
        filter_escaped = filter.replace("'", "''")
        command = f"Get-ADUser -Filter '{filter_escaped}' | Select-Object Name, SamAccountName, UserPrincipalName, DistinguishedName, Enabled | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_group(self, alias: str, identity: str, **kwargs) -> dict:
        """Get information about an Active Directory group."""
        # Escape single quotes in identity to prevent injection
        identity_escaped = identity.replace("'", "''")
        command = f"Get-ADGroup -Identity '{identity_escaped}' -Properties * | Select-Object Name, SamAccountName, DistinguishedName, GroupCategory, GroupScope, Description | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_groups(self, alias: str, filter: str = "*", **kwargs) -> dict:
        """Get a list of Active Directory groups."""
        # Escape single quotes in filter to prevent injection
        filter_escaped = filter.replace("'", "''")
        command = f"Get-ADGroup -Filter '{filter_escaped}' | Select-Object Name, SamAccountName, DistinguishedName, GroupCategory, GroupScope | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_group_members(self, alias: str, identity: str, **kwargs) -> dict:
        """Get members of an Active Directory group."""
        # Escape single quotes in identity to prevent injection
        identity_escaped = identity.replace("'", "''")
        command = f"Get-ADGroupMember -Identity '{identity_escaped}' | Select-Object Name, SamAccountName, DistinguishedName, ObjectClass | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_organizational_unit(self, alias: str, identity: str, **kwargs) -> dict:
        """Get information about an Active Directory organizational unit."""
        # Escape single quotes in identity to prevent injection
        identity_escaped = identity.replace("'", "''")
        command = f"Get-ADOrganizationalUnit -Identity '{identity_escaped}' -Properties * | Select-Object Name, DistinguishedName, Description, ManagedBy | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_organizational_units(self, alias: str, filter: str = "*", **kwargs) -> dict:
        """Get a list of Active Directory organizational units."""
        # Escape single quotes in filter to prevent injection
        filter_escaped = filter.replace("'", "''")
        command = f"Get-ADOrganizationalUnit -Filter '{filter_escaped}' | Select-Object Name, DistinguishedName, Description | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_computer(self, alias: str, identity: str, **kwargs) -> dict:
        """Get information about an Active Directory computer."""
        # Escape single quotes in identity to prevent injection
        identity_escaped = identity.replace("'", "''")
        command = f"Get-ADComputer -Identity '{identity_escaped}' -Properties * | Select-Object Name, DNSHostName, DistinguishedName, Enabled, OperatingSystem, IPv4Address, LastLogonDate | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_computers(self, alias: str, filter: str = "*", **kwargs) -> dict:
        """Get a list of Active Directory computers."""
        # Escape single quotes in filter to prevent injection
        filter_escaped = filter.replace("'", "''")
        command = f"Get-ADComputer -Filter '{filter_escaped}' | Select-Object Name, DNSHostName, DistinguishedName, Enabled, OperatingSystem | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
