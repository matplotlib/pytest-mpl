import os
import sys
import shutil

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    cached_property = property

from jinja2 import Environment, PackageLoader, select_autoescape

__all__ = ['generate_summary_html', 'generate_summary_basic_html']


class Results:
    """
    Data for the whole test run, used for providing data to the template.

    Parameters
    ----------
    results : dict
        The `pytest_mpl.plugin.ImageComparison._test_results` object.
    title : str
        Value for HTML <title>.
    """
    def __init__(self, results, title="Image comparison"):
        self.title = title  # HTML <title>

        # If any baseline images or baseline hashes are present,
        # assume all results should have them
        self.warn_missing = {'baseline_image': False, 'baseline_hash': False}
        for key in self.warn_missing.keys():
            for result in results.values():
                if result[key] is not None:
                    self.warn_missing[key] = True
                    break

        # Additional <body> classes
        self.classes = []
        if self.warn_missing['baseline_hash'] is False:
            self.classes += ['no-hash-test']

        # Generate sorted list of results
        self.cards = []
        pad = len(str(len(results.items())))  # maximum length of a result index
        for collect_n, (name, item) in enumerate(results.items()):
            card_id = str(collect_n).zfill(pad)  # zero pad for alphanumerical sorting
            self.cards += [Result(name, item, card_id, self.warn_missing)]
        self.cards = sorted(self.cards, key=lambda i: i.indexes['status'], reverse=True)

    @cached_property
    def statistics(self):
        """Generate a dictionary of summary statistics."""
        stats = {'passed': 0, 'failed': 0, 'passed_baseline': 0,
                 'failed_baseline': 0, 'skipped': 0}
        for test in self.cards:
            if test.status == 'passed':
                stats['passed'] += 1
                if test.image_status != 'match':
                    stats['failed_baseline'] += 1
            elif test.status == 'failed':
                stats['failed'] += 1
                if test.image_status == 'match':
                    stats['passed_baseline'] += 1
            elif test.status == 'skipped':
                stats['skipped'] += 1
        return stats


class Result:
    """
    Result data for a single image test, used for providing data to the template.

    Parameters
    ----------
    name : str
        Full name of the test including modules.
    item : dict
        Dictionary of summary results for a test in
        `pytest_mpl.plugin.ImageComparison._test_results`.
    id : str
        The test number in order collected. Numbers must be
        zero padded due to alphanumerical sorting.
    warn_missing : dict
        Whether to include relevant status badges for images and/or hashes.
        Must have keys ``baseline_image`` and ``baseline_hash``.
    """
    def __init__(self, name, item, id, warn_missing):
        # Make the summary dictionary available as attributes
        self.__dict__ = item

        # Sort index for collection order
        self.id = id

        # Whether to show image and/or hash status badges
        self.warn_missing = warn_missing

        # Name of test with module and test function together and separate
        self.full_name = name
        self.name = name.split('.')[-1]
        self.module = '.'.join(name.split('.')[:-1])

        # Additional classes to add to the result card
        self.classes = [f'{k}-{str(v).lower()}' for k, v in [
            ('overall', self.status),
            ('image', self.image_status),
            ('hash', self.hash_status),
        ]]

    @cached_property
    def image_status(self):
        """Status of the image comparison test."""
        if self.rms is None and self.tolerance is not None:
            return 'match'
        elif self.rms is not None:
            return 'diff'
        elif self.baseline_image is None:
            return 'missing'
        else:
            raise ValueError('Unknown image result.')

    @cached_property
    def hash_status(self):
        """Status of the hash comparison test."""
        if self.baseline_hash is not None or self.result_hash is not None:
            if self.baseline_hash is None:
                return 'missing'
            elif self.baseline_hash == self.result_hash:
                return 'match'
            else:
                return 'diff'
        return None

    @cached_property
    def indexes(self):
        """Dictionary with strings optimized for sorting."""
        return {'status': self._status_sort, 'rms': self._rms_sort}

    @property
    def _status_sort(self):
        """Status number. Higher means more issues."""
        s = 0
        if self.status == 'failed':
            s += 10
        if self.image_status == 'diff':
            s += 3
        elif self.image_status == 'missing':
            s += 4
        if self.hash_status == 'diff':
            s += 1
        elif self.hash_status == 'missing':
            s += 5
        return f"{s:02.0f}"

    @property
    def _rms_sort(self):
        """RMS to 3 d.p. for sorting."""
        if self.image_status == 'match':
            return "000000"
        elif self.image_status == 'diff':
            # RMS will be in [0, 255]
            return f"{(self.rms + 2) * 1000:06.0f}"
        else:  # Missing baseline image
            return "000001"

    @cached_property
    def rms_str(self):
        """RMS to show in template."""
        if self.image_status == 'match':
            return '< tolerance'  # self.rms is None
        elif self.image_status == 'diff':
            return self.rms
        else:  # Missing baseline image
            return 'None'

    @property
    def badges(self):
        """Additional badges to show beside overall status badge."""
        for test_type, status_getter in [('image', image_status_msg), ('hash', hash_status_msg)]:
            status = getattr(self, f'{test_type}_status')
            if not self.warn_missing[f'baseline_{test_type}']:
                continue  # not expected to exist
            if (
                    (status == 'missing') or
                    (self.status == 'failed' and status == 'match') or
                    (self.status == 'passed' and status == 'diff')
            ):  # Only show if different to overall status
                yield {'status': status, 'svg': test_type, 'tooltip': status_getter(status)}


