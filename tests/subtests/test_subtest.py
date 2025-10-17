import os
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path

import matplotlib.ft2font
import pytest
from packaging.version import Version

from .helpers import (apply_regex, assert_existence, diff_summary, patch_summary,
                      remove_specific_hashes, transform_hashes, transform_images)

# Handle Matplotlib and FreeType versions
MPL_VERSION = Version(matplotlib.__version__)
FTV = matplotlib.ft2font.__freetype_version__.replace('.', '')
VERSION_ID = f"mpl{MPL_VERSION.major}{MPL_VERSION.minor}_ft{FTV}"
HASH_LIBRARY_FLAG = r'--mpl-hash-library={hash_library}'
FULL_BASELINE_PATH = Path(__file__).parent / 'subtest' / 'baseline'

BASELINE_IMAGES_FLAG_REL = ['--mpl-baseline-path=baseline', '--mpl-baseline-relative']
BASELINE_IMAGES_FLAG_ABS = rf'--mpl-baseline-path={FULL_BASELINE_PATH}'

IMAGE_COMPARISON_MODE = ["-k", "image"]
HASH_COMPARISON_MODE = ["-k", "hash"]
# HYBRID_MODE = []

TEST_FILE = Path(__file__).parent / 'subtest'

# Global settings to update baselines when running pytest
# Note: when updating baseline make sure you don't commit "fixes"
# for tests that are expected to fail
# (See also `run_subtest` argument `update_baseline` and `update_summary`.)
UPDATE_BASELINE = os.getenv("MPL_UPDATE_BASELINE") is not None  # baseline images and hashes
UPDATE_SUMMARY = os.getenv("MPL_UPDATE_SUMMARY") is not None  # baseline summaries

# When updating baseline summaries, replace parts of status_msg with regex.
# See helpers.apply_regex for more information.
REGEX_PATHS = [
    str(Path(__file__).parent),  # replace all references to baseline files
    os.path.realpath(tempfile.gettempdir()),  # replace all references to output files
]
REGEX_STRS = [
    r'RMS Value: ',
]


def run_subtest(baseline_summary_name, tmp_path, args, summaries=None, xfail=True,
                has_result_hashes=False, generating_hashes=False, testing_hashes=False, n_xdist_workers=None,
                update_baseline=UPDATE_BASELINE, update_summary=UPDATE_SUMMARY):
    """ Run pytest (within pytest) and check JSON summary report.

    Parameters
    ----------
    baseline_summary_name : str
        String of the filename without extension for the baseline summary.
    tmp_path : pathlib.Path
        Path of a temporary directory to store results.
    args : list
        Extra arguments to pass to pytest.
    summaries : tuple or list or set, optional, default=[]
        Summaries to generate in addition to `json`.
    xfail : bool, optional, default=True
        Whether the overall pytest run should fail.
    has_result_hashes : bool or str, optional, default=False
        Whether a hash library is expected to exist in the results directory.
        If a string, this is the name of the expected results file.
    generating_hashes : bool, optional, default=False
        Whether `--mpl-generate-hash-library` was specified and
        both of `--mpl-hash-library` and `hash_library=` were not.
    testing_hashes : bool, optional, default=False
        Whether the subtest is comparing hashes and therefore needs baseline hashes generated.
    n_xdist_workers : str or int, optional, default=None
        Number of xdist workers to use, or "auto" to use all available cores.
        None will disable xdist. If pytest-xdist is not installed, this will be ignored.
    """
    if update_baseline and update_summary:
        raise ValueError("Cannot enable both `update_baseline` and `update_summary`.")

    # Parse arguments
    if summaries is None:
        summaries = []
    assert isinstance(summaries, (tuple, list, set))
    summaries = ','.join({'json'} | set(summaries))

    # Create the results path
    results_path = tmp_path / 'results'
    results_path.mkdir()

    baseline_hash_library = tmp_path / 'hashes' / 'baseline.json'
    expected_result_hash_library = tmp_path / 'hashes' / 'expected_result.json'

    # Configure the arguments to run the test
    pytest_args = [sys.executable, '-m', 'pytest', str(TEST_FILE)]
    mpl_args = ['--mpl', rf'--mpl-results-path={results_path.as_posix()}',
                f'--mpl-generate-summary={summaries}']
    if update_baseline:
        mpl_args += [rf'--mpl-generate-path={FULL_BASELINE_PATH}']
    args = [
        HASH_LIBRARY_FLAG.format(hash_library=baseline_hash_library)
        if x == HASH_LIBRARY_FLAG else x
        for x in args
    ]

    if testing_hashes or has_result_hashes or generating_hashes:
        hash_gen_args = [f'--mpl-generate-hash-library={expected_result_hash_library}']
        if " ".join(HASH_COMPARISON_MODE) in " ".join(args):
            hash_gen_args += HASH_COMPARISON_MODE
        subprocess.call(pytest_args + hash_gen_args)
        shutil.copy(expected_result_hash_library, baseline_hash_library)
        transform_hashes(baseline_hash_library)

    try:
        import xdist
        if n_xdist_workers is None:
            pytest_args += ["-p", "no:xdist"]
        else:
            pytest_args += ["-n", str(n_xdist_workers)]
    except ImportError:
        pass

    # Run the test and record exit status
    status = subprocess.call(pytest_args + mpl_args + args)

    # If updating baseline, don't check summaries
    if update_baseline:
        assert status == 0
        transform_images(FULL_BASELINE_PATH)  # Make image comparison tests fail correctly
        pytest.skip("Skipping testing, since `update_baseline` is enabled.")
        return

    # Ensure exit status is as expected
    if xfail:
        assert status != 0
    else:
        assert status == 0

    # Load summaries
    baseline_path = Path(__file__).parent / 'summaries'
    baseline_file = baseline_path / (baseline_summary_name + '.json')
    results_file = results_path / 'results.json'
    if update_summary:
        shutil.copy(results_file, baseline_file)
        apply_regex(baseline_file, REGEX_PATHS, REGEX_STRS)
        remove_specific_hashes(baseline_file)
    with open(baseline_file, 'r') as f:
        baseline_summary = json.load(f)
    with open(results_file, 'r') as f:
        result_summary = json.load(f)

    # Apply version specific patches
    patch = baseline_path / (baseline_summary_name + f'_{VERSION_ID}.patch.json')
    if patch.exists():
        baseline_summary = patch_summary(baseline_summary, patch)
    # Note: version specific hashes should be handled by diff_summary instead

    # Compare summaries
    diff_summary(baseline_summary, result_summary,
                 baseline_hash_library=baseline_hash_library,
                 result_hash_library=expected_result_hash_library,
                 generating_hashes=generating_hashes)

    # Ensure reported images exist
    assert_existence(result_summary, path=results_path)

    # Get expected name for the hash library saved to the results directory
    if isinstance(has_result_hashes, str):
        result_hash_file = tmp_path / 'results' / has_result_hashes
        has_result_hashes = True  # convert to bool after processing str
    else:
        result_hash_file = tmp_path / 'results' / 'baseline.json'

    # Compare the generated hash library to the expected hash library
    if has_result_hashes:
        assert result_hash_file.exists()
        with open(expected_result_hash_library, "r") as f:
            baseline = json.load(f)
        with open(result_hash_file, "r") as f:
            result = json.load(f)

        # Baseline contains hashes for all subtests so remove ones not used
        for test in list(baseline.keys()):
            if test not in result:
                del baseline[test]

        diff_summary({'a': baseline}, {'a': result})
    else:
        assert not result_hash_file.exists()

    if update_summary:
        pytest.skip("Skipping testing, since `update_summary` is enabled.")


