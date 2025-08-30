from sysbot.utils.engine import ModuleBase
import json
import configparser
from io import StringIO


class Dnf(ModuleBase):
    def repolist(self, alias):
        output = self.execute_command(alias, "dnf repolist --json")
        return json.loads(output)

    def repofile(self, alias, file):
        output = self.execute_command(alias, f"cat {file}")
        config = configparser.ConfigParser(strict=False, interpolation=None)
        config.read_file(StringIO(output))
        data = {section: dict(config.items(section)) for section in config.sections()}
        return data
