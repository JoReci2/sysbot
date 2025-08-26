class Systemd(object):

    def start(self, name):
        return "systemctl start {name}"

    def stop(self, name):
        return f"systemctl stop {name}"