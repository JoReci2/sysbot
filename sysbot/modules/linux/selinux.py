from sysbot.utils.engine import ComponentBase
import json


class Selinux(ComponentBase):
    def sestatus(self) -> dict:
        output = self.execute_command("sestatus")
        data = {}
        for line in output.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()
        return json.dumps(data, indent=2)

    def getenforce(self) -> str:
        return self.execute_command("getenforce")

    def context_id(self) -> str:
        return self.execute_command("id -Z")

    def context_ps(self, process: str) -> str:
        return self.execute_command(f"ps -axZ | grep {process}")

    def context_file(self, filename: str) -> str:
        return self.execute_command(f"ls -Z {filename}")

    def getsebool(self) -> dict:
        output = self.execute_command("getsebool -a")
        data = {}
        for line in output.splitlines():
            if "-->" in line:
                key, value = line.split("-->", 1)
                data[key.strip()] = value.strip()
        return json.dumps(data, indent=2)
