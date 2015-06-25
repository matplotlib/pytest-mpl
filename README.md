[![Travis Build Status](https://travis-ci.org/astrofrog/pytest-mpl.svg?branch=master)](https://travis-ci.org/astrofrog/pytest-mpl) 
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/mf7hs44scg5mvcyo?svg=true)](https://ci.appveyor.com/project/astrofrog/pytest-mpl)


About
-----

A plugin to faciliate image comparison for [Matplotlib](http://www.matplotlib.org) figures in pytest (which
uses some of the Matplotlib image comparison functions behind the scenes).

Matplotlib includes a number of test utilities and decorators, but these are geared towards the [nose](http://nose.readthedocs.org/) testing framework. Pytest-mpl makes it easy to compare figures produced by tests to reference images when using [pytest](http://pytest.org).

For each figure to test, the reference image is substracted from the generated image, and the RMS of the residual is compared to a user-specified tolerance. If the residual is too large, the test will fail (this is implemented in Matplotlib).

For more information on how to write tests to do this, see the **Using** section below.

Installing
----------

This plugin is compatible with Python 2.6, 2.7, and 3.3 and later, and requires [pytest](http://pytest.org), [matplotlib](http://www.matplotlib.org) and
[nose](http://nose.readthedocs.org/) to be installed (nose is required by Matplotlib).

For now, install this package using:

    git clone http://github.com/astrofrog/pytest-mpl
    cd pytest-mpl
    python setup.py install
    
pytest-mpl will be on PyPI soon!    

Using
-----

To use, you simply need to mark the function where you want to compare images
using ``@pytest.mark.mpl_image_compare``, and make sure that the function
returns a Matplotlib figure (or any figure object that has a ``savefig``
method):

```python
import pytest
import matplotlib.pyplot as plt

@pytest.mark.mpl_image_compare
def test_succeeds():
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot([1,2,3])
    return fig
```

To generate the baseline images, run the tests with:

    py.test --mpl-generate-path=images ...
    
Once you are happy with the baseline images, put them in a sub-directory called
``baseline`` in the same directory as the tests. You can then run the tests
simply with:

    py.test --mpl ...
    
and the tests will pass if the images are the same. If you omit the ``--mpl``
option, the tests will run but will only check that the code runs without
checking the output images.

The ``@pytest.mark.mpl_image_compare`` marker can take an argument which is the
RMS tolerance (which defaults to 10):

```python
@pytest.mark.mpl_image_compare(tolerance=20)
def test_image():
    ...
```

Running the tests
-----------------

To run the tests, first install the plugin then do:

    cd tests
    py.test --mpl

The reason for having to install the plugin first is to ensure that the plugin
is correctly loaded as part of the test suite.
