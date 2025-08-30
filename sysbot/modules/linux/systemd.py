from sysbot.utils.engine import ModuleBase


class Systemd(ModuleBase):
    def is_active(self, alias, name):
        return self.execute_command(alias, f"systemctl is-active {name}")

    def is_enabled(self, alias, name):
        return self.execute_command(alias, f"systemctl is-enabled {name}")

    def is_failed(self, alias, name):
        return self.execute_command(alias, f"systemctl is-failed {name}")
