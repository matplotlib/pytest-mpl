import pytest
from packaging.version import Version

pytest_plugins = ["pytester"]

if Version(pytest.__version__) < Version("6.2.0"):
    @pytest.fixture
    def pytester(testdir):
        return testdir


def pytest_configure(config):
    # Matplotlib versions build with pybind11 3.0.0 or later
    # encounter import issues unless run in subprocess mode.
    # See: https://github.com/matplotlib/pytest-mpl/issues/248
    import matplotlib
    if Version(matplotlib.__version__) > Version("3.10.3"):
        config.option.runpytest = "subprocess"
