from __future__ import print_function

import os
import shutil
import subprocess
import sys

from functools import partial

import setuptools

from .run_command import run_command, CommandException


def _get_testable_packages(where=os.path.curdir):
    return [pkg for pkg in setuptools.find_packages(where, exclude=["tests", "integration_tests"]) if "." not in pkg]


def _full_path(path):
    return os.path.abspath(os.path.expanduser(path))


def _exists_at(parent, child):
    return os.path.exists(os.path.join(parent, child))


def _run_with_safe_error(cmd, safe_error):
    try:
        run_command(cmd, silent=True, capture=True)
    except CommandException as error:
        if safe_error not in str(error.stdout):
            print(error.stdout)
            raise error


def _rm(path):
    path = os.path.join("/project", path)
    shutil.rmtree(path, ignore_errors=True)
    if os.path.exists(path):
        os.remove(path)


def _run_for_project(location, command):
    if not os.path.exists(location):
        sys.exit("'{}' directory does not exist".format(location))

    stat_info = os.stat(location)
    uid = stat_info.st_uid
    gid = stat_info.st_gid

    if uid == 0:  # mounted on behalf of root user (Mac)
        return run_command(command)
    else:  # mounted on behalf of host user (Linux)
        # yapf: disable
        _run_with_safe_error(
            ["addgroup", "-g", str(gid), "tester"],
            "addgroup: group 'tester' in use"
        )
        _run_with_safe_error(
            ["adduser", "-D", "-u", str(uid), "-G", "tester", "tester"],
            "adduser: user 'tester' in use"
        )
        # yapf: enable
        try:
            return run_command(["sudo", "-E", "-S", "-u", "tester"] + command)
        except CommandException as error:
            raise CommandException(error.returncode, command, error.output)


def _style_check(location, pkg_name, pylintrc_file):
    if not _exists_at(location, pkg_name):
        return
    run = partial(_run_for_project, location)
    run(["pycodestyle", "--max-line-length=119", pkg_name])
    run(["pyflakes", pkg_name])
    run(["custom-pylint", "--persistent=n", "--rcfile=/etc/docker-python/{}".format(pylintrc_file), pkg_name])


def _reformat_pkg(location, pkg_name):
    if not _exists_at(location, pkg_name):
        return
    _run_for_project(location, ["yapf", "-i", "-r", "-p", "--style", "/etc/docker-python/yapf", pkg_name])


class EntryPoint(object):
    """
    Docker entry point to run various commands for a Python project in a sandbox.
    """

    # All methods here should remain members of the EntryPoint class
    # pylint: disable=no-self-use

    ARTIFACTS = ["coverage", ".coverage", ".coveragerc", "coverage.xml", "nosetests.xml"]

    def __init__(self, location):
        self._location = _full_path(location)

    def __call__(self, command):
        runnable = getattr(self, command.replace("-", "_"))
        runnable()

    def _get_commands(self):
        for field_name in dir(self):
            if field_name.startswith("_"):
                continue
            field = getattr(self, field_name)
            if callable(field):
                yield (field_name.replace("_", "-"), field.__doc__)

    # We do want it to be called help
    # pylint: disable=redefined-builtin
    def help(self):
        """Shows help message"""
        for name, help in self._get_commands():
            print(name)
            print("\t{}".format(help))

    def repl(self):
        """Runs ipython within a container"""
        subprocess.call(["ipython"])

    def connect(self):
        """Connects into the container's bash"""
        subprocess.call(["/bin/sh"])

    def style_checks(self):
        """Runs pycodestyle, pylint and pyflakes"""
        pkg_configs = list(map(lambda pkg: (pkg, "pylintrc"), _get_testable_packages(self._location)))
        for pkg_name, pylint_rc in pkg_configs + [
            ("tests", "pylintrc-test"),
            ("integration_tests", "pylintrc-test")
        ]:  # yapf: disable
            _style_check(self._location, pkg_name, pylint_rc)

    def tests(self):
        """Runs unit tests with code coverage"""
        # There is no way to make coverage module show missed lines otherwise
        shutil.copy("/etc/docker-python/coveragerc", "/project/.coveragerc")
        _run_for_project(
            self._location,
            [
                "nosetests",
                "-v",
                "--with-xunit",
                "-e",
                "integration_tests",
                "--cover-erase",  # To get proper stats
                "--with-coverage",
                "--cover-min-percentage=100",
                "--cover-inclusive",
                "--cover-html",
                "--cover-html-dir=/project/coverage",
                "--cover-xml",
                "--cover-xml-file=/project/coverage.xml"
            ] + list(map("--cover-package={}".format, _get_testable_packages(self._location)))
        )

    def clean(self):
        """Removes all the artifacts produced by the toolchain"""
        for artifact in self.ARTIFACTS:
            _rm(artifact)

    def validate(self):
        """style-checks + tests"""
        self.style_checks()
        self.tests()

    def reformat(self):
        """Reformats the code to have the best possible style"""
        for pkg_name in _get_testable_packages(self._location) + ["tests", "integration_tests"]:
            _reformat_pkg(self._location, pkg_name)

    def build(self):
        """Produces a bundled build artifact (aka software package) and Sphinx based docs"""
        raise NotImplementedError

    def publish(self):
        """Sends the built code to a binary package storage (e.g. PyPi)"""
        raise NotImplementedError
