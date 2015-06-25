from setuptools import setup

setup(
    name="pytest-mpl",
    packages = ['pytest_mpl'],
    entry_points = {'pytest11': ['pytest_mpl = pytest_mpl.plugin',]},
)
