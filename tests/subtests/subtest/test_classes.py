import matplotlib.pyplot as plt
import pytest

from pytest_mpl.plugin import switch_backend

from .helpers import bar, figure_test


class TestClass:

    @figure_test
    def test_hmatch_imatch_testclass(self):
        return bar([1, 2, 3, 4])

    @figure_test
    def test_hdiff_idiff_testclass(self):
        return bar([1, 3, 2, 4])


class TestClassWithSetupMethod:

    def setup_method(self, method):
        self.x = [4, 2, 3, 1]

    @figure_test
    def test_hmatch_imatch_testclasswithsetupmethod(self):
        return bar(self.x)

    @figure_test
    def test_hdiff_idiff_testclasswithsetupmethod(self):
        return bar(self.x)


class TestClassWithSetupClass:

    @classmethod
    def setup_class(cls):
        cls.x = [1, 0, 3, 2]

    @figure_test
    def test_hmatch_imatch_testclasswithsetupclass(self):
        return bar(self.x)

    @figure_test
    def test_hdiff_idiff_testclasswithsetupclass(self):
        return bar(self.x)


@pytest.fixture()
def figure_axes():
    with plt.style.context("classic", after_reset=True), switch_backend("agg"):
        fig = bar([3, 0, 4, 1])
    yield fig.gca()
    # Should not appear in test result
    fig.gca().plot([3, 0, 4, 1], c="yellow")


class TestClassWithFixture:
    @figure_test
    def test_hmatch_imatch_testclasswithfixture(self, figure_axes):
        figure_axes.plot([4, 1, 5, 2], c="red")
        return figure_axes.get_figure()


def generate_two_figures():
    for num, line in ((1, [1, 0, 1, 0]), (2, [0, 1, 0, 1])):
        plt.close(num)
        fig = plt.figure(num)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(line)


class TestMultipleFigures:
    """
    Test figures are accessible, and can be passed to individual functions.

    See https://github.com/matplotlib/pytest-mpl/issues/133
    """
    @classmethod
    def setup_class(cls):
        # setting style and backend inside decorator has no effect
        # because figures are generated outside the test function
        with plt.style.context("classic", after_reset=True), switch_backend("agg"):
            generate_two_figures()
            cls.figs = [plt.figure(i) for i in (1, 2)]

    @figure_test
    def test_hmatch_imatch_multiplefigures_first(self):
        return self.figs[0]

    @figure_test
    def test_hmatch_imatch_multiplefigures_second(self):
        return self.figs[1]
