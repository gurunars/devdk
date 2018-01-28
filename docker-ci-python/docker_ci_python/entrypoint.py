from __future__ import print_function

import os
import shutil
import subprocess
import sys

from functools import partial

import setuptools

from .run_command import run_command, CommandException


def _get_testable_packages(where=os.path.curdir):
    return [
        pkg for pkg in setuptools.
        find_packages(where, exclude=["tests", "integration_tests"])
        if "." not in pkg
    ]


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


def _rm(location, path):
    path = os.path.join(location, path)
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
        _run_with_safe_error(
            ["addgroup", "-g", str(gid), "tester"],
            "addgroup: group 'tester' in use"
        )
        _run_with_safe_error(
            ["adduser", "-D", "-u",
             str(uid), "-G", "tester", "tester"],
            "adduser: user 'tester' in use"
        )
        try:
            return run_command(["sudo", "-E", "-S", "-u", "tester"] + command)
        except CommandException as error:
            raise CommandException(error.returncode, command, error.output)


def _static_check(location, pkg_name, pylintrc_file):
    if not _exists_at(location, pkg_name):
        return
    run = partial(_run_for_project, location)
    run(["pycodestyle", "--max-line-length=79", pkg_name])
    run(["pyflakes", pkg_name])
    run([
        "custom-pylint", "--persistent=n",
        "--rcfile=/etc/docker-python/{}".format(pylintrc_file), pkg_name
    ])


def _reformat_pkg(location, pkg_name):
    if not _exists_at(location, pkg_name):
        return
    _run_for_project(
        location,
        [
            "yapf", "-i", "-r", "-p", "--style", "/etc/docker-python/yapf",
            pkg_name
        ]
    )


def _format_help_string(help_string):
    return " ".join(help_string.replace("\n", "").split())


DOCS = "gen-docs"


def _apply_theming(location):
    conf = os.path.join(location, DOCS, "conf.py")
    with open(conf) as fil:
        payload = fil.read()
    payload = payload.replace("alabaster", "sphinx_rtd_theme")
    with open(conf, "w") as fil:
        fil.write(payload)


def _generate_api_docs(location, pkg_names):
    for pkg_name in pkg_names:
        _run_for_project(
            location,
            [
                "sphinx-apidoc", "-f", "-M", "-F", "-T", "-E", "-d", "6",
                pkg_name, "-o", DOCS
            ]
        )
    _apply_theming(location)
    _run_for_project(
        location, ["sphinx-build", "-b", "html", DOCS, "{}/html".format(DOCS)]
    )


def _generate_binary(location):
    _run_for_project(location, ["python", "setup.py", "bdist_wheel"])


class EntryPoint(object):
    """
    Docker entry point to run various commands for a Python project
    in a sandbox.
    """

    # All methods here should remain members of the EntryPoint class
    # pylint: disable=no-self-use

    ARTIFACTS = [
        "coverage", ".coverage", ".coveragerc", "coverage.xml",
        "nosetests.xml", DOCS, "dist", "build"
    ]

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
                yield (
                    field_name.replace("_", "-"),
                    _format_help_string(field.__doc__)
                )

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

    def static_checks(self):
        """Runs pycodestyle, pylint and pyflakes"""
        pkg_configs = list(
            map(
                lambda pkg: (pkg, "pylintrc"),
                _get_testable_packages(self._location)
            )
        )
        test_configs = [("tests", "pylintrc-test"),
                        ("integration_tests", "pylintrc-test")]
        for pkg_name, pylint_rc in pkg_configs + test_configs:
            _static_check(self._location, pkg_name, pylint_rc)

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
            ] + list(
                map(
                    "--cover-package={}".format,
                    _get_testable_packages(self._location)
                )
            )
        )

    def clean(self):
        """Removes all the artifacts produced by the toolchain"""
        for artifact in self.ARTIFACTS:
            _rm(self._location, artifact)
        for pkg_name in _get_testable_packages(self._location):
            _rm(self._location, pkg_name + ".egg-info")

    def reformat(self):
        """Reformats the code to have the best possible style"""
        test_configs = ["tests", "integration_tests"]
        for pkg_name in _get_testable_packages(self._location) + test_configs:
            _reformat_pkg(self._location, pkg_name)

    def build(self):
        """Produces a library package and api docs"""
        _generate_api_docs(
            self._location, _get_testable_packages(self._location)
        )
        _generate_binary(self._location)
