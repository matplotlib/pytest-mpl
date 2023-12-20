import sys
from pathlib import Path

import matplotlib
import pytest
from matplotlib.testing.compare import converter
from packaging.version import Version

MPL_VERSION = Version(matplotlib.__version__)


def pytester_path(pytester):
    if hasattr(pytester, "path"):
        return pytester.path
    return Path(pytester.tmpdir)  # pytest v5


def skip_if_format_unsupported(file_format, using_hashes=False):
    if file_format == 'svg' and MPL_VERSION < Version('3.3'):
        pytest.skip('SVG comparison is only supported in Matplotlib 3.3 and above')

    if using_hashes:

        if file_format == 'pdf' and MPL_VERSION < Version('2.1'):
            pytest.skip('PDF hashes are only deterministic in Matplotlib 2.1 and above')
        elif file_format == 'eps' and MPL_VERSION < Version('2.1'):
            pytest.skip('EPS hashes are only deterministic in Matplotlib 2.1 and above')

    if using_hashes and not sys.platform.startswith('linux'):
        pytest.skip('Hashes for vector graphics are only provided in the hash library for Linux')

    if file_format != 'png' and file_format not in converter:
        if file_format == 'svg':
            pytest.skip('Comparing SVG files requires inkscape to be installed')
        else:
            pytest.skip('Comparing EPS and PDF files requires ghostscript to be installed')
