from sysbot.utils.engine import ComponentBase
import json


class Users(ComponentBase):
    def win32_useraccount(self, alias: str, **kwargs) -> dict:
        command = "Get-WmiObject -Class Win32_UserAccount | Select-Object FullName, LocalAccount, Domain, Lockout, Name, PasswordChangeable, PasswordRequired, SID | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)

    def win32_group(self, alias: str, **kwargs) -> dict:
        command = "Get-WmiObject -Class Win32_Group | Select-Object Name, Domain, LocalAccount, SID | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
