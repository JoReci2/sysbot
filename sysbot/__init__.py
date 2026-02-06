"""
SysBot - System Test Automation Library

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

---

For complete documentation, see the README.md and CONTRIBUTING.md files 
included in this package directory.
"""

import os

# Load version from setuptools_scm generated file
try:
    from ._version import __version__
except ImportError:
    # Fallback for development environments where version file doesn't exist
    __version__ = "unknown"

# Load README content for documentation
_pkg_dir = os.path.dirname(__file__)
_readme_path = os.path.join(_pkg_dir, 'README.md')

if os.path.exists(_readme_path):
    try:
        with open(_readme_path, 'r', encoding='utf-8') as f:
            _readme_content = f.read()
            if __doc__ is None:
                __doc__ = _readme_content
            else:
                __doc__ += "\n\n" + _readme_content
    except (IOError, OSError):
        # If we can't read the README, just continue without it
        pass

from .Sysbot import Sysbot
__all__ = ['Sysbot', '__version__']