def test_default(tmp_path):
    run_subtest('test_default', tmp_path, [*IMAGE_COMPARISON_MODE])


def test_hash(tmp_path):
    run_subtest('test_hash', tmp_path,
                [HASH_LIBRARY_FLAG, *HASH_COMPARISON_MODE],
                testing_hashes=True)


def test_results_always(tmp_path):
    run_subtest('test_results_always', tmp_path,
                [HASH_LIBRARY_FLAG, BASELINE_IMAGES_FLAG_ABS, '--mpl-results-always'],
                has_result_hashes=True)


def test_html(tmp_path):
    run_subtest('test_results_always', tmp_path,
                [HASH_LIBRARY_FLAG, BASELINE_IMAGES_FLAG_ABS], summaries=['html'],
                has_result_hashes=True)
    html_path = tmp_path / 'results' / 'fig_comparison.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 200_000
    assert "Baseline image differs" in html_path.read_text()
    assert (tmp_path / 'results' / 'extra.js').exists()
    assert (tmp_path / 'results' / 'styles.css').exists()


@pytest.mark.parametrize("num_workers", [None, 0, 1, 2])
def test_html_xdist(request, tmp_path, num_workers):
    if not request.config.pluginmanager.hasplugin("xdist"):
        pytest.skip("Skipping: pytest-xdist is not installed")
    run_subtest('test_results_always', tmp_path,
                [HASH_LIBRARY_FLAG, BASELINE_IMAGES_FLAG_ABS], summaries=['html'],
                has_result_hashes=True, n_xdist_workers=num_workers)
    html_path = tmp_path / 'results' / 'fig_comparison.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 200_000
    assert "Baseline image differs" in html_path.read_text()
    assert (tmp_path / 'results' / 'extra.js').exists()
    assert (tmp_path / 'results' / 'styles.css').exists()
    if num_workers is not None:
        assert len(list((tmp_path / 'results').glob('generated-hashes-xdist-*-*.json'))) == 0
        assert len(list((tmp_path / 'results').glob('results-xdist-*-*.json'))) == num_workers


def test_html_hashes_only(tmp_path):
    run_subtest('test_html_hashes_only', tmp_path,
                [HASH_LIBRARY_FLAG, *HASH_COMPARISON_MODE],
                summaries=['html'], has_result_hashes=True)
    html_path = tmp_path / 'results' / 'fig_comparison.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 100_000
    assert "Baseline hash differs" in html_path.read_text()
    assert (tmp_path / 'results' / 'extra.js').exists()
    assert (tmp_path / 'results' / 'styles.css').exists()


