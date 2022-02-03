import re
from pathlib import Path

__all__ = ['diff_summary', 'assert_existence']


class MatchError(Exception):
    pass


def diff_summary(baseline, result):
    """Diff a pytest-mpl summary dictionary."""
    # Get test names
    baseline_tests = set(baseline.keys())
    result_tests = set(result.keys())

    # Test names must be identical
    diff_set(baseline_tests, result_tests, error='Test names are not identical.')

    for test in baseline_tests:

        # Get baseline and result summary for the specific test
        baseline_summary = baseline[test]
        result_summary = result[test]

        # Get keys of recorded items
        baseline_keys = set(baseline_summary.keys())
        result_keys = set(result_summary.keys())

        # Summaries must have the same keys
        diff_set(baseline_keys, result_keys, error=f'Summary for {test} is not identical.')

        for key in baseline_keys:
            error = f'Summary item {key} for {test} does not match.\n'
            diff_dict_item(baseline_summary[key], result_summary[key], error=error)


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
