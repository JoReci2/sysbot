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
        "pyVmomi",
        "pywinrm",
        "pyOpenSSL",
        "pytz",
        "requests",
        "requests-oauthlib>=1.3.1",
        "PyJWT>=2.8.0",
        "cryptography",
        "hvac",
        "sqlalchemy",
    ],
    extras_require={
        "mysql": ["mysql-connector-python"],
        "postgresql": ["psycopg2-binary"],
        "mongodb": ["pymongo"],
        "all_databases": ["mysql-connector-python", "psycopg2-binary", "pymongo"],
    },
    author="Thibault SCIRE",
    author_email="thibault.scire@outlook.com",
    description="System test automation library",
    long_description="""SysBot is a comprehensive library designed for system test automation. 
    It provides secure connection management (SSH, WinRM), secret handling 
    capabilities, and seamless integration with various technologies including VMware vSphere, Redfish, 
    and remote system management. Perfect for DevOps teams looking to automate infrastructure tests workflows.""",
    long_description_content_type="text/plain",
    url="https://github.com/JoReci2/sysbot.git",
    license="MIT",
    license_files=["LICENSE"],
    python_requires=">=3.7",
)
