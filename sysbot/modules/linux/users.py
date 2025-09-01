from sysbot.utils.engine import ComponentBase


class Users(ComponentBase):
    def name(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "id -nu", **kwargs)

    def group(self, alias: str, **kwargs) -> list:
        output = self.execute_command(alias, "id -Gn", **kwargs)
        return output.split()

    def uid(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(alias, f"id -u {name}", **kwargs)

    def gid(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(alias, f"id -g {name}", **kwargs)

    def gids(self, alias: str, name: str, **kwargs) -> list:
        output = self.execute_command(alias, f"id -G {name}", **kwargs)
        return output.split()

    def groups(self, alias: str, name: str, **kwargs) -> list:
        output = self.execute_command(alias, f"id -Gn {name}", **kwargs)
        return output.split()

    def home(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(
            alias, f"getent passwd {name} | cut -d: -f6", **kwargs
        )

    def shell(self, alias: str, name: str, **kwargs) -> str:
        return self.execute_command(
            alias, f"getent passwd {name} | cut -d: -f7", **kwargs
        )
