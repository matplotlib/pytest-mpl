# Copyright (c) 2015, Thomas P. Robitaille
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# The code below includes code adapted from WCSAxes, which is released
# under a 3-clause BSD license and can be found here:
#
#   https://github.com/astrofrog/wcsaxes

from functools import wraps

import contextlib
import os
import sys
import shutil
import inspect
import tempfile
import warnings
from distutils.version import LooseVersion

import pytest

if sys.version_info[0] == 2:
    from urllib import urlopen
    string_types = basestring  # noqa
else:
    from urllib.request import urlopen
    string_types = str


def _download_file(baseline, filename):
    # Note that baseline can be a comma-separated list of URLs that we can
    # then treat as mirrors
    for base_url in baseline.split(','):
        try:
            u = urlopen(base_url + filename)
            content = u.read()
        except Exception as exc:
            warnings.warn('Downloading {0} failed'.format(base_url + filename))
        else:
            break
    else:
        raise Exception("Could not download baseline image from any of the "
                        "available URLs")
    result_dir = tempfile.mkdtemp()
    filename = os.path.join(result_dir, 'downloaded')
    with open(filename, 'wb') as tmpfile:
        tmpfile.write(content)
    return filename


def pytest_report_header(config, startdir):
    import matplotlib
    import matplotlib.ft2font
    return ["Matplotlib: {0}".format(matplotlib.__version__),
            "Freetype: {0}".format(matplotlib.ft2font.__freetype_version__)]


def pytest_addoption(parser):
    group = parser.getgroup("matplotlib image comparison")
    group.addoption('--mpl', action='store_true',
                    help="Enable comparison of matplotlib figures to reference files")
    group.addoption('--mpl-generate-path',
                    help="directory to generate reference images in, relative "
                    "to location where py.test is run", action='store')
    group.addoption('--mpl-baseline-path',
                    help="directory containing baseline images, relative to "
                    "location where py.test is run. This can also be a URL or a "
                    "set of comma-separated URLs (in case mirrors are "
                    "specified)", action='store')

    results_path_help = "directory for test results, relative to location where py.test is run"
    group.addoption('--mpl-results-path', help=results_path_help, action='store')
    parser.addini('mpl-results-path', help=results_path_help)


def pytest_configure(config):

    if config.getoption("--mpl") or config.getoption("--mpl-generate-path") is not None:

        baseline_dir = config.getoption("--mpl-baseline-path")
        generate_dir = config.getoption("--mpl-generate-path")
        results_dir = config.getoption("--mpl-results-path") or config.getini("mpl-results-path")

        # Note that results_dir is an empty string if not specified
        if not results_dir:
            results_dir = None

        if generate_dir is not None:
            if baseline_dir is not None:
                warnings.warn("Ignoring --mpl-baseline-path since --mpl-generate-path is set")
            if results_dir is not None and generate_dir is not None:
                warnings.warn("Ignoring --mpl-result-path since --mpl-generate-path is set")

        if baseline_dir is not None:
            baseline_dir = os.path.abspath(baseline_dir)
        if generate_dir is not None:
            baseline_dir = os.path.abspath(generate_dir)
        if results_dir is not None:
            results_dir = os.path.abspath(results_dir)

        config.pluginmanager.register(ImageComparison(config,
                                                      baseline_dir=baseline_dir,
                                                      generate_dir=generate_dir,
                                                      results_dir=results_dir))

    else:

        config.pluginmanager.register(FigureCloser(config))


@contextlib.contextmanager
def switch_backend(backend):
    import matplotlib
    import matplotlib.pyplot as plt
    prev_backend = matplotlib.get_backend().lower()
    if prev_backend != backend.lower():
        plt.switch_backend(backend)
        yield
        plt.switch_backend(prev_backend)
    else:
        yield


def close_mpl_figure(fig):
    "Close a given matplotlib Figure. Any other type of figure is ignored"

    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    # We only need to close actual Matplotlib figure objects. If
    # we are dealing with a figure-like object that provides
    # savefig but is not a real Matplotlib object, we shouldn't
    # try closing it here.
    if isinstance(fig, Figure):
        plt.close(fig)


def get_marker(item, marker_name):
    if hasattr(item, 'get_closest_marker'):
        return item.get_closest_marker(marker_name)
    else:
        # "item.keywords.get" was deprecated in pytest 3.6
        # See https://docs.pytest.org/en/latest/mark.html#updating-code
        return item.keywords.get(marker_name)


