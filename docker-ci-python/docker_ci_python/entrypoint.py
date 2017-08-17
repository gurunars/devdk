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


def _run_for_project(location, command):
    if not os.path.exists(location):
        sys.exit("'{}' directory does not exist".format(location))

    stat_info = os.stat(location)
    uid = stat_info.st_uid
    gid = stat_info.st_gid

    if uid == 0:  # mounted on behalf of root user (Mac)
        return run_command(command)
    else:  # mounted on behalf of host user (Linux)
        run_command(["groupadd", "-f", "-g", str(gid), "tester"], silent=True)
        try:
            run_command(["useradd", "-u", str(uid), "-g", str(gid), "tester"], silent=True)
        except CommandException as error:
            # status code 9 means user already exists
            if error.returncode != 9:
                raise
        try:
            run_command(["sudo", "-E", "-S", "-u", "tester"] + command)
        except CommandException as error:
            raise CommandException(error.returncode, command, error.output)


def _style_check(location, pkg_name, pylintrc_file):
    run = partial(_run_for_project, location)
    run(["pep8", "--max-line-length=119", pkg_name])
    run(["pyflakes", pkg_name])
    run(["custom-pylint", "--persistent=n",
         "--rcfile=/etc/docker-python/{}".format(pylintrc_file), pkg_name])


def _coverage_enabled():
    return not os.path.exists("NOCOVERAGE")


class EntryPoint(object):
    """
    Docker entry point to run various commands for a Python project in a sandbox.
    """

    # All methods here should remain members of the EntryPoint class
    # pylint: disable=no-self-use

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
        """Show help message"""
        for name, help in self._get_commands():
            print(name)
            print("\t{}".format(help))

    def repl(self):
        """Run ipython within a container"""
        subprocess.call(["ipython"])

    def connect(self):
        """Ssh into the container"""
        subprocess.call(["/bin/sh"])

    def style_checks(self):
        """Run pep8, pylint and pyflakes"""
        for pkg_name in _get_testable_packages(self._location):
            _style_check(self._location, pkg_name, "pylintrc")
        _style_check(self._location, "tests", "pylintrc-test")
        if _exists_at(self._location, "integration_tests"):
            _style_check(self._location, "integration_tests", "pylintrc-test")

    def tests(self):
        """Run unit tests with code coverage"""
        cmd = ["nosetests", "-v", "--with-xunit", "-e", "integration_tests"]
        if _coverage_enabled():
            # There is no way to make coverage module show missed lines otherwise
            shutil.copy("/etc/docker-python/coveragerc", "/project/.coveragerc")
            cmd += [
                "--cover-erase",  # To get proper stats
                "--with-coverage", "--cover-min-percentage=100", "--cover-inclusive",
                "--cover-html", "--cover-html-dir=/project/coverage",
                "--cover-xml", "--cover-xml-file=/project/coverage.xml"
            ] + list(map("--cover-package={}".format, _get_testable_packages(self._location)))
        _run_for_project(self._location, cmd)

    def complete_validation(self):
        """style-checks + tests"""
        self.style_checks()
        self.tests()

    def build(self):
        """Produce a bundled build artifact (aka software package)"""
        raise NotImplementedError
