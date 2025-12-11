from sysbot.utils.engine import ComponentBase
import json


class Adds(ComponentBase):
    def get_fsmo(self, alias: str, **kwargs) -> dict:
        """Get FSMO role holders in the domain."""
        command = "Get-ADDomain | Select-Object InfrastructureMaster, RIDMaster, PDCEmulator | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

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
        # Escape single quotes to prevent injection
        safe_identity = identity.replace("'", "''")
        command = f"Get-ADUser -Identity '{safe_identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_users(self, alias: str, filter: str = "*", **kwargs) -> list:
        """Get users matching filter."""
        # Escape single quotes to prevent injection
        safe_filter = filter.replace("'", "''")
        command = f"Get-ADUser -Filter '{safe_filter}' -Properties * | ConvertTo-Json"
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
        # Escape single quotes to prevent injection
        safe_identity = identity.replace("'", "''")
        command = f"Get-ADGroup -Identity '{safe_identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_groups(self, alias: str, filter: str = "*", **kwargs) -> list:
        """Get groups matching filter."""
        # Escape single quotes to prevent injection
        safe_filter = filter.replace("'", "''")
        command = f"Get-ADGroup -Filter '{safe_filter}' -Properties * | ConvertTo-Json"
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
        # Escape single quotes to prevent injection
        safe_identity = identity.replace("'", "''")
        command = f"Get-ADGroupMember -Identity '{safe_identity}' | ConvertTo-Json"
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
        # Escape single quotes to prevent injection
        safe_identity = identity.replace("'", "''")
        command = f"Get-ADOrganizationalUnit -Identity '{safe_identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_organizational_units(self, alias: str, filter: str = "*", **kwargs) -> list:
        """Get organizational units matching filter."""
        # Escape single quotes to prevent injection
        safe_filter = filter.replace("'", "''")
        command = f"Get-ADOrganizationalUnit -Filter '{safe_filter}' -Properties * | ConvertTo-Json"
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
        # Escape single quotes to prevent injection
        safe_identity = identity.replace("'", "''")
        command = f"Get-ADComputer -Identity '{safe_identity}' -Properties * | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def get_computers(self, alias: str, filter: str = "*", **kwargs) -> list:
        """Get computers matching filter."""
        # Escape single quotes to prevent injection
        safe_filter = filter.replace("'", "''")
        command = f"Get-ADComputer -Filter '{safe_filter}' -Properties * | ConvertTo-Json"
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

    def get_gpo_report(self, alias: str, **kwargs) -> dict:
        """Get GPO report in XML format."""
        command = "Get-GPOReport -All -ReportType Xml | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
