from sysbot.utils.engine import ComponentBase


class File(ComponentBase):
    def is_present(self, alias: str, path: str) -> bool:
        return self.execute_command(alias, f"test -e {path} ; echo $?") == "0"
    
    def is_file(self, alias: str, path: str) -> bool:
        return self.execute_command(alias, f"test -f {path} ; echo $?") == "0"
    
    def is_directory(self, alias: str, path: str) -> bool:
        return self.execute_command(alias, f"test -d {path} ; echo $?") == "0"
    
    def is_executable(self, alias: str, path: str) -> bool:
        return self.execute_command(alias, f"test -x {path} ; echo $?") == "0"
    
    def is_pipe(self, alias: str, path: str) -> bool:
        return self.execute_command(alias, f"test -p {path} ; echo $?") == "0" 
    
    def is_socket(self, alias: str, path: str) -> bool:
        return self.execute_command(alias, f"test -S {path} ; echo $?") == "0"
    
    def is_symlink(self, alias: str, path: str) -> bool:
        return self.execute_command(alias, f"test -L {path} ; echo $?") == "0"
    
    def realpath(self, alias: str, path: str) -> str:
        return self.execute_command(alias, f"realpath {path}")
    
    def user(self, alias: str, path: str) -> str:
        return self.execute_command(alias, f"stat -Lc %U {path}")
    
    def uid(self, alias: str, path: str) -> str:
        return self.execute_command(alias, f"stat -Lc %u {path}")
    
    def group(self, alias: str, path: str) -> str:
        return self.execute_command(alias, f"stat -Lc %G {path}")
    
    def gid(self, alias: str, path: str) -> str:
        return self.execute_command(alias, f"stat -Lc %g {path}")
    
    def mode(self, alias: str, path: str) -> str:
        return self.execute_command(alias, f"stat -Lc %a {path}")
    
    def size(self, alias: str, path: str) -> str:
        return self.execute_command(alias, f"stat -Lc %s {path}")
    
    def md5sum(self, alias: str, path: str) -> str:
        return self.execute_command(alias, f"md5sum {path} | cut -d' ' -f1 {path}")
    
    def content(self, alias: str, path: str) -> str:
        return self.execute_command(alias, f"cat {path}")
    
    def contains(self, alias: str, path: str, pattern: str ) -> bool:
        return self.execute_command(alias, f"grep -qs -- {pattern} {path} ; echo $?") == "0"
    
