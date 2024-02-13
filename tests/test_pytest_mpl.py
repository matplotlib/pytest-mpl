import os
import sys
import json
import subprocess
from pathlib import Path
from unittest import TestCase

import matplotlib
import matplotlib.ft2font
import matplotlib.pyplot as plt
import pytest
from helpers import skip_if_format_unsupported
from packaging.version import Version

MPL_VERSION = Version(matplotlib.__version__)

baseline_dir = 'baseline'

if MPL_VERSION >= Version('2'):
    baseline_subdir = '2.0.x'

baseline_dir_local = os.path.join(baseline_dir, baseline_subdir)
baseline_dir_remote = 'http://matplotlib.github.io/pytest-mpl/' + baseline_subdir + '/'

ftv = matplotlib.ft2font.__freetype_version__.replace('.', '')
hash_filename = f"mpl{MPL_VERSION.major}{MPL_VERSION.minor}_ft{ftv}.json"

if "+" in matplotlib.__version__:
    hash_filename = "mpldev.json"

hash_library = (Path(__file__).parent / "baseline" /  # noqa
                "hashes" / hash_filename)

fail_hash_library = Path(__file__).parent / "baseline" / "test_hash_lib.json"
baseline_dir_abs = Path(__file__).parent / "baseline" / baseline_subdir
hash_baseline_dir_abs = Path(__file__).parent / "baseline" / "hybrid"


WIN = sys.platform.startswith('win')

# In some cases, the fonts on Windows can be quite different
DEFAULT_TOLERANCE = 10 if WIN else 2


def call_pytest(args):
    return subprocess.call([sys.executable, '-m', 'pytest', '-s'] + args)


def assert_pytest_fails_with(args, output_substring):
    try:
        subprocess.check_output([sys.executable, '-m', 'pytest', '-s'] + args)
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode()
        assert output_substring in output, output
        return output
    else:
        raise RuntimeError(f'pytest did not fail with args {args}')


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                               tolerance=DEFAULT_TOLERANCE)
def test_succeeds():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_remote,
                               tolerance=DEFAULT_TOLERANCE)
def test_succeeds_remote():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


# The following tries an invalid URL first (or at least a URL where the baseline
# image won't exist), but should succeed with the second mirror.
@pytest.mark.mpl_image_compare(baseline_dir='http://www.python.org,' + baseline_dir_remote,
                               filename='test_succeeds_remote.png',
                               tolerance=DEFAULT_TOLERANCE)
def test_succeeds_faulty_mirror():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


class TestClass(object):

    @pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                                   tolerance=DEFAULT_TOLERANCE)
    def test_succeeds(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot([1, 2, 3])
        return fig


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                               savefig_kwargs={'dpi': 30},
                               tolerance=DEFAULT_TOLERANCE)
def test_dpi():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


TEST_FAILING = """
import pytest
import matplotlib.pyplot as plt
@pytest.mark.mpl_image_compare
def test_fail():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,2])
    return fig
"""


def test_fails(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text(TEST_FAILING)
    test_file = str(test_file)

    # If we use --mpl, it should detect that the figure is wrong
    code = call_pytest(['--mpl', test_file])
    assert code != 0

    # If we don't use --mpl option, the test should succeed
    code = call_pytest([test_file])
    assert code == 0


TEST_OUTPUT_DIR = """
import pytest
import matplotlib.pyplot as plt
@pytest.mark.mpl_image_compare
def test_output_dir():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig
"""


def test_output_dir(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text(TEST_OUTPUT_DIR)

    output_dir = tmp_path / "test_output_dir"

    # When we run the test, we should get output images where we specify
    code = call_pytest([f'--mpl-results-path={output_dir}',
                        '--mpl', str(test_file)])

    assert code != 0
    assert output_dir.exists()
    assert (output_dir / "test.test_output_dir" / "result.png").exists()


TEST_GENERATE = """
import pytest
import matplotlib.pyplot as plt
@pytest.mark.mpl_image_compare
def test_gen():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3])
    return fig
"""


def test_generate(tmp_path):

    test_file = tmp_path / "test.py"
    test_file.write_text(TEST_GENERATE)
    test_file = str(test_file)

    gen_dir = tmp_path / "spam" / "egg"
    gen_dir.mkdir(parents=True)

    # If we don't generate, the test will fail
    assert_pytest_fails_with(['--mpl', test_file], 'Image file not found for comparison test')

    # If we do generate, the test should succeed and a new file will appear
    code = call_pytest([f'--mpl-generate-path={gen_dir}', test_file])
    assert code == 0
    assert os.path.exists(os.path.join(gen_dir, 'test_gen.png'))

    # If we do generate hash, the test will fail as no image is present
    hash_file = os.path.join(gen_dir, 'test_hashes.json')
    code = call_pytest([f'--mpl-generate-hash-library={hash_file}', test_file])
    assert code == 1
    assert os.path.exists(hash_file)

    with open(hash_file) as fp:
        hash_lib = json.load(fp)

    assert "test.test_gen" in hash_lib


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local, tolerance=20)
def test_tolerance():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 2])
    return fig