def status_class(status):
    """Status to Bootstrap class."""
    status = status.split('-')[-1]  # e.g. "overall-passed" -> "passed"
    classes = {
        'passed': 'success',
        'failed': 'danger',
        'skipped': 'warning',
        'match': 'success',
        'diff': 'danger',
        'missing': 'warning',
    }
    return classes[status]


def image_status_msg(status):
    """Image status to status message."""
    messages = {
        'match': 'Baseline image matches',
        'diff': 'Baseline image differs',
        'missing': 'Baseline image not found',
    }
    return messages[status]


def hash_status_msg(status):
    """Hash status to status message."""
    messages = {
        'match': 'Baseline hash matches',
        'diff': 'Baseline hash differs',
        'missing': 'Baseline hash not found',
    }
    return messages[status]


def generate_summary_html(results, results_dir):
    """Generate the HTML summary.

    Parameters
    ----------
    results : dict
        The `pytest_mpl.plugin.ImageComparison._test_results` object.
    results_dir : Path
        Path to the output directory.
    """

    # Initialize Jinja
    env = Environment(
        loader=PackageLoader("pytest_mpl.summary.html"),
        autoescape=select_autoescape()
    )

    # Register additional Jinja filters
    env.filters["status_class"] = status_class
    env.filters["image_status_msg"] = image_status_msg
    env.filters["hash_status_msg"] = hash_status_msg

    # Render HTML starting from the base template
    template = env.get_template("base.html")
    html = template.render(results=Results(results))

    # Write files
    for file in ['styles.css', 'extra.js', 'hash.svg', 'image.svg']:
        path = os.path.join(os.path.dirname(__file__), 'templates', file)
        shutil.copy(path, results_dir / file)
    html_file = results_dir / 'fig_comparison.html'
    with open(html_file, 'w') as f:
        f.write(html + '\n')

    return html_file


def generate_summary_basic_html(results, results_dir):
    """Generate the basic HTML summary.

    Parameters
    ----------
    results : dict
        The `pytest_mpl.plugin.ImageComparison._test_results` object.
    results_dir : Path
        Path to the output directory.
    """

    # Initialize Jinja
    env = Environment(
        loader=PackageLoader("pytest_mpl.summary.html"),
        autoescape=select_autoescape()
    )

    # Render HTML starting from the base template
    template = env.get_template("basic.html")
    html = template.render(results=Results(results))

    # Write files
    html_file = results_dir / 'fig_comparison_basic.html'
    with open(html_file, 'w') as f:
        f.write(html + '\n')

    return html_file
