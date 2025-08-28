from sysbot.utils.engine import BaseModule
import json

class Dnf(BaseModule):

    def repolist(self, alias):
        output = self.execute_command(alias, "dnf repolist --json")
        return json.loads(output)

    def get_package_version(self, alias, name):
        return self.execute_command(alias, f"""rpm -q --queryformat="%{{VERSION}}" {name}""")

    def get_package_release(self, alias, name):
        return self.execute_command(alias, f"""rpm -q --queryformat="%{{RELEASE}}" {name}""")

    def package_is_installed(self, alias, name):
        return self.execute_command(alias, f"""rpm -q {name}""") == 0
