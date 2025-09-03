from sysbot.utils.engine import ComponentBase
import json


class Sysinfo(ComponentBase):
    def win32_networkadapter(self, alias: str, **kwargs) -> dict:
        command = "Get-WmiObject -Class Win32_NetworkAdapter | Select-Object Name, DeviceID, MACAddress, AdapterType, Speed  | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)
    
    def win32_networkadapterconfiguration(self, alias: str, **kwargs) -> dict:
        command = "Get-WmiObject -Class Win32_NetworkAdapterConfiguration | Select-Object DHCPEnabled, IPAddress, IPSubnet, DefaultIPGateway, DNSServerSearchOrder, ServiceName, Index, MTU  | ConvertTo-Json"
        output = self.execute_command(alias, command, **kwargs)
        return json.loads(output)