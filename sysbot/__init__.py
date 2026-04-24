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
