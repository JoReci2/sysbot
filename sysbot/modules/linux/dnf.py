import json

class Dnf(object):

    def repolist(self, name):
        return f"dnf repolist {name}"
    
    def list_installed(self, name):
        return f"dnf list installed {name}"
