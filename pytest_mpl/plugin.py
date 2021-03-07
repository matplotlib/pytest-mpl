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

import io
import os
import json
import shutil
import hashlib
import inspect
import tempfile
import warnings
import contextlib
from pathlib import Path
from functools import wraps
from urllib.request import urlopen

import pytest

from pytest_mpl.utils import wrap_message

SHAPE_MISMATCH_ERROR = """Error: Image dimensions did not match.
  Expected shape: {expected_shape}
    {expected_path}
  Actual shape: {actual_shape}
    {actual_path}"""

HTML_INTRO = """
<!DOCTYPE html>
<html>
<head>
<style>
table, th, td {
    border: 1px solid black;
}
</style>
</head>
<body>
<h2>Image test comparison</h2>
<table>
  <tr>
    <th>Test Name</th>
    <th>Baseline image</th>
    <th>Diff</th>
    <th>New image</th>
  </tr>
"""


def _download_file(baseline, filename):
    # Note that baseline can be a comma-separated list of URLs that we can
    # then treat as mirrors
    for base_url in baseline.split(','):
        try:
            u = urlopen(base_url + filename)
            content = u.read()
        except Exception as e:
            warnings.warn('Downloading {0} failed: {1}'.format(base_url + filename, e))
        else:
            break
    else:
        raise Exception("Could not download baseline image from any of the "
                        "available URLs")
    result_dir = Path(tempfile.mkdtemp())
    filename = result_dir / 'downloaded'
    with open(str(filename), 'wb') as tmpfile:
        tmpfile.write(content)
    return Path(filename)


def _hash_file(in_stream):
    """
    Hashes an already opened file.
    """
    in_stream.seek(0)
    buf = in_stream.read()
    hasher = hashlib.sha256()
    hasher.update(buf)
    return hasher.hexdigest()


def pathify(path):
    """
    Remove non-path safe characters.
    """
    path = Path(path)
    ext = ''
    if path.suffixes[-1] == '.png':
        ext = '.png'
        path = str(path).split(ext)[0]
    path = str(path)
    path = path.replace('[', '_').replace(']', '_')
    path = path.replace('/', '_')
    if path.endswith('_'):
        path = path[:-1]
    return Path(path + ext)


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
    group.addoption('--mpl-generate-hash-library',
                    help="filepath to save a generated hash library, relative "
                    "to location where py.test is run", action='store')
    group.addoption('--mpl-baseline-path',
                    help="directory containing baseline images, relative to "
                    "location where py.test is run unless --mpl-baseline-relative is given. "
                    "This can also be a URL or a set of comma-separated URLs (in case "
                    "mirrors are specified)", action='store')
    group.addoption("--mpl-baseline-relative", help="interpret the baseline directory as "
                    "relative to the test location.", action="store_true")
    group.addoption('--mpl-hash-library',
                    help="json library of image hashes, relative to "
                    "location where py.test is run", action='store')
    group.addoption('--mpl-generate-summary', action='store',
                    help="Generate a summary report of any failed tests"
                    ", in --mpl-results-path. The type of the report should be "
                    "specified, the only format supported at the moment is `html`.")

    results_path_help = "directory for test results, relative to location where py.test is run"
    group.addoption('--mpl-results-path', help=results_path_help, action='store')
    parser.addini('mpl-results-path', help=results_path_help)
    parser.addini('mpl-use-full-test-name', help="use fully qualified test name as the filename.",
                  type='bool')


def pytest_configure(config):

    config.addinivalue_line('markers',
                            "mpl_image_compare: Compares matplotlib figures "
                            "against a baseline image")

    if (config.getoption("--mpl") or
            config.getoption("--mpl-generate-path") is not None or
            config.getoption("--mpl-generate-hash-library") is not None):

        baseline_dir = config.getoption("--mpl-baseline-path")
        generate_dir = config.getoption("--mpl-generate-path")
        generate_hash_lib = config.getoption("--mpl-generate-hash-library")
        results_dir = config.getoption("--mpl-results-path") or config.getini("mpl-results-path")
        hash_library = config.getoption("--mpl-hash-library")
        generate_summary = config.getoption("--mpl-generate-summary")

        if config.getoption("--mpl-baseline-relative"):
            baseline_relative_dir = config.getoption("--mpl-baseline-path")
        else:
            baseline_relative_dir = None

        # Note that results_dir is an empty string if not specified
        if not results_dir:
            results_dir = None

        if generate_dir is not None:
            if baseline_dir is not None:
                warnings.warn("Ignoring --mpl-baseline-path since --mpl-generate-path is set")
            if results_dir is not None and generate_dir is not None:
                warnings.warn("Ignoring --mpl-result-path since --mpl-generate-path is set")

        if baseline_dir is not None and not baseline_dir.startswith(("https", "http")):
            baseline_dir = os.path.abspath(baseline_dir)
        if generate_dir is not None:
            baseline_dir = os.path.abspath(generate_dir)
        if results_dir is not None:
            results_dir = os.path.abspath(results_dir)

        config.pluginmanager.register(ImageComparison(config,
                                                      baseline_dir=baseline_dir,
                                                      baseline_relative_dir=baseline_relative_dir,
                                                      generate_dir=generate_dir,
                                                      results_dir=results_dir,
                                                      hash_library=hash_library,
                                                      generate_hash_library=generate_hash_lib,
                                                      generate_summary=generate_summary))

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


