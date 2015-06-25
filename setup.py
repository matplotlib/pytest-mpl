from setuptools import setup

from pytest_mpl import __version__

setup(
    version=__version__,
    name="pytest-mpl",
    packages = ['pytest_mpl'],
    entry_points = {'pytest11': ['pytest_mpl = pytest_mpl.plugin',]},
)
