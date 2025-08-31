from sysbot.utils.engine import ComponentBase
import json


class Ip(ComponentBase):
    def addr(self, alias: str, interface: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"ip --json addr show {interface}", **kwargs)
        return json.loads(output)

    def route(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "ip --json route", **kwargs)
        return json.loads(output)

    def speed(self, alias: str, interface: str, **kwargs) -> str:
        return self.execute_command(alias, f"cat /sys/class/net/{interface}/speed", **kwargs)

    def link(self, alias: str, interface: str, **kwargs) -> dict:
        output = self.execute_command(alias, f"ip --json link show {interface}", **kwargs)
        return json.loads(output)

    def resolve(self, alias: str, fqdn: str, **kwargs) -> dict:
        return self.execute_command(alias, f"getent hosts {fqdn} | awk '{{print $1}}'", **kwargs)

    def ping(self, alias: str, host: str, **kwargs) -> dict:
        return self.execute_command(
            alias, f"ping -W 1 -c 1 {host} > /dev/null 2>&1 ; echo $?", **kwargs
        )
