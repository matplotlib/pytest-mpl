import os
import sys
import json
import subprocess
from pathlib import Path
from unittest import TestCase

import matplotlib
import matplotlib.pyplot as plt
import pytest
from helpers import skip_if_format_unsupported

baseline_dir = 'baseline'
baseline_subdir = '2.0.x'

baseline_dir_local = os.path.join(baseline_dir, baseline_subdir)
baseline_dir_remote = 'http://matplotlib.github.io/pytest-mpl/' + baseline_subdir + '/'

baseline_dir_abs = Path(__file__).parent / "baseline" / baseline_subdir


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
def test_formats(pytester, tmp_path, use_hash_library, passes, file_format):
    """
    Note that we don't test all possible formats as some do not compress well
    and would bloat the baseline directory.
    """
    skip_if_format_unsupported(file_format, using_hashes=use_hash_library)

    tmp_hash_library = tmp_path / f"hash_library_{file_format}.json"
    tmp_hash_library.write_text("{}")

    pytester.makepyfile(
        f"""
        import os
        import pytest
        import matplotlib.pyplot as plt
        @pytest.mark.mpl_image_compare(baseline_dir=r"{baseline_dir_abs}",
                                       {f'hash_library=r"{tmp_hash_library}",' if use_hash_library else ''}
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

    if use_hash_library:
        pytester.runpytest(f'--mpl-generate-hash-library={tmp_hash_library.as_posix()}', '-rs')
        hash_data = json.loads(tmp_hash_library.read_text())
        assert len(hash_data[f"test_formats.test_format_{file_format}"]) == 64
        if not passes:
            hash_data[f"test_formats.test_format_{file_format}"] = (
                "d1ff" + hash_data[f"test_formats.test_format_{file_format}"][4:]
            )
            tmp_hash_library.write_text(json.dumps(hash_data))

    result = pytester.runpytest('--mpl', '-rs')
    if passes:
        result.assert_outcomes(passed=1)
    else:
        result.assert_outcomes(failed=1)


def test_hash_method_phash(pytester, tmp_path):
    imagehash = pytest.importorskip("imagehash")
    try:
        from PIL import Image
        imagehash.phash(Image.new("L", (8, 8)))
    except Exception as exc:
        pytest.skip(f"imagehash.phash not available: {exc}")

    tmp_hash_library = tmp_path / "hash_library_phash.json"
    tmp_hash_library.write_text("{}")

    pytester.makepyfile(
        f"""
        import pytest
        import matplotlib.pyplot as plt

        @pytest.mark.mpl_image_compare(baseline_dir=r"{baseline_dir_abs}",
                                       hash_library=r"{tmp_hash_library}",
                                       hash_method="phash",
                                       deterministic=True,
                                       savefig_kwargs={{'format': 'png'}})
        def test_format_phash():
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot([1, 2, 3])
            return fig
        """
    )

    pytester.runpytest(f'--mpl-generate-hash-library={tmp_hash_library.as_posix()}', '-rs')
    hash_data = json.loads(tmp_hash_library.read_text())
    assert len(hash_data["test_hash_method_phash.test_format_phash"]) == 16
