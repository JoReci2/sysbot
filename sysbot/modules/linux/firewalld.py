from sysbot.utils.engine import ComponentBase
from typing import Dict, List


class Firewalld(ComponentBase):
    def getZones(self, alias: str, **kwargs) -> List[str]:
        output = self.execute_command(alias, "firewall-cmd --get-zones", **kwargs)
        return output.strip().split()

    def getActiveZones(self, alias: str, **kwargs) -> Dict[str, List[str]]:
        output = self.execute_command(
            alias, "firewall-cmd --get-active-zones", **kwargs
        )
        zones: Dict[str, List[str]] = {}
        current = None
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            if not line.startswith("interfaces:"):
                current = line
                zones[current] = []
            elif current and line.startswith("interfaces:"):
                ifaces = line.split("interfaces:", 1)[1].strip().split()
                zones[current].extend(ifaces)
        return zones

    def getDefaultZone(self, alias: str, **kwargs) -> str:
        output = self.execute_command(
            alias, "firewall-cmd --get-default-zone", **kwargs
        )
        return output.strip()

    def getForwardPorts(self, alias: str, zone: str, **kwargs) -> List[str]:
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-forward-ports", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getPorts(self, alias: str, zone: str, **kwargs) -> List[str]:
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-ports", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getInterface(self, alias: str, zone: str, **kwargs) -> List[str]:
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-interfaces", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getServices(self, alias: str, zone: str, **kwargs) -> List[str]:
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-services", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getProtocols(self, alias: str, zone: str, **kwargs) -> List[str]:
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-protocols", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getSourcePorts(self, alias: str, zone: str, **kwargs) -> List[str]:
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-source-ports", **kwargs
        )
        return output.strip().split() if output.strip() else []

    def getSources(self, alias: str, zone: str, **kwargs) -> List[str]:
        output = self.execute_command(
            alias, f"firewall-cmd --zone={zone} --list-sources", **kwargs
        )
        return output.strip().split() if output.strip() else []
