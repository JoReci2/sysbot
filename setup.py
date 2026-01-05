"""
Setup script for SysBot package.

SysBot is a comprehensive library for system test automation with support for
multiple protocols (SSH, WinRM, HTTP, Socket), secret management, and integration
with Robot Framework and various database systems.
"""
from setuptools import setup, find_packages

setup(
    name="sysbot",
    version="0.1.0",
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
    ],
    extras_require={
        "dev": ["pdoc3"],
    },
    author="Thibault SCIRE",
    author_email="thibault.scire@outlook.com",
    description="System test automation library",
    long_description="""SysBot is a comprehensive library designed for system test automation. 
    It provides secure connection management (SSH, WinRM), secret handling 
    capabilities, and seamless integration with various technologies including Redfish 
    and remote system management. Perfect for DevOps teams looking to automate infrastructure tests workflows.""",
    long_description_content_type="text/plain",
    url="https://github.com/JoReci2/sysbot.git",
    license="MIT",
    license_files=["LICENSE"],
    python_requires=">=3.7",
)
