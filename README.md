[![Build Status](https://travis-ci.org/astrofrog/pytest-mpl.svg?branch=master)](https://travis-ci.org/astrofrog/pytest-mpl) [![Coverage Status](https://coveralls.io/repos/astrofrog/pytest-mpl/badge.svg)](https://coveralls.io/r/astrofrog/pytest-mpl)


About
=====

A plugin to faciliate image comparison for Matplotlib figures in pytest (which uses some of the Matplotlib image comparison functions behind the scenes).

Dependencies
============

This plugin requires [matplotlib](http://www.matplotlib.org) and
[nose](http://nose.readthedocs.org/) to be installed, but in future we will
remove these dependencies.

Install
=======

For now, install this package using:

    git clone http://github.com/astrofrog/pytest-mpl
    cd pytest-mpl
    python setup.py install
    
pytest-mpl will be on PyPI soon!    

Using
=====

To use, you simply need to mark the function where you want to compare images
using ``@pytest.mark.mpl_image_compare``, and make sure that the function returns a Matplotlib figure (or any figure object that has a ``savefig`` method):

    import pytest
    import matplotlib.pyplot as plt

    @pytest.mark.mpl_image_compare
    def test_succeeds():
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot([1,2,3])
        return fig
        
To generate the baseline images, run the tests with:

    py.test --generate-images-path=images ...
    
Once you are happy with the baseline images, put them in a sub-directory called ``baseline`` in the same directory as the tests. You can then run the tests simply with:

    py.test ...
    
and the tests will pass if the images are the same.

The ``@pytest.mark.mpl_image_compare`` marker can take an argument which is the RMS tolerance (which defaults to 10):

    @pytest.mark.mpl_image_compare(tolerance=20)
    def test_image():
        ...
        