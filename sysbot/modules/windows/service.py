from sysbot.utils.engine import ModuleBase

class Service(ModuleBase):

    def start(self, name):
        return f"Starting service: {name}"