def test_nofigure():
    pass


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                               style='fivethirtyeight',
                               tolerance=DEFAULT_TOLERANCE)
def test_base_style():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                               remove_text=True)
def test_remove_text():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


@pytest.mark.parametrize('s', [5, 50, 500])
@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                               remove_text=True)
def test_parametrized(s):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter([1, 3, 4, 3, 2], [1, 4, 3, 3, 1], s=s)
    return fig


class TestClassWithSetup:

    # Regression test for a bug that occurred when using setup_method

    def setup_method(self, method):
        self.x = [1, 2, 3]

    @pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                                   filename='test_succeeds.png',
                                   tolerance=DEFAULT_TOLERANCE)
    def test_succeeds(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.x)
        return fig


class TestClassWithTestCase(TestCase):

    # Regression test for a bug that occurred when using unittest.TestCase

    def setUp(self):
        self.x = [1, 2, 3]

    @pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                                   filename='test_succeeds.png',
                                   tolerance=DEFAULT_TOLERANCE)
    def test_succeeds(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.x)
        return fig


# hashlib

@pytest.mark.skipif(not hash_library.exists(), reason="No hash library for this mpl version")
@pytest.mark.mpl_image_compare(hash_library=hash_library, deterministic=True)
def test_hash_succeeds():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


TEST_FAILING_HASH = rf"""
import pytest
import matplotlib.pyplot as plt
@pytest.mark.mpl_image_compare(hash_library=r"{fail_hash_library}", deterministic=True)
def test_hash_fails():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,2])
    return fig
"""


