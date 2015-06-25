import os
import subprocess

import pytest
import matplotlib.pyplot as plt

@pytest.mark.mpl_image_compare
def test_succeeds():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3])
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

def test_generate(tmpdir):

    test_file = tmpdir.join('test.py').strpath
    with open(test_file, 'w') as f:
        f.write(TEST_GENERATE)

    gen_dir = tmpdir.join('spam').join('egg').strpath
    print(gen_dir)

    # If we don't generate, the test will fail
    output = subprocess.check_output('py.test --mpl {0}; exit 0'.format(test_file), shell=True)
    assert b'Image file not found for comparison test' in output

    # If we do generate, the test should succeed and a new file will appear
    code = subprocess.call('py.test --mpl-generate-path={0} {1}'.format(gen_dir, test_file), shell=True)
    assert code == 0
    assert os.path.exists(os.path.join(gen_dir, 'test_gen.png'))


@pytest.mark.mpl_image_compare(tolerance=20)
def test_tolerance():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,2])
    return fig

def test_nofigure():
    pass
