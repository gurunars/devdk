from __future__ import print_function

import subprocess

# This prefix is necessary to prevent Docker from buffering Python subprocess
# output to pipe. This is required to e.g. enable continuous monitoring of
# unit test or integration test execution.
UNBUFFER_PREFIX = ["stdbuf", "-oL", "-eL"]


class CommandException(subprocess.CalledProcessError):
    """Exception which is raised if the command fails to execute."""


def _run_yieldable_command(command):
    # Please note - joining stdout and stderr is a must since tools
    # like pep8, pylint and mvn write errors to STDOUT and not STDERR.
    # This leads us to really polluted exceptions in case of failures,
    # but unfortunately there is nothing that can be done about it.
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)

    for line in iter(process.stdout.readline, b""):
        yield line if isinstance(line, str) else line.decode("utf-8")

    process.stdout.close()

    status = process.wait()

    if status:
        raise CommandException(status, command)


def _run_with_accumulation(accumulator, command, silent, printable, capture):
    for line in _run_yieldable_command(command):
        if printable(line):
            if capture:
                accumulator.append(line)
            if not silent:
                print(line, end="")


def run_command(command, silent=False, printable=None, capture=False):
    """stdout
    Execute a command, print output to stdout line by line and return the whole
    output as a string.

    :param command: shell statements to execute
    :type command: list
    :param silent: if True - output is not printed on the screen
    :type silent: bool
    :param printable: a function that takes a line as input and returns boolean
                      denoting whether this line should be printed or not.
                      True if it should be printed. False otherwise.
    :type printable: lambda line: True/False
    :param capture: if True - all output shall be accumulated and returned as a giant string
    :type capture: bool
    :return: output of the command
    :rtype: str
    :raises: CommandException if the status code returned by the command is > 0
    """
    lines = []

    def _msg():
        return "".join(lines).rstrip("\n")

    try:
        _run_with_accumulation(
            accumulator=lines,
            command=UNBUFFER_PREFIX + command,
            silent=silent,
            printable=printable or (lambda line: True),
            capture=capture
        )
    except CommandException as error:
        raise CommandException(error.returncode, command, _msg())
    return _msg()
