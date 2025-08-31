from sysbot.utils.engine import ComponentBase
import json


class Selinux(ComponentBase):
    def sestatus(self, alias: str) -> dict:
        output = self.execute_command(alias, "sestatus")
        
        def normalize_key(key: str) -> str:
            return key.strip().lower().replace(" ", "_")
    
        data = {}
        for line in output.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                data[normalize_key(key)] = value.strip()
        return data

    def getenforce(self, alias: str) -> str:
        return self.execute_command(alias, "getenforce")

    def context_id(self, alias: str) -> str:
        return self.execute_command(alias, "id -Z")

    def context_ps(self, alias: str, process: str) -> str:
        return self.execute_command(alias, f"ps -axZ | grep {process}")

    def context_file(self, alias: str, filename: str) -> str:
        return self.execute_command(alias, f"ls -Z {filename}")

    def getsebool(self, alias: str) -> dict:
        output = self.execute_command(alias, "getsebool -a")
        
        def normalize_key(key: str) -> str:
            return key.strip().lower().replace(" ", "_")

        data = {}
        for line in output.splitlines():
            if "-->" in line:
                key, value = line.split("-->", 1)
                data[normalize_key(key)] = value.strip()

        return data
