import os
import sys
import subprocess
from distutils.version import LooseVersion

import pytest
import matplotlib
import matplotlib.pyplot as plt

MPL_VERSION = LooseVersion(matplotlib.__version__)
MPL_LT_2 = LooseVersion(matplotlib.__version__) < LooseVersion("2.0")

baseline_dir = 'baseline'

if MPL_VERSION >= LooseVersion('2'):
    baseline_subdir = '2.0.x'
elif MPL_VERSION >= LooseVersion('1.5'):
    baseline_subdir = '1.5.x'

baseline_dir_local = os.path.join(baseline_dir, baseline_subdir)
baseline_dir_remote = 'http://matplotlib.github.io/pytest-mpl/' + baseline_subdir + '/'

WIN = sys.platform.startswith('win')


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local)
def test_succeeds():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_remote)
def test_succeeds_remote():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


# The following tries an invalid URL first (or at least a URL where the baseline
# image won't exist), but should succeed with the second mirror.
@pytest.mark.mpl_image_compare(baseline_dir='http://www.python.org,' + baseline_dir_remote,
                               filename='test_succeeds_remote.png')
def test_succeeds_faulty_mirror():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 3])
    return fig


class TestClass(object):

    @pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local)
    def test_succeeds(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot([1, 2, 3])
        return fig


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local, savefig_kwargs={'dpi': 30})
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


def test_fails(tmpdir):

    test_file = tmpdir.join('test.py').strpath
    with open(test_file, 'w') as f:
        f.write(TEST_FAILING)

    # If we use --mpl, it should detect that the figure is wrong
    code = subprocess.call('{0} -m pytest --mpl {1}'.format(sys.executable, test_file), shell=True)
    assert code != 0

    # If we don't use --mpl option, the test should succeed
    code = subprocess.call('{0} -m pytest {1}'.format(sys.executable, test_file), shell=True)
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


def test_output_dir(tmpdir):
    test_file = tmpdir.join('test.py').strpath
    with open(test_file, 'w') as f:
        f.write(TEST_OUTPUT_DIR)

    # When we run the test, we should get output images where we specify
    output_dir = tmpdir.join('test_output_dir').strpath
    code = subprocess.call('{0} -m pytest --mpl-results-path={1} --mpl {2}'.format(sys.executable, output_dir, test_file),
                           shell=True)

    assert code != 0
    assert os.path.exists(output_dir)

    # Listdir() is to get the random name that the output for the one test is written into
    assert os.path.exists(os.path.join(output_dir, os.listdir(output_dir)[0], 'test_output_dir.png'))


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


# TODO: We skip the following test on Windows since the first subprocess calls.
# This should be fixed in the long term, but is not critical since we already
# test this on Linux.


@pytest.mark.skipif("WIN")
def test_generate(tmpdir):

    test_file = tmpdir.join('test.py').strpath
    with open(test_file, 'w') as f:
        f.write(TEST_GENERATE)

    gen_dir = tmpdir.mkdir('spam').mkdir('egg').strpath

    # If we don't generate, the test will fail
    p = subprocess.Popen('{0} -m pytest --mpl {1}'.format(sys.executable, test_file), shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    assert b'Image file not found for comparison test' in p.stdout.read()

    # If we do generate, the test should succeed and a new file will appear
    code = subprocess.call('{0} -m pytest --mpl-generate-path={1} {2}'.format(sys.executable, gen_dir, test_file), shell=True)
    assert code == 0
    assert os.path.exists(os.path.join(gen_dir, 'test_gen.png'))


@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local, tolerance=20)
def test_tolerance():
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2, 2])
    return fig


def test_nofigure():
    pass


@pytest.mark.skipif(MPL_LT_2, reason="the fivethirtyeight style is only available in Matplotlib 2.0 and later")
@pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                               style='fivethirtyeight')
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
    ax.scatter([1,3,4,3,2],[1,4,3,3,1], s=s)
    return fig


class TestClassWithSetup(object):

    # Regression test for a bug that occurred when using setup_method

    def setup_method(self, method):
        self.x = [1, 2, 3]

    @pytest.mark.mpl_image_compare(baseline_dir=baseline_dir_local,
                                   filename='test_succeeds.png')
    def test_succeeds(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(self.x)
        return fig