def test_html_images_only(tmp_path):
    run_subtest('test_html_images_only', tmp_path, [*IMAGE_COMPARISON_MODE], summaries=['html'])
    html_path = tmp_path / 'results' / 'fig_comparison.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 200_000
    assert "Baseline image differs" in html_path.read_text()
    assert (tmp_path / 'results' / 'extra.js').exists()
    assert (tmp_path / 'results' / 'styles.css').exists()


def test_basic_html(tmp_path):
    run_subtest('test_results_always', tmp_path,
                [HASH_LIBRARY_FLAG, *BASELINE_IMAGES_FLAG_REL], summaries=['basic-html'],
                has_result_hashes=True)
    html_path = tmp_path / 'results' / 'fig_comparison_basic.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 20_000
    assert "hash comparison, although" in html_path.read_text()


def test_generate(tmp_path):
    # generating hashes and images; no testing
    run_subtest('test_generate', tmp_path,
                [rf'--mpl-generate-path={tmp_path}',
                 rf'--mpl-generate-hash-library={tmp_path / "test_hashes.json"}'],
                xfail=False, generating_hashes=True)


def test_generate_images_only(tmp_path):
    # generating images; no testing
    run_subtest('test_generate_images_only', tmp_path,
                [rf'--mpl-generate-path={tmp_path}', *IMAGE_COMPARISON_MODE], xfail=False)


def test_generate_hashes_only(tmp_path):
    # generating hashes; testing images
    run_subtest('test_generate_hashes_only', tmp_path,
                [rf'--mpl-generate-hash-library={tmp_path / "test_hashes.json"}'],
                generating_hashes=True)


def test_html_generate(tmp_path):
    # generating hashes and images; no testing
    run_subtest('test_html_generate', tmp_path,
                [rf'--mpl-generate-path={tmp_path}',
                 rf'--mpl-generate-hash-library={tmp_path / "test_hashes.json"}'],
                summaries=['html'], xfail=False, has_result_hashes="test_hashes.json",
                generating_hashes=True)
    html_path = tmp_path / 'results' / 'fig_comparison.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 100_000
    assert "Baseline image was generated" in html_path.read_text()


@pytest.mark.parametrize("num_workers", [None, 0, 1, 2])
def test_html_generate_xdist(request, tmp_path, num_workers):
    # generating hashes and images; no testing
    if not request.config.pluginmanager.hasplugin("xdist"):
        pytest.skip("Skipping: pytest-xdist is not installed")
    run_subtest('test_html_generate', tmp_path,
                [rf'--mpl-generate-path={tmp_path}',
                 rf'--mpl-generate-hash-library={tmp_path / "test_hashes.json"}'],
                summaries=['html'], xfail=False, has_result_hashes="test_hashes.json",
                generating_hashes=True, n_xdist_workers=num_workers)
    html_path = tmp_path / 'results' / 'fig_comparison.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 100_000
    assert "Baseline image was generated" in html_path.read_text()
    assert (tmp_path / 'results' / 'extra.js').exists()
    assert (tmp_path / 'results' / 'styles.css').exists()
    if num_workers is not None:
        assert len(list((tmp_path / 'results').glob('generated-hashes-xdist-*-*.json'))) == num_workers
        assert len(list((tmp_path / 'results').glob('results-xdist-*-*.json'))) == num_workers


def test_html_generate_images_only(tmp_path):
    # generating images; no testing
    run_subtest('test_html_generate_images_only', tmp_path,
                [rf'--mpl-generate-path={tmp_path}', *IMAGE_COMPARISON_MODE],
                summaries=['html'], xfail=False)
    html_path = tmp_path / 'results' / 'fig_comparison.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 100_000
    assert "Baseline image was generated" in html_path.read_text()


def test_html_generate_hashes_only(tmp_path):
    # generating hashes; testing images
    run_subtest('test_html_generate_hashes_only', tmp_path,
                [rf'--mpl-generate-hash-library={tmp_path / "test_hashes.json"}'],
                summaries=['html'], has_result_hashes="test_hashes.json", generating_hashes=True)
    html_path = tmp_path / 'results' / 'fig_comparison.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 200_000
    assert "Baseline hash was generated" in html_path.read_text()


def test_html_run_generate_hashes_only(tmp_path):
    # generating hashes; testing hashes
    run_subtest('test_html_hashes_only', tmp_path,
                [rf'--mpl-generate-hash-library={tmp_path / "test_hashes.json"}',
                 HASH_LIBRARY_FLAG, *HASH_COMPARISON_MODE],
                summaries=['html'], has_result_hashes="test_hashes.json")
    html_path = tmp_path / 'results' / 'fig_comparison.html'
    assert html_path.exists()
    assert html_path.stat().st_size > 100_000
    assert "Baseline hash differs" in html_path.read_text()


# Run a hybrid mode test last so if generating hash libraries, it includes all the hashes.
def test_hybrid(tmp_path):
    run_subtest('test_hybrid', tmp_path, [HASH_LIBRARY_FLAG, BASELINE_IMAGES_FLAG_ABS], testing_hashes=True)
