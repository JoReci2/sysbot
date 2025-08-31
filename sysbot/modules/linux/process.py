from sysbot.utils.engine import ComponentBase


class Process(ComponentBase):

    def ps(self, alias: str, name: str) -> dict:
        output = self.execute_command(alias, f"ps aux | grep {name} | grep -v grep")
        processes = []
        for line in output.splitlines():
            parts = line.split(maxsplit=10)
            if len(parts) >= 11:
                process = {
                    "user": parts[0],
                    "pid": int(parts[1]),
                    "cpu": float(parts[2]),
                    "mem": float(parts[3]),
                    "vsz": int(parts[4]),
                    "rss": int(parts[5]),
                    "tty": parts[6],
                    "stat": parts[7],
                    "start": parts[8],
                    "time": parts[9],
                    "command": parts[10],
                }
                processes.append(process)
        return processes

    def thread(self, alias: str, name: str) -> dict:
        output = self.execute_command(alias, f"ps axms | grep {name} | grep -v grep")
        processes = []
        for line in output.splitlines():
            parts = line.split(maxsplit=10)
            if len(parts) >= 11:
                process = {
                    "uid": int(parts[0]),
                    "pid": int(parts[1]),
                    "stack_ptr": parts[2],
                    "tty": parts[9],
                    "time": parts[10],
                    "command": parts[11] if len(parts) > 11 else ""
                }
                processes.append(process)
        return processes

    def security(self, alias: str, name: str) -> dict:
        output = self.execute_command(alias, f"ps -eo euser,ruser,suser,fuser,f,comm,label | grep {name} | grep -v grep")
        headers = ["euser", "ruser", "suser", "fuser", "f", "comm", "label"]
        processes = []
        for line in output.splitlines():
            line = line.strip()
            if not line or line.lower().startswith("euser"):
                continue
            parts = line.split(None, len(headers) - 1)
            if len(parts) < len(headers):
                continue
            processes.append(dict(zip(headers, parts)))
        return processes