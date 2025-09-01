from sysbot.utils.engine import ComponentBase
import json
from datetime import datetime, timezone


class Sysinfo(ComponentBase):
    def os_release(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "cat /etc/os-release", **kwargs)
        data = {}
        for line in output.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    data[key] = value.strip("\"'")
        return data

    def hostname(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "hostname -s", **kwargs)

    def fqdn(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "hostname -f", **kwargs)

    def domain(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "hostname -d", **kwargs)

    def uptime(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "uptime --pretty", **kwargs)

    def kernel(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "uname -r", **kwargs)

    def architecture(self, alias: str, **kwargs) -> str:
        return self.execute_command(alias, "uname -m", **kwargs)

    def ram(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "cat /proc/meminfo", **kwargs)
        data = {}
        for line in output.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = (
                key.strip().lower().replace("(", "").replace(")", "").replace(" ", "_")
            )
            parts = value.strip().split()
            val = int(parts[0]) if parts else 0
            unit = parts[1] if len(parts) > 1 else None

            data[key] = {"value": val, "unit": unit}

        return data

    def cpu(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "lscpu", **kwargs)
        lines = output.splitlines()
        cpu_info = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                cpu_info[key.strip()] = value.strip()
        return cpu_info

    def keyboard(self, alias: str, **kwargs) -> str:
        return self.execute_command(
            alias, "localectl | grep Keymap | awk '{print $3}' | tr -d ' '", **kwargs
        )

    def timezone(self, alias: str, **kwargs) -> str:
        return self.execute_command(
            alias,
            "timedatectl | grep 'Time zone' | awk '{print $3}' | tr -d ' '",
            **kwargs,
        )

    def datetime_utc(self, alias: str) -> str:
        output = self.execute_command(alias, "date '+%a %b %d %H:%M:%S %Y %z'")
        current_time = datetime.strptime(output, "%a %b %d %H:%M:%S %Y %z")
        utc_time = current_time.astimezone(timezone.utc)
        return utc_time.strftime("%Y/%m/%d %H:%M")

    def env(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "printenv", **kwargs)
        env_vars = {}
        for line in output.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key] = value.strip()
        return env_vars

    def process(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(
            alias, "ps -Aww -o pid,user,comm,pcpu,pmem", **kwargs
        )
        processes = {}
        for line in output.splitlines()[1:]:
            if line:
                pid, user, comm, pcpu, pmem = line.split(None, 4)
                processes[pid] = {
                    "user": user,
                    "command": comm,
                    "cpu": pcpu,
                    "memory": pmem,
                }
        return processes

    def lsblk(self, alias: str, **kwargs) -> dict:
        output = self.execute_command(alias, "lsblk --json", **kwargs)
        return json.loads(output)

    def sysctl(self, alias: str, variable: str) -> str:
        return self.execute_command(alias, f"sysctl -n {variable}")
    
    def dns(self, alias: str) -> list[str]:
        output = self.execute_command(alias, "cat /etc/resolv.conf")
        result = [srv.replace('nameserver ', '') for srv in output.splitlines if srv.startswith('nameserver')]
        return result