def test_hash_fails(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text(TEST_FAILING_HASH, encoding="ascii")
    test_file = str(test_file)

    # If we use --mpl, it should detect that the figure is wrong
    output = assert_pytest_fails_with(['--mpl', test_file], "doesn't match hash FAIL in library")
    # We didn't specify a baseline dir so we shouldn't attempt to find one
    assert "Image file not found for comparison test" not in output, output

    # Check that the summary path is printed and that it exists.
    output = assert_pytest_fails_with(['--mpl', test_file, '--mpl-generate-summary=html'],
                                      "doesn't match hash FAIL in library")
    # We didn't specify a baseline dir so we shouldn't attempt to find one
    print_message = "A summary of test results can be found at:"
    assert print_message in output, output
    printed_path = Path(output.split(print_message)[1].strip())
    assert printed_path.exists()

    # If we don't use --mpl option, the test should succeed
    code = call_pytest([test_file])
    assert code == 0


TEST_FAILING_HYBRID = rf"""
import pytest
import matplotlib.pyplot as plt
@pytest.mark.mpl_image_compare(hash_library=r"{fail_hash_library}",
                               tolerance=2, deterministic=True)
def test_hash_fail_hybrid():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3])
    return fig
"""


@pytest.mark.skipif(ftv != '261', reason="Incorrect freetype version for hash check")
def test_hash_fail_hybrid(tmp_path):

    test_file = tmp_path / "test.py"
    test_file.write_text(TEST_FAILING_HYBRID, encoding="ascii")
    test_file = str(test_file)

    # Assert that image comparison runs and fails
    output = assert_pytest_fails_with(['--mpl', test_file,
                                       rf'--mpl-baseline-path={hash_baseline_dir_abs / "fail"}'],
                                      "doesn't match hash FAIL in library")
    assert "Error: Image files did not match." in output, output

    # Assert reports missing baseline image
    output = assert_pytest_fails_with(['--mpl', test_file,
                                       '--mpl-baseline-path=/not/a/path'],
                                      "doesn't match hash FAIL in library")
    assert "Image file not found for comparison test" in output, output

    # Assert reports image comparison succeeds
    output = assert_pytest_fails_with(['--mpl', test_file,
                                       rf'--mpl-baseline-path={hash_baseline_dir_abs / "succeed"}'],
                                      "doesn't match hash FAIL in library")
    assert "The comparison to the baseline image succeeded." in output, output

    # If we don't use --mpl option, the test should succeed
    code = call_pytest([test_file])
    assert code == 0


TEST_FAILING_NEW_HASH = r"""
import pytest
import matplotlib.pyplot as plt
@pytest.mark.mpl_image_compare
def test_hash_fails():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,2])
    return fig
"""


@pytest.mark.skipif(ftv != '261', reason="Incorrect freetype version for hash check")
def test_hash_fail_new_hashes(tmp_path):
    # Check that the hash comparison fails even if a new hash file is requested
    test_file = tmp_path / "test.py"
    test_file.write_text(TEST_FAILING_NEW_HASH, encoding="ascii")
    test_file = str(test_file)

    # Assert that image comparison runs and fails
    assert_pytest_fails_with(['--mpl', test_file,
                              f'--mpl-hash-library={fail_hash_library}'],
                             "doesn't match hash FAIL in library")

    hash_file = tmp_path / "new_hashes.json"
    # Assert that image comparison runs and fails
    assert_pytest_fails_with(['--mpl', test_file,
                              f'--mpl-hash-library={fail_hash_library}',
                              f'--mpl-generate-hash-library={hash_file}'],
                             "doesn't match hash FAIL")


TEST_MISSING_HASH = """
import pytest
import matplotlib.pyplot as plt
@pytest.mark.mpl_image_compare
def test_hash_missing():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,2])
    return fig
"""


def test_hash_missing(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text(TEST_MISSING_HASH)
    test_file = str(test_file)

    # Assert fails if hash library missing
    assert_pytest_fails_with(['--mpl', test_file, '--mpl-hash-library=/not/a/path'],
                             "Can't find hash library at path")

    # Assert fails if hash not in library
    assert_pytest_fails_with(['--mpl', test_file, f'--mpl-hash-library={fail_hash_library}'],
                             "Hash for test 'test.test_hash_missing' not found in")

    # If we don't use --mpl option, the test should succeed
    code = call_pytest([test_file])
    assert code == 0


TEST_RESULTS_ALWAYS = """
import pytest
import matplotlib.pyplot as plt
def plot():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,2])
    return fig
@pytest.mark.mpl_image_compare(deterministic=True)
def test_modified(): return plot()
@pytest.mark.mpl_image_compare(deterministic=True)
def test_new(): return plot()
@pytest.mark.mpl_image_compare(deterministic=True)
def test_unmodified(): return plot()
"""


@pytest.mark.skipif(not hash_library.exists(), reason="No hash library for this mpl version")
def test_results_always(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text(TEST_RESULTS_ALWAYS)
    results_path = tmp_path / "results"
    results_path.mkdir()

    code = call_pytest(['--mpl', str(test_file), '--mpl-results-always',
                        rf'--mpl-hash-library={hash_library}',
                        rf'--mpl-baseline-path={baseline_dir_abs}',
                        '--mpl-generate-summary=html,json,basic-html',
                        rf'--mpl-results-path={results_path}'])
    assert code == 0  # hashes correct, so all should pass

    # assert files for interactive HTML exist
    assert (results_path / "fig_comparison.html").exists()
    assert (results_path / "styles.css").exists()
    assert (results_path / "extra.js").exists()

    html = (results_path / "fig_comparison_basic.html").read_text()
    with (results_path / "results.json").open("r") as f:
        json_results = json.load(f)

    # each test, and which images should exist
    for test, exists in [
        ('test_modified', ['baseline', 'result-failed-diff', 'result']),
        ('test_new', ['result']),
        ('test_unmodified', ['baseline', 'result']),
    ]:

        test_name = f'test.{test}'

        summary = f'<div class="test-name">{test_name.split(".")[-1]}</div>'
        assert summary in html

        assert test_name in json_results.keys()
        json_res = json_results[test_name]
        assert json_res['status'] == 'passed'

        for image_type in ['baseline', 'result-failed-diff', 'result']:
            image = f'{test_name}/{image_type}.png'
            image_exists = (results_path / image).exists()
            json_image_key = f"{image_type.split('-')[-1]}_image"
            if image_type in exists:  # assert image so pytest prints it on error
                assert image and image_exists
                assert image in html
                assert json_res[json_image_key] == image
            else:
                assert image and not image_exists
                assert image not in html
                assert json_res[json_image_key] is None


TEST_FAILING_CLASS = """
import pytest
import matplotlib.pyplot as plt
class TestClass(object):
    @pytest.mark.mpl_image_compare
    def test_fails(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot([1, 2, 3])
        return fig
"""

TEST_FAILING_CLASS_SETUP_METHOD = """
import pytest
import matplotlib.pyplot as plt
class TestClassWithSetup:
    def setup_method(self, method):
        self.x = [1, 2, 3]
    @pytest.mark.mpl_image_compare
    def test_fails(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.x)
        return fig
"""

TEST_FAILING_UNITTEST_TESTCASE = """
from unittest import TestCase
import pytest
import matplotlib.pyplot as plt
class TestClassWithTestCase(TestCase):
    def setUp(self):
        self.x = [1, 2, 3]
    @pytest.mark.mpl_image_compare
    def test_fails(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.x)
        return fig
"""


@pytest.mark.parametrize("code", [
    TEST_FAILING_CLASS,
    TEST_FAILING_CLASS_SETUP_METHOD,
    TEST_FAILING_UNITTEST_TESTCASE,
])
def test_class_fail(code, tmp_path):

    test_file = tmp_path / "test.py"
    test_file.write_text(code)
    test_file = str(test_file)

    # Assert fails if hash library missing
    assert_pytest_fails_with(['--mpl', test_file, '--mpl-hash-library=/not/a/path'],
                             "Can't find hash library at path")

    # If we don't use --mpl option, the test should succeed
    code = call_pytest([test_file])
    assert code == 0


@pytest.mark.parametrize("runpytest_args", [(), ("--mpl",)])
def test_user_fail(pytester, runpytest_args):
    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.mpl_image_compare
        def test_fail():
            pytest.fail("Manually failed by user.")
    """
    )
    result = pytester.runpytest(*runpytest_args)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines("FAILED*Manually failed by user.*")


@pytest.mark.parametrize("runpytest_args", [(), ("--mpl",)])
def test_user_skip(pytester, runpytest_args):
    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.mpl_image_compare
        def test_skip():
            pytest.skip("Manually skipped by user.")
    """
    )
    result = pytester.runpytest(*runpytest_args)
    result.assert_outcomes(skipped=1)


@pytest.mark.parametrize("runpytest_args", [(), ("--mpl",)])
def test_user_importorskip(pytester, runpytest_args):
    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.mpl_image_compare
        def test_importorskip():
            pytest.importorskip("nonexistantmodule")
    """
    )
    result = pytester.runpytest(*runpytest_args)
    result.assert_outcomes(skipped=1)


@pytest.mark.parametrize("runpytest_args", [(), ("--mpl",)])
def test_user_xfail(pytester, runpytest_args):
    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.mpl_image_compare
        def test_xfail():
            pytest.xfail()
    """
    )
    result = pytester.runpytest(*runpytest_args)
    result.assert_outcomes(xfailed=1)


@pytest.mark.parametrize("runpytest_args", [(), ("--mpl",)])
def test_user_exit_success(pytester, runpytest_args):
    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.mpl_image_compare
        def test_exit_success():
            pytest.exit("Manually exited by user.", returncode=0)
    """
    )
    result = pytester.runpytest(*runpytest_args)
    result.assert_outcomes()
    assert result.ret == 0
    result.stdout.fnmatch_lines("*Exit*Manually exited by user.*")


@pytest.mark.parametrize("runpytest_args", [(), ("--mpl",)])
def test_user_exit_failure(pytester, runpytest_args):
    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.mpl_image_compare
        def test_exit_fail():
            pytest.exit("Manually exited by user.", returncode=1)
    """
    )
    result = pytester.runpytest(*runpytest_args)
    result.assert_outcomes()
    assert result.ret == 1
    result.stdout.fnmatch_lines("*Exit*Manually exited by user.*")


