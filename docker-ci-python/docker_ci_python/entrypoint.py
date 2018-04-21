from __future__ import print_function

import os
import shutil
import subprocess
import sys

import setuptools

from .run_command import run_command, CommandException


def _exists(*args):
    return os.path.exists(os.path.join(*args))


def _wrap(strings, fmt):
    return list(map(fmt.format, strings))


def _rm(*args):
    path = os.path.join(*args)
    shutil.rmtree(path, ignore_errors=True)
    if os.path.exists(path):
        os.remove(path)


def _run_with_safe_error(cmd, safe_error):
    try:
        run_command(cmd, silent=True, capture=True)
    except CommandException as error:
        if safe_error not in str(error.stdout):
            print(error.stdout)
            raise error


def _run_for_project(project_path, command):
    if not os.path.exists(project_path):
        sys.exit("'{}' directory does not exist".format(project_path))

    stat_info = os.stat(project_path)
    uid = stat_info.st_uid
    gid = stat_info.st_gid

    if uid == 0:  # mounted on behalf of root user (Mac)
        return run_command(command, capture=True)
    else:  # mounted on behalf of host user (Linux)
        _run_with_safe_error(
            ["addgroup", "-g", str(gid), "tester"],
            "addgroup: group 'tester' in use"
        )
        _run_with_safe_error(
            ["adduser", "-D", "-u", str(uid), "-G", "tester", "tester"],
            "adduser: user 'tester' in use"
        )
        try:
            return run_command(
                ["sudo", "-E", "-S", "-u", "tester"] + command,
                capture=True
            )
        except CommandException as error:
            raise CommandException(error.returncode, command, error.output)


def _format_help_string(help_string):
    return " ".join(help_string.replace("\n", "").split())


DOCS = "gen-docs"


class ModuleUtils(object):
    # pylint: disable=missing-docstring

    def __init__(self, project_path, config_path):
        self._project_path = project_path
        self._config_path = config_path

    def _run(self, args):
        return _run_for_project(self._project_path, args)

    # pylint: disable=missing-docstring
    def reformat_pkg(self, module_name):
        if not _exists(self._project_path, module_name):
            return
        self._run([
            "yapf", "-i", "-r", "-p", "--style", "{}/yapf".format(
                self._config_path),
            module_name
        ])

    # pylint: disable=missing-docstring
    def static_check(self, module_name, pylintrc_file):
        if not _exists(self._project_path, module_name):
            return
        run = self._run
        run(["pycodestyle", "--max-line-length=79", module_name])
        run(["pyflakes", module_name])
        run([
            "custom-pylint", "--persistent=n",
            "--rcfile={}".format(os.path.join(self._config_path,
                                              pylintrc_file)), module_name
        ])

    # pylint: disable=missing-docstring
    def get_testable_packages(self):
        return [
            pkg for pkg in setuptools.find_packages(
                self._project_path, exclude=["tests", 'integration_tests']
            ) if "." not in pkg
        ]

    # pylint: disable=missing-docstring
    def copy_config(self):
        with open("{}/conf.py".format(self._config_path)) as fil:
            config = fil.read()

        def _meta(title):
            return self._run([
                "python",
                os.path.join(self._config_path, "setup.py"),
                "--{}".format(title)
            ])

        with open(
            os.path.join(self._project_path, DOCS, "conf.py"), "w"
        ) as fil:
            fil.write(config.format(
                project_name=_meta("name"),
                version=_meta("version"),
                author=_meta("author")
            ))


class EntryPoint(object):
    """
    Docker entry point to run various commands for a Python project
    in a sandbox.
    """

    # All methods here should remain members of the EntryPoint class
    # pylint: disable=no-self-use

    ARTIFACTS = [
        "coverage", ".coverage", "coverage.xml", "pytest.ini"
        "nosetests.xml", DOCS, "dist", "build"
    ]

    def __init__(self, project_path, config_path):
        self._project_path = project_path
        self._config_path = config_path
        self._package_utils = ModuleUtils(project_path, config_path)

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

    def _run(self, args):
        return _run_for_project(
            self._project_path,
            list(filter(lambda it: it, args))
        )

    @property
    def _modules(self):
        return self._package_utils.get_testable_packages()

    # We do want it to be called help
    # pylint: disable=redefined-builtin
    def help(self):
        """Shows help message"""
        for name, _help in self._get_commands():
            print(name)
            print("\t{}".format(_help))

    # noinspection PyMethodMayBeStatic
    def repl(self):
        """Runs ipython within a container"""
        subprocess.call(["ipython"])

    # noinspection PyMethodMayBeStatic
    def connect(self):
        """Connects into the container's bash"""
        subprocess.call(["/bin/sh"])

    def static_checks(self):
        """Runs pycodestyle, pylint and pyflakes"""
        pkg_configs = list(
            map(
                lambda pkg: (pkg, "pylintrc"),
                self._modules
            )
        )
        test_configs = [("tests", "pylintrc-test"),
                        ("integration_tests", "pylintrc-test")]
        for pkg_name, pylint_rc in pkg_configs + test_configs:
            self._package_utils.static_check(pkg_name, pylint_rc)

    def tests(self):
        """Runs unit tests with code coverage"""
        # There is no way to make coverage module show missed lines otherwise
        self._run([
            "pytest",
            "--cov-report=term:skip-covered",
            "--cov-report=html:coverage",
            "--cov-report=xml:coverage.xml",
            "--doctest-modules",
            "--cov-fail-under=100",
            "--junit-xml=nosetests.xml"
        ] + _wrap(self._modules, "--cov={}"))

    def _eggs(self):
        return list(
            filter(
                lambda fil: fil.endswith(".egg-info"),
                os.listdir(".")
            )
        )

    def clean(self):
        """Removes all the artifacts produced by the toolchain"""
        for artifact in self.ARTIFACTS + self._eggs():
            _rm(self._project_path, artifact)

    def reformat(self):
        """Reformats the code to have the best possible style"""
        for pkg_name in ["tests", "integration_tests"] + self._modules:
            self._package_utils.reformat_pkg(pkg_name)

    def build(self):
        """Produces a library package in the form of wheel package"""
        self._run(["python", os.path.join(
            self._config_path, "setup.py"), "bdist_wheel"])

    def build_docs(self):
        """Produces api docs in the form of .rst and .html files"""
        for module in self._modules:
            self._run([
                "sphinx-apidoc", "-f", "-M", "-F", "-T", "-E", "-d", "6",
                module, "-o", DOCS
            ])
        self._package_utils.copy_config()
        self._run([
            "sphinx-build", "-b", "html", DOCS, "{}/html".format(DOCS)
        ])
