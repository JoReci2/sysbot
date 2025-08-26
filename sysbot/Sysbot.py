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

import importlib
import os
from pathlib import Path
from .utils.engine import MetaModules
from .utils.engine import ModuleGroup
from .utils.engine import TunnelingManager

class Sysbot(metaclass=MetaModules):

    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def __init__(self, modules=None):
        if modules is None:
            modules = self._discover_all_modules()
        self._load_modules(modules)
    
    def _discover_all_modules(self):
        modules_dir = Path(__file__).parent / "modules"
        available_modules = []
        
        def scan_directory(directory, prefix=""):
            if not directory.exists():
                return
            
            for item in directory.iterdir():
                if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
                    module_path = f"{prefix}.{item.stem}" if prefix else item.stem
                    available_modules.append(module_path)
                elif item.is_dir() and not item.name.startswith('.'):
                    new_prefix = f"{prefix}.{item.name}" if prefix else item.name
                    scan_directory(item, new_prefix)
        
        scan_directory(modules_dir)
        return available_modules
    
    def _load_modules(self, module_names):
        for module_path in module_names:
            try:
                full_module_path = f"sysbot.modules.{module_path}"
                module = importlib.import_module(full_module_path)
                module_name = module_path.split('.')[-1]
                class_name = module_name.capitalize()
                
                if hasattr(module, class_name):
                    module_class = getattr(module, class_name)
                    module_instance = module_class()
                    self._create_hierarchy(module_path, module_instance)
            except ImportError as e:
                raise Exception(f"Unable to load module {module_path}: {e}")
    
    def _create_hierarchy(self, module_path, module_instance):
        parts = module_path.split('.')
        current_obj = self
        for i, part in enumerate(parts[:-1]):
            if not hasattr(current_obj, part):
                setattr(current_obj, part, ModuleGroup(part))
            current_obj = getattr(current_obj, part)
        final_name = parts[-1]
        setattr(current_obj, final_name, module_instance)
    
    def get_available_modules(self):
        def _collect_modules(obj, prefix=""):
            modules = []
            for attr_name in dir(obj):
                if not attr_name.startswith('_') and attr_name not in ['get_available_modules', 'list_discovered_modules', 'name']:
                    attr = getattr(obj, attr_name)
                    current_path = f"{prefix}.{attr_name}" if prefix else attr_name
                    
                    if isinstance(attr, ModuleGroup):
                        modules.extend(_collect_modules(attr, current_path))
                    elif hasattr(attr, '__class__') and not callable(attr):
                        modules.append(current_path)
            return modules
        
        return _collect_modules(self)
    
    def list_discovered_modules(self):
        return self._discover_all_modules()
    
