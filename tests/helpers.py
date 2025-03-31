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

    if using_hashes and not sys.platform.startswith('linux'):
        pytest.skip('Hashes for vector graphics are only provided in the hash library for Linux')

    if file_format != 'png' and file_format not in converter:
        if file_format == 'svg':
            pytest.skip('Comparing SVG files requires inkscape to be installed')
        else:
            pytest.skip('Comparing EPS and PDF files requires ghostscript to be installed')
