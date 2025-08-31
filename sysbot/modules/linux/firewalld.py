from sysbot.utils.engine import ComponentBase
import json


class Firewalld(ComponentBase):
    def getZone(self, alias: str) -> dict:
        output = self.execute_command(alias, "gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getZones")
        return json.loads(output)

    def getActiveZones(self, alias: str) -> dict:
        output = self.execute_command(alias, "gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getActiveZones")
        return json.loads(output)

    def getDefaultZone(self, alias: str) -> str:
        output = self.execute_command(alias, "gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.getDefaultZone")
        return json.loads(output)
    
    def getForwardPorts(self, alias: str, zone: str) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getForwardPorts {zone}")
        return json.loads(output)
    
    def getPorts(self, alias: str, zone: str) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getPorts {zone}")
        return json.loads(output)

    def getInterface(self, alias: str, zone: str) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getInterface {zone}")
        return json.loads(output)
    
    def getServices(self, alias: str, zone: str) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getServices {zone}")
        return json.loads(output)

    def getProtocols(self, alias: str, zone: str) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getProtocols {zone}")
        return json.loads(output)

    def getSourcePorts(self, alias: str, zone: str) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getSourcePorts {zone}")
        return json.loads(output)
    
    def getSources(self, alias: str, zone: str) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getSources {zone}")
        return json.loads(output)