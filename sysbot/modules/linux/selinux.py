from sysbot.utils.engine import ComponentBase


class Selinux(ComponentBase):
    def sestatus(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "sestatus", **kwargs)

        def normalize_key(key: str) -> str:
            return key.strip().lower().replace(" ", "_")

        data = {}
        for line in output.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                data[normalize_key(key)] = value.strip()
        return data

    def getenforce(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "getenforce", **kwargs)

    def context_id(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "id -Z", **kwargs)

    def context_ps(self, alias: str, process: str, **kwargs) -> str:
        return self.execute_command(alias, f"ps -axZ | grep {process}", **kwargs)

    def context_file(self, alias: str, filename: str, **kwargs) -> str:
        return self.execute_command(alias, f"ls -Z {filename}", **kwargs)

    def getsebool(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "getsebool -a", **kwargs)

        def normalize_key(key: str) -> str:
            return key.strip().lower().replace(" ", "_")

        data = {}
        for line in output.splitlines():
            if "-->" in line:
                key, value = line.split("-->", 1)
                data[normalize_key(key)] = value.strip()

        return data
