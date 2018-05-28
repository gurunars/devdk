from docker_ci_python.main import main
from docker_ci_python.run_command import CommandException

from .base_test import BaseTest


class MainTest(BaseTest.with_module("docker_ci_python.main")):  # type: ignore

    def setUp(self):
        self.exit = self.patch("sys.exit")
        self.ep = self.patch("EntryPoint").return_value
        self.ep._get_commands.return_value = [("subcommand", "Help")]

    def test_ok(self):
        main(["subcommand"])
        self.assertTrue(self.ep.called)

    def test_nok(self):
        self.ep.side_effect = CommandException(42, ["subcommand"], "MSG")
        main(["subcommand"])
        self.exit.assert_called_once_with("MSG")
