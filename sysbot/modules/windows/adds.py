from sysbot.utils.engine import ComponentBase
import json


class Adds(ComponentBase):
    def get_domain(self, alias: str, **kwargs) -> dict:
        """Get Active Directory domain information."""
        command = "Get-ADDomain | Select-Object DNSRoot, DomainMode, Forest, Name, NetBIOSName, PDCEmulator | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_domain_controller(self, alias: str, **kwargs) -> dict:
        """Get Active Directory domain controller information."""
        command = "Get-ADDomainController | Select-Object Name, Domain, Forest, HostName, IPv4Address, IsGlobalCatalog, IsReadOnly, OperatingSystem, Site | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_user(self, alias: str, identity: str, **kwargs) -> dict:
        """Get a specific Active Directory user by identity."""
        # Escape single quotes to prevent injection
        identity_escaped = identity.replace("'", "''")
        command = f"Get-ADUser -Identity '{identity_escaped}' -Properties * | Select-Object Name, SamAccountName, UserPrincipalName, DistinguishedName, Enabled, EmailAddress, Department, Title, Manager, Created, Modified | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_users(self, alias: str, **kwargs) -> list:
        """Get all Active Directory users."""
        command = "Get-ADUser -Filter * -Properties Name, SamAccountName, UserPrincipalName, DistinguishedName, Enabled | Select-Object Name, SamAccountName, UserPrincipalName, DistinguishedName, Enabled | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        return json.loads(output)

    def search_users(self, alias: str, filter_query: str, **kwargs) -> list:
        """Search Active Directory users with a custom filter."""
        # Escape single quotes to prevent injection
        filter_escaped = filter_query.replace("'", "''")
        command = f"Get-ADUser -Filter '{filter_escaped}' -Properties Name, SamAccountName, UserPrincipalName, Enabled | Select-Object Name, SamAccountName, UserPrincipalName, Enabled | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        return json.loads(output)

    def get_group(self, alias: str, identity: str, **kwargs) -> dict:
        """Get a specific Active Directory group by identity."""
        # Escape single quotes to prevent injection
        identity_escaped = identity.replace("'", "''")
        command = f"Get-ADGroup -Identity '{identity_escaped}' -Properties * | Select-Object Name, SamAccountName, DistinguishedName, GroupCategory, GroupScope, Description, Created, Modified | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_groups(self, alias: str, **kwargs) -> list:
        """Get all Active Directory groups."""
        command = "Get-ADGroup -Filter * -Properties Name, SamAccountName, DistinguishedName, GroupCategory, GroupScope | Select-Object Name, SamAccountName, DistinguishedName, GroupCategory, GroupScope | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        return json.loads(output)

    def get_group_members(self, alias: str, identity: str, **kwargs) -> list:
        """Get members of a specific Active Directory group."""
        # Escape single quotes to prevent injection
        identity_escaped = identity.replace("'", "''")
        command = f"Get-ADGroupMember -Identity '{identity_escaped}' | Select-Object Name, SamAccountName, DistinguishedName, objectClass | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        return json.loads(output)

    def get_ou(self, alias: str, identity: str, **kwargs) -> dict:
        """Get a specific Active Directory organizational unit by identity."""
        # Escape single quotes to prevent injection
        identity_escaped = identity.replace("'", "''")
        command = f"Get-ADOrganizationalUnit -Identity '{identity_escaped}' -Properties * | Select-Object Name, DistinguishedName, Description, Created, Modified | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_ous(self, alias: str, **kwargs) -> list:
        """Get all Active Directory organizational units."""
        command = "Get-ADOrganizationalUnit -Filter * -Properties Name, DistinguishedName, Description | Select-Object Name, DistinguishedName, Description | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        return json.loads(output)

    def get_gpo(self, alias: str, name: str, **kwargs) -> dict:
        """Get a specific Group Policy Object by name."""
        # Escape single quotes to prevent injection
        name_escaped = name.replace("'", "''")
        command = f"Get-GPO -Name '{name_escaped}' | Select-Object DisplayName, Id, GpoStatus, CreationTime, ModificationTime, Description, DomainName | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_gpos(self, alias: str, **kwargs) -> list:
        """Get all Group Policy Objects."""
        command = "Get-GPO -All | Select-Object DisplayName, Id, GpoStatus, CreationTime, ModificationTime, DomainName | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        if not output or output.strip() == "":
            return []
        return json.loads(output)

    def get_gpo_report(self, alias: str, name: str, **kwargs) -> str:
        """Get a Group Policy Object report in XML format."""
        # Escape single quotes to prevent injection
        name_escaped = name.replace("'", "''")
        command = f"Get-GPOReport -Name '{name_escaped}' -ReportType Xml"
        output = self.execute_command(alias, command, **kwargs)
        return output
