import os
import sys
import subprocess
import tempfile
from distutils.version import LooseVersion

import pytest
import matplotlib
import matplotlib.pyplot as plt

MPL_VERSION = LooseVersion(matplotlib.__version__)

baseline_dir = 'baseline'

if MPL_VERSION >= LooseVersion('1.5.0'):
    baseline_subdir = '1.5.x'
else:
    baseline_subdir = '1.4.x'

baseline_dir_local = os.path.join(baseline_dir, baseline_subdir)
baseline_dir_remote = 'http://astrofrog.github.io/pytest-mpl/' + baseline_subdir + '/'

PY26 = sys.version_info[:2] == (2, 6)

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


def test_fails():

    tmpdir = tempfile.mkdtemp()

    test_file = os.path.join(tmpdir, 'test.py')
    with open(test_file, 'w') as f:
        f.write(TEST_FAILING)

    # If we use --mpl, it should detect that the figure is wrong
    code = subprocess.call('py.test --mpl {0}'.format(test_file), shell=True)
    assert code != 0

    # If we don't use --mpl option, the test should succeed
    code = subprocess.call('py.test {0}'.format(test_file), shell=True)
    assert code == 0


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


@pytest.mark.skipif("PY26")
def test_generate():

    tmpdir = tempfile.mkdtemp()

    test_file = os.path.join(tmpdir, 'test.py')
    with open(test_file, 'w') as f:
        f.write(TEST_GENERATE)

    gen_dir = os.path.join(tmpdir, 'spam', 'egg')

    # If we don't generate, the test will fail
    p = subprocess.Popen('py.test --mpl {0}'.format(test_file), shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    assert b'Image file not found for comparison test' in p.stdout.read()

    # If we do generate, the test should succeed and a new file will appear
    code = subprocess.call('py.test --mpl-generate-path={0} {1}'.format(gen_dir, test_file), shell=True)
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
