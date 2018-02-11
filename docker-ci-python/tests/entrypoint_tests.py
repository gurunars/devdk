from unittest import mock

from docker_ci_python.run_command import CommandException

from docker_ci_python.entrypoint import EntryPoint, PackageUtils, \
    _run_for_project, _exists, _run_with_safe_error, _rm

from .base_test import BaseTest


class UtilsTest(BaseTest.with_module("docker_ci_python.entrypoint")):

    def test_rm(self):
        self.patch("os.path.exists", lambda path: path == "/project/exists")
        remove = self.patch("os.remove")
        rmtree = self.patch("shutil.rmtree")
        _rm("/project", "exists")
        remove.assert_called_once_with("/project/exists")
        rmtree.assert_called_once_with("/project/exists", ignore_errors=True)

    def test_exists(self):
        self.patch("os.path.exists", lambda path: path == "/parent/exists")
        self.assertTrue(_exists("/parent", "exists"))
        self.assertFalse(_exists("/parent", "not-exists"))

    def test_run_with_safe_error(self):
        run = self.patch("run_command")
        run.side_effect = CommandException(42, ["cmd"], "SAFE")
        _run_with_safe_error(["cmd"], "SAFE")

    def test_run_and_rethrow_with_unknown_error(self):
        run = self.patch("run_command")
        run.side_effect = CommandException(42, ["cmd"], "BOOM!")
        with self.assertRaises(CommandException):
            _run_with_safe_error(["cmd"], "SAFE")


class PackageUtilsTest(BaseTest.with_module("docker_ci_python.entrypoint")):

    def setUp(self):
        self.run = self.patch("_run_for_project")
        self.utils = PackageUtils("/project", "/etc/docker-python")

    def _ex(self, flag):
        self.patch("_exists", lambda location, pkg: flag)

    def test_static_check(self):
        self._ex(True)
        self.utils.static_check("one", "pylintrc")
        self.assertEqual([
            mock.call(
                '/project', ['pycodestyle', '--max-line-length=79', 'one']
            ),
            mock.call('/project', ['pyflakes', 'one']),
            mock.call(
                '/project', [
                    'custom-pylint', '--persistent=n',
                    '--rcfile=/etc/docker-python/pylintrc', 'one'
                ]
            ),
        ], self.run.call_args_list)

    def test_static_check_doest_not_exist(self):
        self._ex(False)
        self.utils.static_check("one", "pylintrc")
        self.assertFalse(self.run.called)

    def test_get_testable_packages(self):
        find_pkgs = self.patch("setuptools").find_packages
        find_pkgs.return_value = ["one", "two", "one.subone"]
        self.assertEqual(["one", "two"], self.utils.get_testable_packages())
        find_pkgs.assert_called_once_with(
            "/project", exclude=["tests", "integration_tests"]
        )

    def test_reformat_pkg(self):
        self._ex(True)
        self.utils.reformat_pkg("module_name")
        self.run.assert_called_once_with(
            "/project", [
                "yapf", "-i", "-r", "-p", "--style", "/etc/docker-python/yapf",
                "module_name"
            ]
        )

    def test_reformat_pkg_does_not_exist(self):
        self._ex(False)
        self.utils.reformat_pkg("module_name")
        self.assertFalse(self.run.called)

    def test_copy_conifg(self):
        _open = self.patch("open", mock.MagicMock())
        self.utils.copy_config()
        self.assertEqual([
            mock.call("/etc/docker-python/conf.py"),
            mock.call("/project/gen-docs/conf.py", "w")
        ], _open.call_args_list)
        self.assertEqual([
            mock.call(
                "/project", ["python", "/etc/docker-python/setup.py",
                             "--name"]),
            mock.call(
                "/project", ["python", "/etc/docker-python/setup.py",
                             "--version"]),
            mock.call(
                "/project", ["python", "/etc/docker-python/setup.py",
                             "--author"])
        ], self.run.call_args_list)


class RunForProjectTest(BaseTest.with_module("docker_ci_python.entrypoint")):

    def setUp(self):
        self.exists = self.patch("os.path.exists")
        self.run = self.patch("run_command")
        self.stat = stat = self.patch("os.stat").return_value
        stat.st_uid = 42
        stat.st_gid = 42

    def test_non_existent_location(self):
        self.exists.return_value = False
        self.assertRaises(
            SystemExit, _run_for_project, "/nonexistent", ["cmd"]
        )

    def test_root_user(self):
        self.stat.st_uid = 0
        _run_for_project("/normal-path", ["cmd"])
        self.assertEqual([mock.call(["cmd"], capture=True)],
                         self.run.call_args_list)

    def test_rethrow_without_sudo_part(self):
        self.run.side_effect = [None, None, CommandException(42, ["cmd"])]
        with self.assertRaises(CommandException) as error:
            _run_for_project("/normal-path", ["cmd"])
        self.assertEqual(["cmd"], error.exception.cmd)

    def test_ok(self):
        _run_for_project("/normal-path", ["cmd"])
        self.assertEqual([
            mock.call(["addgroup", "-g", "42", "tester"],
                      silent=True,
                      capture=True),
            mock.call(["adduser", "-D", "-u", "42", "-G", "tester", "tester"],
                      silent=True,
                      capture=True),
            mock.call(["sudo", "-E", "-S", "-u", "tester", "cmd"],
                      capture=True)
        ], self.run.call_args_list)


