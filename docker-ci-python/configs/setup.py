import os
import sys

from setuptools import setup, find_packages
from pip.req import parse_requirements


assert sys.version_info.major == 3, "Only Python 3 is supported"


PROJECT_PATH = "/project"


def _pt(name):
    return os.path.join(PROJECT_PATH, name)


def _read(name):
    if not os.path.exists(name):
        return "<TBD>"
    with open(_pt(name)) as fil:
        return fil.read()


def _get_version():
    return _read("CHANGES").split("\n")[0].split()[0]


def _get_long_description():
    return _read("README.rst")


def _get_requirements():
    req_f = _pt("requirements.txt")
    if os.path.exists(req_f):
        return [str(ir.req) for ir in parse_requirements(req_f)]
    else:
        return []


setup(
    install_requires=_get_requirements(),
    version=_get_version(),
    packages=find_packages(exclude=["tests", "integration_tests"]),
    include_package_data=True
)
