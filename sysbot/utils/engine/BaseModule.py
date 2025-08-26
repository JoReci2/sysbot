class BaseModule:
    def __init__(self):
        self._sysbot = None
    
    def set_sysbot_instance(self, sysbot_instance):
        self._sysbot = sysbot_instance
    
    def execute_command(self, alias, command, **kwargs):
        if self._sysbot is None:
            raise RuntimeError("No Sysbot instance available")
        return self._sysbot.execute_command(alias, command, **kwargs)