class EntryPointTest(BaseTest.with_module("docker_ci_python.entrypoint")):

    # This is intentional to have a bunch of patches
    # pylint: disable=too-many-instance-attributes
    def setUp(self):
        self.call = self.patch("subprocess.call")
        self.run = self.patch("_run_for_project")

        utils = self.patch("PackageUtils").return_value

        self.get_packages = utils.get_testable_packages
        self.static_check = utils.static_check
        self.reformat = utils.reformat_pkg
        self.copy_config = utils.copy_config

        self.exists_at = self.patch("_exists")
        self.print_f = self.patch("print")
        self.shutil = self.patch("shutil")
        self.rm = self.patch("_rm")
        self.ep = EntryPoint("/project", "/etc/docker-python")

    def test_help(self):
        self.ep("help")
        print(self.print_f.call_args_list)
        self.assertEqual([
            mock.call('build'),
            mock.
            call('\tProduces a library package in the form of wheel package'),
            mock.call('build-docs'),
            mock.
            call('\tProduces api docs in the form of .rst and .html files'),
            mock.call('clean'),
            mock.call('\tRemoves all the artifacts produced by the toolchain'),
            mock.call('connect'),
            mock.call('\tConnects into the container\'s bash'),
            mock.call('help'),
            mock.call('\tShows help message'),
            mock.call('reformat'),
            mock.call('\tReformats the code to have the best possible style'),
            mock.call('repl'),
            mock.call('\tRuns ipython within a container'),
            mock.call('static-checks'),
            mock.call('\tRuns pycodestyle, pylint and pyflakes'),
            mock.call('tests'),
            mock.call('\tRuns unit tests with code coverage')
        ], self.print_f.call_args_list)

    def test_repl(self):
        self.ep("repl")
        self.call.assert_called_once_with(["ipython"])

    def test_connect(self):
        self.ep("connect")
        self.call.assert_called_once_with(["/bin/sh"])

    def test_static_checks(self):
        self.get_packages.return_value = ["one", "two"]
        self.ep("static-checks")
        self.assertEqual([
            mock.call('one', 'pylintrc'),
            mock.call('two', 'pylintrc'),
            mock.call('tests', 'pylintrc-test'),
            mock.call('integration_tests', 'pylintrc-test'),
        ], self.static_check.call_args_list)

    def test_tests(self):
        self.get_packages.return_value = ["one", "two"]
        self.ep("tests")
        cmd = [
            'nosetests', '-v', '--with-xunit', '-e', 'integration_tests',
            '--cover-erase', '--with-coverage', '--with-doctest',
            '--cover-min-percentage=100', '--cover-inclusive', '--cover-html',
            '--cover-html-dir=/project/coverage', '--cover-xml',
            '--cover-xml-file=/project/coverage.xml', '--cover-package=one',
            '--cover-package=two'
        ]
        self.assertEqual([mock.call('/project', cmd)], self.run.call_args_list)
        self.shutil.copy.assert_called_once_with(
            "/etc/docker-python/coveragerc", "/project/.coveragerc"
        )

    def test_clean(self):
        self.get_packages.return_value = ["one", "two"]
        self.ep.clean()
        print(self.rm.call_args_list)
        self.assertEqual(
            list(
                map(
                    lambda path: mock.call("/project", path),
                    self.ep.ARTIFACTS + ["one.egg-info", "two.egg-info"]
                )
            ),
            self.rm.call_args_list,
        )

    def test_reformat(self):
        self.get_packages.return_value = ["one", "two"]
        self.ep.reformat()
        self.assertEqual(
            list(
                map(
                    mock.call,
                    ["tests", "integration_tests", "one", "two"]
                )
            ),
            self.reformat.call_args_list,
        )

    def test_build(self):
        self.ep.build()
        self.run.assert_called_once_with(
            "/project", ["python",
                         "/etc/docker-python/setup.py", "bdist_wheel"]
        )

    def test_build_docs(self):
        self.get_packages.return_value = ["one", "two"]
        self.ep.build_docs()
        self.assertEqual(3, len(self.run.call_args_list))
        self.assertTrue(self.copy_config.called)
