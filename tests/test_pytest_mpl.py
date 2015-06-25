import pytest
import matplotlib.pyplot as plt


@pytest.mark.mpl_image_compare
def test_succeeds():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3])
    return fig

@pytest.mark.xfail
@pytest.mark.mpl_image_compare
def test_fails():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,2])
    return fig
    
@pytest.mark.mpl_image_compare(tolerance=20)
def test_tolerance():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,2])
    return fig

def test_nofigure():
    pass
