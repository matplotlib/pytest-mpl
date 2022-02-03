import sys
import json
import shutil
import subprocess
from pathlib import Path

from helpers import assert_existence, diff_summary

TEST_FILE = Path(__file__).parent / 'subtest.py'

# Set to True to replace existing baseline summaries with current result
UPDATE_BASELINE_SUMMARIES = True


def run_subtest(baseline_summary, tmp_path, args, summaries=None, xfail=True):
    """ Run pytest (within pytest) and check JSON summary report.

    Parameters
    ----------
    baseline_summary : str
        String of the filename without extension for the baseline summary.
    tmp_path : pathlib.Path
        Path of a temporary directory to store results.
    args : list
        Extra arguments to pass to pytest.
    summaries : tuple or list or set, optional, default=[]
        Summaries to generate in addition to `json`.
    xfail : bool, optional, default=True
        Whether the overall pytest run should fail.
    """
    # Parse arguments
    if summaries is None:
        summaries = []
    assert isinstance(summaries, (tuple, list, set))
    summaries = ','.join({'json'} | set(summaries))

    # Create the results path
    results_path = tmp_path / 'results'
    results_path.mkdir()

    # Configure the arguments to run the test
    pytest_args = [sys.executable, '-m', 'pytest', str(TEST_FILE)]
    mpl_args = ['--mpl', rf'--mpl-results-path={results_path.as_posix()}',
                f'--mpl-generate-summary={summaries}']

    # Run the test and record exit status
    status = subprocess.call(pytest_args + mpl_args + args)

    # Ensure exit status is as expected
    if xfail:
        assert status != 0
    else:
        assert status == 0

    # Load summaries
    baseline_path = Path(__file__).parent / 'summaries'
    baseline_file = baseline_path / (baseline_summary + '.json')
    with open(baseline_file, 'r') as f:
        baseline_summary = json.load(f)
    results_file = results_path / 'results.json'
    with open(results_file, 'r') as f:
        result_summary = json.load(f)

    if UPDATE_BASELINE_SUMMARIES:
        shutil.copy(results_file, baseline_file)

    # Compare summaries
    diff_summary(baseline_summary, result_summary)

    # Ensure reported images exist
    assert_existence(result_summary, path=results_path)
