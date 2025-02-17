from setuptools import setup, find_packages

setup(
    name="sysbotCore",
    version="version",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    author="Thibault SCIRE",
    author_email="thibault.scire@outlook.com",
    description="Sysbot core library",
    long_description="""This library provides core functionalities for the SysBot project.""",
    url="https://gitlab.com/home9344428/app/sysbot/sysbotCore.git",
    license="MIT",
    license_files=['LICENSE'],
    python_requires=">=3.7",
)