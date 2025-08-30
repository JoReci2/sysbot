from sysbot.utils.engine import ComponentBase


class Service(ComponentBase):
    def start(self, name):
        return f"Starting service: {name}"
