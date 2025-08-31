from sysbot.utils.engine import ComponentBase
import json


class Ip(ComponentBase):
    def addr(self, alias: str, interface: str) -> dict:
        output = self.execute_command(alias, f"ip --json addr show {interface}")
        return json.loads(output)

    def route(self, alias: str) -> dict:
        output = self.execute_command(alias, "ip --json route")
        return json.loads(output)

    def speed(self, alias: str, interface: str) -> str:
        return self.execute_command(alias, f"cat /sys/class/net/{interface}/speed")

    def link(self, alias: str, interface: str) -> dict:
        output = self.execute_command(alias, f"ip --json link show {interface}")
        return json.loads(output)

    def resolve(self, alias: str, fqdn: str) -> dict:
        return self.execute_command(alias, f"getent hosts {fqdn} | awk '{{print $1}}'")

    def ping(self, alias: str, host: str) -> dict:
        return self.execute_command(
            alias, f"ping -W 1 -c 1 {host} > /dev/null 2>&1 ; echo $?"
        )
