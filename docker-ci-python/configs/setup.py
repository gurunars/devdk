import os
import sys

from setuptools import setup, find_packages
from yaml import load


assert sys.version_info.major == 3, "Only Python 3 is supported"


PROJECT_PATH = "/project"


def _pt(name):
    return os.path.join(PROJECT_PATH, name)


def _read(name):
    name = _pt(name)
    if not os.path.exists(name):
        raise ValueError("File does not exist: {}".format(name))
    with open(name) as fil:
        return fil.read()


def _setup_yml():
    return load(_read("setup.yml"))


def _get_version():
    return _read("CHANGES").split("\n")[0].split()[0]


setup(
    version=_get_version(),
    packages=find_packages(exclude=["tests", "integration_tests"]),
    include_package_data=True,
    long_description=_read("README.rst"),
    **_setup_yml()
)
