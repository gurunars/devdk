import unittest

from unittest import mock

from docker_ci_python.run_command import run_command, _run_yieldable_command, \
    _run_with_accumulation, CommandException, _get_printability_checker

from .base_test import BaseTest


def _run():
    return _run_yieldable_command(["cmd"])


class RunYieldableCommandTest(BaseTest.with_module("docker_ci_python.run_command")):

    def setUp(self):
        self.process = self.patch("subprocess.Popen").return_value
        self.process.stdout.readline.side_effect = [b"one", b"two", b"three"]
        self.process.wait.return_value = 0

    def test_ok(self):
        self.assertEqual(["one", "two", "three"], list(_run()))

    def test_nok(self):
        self.process.wait.return_value = 1
        self.assertRaises(CommandException, list, _run())


def _to_calls(array):
    return [mock.call(item, end="") for item in array]


class RunWithAccumulationCommandTest(BaseTest.with_module("docker_ci_python.run_command")):

    def setUp(self):
        self.run_yieldable_command = self.patch("_run_yieldable_command", mock.Mock(
            return_value=["one", "two", "three"]
        ))
        self.print_f = self.patch("print")
        self.accumulator = []

    def _assert_prints(self, expected_lines):
        self.assertEqual(
            [mock.call(item, end="") for item in expected_lines],
            self.print_f.call_args_list
        )

    def test_all_output(self):
        _run_with_accumulation(
            self.accumulator, ["cmd"], lambda line: True, capture=True
        )
        self.assertEqual(["one", "two", "three"], self.accumulator)
        self._assert_prints(["one", "two", "three"])

    def test_partial_output(self):
        _run_with_accumulation(
            self.accumulator, ["cmd"], lambda line: line != "two", capture=True
        )
        self.assertEqual(["one", "three"], self.accumulator)
        self._assert_prints(["one", "three"])

    def test_no_capture(self):
        _run_with_accumulation(
            self.accumulator, ["cmd"], lambda line: True, capture=False
        )
        self.assertEqual([], self.accumulator)
        self._assert_prints(["one", "two", "three"])


class RunCommandTest(BaseTest.with_module("docker_ci_python.run_command")):

    def test_ok(self):

        # pylint: disable=unused-argument
        def fake_run(accumulator, command, printable, capture):
            accumulator.extend(["Line #1", "Line #2"])

        self.patch("_run_with_accumulation", fake_run)
        self.assertEqual("Line #1Line #2", run_command(["CMD"]))

    def test_nok(self):
        run = self.patch("_run_with_accumulation")
        run.side_effect = CommandException(42, ["cmd"])
        self.assertRaises(CommandException, run_command, ["cmd"])


class PrintabilityTest(unittest.TestCase):

    def test_printable(self):
        printable = _get_printability_checker(printable=lambda line: line != "ignore")
        self.assertTrue(printable("normal"))
        self.assertFalse(printable("ignore"))

    def test_silent_printable_none(self):
        printable = _get_printability_checker(silent=True)
        self.assertFalse(printable("normal"))
        self.assertFalse(printable("ignore"))

    def test_silent_and_printable(self):
        printable = _get_printability_checker(silent=True, printable=lambda line: True)
        self.assertFalse(printable("normal"))
        self.assertFalse(printable("ignore"))
