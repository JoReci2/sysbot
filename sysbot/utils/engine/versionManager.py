"""
MIT License

Copyright (c) 2024 Thibault SCIRE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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