class ImageComparison(object):

    def __init__(self, config, baseline_dir=None, generate_dir=None, results_dir=None):
        self.config = config
        self.baseline_dir = baseline_dir
        self.generate_dir = generate_dir
        self.results_dir = results_dir
        if self.results_dir and not os.path.exists(self.results_dir):
            os.mkdir(self.results_dir)

    def pytest_runtest_setup(self, item):

        compare = get_marker(item, 'mpl_image_compare')

        if compare is None:
            return

        import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.testing.compare import compare_images
        try:
            from matplotlib.testing.decorators import remove_ticks_and_titles
        except ImportError:
            from matplotlib.testing.decorators import ImageComparisonTest as MplImageComparisonTest
            remove_ticks_and_titles = MplImageComparisonTest.remove_text

        MPL_LT_15 = LooseVersion(matplotlib.__version__) < LooseVersion('1.5')

        tolerance = compare.kwargs.get('tolerance', 2)
        savefig_kwargs = compare.kwargs.get('savefig_kwargs', {})
        style = compare.kwargs.get('style', 'classic')
        remove_text = compare.kwargs.get('remove_text', False)
        backend = compare.kwargs.get('backend', 'agg')

        if MPL_LT_15 and style == 'classic':
            style = os.path.join(os.path.dirname(__file__), 'classic.mplstyle')

        original = item.function

        @wraps(item.function)
        def item_function_wrapper(*args, **kwargs):

            baseline_dir = compare.kwargs.get('baseline_dir', None)
            if baseline_dir is None:
                if self.baseline_dir is None:
                    baseline_dir = os.path.join(os.path.dirname(item.fspath.strpath), 'baseline')
                else:
                    baseline_dir = self.baseline_dir
                baseline_remote = False
            else:
                baseline_remote = baseline_dir.startswith(('http://', 'https://'))
                if not baseline_remote:
                    baseline_dir = os.path.join(os.path.dirname(item.fspath.strpath), baseline_dir)

            with plt.style.context(style, after_reset=True), switch_backend(backend):

                # Run test and get figure object
                if inspect.ismethod(original):  # method
                    # In some cases, for example if setup_method is used,
                    # original appears to belong to an instance of the test
                    # class that is not the same as args[0], and args[0] is the
                    # one that has the correct attributes set up from setup_method
                    # so we ignore original.__self__ and use args[0] instead.
                    fig = original.__func__(*args, **kwargs)
                else:  # function
                    fig = original(*args, **kwargs)

                if remove_text:
                    remove_ticks_and_titles(fig)

                # Find test name to use as plot name
                filename = compare.kwargs.get('filename', None)
                if filename is None:
                    filename = item.name + '.png'
                    filename = filename.replace('[', '_').replace(']', '_')
                    filename = filename.replace('/', '_')
                    filename = filename.replace('_.png', '.png')

                # What we do now depends on whether we are generating the
                # reference images or simply running the test.
                if self.generate_dir is None:

                    # Save the figure
                    result_dir = tempfile.mkdtemp(dir=self.results_dir)
                    test_image = os.path.abspath(os.path.join(result_dir, filename))

                    fig.savefig(test_image, **savefig_kwargs)
                    close_mpl_figure(fig)

                    # Find path to baseline image
                    if baseline_remote:
                        baseline_image_ref = _download_file(baseline_dir, filename)
                    else:
                        baseline_image_ref = os.path.abspath(os.path.join(os.path.dirname(item.fspath.strpath), baseline_dir, filename))

                    if not os.path.exists(baseline_image_ref):
                        pytest.fail("Image file not found for comparison test in: "
                                    "\n\t{baseline_dir}"
                                    "\n(This is expected for new tests.)\nGenerated Image: "
                                    "\n\t{test}".format(baseline_dir=baseline_dir, test=test_image), pytrace=False)

                    # distutils may put the baseline images in non-accessible places,
                    # copy to our tmpdir to be sure to keep them in case of failure
                    baseline_image = os.path.abspath(os.path.join(result_dir, 'baseline-' + filename))
                    shutil.copyfile(baseline_image_ref, baseline_image)

                    msg = compare_images(baseline_image, test_image, tol=tolerance)

                    if msg is None:
                        shutil.rmtree(result_dir)
                    else:
                        pytest.fail(msg, pytrace=False)

                else:

                    if not os.path.exists(self.generate_dir):
                        os.makedirs(self.generate_dir)

                    fig.savefig(os.path.abspath(os.path.join(self.generate_dir, filename)), **savefig_kwargs)
                    close_mpl_figure(fig)
                    pytest.skip("Skipping test, since generating data")

        if item.cls is not None:
            setattr(item.cls, item.function.__name__, item_function_wrapper)
        else:
            item.obj = item_function_wrapper


class FigureCloser(object):
    """
    This is used in place of ImageComparison when the --mpl option is not used,
    to make sure that we still close figures returned by tests.
    """

    def __init__(self, config):
        self.config = config

    def pytest_runtest_setup(self, item):

        compare = get_marker(item, 'mpl_image_compare')

        if compare is None:
            return

        import matplotlib.pyplot as plt

        original = item.function

        @wraps(item.function)
        def item_function_wrapper(*args, **kwargs):

            if inspect.ismethod(original):  # method
                fig = original.__func__(*args, **kwargs)
            else:  # function
                fig = original(*args, **kwargs)

            close_mpl_figure(fig)

        if item.cls is not None:
            setattr(item.cls, item.function.__name__, item_function_wrapper)
        else:
            item.obj = item_function_wrapper
