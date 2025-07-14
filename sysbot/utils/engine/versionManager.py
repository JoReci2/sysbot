from functools import wraps

class VersionManager:
    """Classe gérant les versions des fonctions."""
    
    def __init__(self):
        self._function_versions = {}

    def versioned(self, *versions):
        """Décorateur pour associer une fonction à plusieurs versions."""
        def decorator(func):
            name = func.__name__
            if name not in self._function_versions:
                self._function_versions[name] = {}

            for version in versions:
                self._function_versions[name][version] = func  # Associe une fonction à une version
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        return decorator

    def get_versioned_function(self, name, version):
        """Récupère une fonction selon son nom et sa version."""
        if name in self._function_versions and version in self._function_versions[name]:
            return self._function_versions[name][version]
        raise ValueError(f"Version '{version}' de '{name}' non trouvée")