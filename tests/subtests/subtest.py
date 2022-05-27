import matplotlib.pyplot as plt
import pytest


def plot(line, **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(line, **kwargs)
    return fig


# ### Test all permutations of:
# baseline hash: match, diff, or missing
# baseline image: match, diff, or missing

# hash match

@pytest.mark.image
@pytest.mark.hash
@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hmatch_imatch():
    return plot([1, 2, 3, 4])


@pytest.mark.image
@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hmatch_idiff():
    return plot([1, 3, 2, 4])


@pytest.mark.image
@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hmatch_idiffshape():
    return plot([4, 2, 3, 1, 2])


@pytest.mark.image
@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hmatch_imissing():
    return plot([4, 3, 2, 1])


# hash diff

@pytest.mark.hash
@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hdiff_imatch():
    return plot([1, 4, 2, 3])


@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hdiff_idiff():
    return plot([1, 2, 4, 3])


@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hdiff_idiffshape():
    return plot([4, 2, 3, 1, 3])


@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hdiff_imissing():
    return plot([3, 2, 4, 1])


# hash missing

@pytest.mark.hash
@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hmissing_imatch():
    return plot([1, 3, 4, 2])


@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hmissing_idiff():
    return plot([1, 4, 3, 2])


@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hmissing_idiffshape():
    return plot([4, 2, 3, 1, 4])


@pytest.mark.mpl_image_compare(savefig_kwargs={'metadata': {'Software': None}})
def test_hmissing_imissing():
    return plot([2, 4, 3, 1])


# ### Specialized tests

# Tolerance: high to force image match
@pytest.mark.image
@pytest.mark.hash
@pytest.mark.mpl_image_compare(tolerance=200, savefig_kwargs={'metadata': {'Software': None}})
def test_hdiff_imatch_tolerance():
    return plot([1, 2, 3, 4], linestyle='--')


# Tolerance: non-default to verify option recorded in JSON
@pytest.mark.image
@pytest.mark.hash
@pytest.mark.mpl_image_compare(tolerance=3, savefig_kwargs={'metadata': {'Software': None}})
def test_hdiff_idiff_tolerance():
    return plot([1, 2, 3, 4], linestyle='--')


# Savefig kwargs
@pytest.mark.image
@pytest.mark.hash
@pytest.mark.mpl_image_compare(savefig_kwargs={'facecolor': 'r', 'metadata': {'Software': None}})
def test_hdiff_imatch_savefig():
    return plot([1, 2, 3, 4])


# TODO: Implement these path altering tests later
# # Different baseline directory
# # TODO: Test with a remote `baseline_dir`
# @pytest.mark.mpl_image_compare(baseline_dir='baseline/other')
# def test_hdiff_imatch_baselinedir():
#     return plot([4, 2, 1, 4])
#
#
# # Different filename
# @pytest.mark.mpl_image_compare(filename='test_hdiff_imatch_filename_other.png')
# def test_hdiff_imatch_filename():
#     return plot([4, 2, 1, 4])
#
#
# # Different hash library
# @pytest.mark.mpl_image_compare(hash_library='hashes/other/other.json')
# def test_hdiff_imatch_hashlibrary():
#     return plot([4, 2, 1, 4])


# Different style
@pytest.mark.image
@pytest.mark.hash
@pytest.mark.mpl_image_compare(style='fivethirtyeight', savefig_kwargs={'metadata': {'Software': None}})
def test_hdiff_imatch_style():
    return plot([4, 2, 1, 4])


# Remove text
@pytest.mark.image
@pytest.mark.hash
@pytest.mark.mpl_image_compare(remove_text=True, savefig_kwargs={'metadata': {'Software': None}})
def test_hdiff_imatch_removetext():
    return plot([4, 2, 1, 4])
