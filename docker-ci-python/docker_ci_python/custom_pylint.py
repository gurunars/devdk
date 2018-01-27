#!/usr/bin/env python

import sys

from pylint.checkers.base import DocStringChecker as OriginalDocStringChecker
from pylint.checkers import utils
from pylint.lint import Run as OriginalRun, PyLinter as OriginalPyLinter

# This is not a public API - docstrings are not necessary
# Too many ancestors is the issue in the original PyLint
# pylint: disable=missing-docstring, too-many-ancestors

# NOTE: there is no point to cover this class since it is extends
# the original pylint without adding any extra logic


class DocStringChecker(OriginalDocStringChecker):

    @utils.check_messages('missing-docstring', 'empty-docstring')
    def visit_module(self, node):
        """Do not enforce module docstrings."""


class PyLinter(OriginalPyLinter):

    def register_checker(self, checker):  # pragma: nocover
        if checker.__class__ is OriginalDocStringChecker:
            checker = DocStringChecker(self)
        super(PyLinter, self).register_checker(checker)


class CustomRun(OriginalRun):
    LinterClass = PyLinter


def run_pylint():  # pragma: nocover
    CustomRun(sys.argv[1:])
