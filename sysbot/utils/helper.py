class Windows:
    @staticmethod
    def get_cim_class(namespace: str, classname: str, property: str) -> dict:
        return f"Get-CimInstance -Namespace {namespace} -ClassName {classname} | Select-Object {property} | ConvertTo-Json"