def path_is_not_none(apath):
    return Path(apath) if apath is not None else apath


class ImageComparison:

    def __init__(self,
                 config,
                 baseline_dir=None,
                 baseline_relative_dir=None,
                 generate_dir=None,
                 results_dir=None,
                 hash_library=None,
                 generate_hash_library=None,
                 generate_summary=None
                 ):
        self.config = config
        self.baseline_dir = baseline_dir
        self.baseline_relative_dir = path_is_not_none(baseline_relative_dir)
        self.generate_dir = path_is_not_none(generate_dir)
        self.results_dir = path_is_not_none(results_dir)
        self.hash_library = path_is_not_none(hash_library)
        self.generate_hash_library = path_is_not_none(generate_hash_library)
        if generate_summary and generate_summary.lower() not in ("html",):
            raise ValueError(f"The mpl summary type '{generate_summary}' is not supported.")
        self.generate_summary = generate_summary

        # Generate the containing dir for all test results
        if not self.results_dir:
            self.results_dir = Path(tempfile.mkdtemp(dir=self.results_dir))
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # We need global state to store all the hashes generated over the run
        self._generated_hash_library = {}

    def get_compare(self, item):
        """
        Return the mpl_image_compare marker for the given item.
        """
        return get_marker(item, 'mpl_image_compare')

    def generate_filename(self, item):
        """
        Given a pytest item, generate the figure filename.
        """
        if self.config.getini('mpl-use-full-test-name'):
            filename = self.generate_test_name(item) + '.png'
        else:
            compare = self.get_compare(item)
            # Find test name to use as plot name
            filename = compare.kwargs.get('filename', None)
            if filename is None:
                filename = item.name + '.png'

        filename = str(pathify(filename))
        return filename

    def generate_test_name(self, item):
        """
        Generate a unique name for the hash for this test.
        """
        return f"{item.module.__name__}.{item.name}"

    def make_test_results_dir(self, item):
        """
        Generate the directory to put the results in.
        """
        test_name = pathify(self.generate_test_name(item))
        results_dir = self.results_dir / test_name
        results_dir.mkdir(exist_ok=True, parents=True)
        return results_dir

    def baseline_directory_specified(self, item):
        """
        Returns `True` if a non-default baseline directory is specified.
        """
        compare = self.get_compare(item)
        item_baseline_dir = compare.kwargs.get('baseline_dir', None)
        return item_baseline_dir or self.baseline_dir or self.baseline_relative_dir

    def get_baseline_directory(self, item):
        """
        Return a full path to the baseline directory, either local or remote.

        Using the global and per-test configuration return the absolute
        baseline dir, if the baseline file is local else return base URL.
        """
        compare = self.get_compare(item)
        baseline_dir = compare.kwargs.get('baseline_dir', None)
        if baseline_dir is None:
            if self.baseline_dir is None:
                baseline_dir = Path(item.fspath).parent / 'baseline'
            else:
                if self.baseline_relative_dir:
                    # baseline dir is relative to the current test
                    baseline_dir = Path(item.fspath).parent / self.baseline_relative_dir
                else:
                    # baseline dir is relative to where pytest was run
                    baseline_dir = self.baseline_dir

        baseline_remote = (isinstance(baseline_dir, str) and  # noqa
                           baseline_dir.startswith(('http://', 'https://')))
        if not baseline_remote:
            return Path(item.fspath).parent / baseline_dir

        return baseline_dir

    def obtain_baseline_image(self, item, target_dir):
        """
        Copy the baseline image to our working directory.

        If the image is remote it is downloaded, if it is local it is copied to
        ensure it is kept in the event of a test failure.
        """
        filename = self.generate_filename(item)
        baseline_dir = self.get_baseline_directory(item)
        baseline_remote = (isinstance(baseline_dir, str) and  # noqa
                           baseline_dir.startswith(('http://', 'https://')))
        if baseline_remote:
            # baseline_dir can be a list of URLs when remote, so we have to
            # pass base and filename to download
            baseline_image = _download_file(baseline_dir, filename)
        else:
            baseline_image = (baseline_dir / filename).absolute()

        return baseline_image

    def generate_baseline_image(self, item, fig):
        """
        Generate reference figures.
        """
        compare = self.get_compare(item)
        savefig_kwargs = compare.kwargs.get('savefig_kwargs', {})

        if not os.path.exists(self.generate_dir):
            os.makedirs(self.generate_dir)

        fig.savefig(str((self.generate_dir / self.generate_filename(item)).absolute()),
                    **savefig_kwargs)

        close_mpl_figure(fig)
        pytest.skip("Skipping test, since generating image")

    def generate_image_hash(self, item, fig):
        """
        For a `matplotlib.figure.Figure`, returns the SHA256 hash as a hexadecimal
        string.
        """
        compare = self.get_compare(item)
        savefig_kwargs = compare.kwargs.get('savefig_kwargs', {})

        imgdata = io.BytesIO()

        fig.savefig(imgdata, **savefig_kwargs)

        out = _hash_file(imgdata)
        imgdata.close()

        close_mpl_figure(fig)
        return out

    def compare_image_to_baseline(self, item, fig, result_dir):
        """
        Compare a test image to a baseline image.
        """
        from matplotlib.image import imread
        from matplotlib.testing.compare import compare_images

        compare = self.get_compare(item)
        tolerance = compare.kwargs.get('tolerance', 2)
        savefig_kwargs = compare.kwargs.get('savefig_kwargs', {})

        baseline_image_ref = self.obtain_baseline_image(item, result_dir)

        test_image = (result_dir / "result.png").absolute()
        fig.savefig(str(test_image), **savefig_kwargs)

        if not os.path.exists(baseline_image_ref):
            return ("Image file not found for comparison test in: \n\t"
                    f"{self.get_baseline_directory(item)}\n"
                    "(This is expected for new tests.)\n"
                    "Generated Image: \n\t"
                    f"{test_image}")

        # distutils may put the baseline images in non-accessible places,
        # copy to our tmpdir to be sure to keep them in case of failure
        baseline_image = (result_dir / "baseline.png").absolute()
        shutil.copyfile(baseline_image_ref, baseline_image)

        # Compare image size ourselves since the Matplotlib
        # exception is a bit cryptic in this case and doesn't show
        # the filenames
        expected_shape = imread(str(baseline_image)).shape[:2]
        actual_shape = imread(str(test_image)).shape[:2]
        if expected_shape != actual_shape:
            return SHAPE_MISMATCH_ERROR.format(expected_path=baseline_image,
                                               expected_shape=expected_shape,
                                               actual_path=test_image,
                                               actual_shape=actual_shape)

        return compare_images(str(baseline_image), str(test_image), tol=tolerance)

    def load_hash_library(self, library_path):
        with open(str(library_path)) as fp:
            return json.load(fp)

    def compare_image_to_hash_library(self, item, fig, result_dir):
        compare = self.get_compare(item)
        savefig_kwargs = compare.kwargs.get('savefig_kwargs', {})

        hash_library_filename = self.hash_library or compare.kwargs.get('hash_library', None)
        if self.config.getini("mpl-use-full-test-name"):
            hash_library_filename = hash_library_filename.absolute()
        else:
            hash_library_filename = (Path(item.fspath).parent / hash_library_filename).absolute()

        if not Path(hash_library_filename).exists():
            pytest.fail(f"Can't find hash library at path {hash_library_filename}")

        hash_library = self.load_hash_library(hash_library_filename)
        hash_name = self.generate_test_name(item)

        test_hash = self.generate_image_hash(item, fig)

        if hash_name not in hash_library:
            error_message = (f"Hash for test '{hash_name}' not found in"
                             f" {hash_library_filename}. "
                             f"Generated hash is {test_hash}.")
            error_message = wrap_message(error_message)
            return error_message

        if test_hash == hash_library[hash_name]:
            return

        error_message = (f"Hash {test_hash} doesn't match hash "
                         f"{hash_library[hash_name]} in library "
                         f"{hash_library_filename} for test {hash_name}.")
        error_message = wrap_message(error_message)

        # If the compare has only been specified with hash and not baseline
        # dir, don't attempt to find a baseline image at the default path.
        if not self.baseline_directory_specified(item):
            # Save the figure for later summary
            test_image = (result_dir / "result.png").absolute()
            fig.savefig(str(test_image), **savefig_kwargs)
            return error_message

        baseline_image_path = self.obtain_baseline_image(item, result_dir)
        try:
            baseline_image = baseline_image_path
            baseline_image = None if not baseline_image.exists() else baseline_image
        except Exception:
            baseline_image = None

        if baseline_image is None:
            error_message += f"\nUnable to find baseline image {baseline_image_path}."
            return wrap_message(error_message)

        # Override the tolerance (if not explicitly set) to 0 as the hashes are not forgiving
        tolerance = compare.kwargs.get('tolerance', None)
        if not tolerance:
            compare.kwargs['tolerance'] = 0

        comparison_error = (self.compare_image_to_baseline(item, fig, result_dir) or
                            "\nHowever, the comparison to the baseline image succeeded.")

        return f"{error_message}\n{comparison_error}"

    def pytest_runtest_setup(self, item):  # noqa

        compare = self.get_compare(item)

        if compare is None:
            return

        import matplotlib.pyplot as plt
        try:
            from matplotlib.testing.decorators import remove_ticks_and_titles
        except ImportError:
            from matplotlib.testing.decorators import ImageComparisonTest as MplImageComparisonTest
            remove_ticks_and_titles = MplImageComparisonTest.remove_text

        style = compare.kwargs.get('style', 'classic')
        remove_text = compare.kwargs.get('remove_text', False)
        backend = compare.kwargs.get('backend', 'agg')

        original = item.function

        @wraps(item.function)
        def item_function_wrapper(*args, **kwargs):

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

                # What we do now depends on whether we are generating the
                # reference images or simply running the test.
                if self.generate_dir is not None:
                    self.generate_baseline_image(item, fig)

                if self.generate_hash_library is not None:
                    hash_name = self.generate_test_name(item)
                    self._generated_hash_library[hash_name] = self.generate_image_hash(item, fig)

                # Only test figures if we are not generating hashes or images
                if self.generate_dir is None and self.generate_hash_library is None:
                    result_dir = self.make_test_results_dir(item)

                    # Compare to hash library
                    if self.hash_library or compare.kwargs.get('hash_library', None):
                        msg = self.compare_image_to_hash_library(item, fig, result_dir)

                    # Compare against a baseline if specified
                    else:
                        msg = self.compare_image_to_baseline(item, fig, result_dir)

                    close_mpl_figure(fig)

                    if msg is None:
                        shutil.rmtree(result_dir)
                    else:
                        pytest.fail(msg, pytrace=False)

                close_mpl_figure(fig)

        if item.cls is not None:
            setattr(item.cls, item.function.__name__, item_function_wrapper)
        else:
            item.obj = item_function_wrapper

    def generate_summary_html(self, dir_list):
        """
        Generate a simple HTML table of the failed test results
        """
        html_file = self.results_dir / 'fig_comparison.html'
        with open(html_file, 'w') as f:
            f.write(HTML_INTRO)

            for directory in dir_list:
                f.write('<tr>'
                        f'<td>{directory.parts[-1]}\n'
                        f'<td><img src="{directory / "baseline.png"}"></td>\n'
                        f'<td><img src="{directory / "result-failed-diff.png"}"></td>\n'
                        f'<td><img src="{directory / "result.png"}"></td>\n'
                        '</tr>\n\n')

            f.write('</table>\n')
            f.write('</body>\n')
            f.write('</html>')

        return html_file

    def pytest_unconfigure(self, config):
        """
        Save out the hash library at the end of the run.
        """
        if self.generate_hash_library is not None:
            hash_library_path = Path(config.rootdir) / self.generate_hash_library
            hash_library_path.parent.mkdir(parents=True, exist_ok=True)
            with open(hash_library_path, "w") as fp:
                json.dump(self._generated_hash_library, fp, indent=2)

        if self.generate_summary and self.generate_summary.lower() == 'html':
            # Generate a list of test directories
            dir_list = [p.relative_to(self.results_dir)
                        for p in self.results_dir.iterdir() if p.is_dir()]
            html_summary = self.generate_summary_html(dir_list)
            print(f"A summary of the failed tests can be found at: {html_summary}")


class FigureCloser:
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
