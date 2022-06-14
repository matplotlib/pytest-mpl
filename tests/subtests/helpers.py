import os
import re
import json
from pathlib import Path

from PIL import Image, ImageDraw

__all__ = ['diff_summary', 'assert_existence', 'patch_summary', 'apply_regex',
           'remove_specific_hashes', 'transform_hashes', 'transform_images']


class MatchError(Exception):
    pass


def diff_summary(baseline, result, baseline_hash_library=None, result_hash_library=None,
                 generating_hashes=False):
    """Diff a pytest-mpl summary dictionary.

    Parameters
    ----------
    baseline : dict
        Baseline pytest-mpl summary.
    result : dict
        Generated result pytest-mpl summary.
    baseline_hash_library : Path, optional, default=None
        Path to the baseline hash library.
        Baseline hashes in the baseline summary are updated to these values
        to handle different Matplotlib versions.
    result_hash_library : Path, optional, default=None
        Path to the "baseline" image hash library.
        Result hashes in the baseline summary are updated to these values
        to handle different Matplotlib versions.
    generating_hashes : bool, optional, default=False
        Whether `--mpl-generate-hash-library` was specified and
        both of `--mpl-hash-library` and `hash_library=` were not.
    """
    if baseline_hash_library and baseline_hash_library.exists():
        # Load "correct" baseline hashes
        with open(baseline_hash_library, 'r') as f:
            baseline_hash_library = json.load(f)
    else:
        baseline_hash_library = {}
    if result_hash_library and result_hash_library.exists():
        # Load "correct" result hashes
        with open(result_hash_library, 'r') as f:
            result_hash_library = json.load(f)
    else:
        result_hash_library = {}

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

        # Swap the baseline and result hashes in the summary
        # for the corresponding hashes in each hash library
        if baseline_hash_library and test in baseline_hash_library and not generating_hashes:
            baseline_summary = replace_hash(baseline_summary, 'baseline_hash',
                                            baseline_hash_library[test])
        if result_hash_library:
            if generating_hashes:  # Newly generate result will appear as baseline_hash
                baseline_summary = replace_hash(baseline_summary, 'baseline_hash',
                                                result_hash_library[test])
            baseline_summary = replace_hash(baseline_summary, 'result_hash',
                                            result_hash_library[test])

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

    # Handle float
    if isinstance(baseline, float) and abs(baseline - result) < 1e-4:
        return

    # Handle str and int
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


def replace_hash(summary, hash_key, new_hash):
    """Replace a hash in a pytest-mpl summary with a different hash.

    Parameters
    ----------
    summary : dict
        A single test from a pytest-mpl summary.
    hash_key : str
        Key of the hash. Either `baseline_hash` or `result_hash`.
    new_hash : str
        The new hash.
    """
    assert isinstance(new_hash, str)
    old_hash = summary[hash_key]
    if not isinstance(old_hash, str) or old_hash == new_hash:
        return summary  # Either already correct or missing

    # Update the hash
    summary[hash_key] = new_hash
    summary['status_msg'] = summary['status_msg'].replace(old_hash, new_hash)

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


def _escape_regex(msg):
    if not msg.startswith('REGEX:'):
        msg = msg.replace('.', r'\.').replace('(', r'\(').replace(')', r'\)')
        msg = 'REGEX:' + msg
    return msg


def _escape_path(msg, path):
    pattern = (rf"({path}[A-Za-z0-9_\-\/.\\]*)" +
               r"(baseline\\.png|result-failed-diff\\.png|result\\.png|\\.json)")
    msg = re.sub(pattern, r".*\2", msg)
    pattern = rf"({path}[A-Za-z0-9_\-\/.\\]*)"
    msg = re.sub(pattern, r".*", msg)
    return msg


def _escape_float(msg, key):
    pattern = rf"({key}[0-9]+\\\.[0-9]{{1}})([0-9]+)"
    msg = re.sub(pattern, r"\1[0-9]*", msg)
    return msg


