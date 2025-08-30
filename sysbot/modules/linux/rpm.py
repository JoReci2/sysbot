from sysbot.utils.engine import ComponentBase


class Rpm(ComponentBase):
    def is_installed(self, alias, name):
        return self.execute_command(alias, f"rpm -q --quiet {name} ; echo $?")

    def version(self, alias, name):
        return self.execute_command(
            alias, f"""rpm -q --queryformat="%{{VERSION}}" {name}"""
        )

    def release(self, alias, name):
        return self.execute_command(
            alias, f"""rpm -q --queryformat="%{{RELEASE}}" {name}"""
        )
