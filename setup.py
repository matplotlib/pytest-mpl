import sys
from setuptools import setup

from pytest_mpl import __version__

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    if 'register' in sys.argv:
        raise
    else:
        with open('README.md') as infile:
            long_description = infile.read()

setup(
    version=__version__,
    url="https://github.com/astrofrog/pytest-mpl",
    name="pytest-mpl",
    description='pytest plugin to help with testing figures output from Matplotlib',
    long_description=long_description,
    packages = ['pytest_mpl'],
    package_data = {'pytest_mpl': ['classic.mplstyle']},
    license='BSD',
    author='Thomas Robitaille',
    author_email='thomas.robitaille@gmail.com',
    entry_points = {'pytest11': ['pytest_mpl = pytest_mpl.plugin',]},
)
