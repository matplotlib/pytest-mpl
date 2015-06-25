from setuptools import setup

from pytest_mpl import __version__

setup(
    version=__version__,
    name="pytest-mpl",
    description='pytest plugin to help with testing figures output from Matplotlib',
    packages = ['pytest_mpl'],
    license='BSD',
    author='Thomas Robitaille',
    author_email='thomas.robitaille@gmail.com',
    entry_points = {'pytest11': ['pytest_mpl = pytest_mpl.plugin',]},
)
