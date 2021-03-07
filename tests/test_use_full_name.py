import os
import subprocess
import sys
import configparser
import json

TEST_FILE = """
import pytest
import matplotlib.pyplot as plt
@pytest.mark.mpl_image_compare
def test_plot():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,2])
    return fig
"""

def call_pytest(args, cwd):
    """Run python -m pytest -s [args] from cwd and return its output"""
    try:
        output = subprocess.check_output([sys.executable, '-m', 'pytest', '-s'] + args,
                                  cwd=cwd,
                           shell=False)
        return output.decode()
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode()
        return output


def make_ini_file(mpl_use_full_test_name, path):
    config = configparser.ConfigParser()
    config["tool:pytest"] = {"mpl-use-full-test-name": mpl_use_full_test_name}
    with open(os.path.join(path, 'setup.cfg'), 'w') as configfile:
        config.write(configfile)


def make_test_code_file(path, fname):
    with open(os.path.join(path, fname), "w") as f:
        f.write(TEST_FILE)

def make_test_subdir(pardir, subdir_name):
    sub_dir = pardir.mkdir(subdir_name)
    with open(os.path.join(sub_dir, "__init__.py"), "w") as f:
        pass
    return sub_dir


def test_success(tmpdir):
    basedir = tmpdir
    tests_basedir = make_test_subdir(basedir, "tests")
    subtest_dir1 = make_test_subdir(tests_basedir, "test_1")
    subtest_dir2 = make_test_subdir(tests_basedir, "test_2")
    # Create test files with identical names but in different test directories
    make_test_code_file(tests_basedir, "test_foo.py")
    make_test_code_file(subtest_dir1, "test_foo.py")
    make_test_code_file(subtest_dir2, "test_foo.py")
    make_ini_file(True, basedir)

    has_lib_file = os.path.join('mpl_generate_dir', "baseline_hashes.json")

    output1 = call_pytest(args=[f"--mpl-generate-hash-library",
                              has_lib_file,
                              "tests"],
                        cwd=basedir.strpath)
    output2 = call_pytest(args=["--mpl",
                              f"--mpl-hash-library",
                              has_lib_file,
                              "tests"],
                        cwd=basedir.strpath)
    assert "3 passed" in output1
    assert "3 passed" in output2

def test_missing_hash(tmpdir):
    basedir = tmpdir
    tests_basedir = make_test_subdir(basedir, "tests")
    subtest_dir1 = make_test_subdir(tests_basedir, "test_1")
    subtest_dir2 = make_test_subdir(tests_basedir, "test_2")
    make_test_code_file(tests_basedir, "test_foo.py")
    make_test_code_file(subtest_dir1, "test_foo.py")
    make_test_code_file(subtest_dir2, "test_foo.py")
    make_ini_file(True, basedir)

    has_lib_file = os.path.join('mpl_generate_dir', "baseline_hashes.json")

    output1 = call_pytest(args=[f"--mpl-generate-hash-library",
                              has_lib_file,
                              "tests"],
                        cwd=basedir.strpath)
    # Manually delete one entry from the hash lib
    with open(os.path.join(basedir, has_lib_file), "r") as handle:
        hash_lib = json.loads(handle.read())
    hash_lib.pop(list(hash_lib.keys())[0])
    with open(os.path.join(basedir, has_lib_file), "w") as handle:
        json.dump(hash_lib, handle)

    output2 = call_pytest(args=["--mpl",
                              f"--mpl-hash-library",
                              has_lib_file,
                              "tests"],
                        cwd=basedir.strpath)
    assert "3 passed" in output1
    assert "1 failed, 2 passed" in output2
    assert "Hash for test 'tests.test_foo.test_plot' not found" in output2.strip("\n")

def test_incorrect_hash(tmpdir):
    basedir = tmpdir
    tests_basedir = make_test_subdir(basedir, "tests")
    subtest_dir1 = make_test_subdir(tests_basedir, "test_1")
    subtest_dir2 = make_test_subdir(tests_basedir, "test_2")
    make_test_code_file(tests_basedir, "test_foo.py")
    make_test_code_file(subtest_dir1, "test_foo.py")
    make_test_code_file(subtest_dir2, "test_foo.py")
    make_ini_file(True, basedir)

    has_lib_file = os.path.join('mpl_generate_dir', "baseline_hashes.json")

    output1 = call_pytest(args=[f"--mpl-generate-hash-library",
                              has_lib_file,
                              "tests"],
                        cwd=basedir.strpath)
    # Manually delete one entry from the hash lib
    with open(os.path.join(basedir, has_lib_file), "r") as handle:
        hash_lib = json.loads(handle.read())
    hash_lib[list(hash_lib.keys())[0]] = 12345
    with open(os.path.join(basedir, has_lib_file), "w") as handle:
        json.dump(hash_lib, handle)

    output2 = call_pytest(args=["--mpl",
                              f"--mpl-hash-library",
                              has_lib_file,
                              "tests"],
                        cwd=basedir.strpath)
    assert "3 passed" in output1
    assert "1 failed, 2 passed" in output2
    assert "doesn't match hash 12345 in library" in output2.strip("\n")
