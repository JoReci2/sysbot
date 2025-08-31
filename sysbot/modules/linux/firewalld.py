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
    
    