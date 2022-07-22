import pytest
from packaging.version import Version

pytest_plugins = ["pytester"]

if Version(pytest.__version__) < Version("6.2.0"):
    @pytest.fixture
    def pytester(testdir):
        return testdir