@pytest.mark.parametrize("runpytest_args", [(), ("--mpl",)])
def test_user_function_raises(pytester, runpytest_args):
    pytester.makepyfile(
        """
        import pytest
        @pytest.mark.mpl_image_compare
        def test_raises():
            raise ValueError("User code raised an exception.")
    """
    )
    result = pytester.runpytest(*runpytest_args)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines("FAILED*ValueError*User code*")


@pytest.mark.parametrize('use_hash_library', (False, True))
@pytest.mark.parametrize('passes', (False, True))
@pytest.mark.parametrize("file_format", ['eps', 'pdf', 'png', 'svg'])
def test_formats(pytester, use_hash_library, passes, file_format):
    """
    Note that we don't test all possible formats as some do not compress well
    and would bloat the baseline directory.
    """
    skip_if_format_unsupported(file_format, using_hashes=use_hash_library)
    if use_hash_library and not hash_library.exists():
        pytest.skip("No hash library for this mpl version")

    pytester.makepyfile(
        f"""
        import os
        import pytest
        import matplotlib.pyplot as plt
        @pytest.mark.mpl_image_compare(baseline_dir=r"{baseline_dir_abs}",
                                       {f'hash_library=r"{hash_library}",' if use_hash_library else ''}
                                       tolerance={DEFAULT_TOLERANCE},
                                       deterministic=True,
                                       savefig_kwargs={{'format': '{file_format}'}})
        def test_format_{file_format}():
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot([{1 if passes else 3}, 2, 3])
            return fig
        """
    )
    result = pytester.runpytest('--mpl', '-rs')
    if passes:
        result.assert_outcomes(passed=1)
    else:
        result.assert_outcomes(failed=1)