def apply_regex(file, regex_paths, regex_strs):
    """Convert all `status_msg` entries in JSON summary file to regex.

    Use in your own script to assist with updating baseline summaries.

    Parameters
    ----------
    file : Path
        JSON summary file to convert `status_msg` to regex in. Overwritten.
    regex_paths : list of str
        List of path beginnings to identify paths that need to be converted to regex.
        E.g. `['/home/user/']`
        Does: `aaa /home/user/pytest/tmp/result\\.png bbb` -> `aaa .*result\\.png bbb`
    regex_strs : list of str
        List of keys to convert following floats to 1 d.p.
        E.g. ['RMS Value: ']
        Does: `aaa RMS Value: 12\\.432644 bbb` -> `aaa RMS Value: 12\\.4[0-9]* bbb`
    """

    with open(file, 'r') as f:
        summary = json.load(f)

    for test in summary.keys():

        msg = summary[test]['status_msg']

        for signal in [*regex_paths, *regex_strs]:
            if signal in msg:
                msg = _escape_regex(msg)
        if not msg.startswith('REGEX:'):
            continue

        for signal in regex_paths:
            if signal in msg:
                msg = _escape_path(msg, path=signal)

        for signal in regex_strs:
            if signal in msg:
                msg = _escape_float(msg, key=signal)

        summary[test]['status_msg'] = msg

    with open(file, 'w') as f:
        json.dump(summary, f, indent=2)


def remove_specific_hashes(summary_file):
    """Replace all hashes in a summary file with placeholder values.

    This is done because the actual hashes used for testing are taken from
    separate files for each specific matplotlib version.
    """

    baseline_placeholder = "###_BASELINE_HASH_###"
    result_placeholder = "###_RESULT_HASH_###"

    with open(summary_file, "r") as f:
        summary = json.load(f)

    for test in summary.keys():

        # Get actual hashes
        baseline = summary[test]["baseline_hash"]
        result = summary[test]["result_hash"]

        # Replace with placeholders (if summary has hashes)
        if baseline is not None:
            summary[test]["baseline_hash"] = baseline_placeholder
            summary[test]["status_msg"] = \
                summary[test]["status_msg"].replace(baseline, baseline_placeholder)
        if result is not None:
            summary[test]["result_hash"] = result_placeholder
            summary[test]["status_msg"] = \
                summary[test]["status_msg"].replace(result, result_placeholder)

    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)


def transform_hashes(hash_file):
    """Make hash comparison tests fail correctly.

    Makes hashes of tests *hdiff* in hash_file fail hash comparison
    and remove *hmissing* hashes that should be missing.
    """

    with open(hash_file, "r") as f:
        hashes = json.load(f)

    for test in list(hashes.keys()):
        h = hashes[test]
        if "hdiff" in test and h is not None:
            # Replace first four letters with d1ff to force mismatch
            hashes[test] = "d1ff" + h[4:]
        if "hmissing" in test and h is not None:
            # Remove hashes that should be missing
            del hashes[test]

    with open(hash_file, "w") as f:
        json.dump(hashes, f, indent=2)


def transform_images(baseline_path):
    """Make image comparison tests fail correctly.

    Makes images of tests *idiff* under baseline_path fail image comparison
    and deletes images for *imissing* tests.
    """

    # Delete imissing files
    for file in baseline_path.glob("**/*imissing*.png"):
        file.unlink()

    # Add red cross to idiff files
    for file in baseline_path.glob("**/*idiff*.png"):
        with Image.open(file) as im:
            draw = ImageDraw.Draw(im)
            draw.line((0, 0) + im.size, "#f00", 3)
            draw.line((0, im.size[1], im.size[0], 0), "#f00", 3)
            im.save(file)

    # Resize idiffshape files
    for file in baseline_path.glob("**/*idiffshape*.png"):
        with Image.open(file) as im:
            (width, height) = (im.width // 2, im.height // 2)
            im_resized = im.resize((width, height))
            im_resized.save(file)
