from unittest import mock

from docker_ci_python.run_command import CommandException

from docker_ci_python.entrypoint import EntryPoint, _get_testable_packages, \
    _run_for_project, _full_path, _exists_at, _style_check, _run_with_safe_error

from .base_test import BaseTest


class UtilsTest(BaseTest.with_module("docker_ci_python.entrypoint")):

    def test_get_testable_packages(self):
        find_pkgs = self.patch("setuptools").find_packages
        find_pkgs.return_value = ["one", "two", "one.subone"]
        self.assertEqual(["one", "two"], _get_testable_packages())
        find_pkgs.assert_called_once_with(".", exclude=["tests", "integration_tests"])

    def test_full_path(self):
        path = self.patch("os.path")
        path.abspath = lambda path: "A(" + path + ")"
        path.expanduser = lambda path: "E(" + path + ")"
        self.assertEqual("A(E(/path))", _full_path("/path"))

    def test_exists_at(self):
        self.patch("os.path.exists", lambda path: path == "/parent/exists")
        self.assertTrue(_exists_at("/parent", "exists"))
        self.assertFalse(_exists_at("/parent", "not-exists"))

    def test_style_check(self):
        run = self.patch("_run_for_project")
        _style_check("/project", "one", "pylintrc")
        self.assertEqual([
            mock.call('/project', ['pep8', '--max-line-length=119', 'one']),
            mock.call('/project', ['pyflakes', 'one']),
            mock.call('/project', ['custom-pylint', '--persistent=n', '--rcfile=/etc/docker-python/pylintrc', 'one']),
        ], run.call_args_list)

    def test_run_with_safe_error(self):
        run = self.patch("run_command")
        run.side_effect = CommandException(42, ["cmd"], "SAFE")
        _run_with_safe_error(["cmd"], "SAFE")

    def test_run_and_rethrow_with_unknown_error(self):
        run = self.patch("run_command")
        run.side_effect = CommandException(42, ["cmd"], "BOOM!")
        with self.assertRaises(CommandException):
            _run_with_safe_error(["cmd"], "SAFE")


class RunForProjectTest(BaseTest.with_module("docker_ci_python.entrypoint")):

    def setUp(self):
        self.exists = self.patch("os.path.exists")
        self.run = self.patch("run_command")
        self.stat = stat = self.patch("os.stat").return_value
        stat.st_uid = 42
        stat.st_gid = 42

    def test_non_existent_location(self):
        self.exists.return_value = False
        self.assertRaises(SystemExit, _run_for_project, "/nonexistent", ["cmd"])

    def test_root_user(self):
        self.stat.st_uid = 0
        _run_for_project("/normal-path", ["cmd"])
        self.assertEqual([mock.call(["cmd"])], self.run.call_args_list)

    def test_rethrow_without_sudo_part(self):
        self.run.side_effect = [None, None, CommandException(42, ["cmd"])]
        with self.assertRaises(CommandException) as error:
            _run_for_project("/normal-path", ["cmd"])
        self.assertEqual(["cmd"], error.exception.cmd)

    def test_ok(self):
        _run_for_project("/normal-path", ["cmd"])
        self.assertEqual([
            mock.call(["addgroup", "-g", "42", "tester"], silent=True),
            mock.call(["adduser", "-D", "-u", "42", "-G", "tester", "tester"], silent=True),
            mock.call(["sudo", "-E", "-S", "-u", "tester", "cmd"])
        ], self.run.call_args_list)


class EntryPointTest(BaseTest.with_module("docker_ci_python.entrypoint")):

    # This is intentional to have a bunch of patches
    # pylint: disable=too-many-instance-attributes
    def setUp(self):
        self.patch("_full_path").return_value = "/project"
        self.call = self.patch("subprocess.call")
        self.run = self.patch("_run_for_project")
        self.get_packages = self.patch("_get_testable_packages")
        self.exists_at = self.patch("_exists_at")
        self.print_f = self.patch("print")
        self.style_check = self.patch("_style_check")
        self.shutil = self.patch("shutil")
        self.ep = EntryPoint("/project")

    def test_help(self):
        self.ep("help")
        self.assertEqual([
            mock.call('build'),
            mock.call('\tProduce a bundled build artifact (aka software package)'),
            mock.call('complete-validation'),
            mock.call('\tstyle-checks + tests'),
            mock.call('connect'),
            mock.call('\tSsh into the container'),
            mock.call('help'),
            mock.call('\tShow help message'),
            mock.call('repl'),
            mock.call('\tRun ipython within a container'),
            mock.call('style-checks'),
            mock.call('\tRun pep8, pylint and pyflakes'),
            mock.call('tests'),
            mock.call('\tRun unit tests with code coverage')
        ], self.print_f.call_args_list)

    def test_repl(self):
        self.ep("repl")
        self.call.assert_called_once_with(["ipython"])

    def test_connect(self):
        self.ep("connect")
        self.call.assert_called_once_with(["/bin/sh"])

    def test_style_checks(self):
        self.get_packages.return_value = ["one", "two"]
        self.ep("style-checks")
        self.assertEqual([
            mock.call('/project', 'one', 'pylintrc'),
            mock.call('/project', 'two', 'pylintrc'),
            mock.call('/project', 'tests', 'pylintrc-test'),
            mock.call('/project', 'integration_tests', 'pylintrc-test'),
        ], self.style_check.call_args_list)

    def test_style_checks_no_integration_tests(self):
        self.exists_at.return_value = False
        self.get_packages.return_value = ["one", "two"]
        self.ep("style-checks")
        self.assertEqual([
            mock.call('/project', 'one', 'pylintrc'),
            mock.call('/project', 'two', 'pylintrc'),
            mock.call('/project', 'tests', 'pylintrc-test')
        ], self.style_check.call_args_list)

    def test_build(self):
        self.assertRaises(NotImplementedError, self.ep, "build")

    def test_tests(self):
        self.get_packages.return_value = ["one", "two"]
        self.ep("tests")
        cmd = [
            'nosetests', '-v', '--with-xunit', '-e', 'integration_tests',
            '--cover-erase',
            '--with-coverage', '--cover-min-percentage=100', '--cover-inclusive',
            '--cover-html', '--cover-html-dir=/project/coverage',
            '--cover-xml', '--cover-xml-file=/project/coverage.xml',
            '--cover-package=one', '--cover-package=two'
        ]
        self.assertEqual([mock.call('/project', cmd)], self.run.call_args_list)
        self.shutil.copy.assert_called_once_with("/etc/docker-python/coveragerc", "/project/.coveragerc")

    def test_complete_validation(self):
        self.ep.style_checks = style_checks = mock.Mock()
        self.ep.tests = tests = mock.Mock()
        self.ep.complete_validation()
        self.assertEqual(1, style_checks.call_count)
        self.assertEqual(1, tests.call_count)
