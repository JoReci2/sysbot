from sysbot.utils.engine import ComponentBase
import json
 
class Sysinfo(ComponentBase):
 
    def hostname(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "$env:computername", **kwargs)
 
    def fqdn(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "[System.Net.Dns]::GetHostByName($env:computerName).HostName", **kwargs)
 
    def domain(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "$env:USERDNSDOMAIN", **kwargs)
 
    def timezone(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "(Get-Date).ToUniversalTime().ToString('zzz')", **kwargs)
 
    def datetime_utc(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "[DateTimeOffset]::Now.ToString('dddd, MMMM dd, yyyy hh:mm:ss tt zzz')", **kwargs)
 
    def env(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(alias, f"[Environment]::GetEnvironmentVariable('{name}')", **kwargs)
 
    def process(self, alias: str, name: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"Get-Process -Name {name} | ConvertTo-Json", **kwargs)
        return json.loads(output)
 
    def win32_operatingsystem(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "Get-WmiObject -Class Win32_OperatingSystem | ConvertTo-Json", **kwargs)
        return json.loads(output)
 
    def win32_physicalmemory(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "Get-WmiObject -Class Win32_PhysicalMemory | ConvertTo-Json", **kwargs)
        return json.loads(output)
 
    def win32_processor(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "Get-WmiObject -class Win32_Processor | ConvertTo-Json", **kwargs)
        return json.loads(output)
 
    def win32_diskdrive(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "Get-WmiObject -Class Win32_DiskDrive | ConvertTo-Json", **kwargs)
        return json.loads(output)
 
    def win32_logicaldisk(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "Get-WmiObject -Class Win32_LogicalDisk | ConvertTo-Json", **kwargs)
        return json.loads(output)
 
    def roles(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "Get-WindowsFeature | ConvertTo-Json", **kwargs)
        return json.loads(output)
 
    def software(self, alias: str, **kwargs) -> list:
        output = self.execute_command(alias, "(Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Where-Object {$_.DisplayName -ne $null}).DisplayName", **kwargs)
        return output.splitlines()
 
    def registry(self, alias: str, path: str, **kwargs) -> list:
        output = self.execute_command(alias, f"Get-Item -Path Registry::{path} | Select-Object -ExpandProperty Property", **kwargs)
        return output.splitlines()