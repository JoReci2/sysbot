from sysbot.utils.engine import BaseModule

class Systemd(BaseModule):

    def start(self, alias, name):
        return self.execute_command(alias, f"systemctl start {name}")

    def stop(self, alias, name):
        return self.execute_command(alias, f"systemctl stop {name}")

    def is_active(self, alias, name):
        return self.execute_command(alias, f"systemctl is-active {name}")