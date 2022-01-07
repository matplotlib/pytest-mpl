import os
import shutil

__all__ = ['generate_summary_html']

BTN_CLASS = {
    'passed': 'success',
    'failed': 'danger',
    'skipped': 'warning',
    'match': 'success',
    'diff': 'danger',
    'missing': 'warning',
}

IMAGE_STATUS = {
    'match': 'Baseline image matches',
    'diff': 'Baseline image differs',
    'missing': 'Baseline image not found',
}

HASH_STATUS = {
    'match': 'Baseline hash matches',
    'diff': 'Baseline hash differs',
    'missing': 'Baseline hash not found',
}


def template(name):
    file = os.path.join(os.path.dirname(__file__), 'templates', f'{name}.html')
    f = open(file, 'r')
    return f.read()


BASE = template('base')
NAVBAR = template('navbar')
FILTER = template('filter')
RESULT = template('result')
RESULT_DIFFIMAGE = template('result_diffimage')
RESULT_BADGE = template('result_badge')
RESULT_BADGE_ICON = template('result_badge_icon')
RESULT_IMAGES = template('result_images')


def status_sort(status):
    s = 50
    if status['overall'] == 'failed':
        s -= 10
    if status['image'] == 'diff':
        s -= 3
    elif status['image'] == 'missing':
        s -= 4
    if status['hash'] == 'diff':
        s -= 1
    elif status['hash'] == 'missing':
        s -= 5
    return s


def get_status(item, card_id, warn_missing):
    status = {
        'overall': None,
        'image': None,
        'hash': None,
    }

    assert item['status'] in BTN_CLASS.keys()
    status['overall'] = item['status']

    if item['rms'] is None and item['tolerance'] is not None:
        status['image'] = 'match'
    elif item['rms'] is not None:
        status['image'] = 'diff'
    elif item['baseline_image'] is None:
        status['image'] = 'missing'
    else:
        raise ValueError('Unknown image result.')

    baseline_hash = item['baseline_hash']
    result_hash = item['result_hash']
    if baseline_hash is not None or result_hash is not None:
        if baseline_hash is None:
            status['hash'] = 'missing'
        elif baseline_hash == result_hash:
            status['hash'] = 'match'
        else:
            status['hash'] = 'diff'

    classes = [f'{k}-{str(v).lower()}' for k, v in status.items()]

    extra_badges = ''
    for test_type, status_dict in [('image', IMAGE_STATUS), ('hash', HASH_STATUS)]:
        if not warn_missing[f'baseline_{test_type}']:
            continue  # not expected to exist
        if (
                (status[test_type] == 'missing') or
                (status['overall'] == 'failed' and status[test_type] == 'match') or
                (status['overall'] == 'passed' and status[test_type] == 'diff')
        ):
            extra_badges += RESULT_BADGE_ICON.format(
                card_id=card_id,
                btn_class=BTN_CLASS[status[test_type]],
                svg=test_type,
                tooltip=status_dict[status[test_type]],
            )

    badge = RESULT_BADGE.format(
        card_id=card_id,
        status=status['overall'].upper(),
        btn_class=BTN_CLASS[status['overall']],
        extra_badges=extra_badges,
    )

    return status, classes, badge


def card(name, item, warn_missing=None):
    card_id = name.replace('.', '-')
    test_name = name.split('.')[-1]
    module = '.'.join(name.split('.')[:-1])

    status, classes, badge = get_status(item, card_id, warn_missing)

    if item['diff_image'] is None:
        image = f'<img src="{item["result_image"]}" class="card-img-top" alt="result image">'
    else:  # show overlapping diff and result images
        image = RESULT_DIFFIMAGE.format(diff=item['diff_image'], result=item["result_image"])

    image_html = {}
    for image_type in ['baseline_image', 'diff_image', 'result_image']:
        if item[image_type] is not None:
            image_html[image_type] = f'<img src="{item[image_type]}" class="card-img-top" alt="">'
        else:
            image_html[image_type] = ''

    if status['image'] == 'match':
        rms = '&lt; tolerance'
    else:
        rms = item['rms']

    offcanvas = RESULT_IMAGES.format(

        id=card_id,
        test_name=test_name,
        module=module,

        baseline_image=image_html['baseline_image'],
        diff_image=image_html['diff_image'],
        result_image=image_html['result_image'],

        status=status['overall'].upper(),
        btn_class=BTN_CLASS[status['overall']],
        status_msg=item['status_msg'],

        image_status=IMAGE_STATUS[status['image']],
        image_btn_class=BTN_CLASS[status['image']],
        rms=rms,
        tolerance=item['tolerance'],

        hash_status=HASH_STATUS[status['hash']],
        hash_btn_class=BTN_CLASS[status['hash']],
        baseline_hash=item['baseline_hash'],
        result_hash=item['result_hash'],

    )

    result_card = RESULT.format(

        classes=" ".join(classes),

        id=card_id,
        test_name=test_name,
        module=module,
        status_sort=status_sort(status),

        image=image,
        badge=badge,
        offcanvas=offcanvas,

    )

    return result_card


def generate_summary_html(results, results_dir):
    # If any baseline images or baseline hashes are present,
    # assume all results should have them
    warn_missing = {'baseline_image': False, 'baseline_hash': False}
    for key in warn_missing.keys():
        for result in results.values():
            if result[key] is not None:
                warn_missing[key] = True
                break

    classes = []
    if warn_missing['baseline_hash'] is False:
        classes += ['no-hash-test']

    # Generate result cards
    cards = ''
    for name, item in results.items():
        cards += card(name, item, warn_missing=warn_missing)

    # Generate HTML
    html = BASE.format(
        title="Image comparison",
        navbar=NAVBAR,
        cards=cards,
        filter=FILTER,
        classes=" ".join(classes),
    )

    # Write files
    for file in ['styles.css', 'extra.js', 'hash.svg', 'image.svg']:
        path = os.path.join(os.path.dirname(__file__), 'templates', file)
        shutil.copy(path, results_dir / file)
    html_file = results_dir / 'fig_comparison.html'
    with open(html_file, 'w') as f:
        f.write(html)

    return html_file
