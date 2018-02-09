import argparse
import sys

from .entrypoint import EntryPoint
from .run_command import CommandException

# Docstrings are not needed for the main CLI function
# Protected method is actually meant to be "package private"
# pylint: disable=missing-docstring, protected-access


def main(argv=None):
    entrypoint = EntryPoint("/project", "/etc/docker-python")

    parser = argparse.ArgumentParser(
        "Run CI related tasks for Python packages in a Docker container"
    )
    parser.add_argument(
        "subcommand", choices=dict(entrypoint._get_commands()).keys()
    )

    args = parser.parse_args(argv)

    try:
        entrypoint(args.subcommand)
    except CommandException as error:
        sys.exit(error.output)
