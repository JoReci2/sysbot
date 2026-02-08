"""
Setup script for SysBot package.

SysBot is a comprehensive library for system test automation with support for
multiple protocols (SSH, WinRM, HTTP, Socket), secret management, and integration
with Robot Framework and various database systems.
"""
from setuptools import setup, find_packages

# Read the README file for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = """SysBot is a comprehensive library designed for system test automation. 
    It provides secure connection management (SSH, WinRM), secret handling 
    capabilities, and seamless integration with various technologies including Redfish 
    and remote system management. Perfect for DevOps teams looking to automate infrastructure tests workflows."""

setup(
    name="sysbot",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "robotframework",
        "paramiko",
        "sshtunnel",
        "netmiko",
        "redfish",
        "pywinrm",
        "pyOpenSSL",
        "pytz",
        "requests",
        "requests-oauthlib",
        "PyJWT",
        "cryptography",
        "hvac",
        "sqlalchemy",
        "ansible-runner",
    ],
    extras_require={
        "mysql": ["mysql-connector-python"],
        "postgresql": ["psycopg2-binary"],
        "mongodb": ["pymongo"],
        "all_databases": ["mysql-connector-python", "psycopg2-binary", "pymongo"],
        "dev": ["build", "pdoc3", "ruff", "bandit", "radon", "safety"],
    },
    author="Thibault SCIRE",
    author_email="thibault.scire@outlook.com",
    description="System test automation library with support for SSH, WinRM, HTTP, databases, and Robot Framework integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JoReci2/sysbot",
    project_urls={
        "Documentation": "https://joreci2.github.io/sysbot/",
        "Source": "https://github.com/JoReci2/sysbot",
        "Bug Tracker": "https://github.com/JoReci2/sysbot/issues",
    },
    keywords=[
        "automation",
        "testing",
        "system-testing",
        "ssh",
        "winrm",
        "robot-framework",
        "redfish",
        "devops",
        "infrastructure",
        "test-automation",
        "paramiko",
        "netmiko",
        "database",
        "vault",
        "secret-management",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Robot Framework",
        "Framework :: Robot Framework :: Library",
    ],
    license="MIT",
    license_files=["LICENSE"],
    python_requires=">=3.7",
)
