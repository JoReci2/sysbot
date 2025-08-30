from sysbot.utils.engine import ComponentBase


class Service(ComponentBase):
    def start(self, name: str) -> str:
        return f"Starting service: {name}"
