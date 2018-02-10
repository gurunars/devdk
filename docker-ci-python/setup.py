#!/usr/bin/python
import os
import sys

from setuptools import setup, find_packages
from pip.req import parse_requirements


assert sys.version_info.major == 3, "Only Python 3 is supported"


def _pt(name):
    return os.path.join(os.path.dirname(__file__), name)


def _read(name):
    with open(_pt(name)) as fil:
        return fil.read()


def _get_version():
    return _read("CHANGES").split("\n")[0].split()[0]


def _get_requirements():
    req_f = _pt("requirements.txt")
    if os.path.exists(req_f):
        return [str(ir.req) for ir in parse_requirements(req_f, session=False)]
    else:
        return []


setup(
    name="docker-ci-python",
    provides=["docker_ci_python"],
    author="Anton Berezin",
    install_requires=_get_requirements(),
    version=_get_version(),
    data_files=[('/etc/docker-python', [
        'configs/pylintrc',
        'configs/pylintrc-test',
        'configs/coveragerc',
        'configs/yapf',
        'configs/conf.py'
    ])],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            'entry-point = docker_ci_python.main:main',
            'custom-pylint = docker_ci_python.custom_pylint:run_pylint'
        ]
    }
)
