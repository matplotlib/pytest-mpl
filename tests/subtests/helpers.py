import re
import json
from pathlib import Path

__all__ = ['diff_summary', 'assert_existence', 'replace_baseline_hash', 'patch_summary']


class MatchError(Exception):
    pass


def diff_summary(baseline, result, hash_library=None):
    """Diff a pytest-mpl summary dictionary."""
    if hash_library and hash_library.exists():
        # Load "correct" baseline hashes
        with open(hash_library, 'r') as f:
            hash_library = json.load(f)

    # Get test names
    baseline_tests = set(baseline.keys())
    result_tests = set(result.keys())

    # Test names must be identical
    diff_set(baseline_tests, result_tests, error='Test names are not identical.')

    item_match_errors = []  # Raise a MatchError for all mismatched values at the end

    for test in baseline_tests:

        # Get baseline and result summary for the specific test
        baseline_summary = baseline[test]
        result_summary = result[test]

        # Swap the baseline hashes in the summary for the baseline hashes in the hash library
        if hash_library:
            baseline_summary = replace_baseline_hash(baseline_summary, hash_library[test])

        # Get keys of recorded items
        baseline_keys = set(baseline_summary.keys())
        result_keys = set(result_summary.keys())

        # Summaries must have the same keys
        diff_set(baseline_keys, result_keys, error=f'Summary for {test} is not identical.')

        for key in baseline_keys:
            error = f'Summary item {key} for {test} does not match.\n'
            try:
                diff_dict_item(baseline_summary[key], result_summary[key], error=error)
            except MatchError as e:
                item_match_errors.append(str(e))

    if len(item_match_errors) > 0:
        raise MatchError('\n\n----------\n\n'.join(item_match_errors))


def diff_set(baseline, result, error=''):
    """Raise and show the difference between Python sets."""
    if baseline != result:
        missing_from_result = baseline - result
        missing_from_baseline = result - baseline
        if len(missing_from_result) > 0:
            error += f'\nKeys {sorted(missing_from_result)} missing from the result.'
        if len(missing_from_baseline) > 0:
            error += f'\nKeys {sorted(missing_from_baseline)} missing from the baseline.'
        raise MatchError(error)


def diff_dict_item(baseline, result, error=''):
    """Diff a specific item in a pytest-mpl summary dictionary."""
    # Comparison makes the following (good) assumptions
    expected_types = (str, int, float, bool, type(None))
    assert isinstance(baseline, expected_types)
    assert isinstance(result, expected_types)

    # Prepare error message
    error += f'Baseline:\n"{baseline}"\n\n'
    error += f'Result:\n"{result}"\n'

    # Matching items must have the same type
    if type(baseline) is not type(result):
        raise MatchError(error + '\nTypes are not equal.\n')

    # Handle regex in baseline string (so things like paths can be ignored)
    if isinstance(baseline, str) and baseline.startswith('REGEX:'):
        if re.fullmatch(baseline[6:], result) is not None:
            return

    # Handle bool and NoneType
    if isinstance(baseline, (bool, type(None))) and baseline is result:
        return

    # Handle str, int and float
    if baseline == result:
        return

    raise MatchError(error)


def patch_summary(summary, patch_file):
    """Replace in `summary` any items defined in `patch_file`."""
    # By only applying patches, changes between MPL versions are more obvious.
    with open(patch_file, 'r') as f:
        patch = json.load(f)
    for test, test_summary in patch.items():
        for k, v in test_summary.items():
            summary[test][k] = v
    return summary


def replace_baseline_hash(summary, new_baseline):
    """Replace a baseline hash in a pytest-mpl summary with a different baseline.

    Result hashes which match the existing baseline are also updated.

    Parameters
    ----------
    summary : dict
        A single test from a pytest-mpl summary.
    new_baseline : str
        The new baseline.
    """
    assert isinstance(new_baseline, str)
    old_baseline = summary['baseline_hash']
    if not isinstance(old_baseline, str) or old_baseline == new_baseline:
        return summary  # Either already correct or missing

    # If the old result hash matches the old baseline hash, also update the result hash
    old_result = summary['result_hash']
    if isinstance(old_result, str) and old_result == old_baseline:
        summary['result_hash'] = new_baseline

    # Update the baseline hash
    summary['baseline_hash'] = new_baseline
    summary['status_msg'] = summary['status_msg'].replace(old_baseline, new_baseline)

    return summary


def assert_existence(summary, items=('baseline_image', 'diff_image', 'result_image'), path=''):
    """Assert that images included in a pytest-mpl summary exist.

    Parameters
    ----------
    summary : dict
        The pytest-mpl summary dictionary to check.
    items : tuple or list, optional
        The image keys to check if reported.
    path : str or path_like, optional, default=''
        Path to results directory. Defaults to current directory.
    """
    for test in summary.values():
        for item in items:
            if test[item] is not None:
                assert (Path(path) / test[item]).exists()
