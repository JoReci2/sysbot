from sysbot.utils.engine import ComponentBase


class Users(ComponentBase):
    def name(self, alias: str) -> str:
        return self.execute_command(alias, "id -nu")

    def group(self, alias: str) -> list:
        output = self.execute_command(alias, "id -Gn")
        return output.split()

    def uid(self, alias: str, name: str) -> str:
        return self.execute_command(alias, f"id -u {name}")

    def gid(self, alias: str, name: str) -> str:
        return self.execute_command(alias, f"id -g {name}")

    def gids(self, alias: str, name: str) -> list:
        output = self.execute_command(alias, f"id -G {name}")
        return output.split()

    def groups(self, alias: str, name: str) -> list:
        output = self.execute_command(alias, f"id -Gn {name}")
        return output.split()

    def home(self, alias: str, name: str) -> str:
        return self.execute_command(alias, f"getent passwd {name} | cut -d: -f6")

    def shell(self, alias: str, name: str) -> str:
        return self.execute_command(alias, f"getent passwd {name} | cut -d: -f7")
