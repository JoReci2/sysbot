from sysbot.utils.engine import ComponentBase
import json

class Ip(ComponentBase):

    def addr(self, alias: str, name: str) -> dict:
        output = self.execute_command(alias, f"ip --json addr show {name}")
        return json.loads(output)

    def route(self, alias: str) -> dict:
        output = self.execute_command(alias, f"ip --json route")
        return json.loads(output)
