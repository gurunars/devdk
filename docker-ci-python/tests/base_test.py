from abc import ABCMeta, abstractmethod

import unittest

from unittest import mock


class BaseTest(unittest.TestCase):

    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def MODULE_NAME(self):
        pass

    @classmethod
    def with_module(cls, module_name):

        class ModuledBaseTest(cls):
            MODULE_NAME = module_name

        return ModuledBaseTest

    def patch(self, what, with_what=None):
        target = mock.patch(
            self.MODULE_NAME + "." + what, with_what or mock.Mock()
        )
        patch = target.start()
        self.addCleanup(target.stop)
        return patch
