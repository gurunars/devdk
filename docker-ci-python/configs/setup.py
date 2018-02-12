import os
import sys

from setuptools import setup, find_packages
from yaml import load


assert sys.version_info.major == 3, "Only Python 3 is supported"


def _read(name):
    if not os.path.exists(name):
        raise ValueError("File does not exist: {}".format(name))
    with open(name) as fil:
        return fil.read()


def _setup_yml():
    return load(_read("setup.yml"))


def _get_version():
    return _read("CHANGES").split("\n")[0].split()[0]


def _print_all_requirements():
    data = _setup_yml()
    for reqs in ["install_requires", "setup_requires", "tests_require"]:
        for req in data.get(reqs, []):
            print(req, end=' ')


if sys.argv[1] == "list-requirements":
    _print_all_requirements()
else:
    setup(
        version=_get_version(),
        packages=find_packages(exclude=["tests", "integration_tests"]),
        include_package_data=True,
        long_description=_read("README.rst"),
        **_setup_yml()
    )
