import pytest

from .helpers import plot

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
