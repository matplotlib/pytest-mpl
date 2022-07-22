import unittest

from .helpers import bar, figure_test


class TestCase(unittest.TestCase):

    @figure_test
    def test_hmatch_imatch_testclass(self):
        return bar([1, 2, 3, 4])

    @figure_test
    def test_hdiff_idiff_testclass(self):
        return bar([1, 3, 2, 4])


class TestCaseWithSetUp(unittest.TestCase):

    def setUp(self):
        self.x = [4, 2, 3, 1]

    @figure_test
    def test_hmatch_imatch_testcasewithsetup(self):
        return bar(self.x)

    @figure_test
    def test_hdiff_idiff_testcasewithsetup(self):
        return bar(self.x)


class TestCaseWithSetUpClass(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.x = [4, 3, 2, 4]

    @figure_test
    def test_hmatch_imatch_testcasewithsetupclass(self):
        return bar(self.x)

    @figure_test
    def test_hdiff_idiff_testcasewithsetupclass(self):
        return bar(self.x)
