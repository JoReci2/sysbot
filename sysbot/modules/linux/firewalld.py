from sysbot.utils.engine import ComponentBase
import json


class Firewalld(ComponentBase):
    def getZones(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getZones", **kwargs)
        return json.loads(output)

    def getActiveZones(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getActiveZones", **kwargs)
        return json.loads(output)

    def getDefaultZone(self, alias: str, **kwargs) -> str:
        output = self.execute_command(alias, "gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.getDefaultZone", **kwargs)
        return json.loads(output)

    def getForwardPorts(self, alias: str, zone: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getForwardPorts {zone}", **kwargs)
        return json.loads(output)

    def getPorts(self, alias: str, zone: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getPorts {zone}", **kwargs)
        return json.loads(output)

    def getInterface(self, alias: str, zone: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getInterface {zone}", **kwargs)
        return json.loads(output)

    def getServices(self, alias: str, zone: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getServices {zone}", **kwargs)
        return json.loads(output)

    def getProtocols(self, alias: str, zone: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getProtocols {zone}", **kwargs)
        return json.loads(output)

    def getSourcePorts(self, alias: str, zone: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getSourcePorts {zone}", **kwargs)
        return json.loads(output)

    def getSources(self, alias: str, zone: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"gdbus call --system   --dest org.fedoraproject.FirewallD1   --object-path /org/fedoraproject/FirewallD1   --method org.fedoraproject.FirewallD1.zone.getSources {zone}", **kwargs)
        return json.loads(output)