About
-----

This is a plugin to facilitate image comparison for
`Matplotlib <http://www.matplotlib.org>`__ figures in pytest.

For each figure to test, the reference image is subtracted from the
generated image, and the RMS of the residual is compared to a
user-specified tolerance. If the residual is too large, the test will
fail (this is implemented using helper functions from
``matplotlib.testing``).

For more information on how to write tests to do this, see the **Using**
section below.

Installing
----------

This plugin is compatible with Python 2.7, and 3.6 and later, and
requires `pytest <http://pytest.org>`__ and
`matplotlib <http://www.matplotlib.org>` to be installed.

To install, you can do::

    pip install pytest-mpl

You can check that the plugin is registered with pytest by doing::

    pytest --version

which will show a list of plugins:

::

    This is pytest version 2.7.1, imported from ...
    setuptools registered plugins:
      pytest-mpl-0.1 at ...

Using
-----

With Baseline Images
^^^^^^^^^^^^^^^^^^^^

To use, you simply need to mark the function where you want to compare
images using ``@pytest.mark.mpl_image_compare``, and make sure that the
function returns a Matplotlib figure (or any figure object that has a
``savefig`` method):

.. code:: python

    import pytest
    import matplotlib.pyplot as plt

    @pytest.mark.mpl_image_compare
    def test_succeeds():
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot([1,2,3])
        return fig

To generate the baseline images, run the tests with the
``--mpl-generate-path`` option with the name of the directory where the
generated images should be placed::

    pytest --mpl-generate-path=baseline

If the directory does not exist, it will be created. The directory will
be interpreted as being relative to where you are running ``pytest``.
Once you are happy with the generated images, you should move them to a
sub-directory called ``baseline`` relative to the test files (this name
is configurable, see below). You can also generate the baseline image
directly in the right directory.

With a Hash Library
^^^^^^^^^^^^^^^^^^^

Instead of comparing to baseline images, you can instead compare against a json
library of sha256 hashes. This has the advantage of not having to check baseline
images into the repository with the tests, or download them from a remote
source.

The hash library can be generated with
``--mpl-generate-hash-library=path_to_file.json``. The hash library to be used
can either be specified via the ``--mpl-hash-library=`` command line argument,
or via the ``hash_library=`` keyword argument to the
``@pytest.mark.mpl_image_comapre`` decorator.


Hybrid Mode: Hashes and Images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to configure both hashes and baseline images. In this scenario
the hashes will be compared first, and the baseline images used if the hash
comparison fails.

This is especially useful if the baseline images are external to the repository
with the tests in, and can be accessed remotely. In this situation if the hashes
match the baseline images wont be retrieved, saving time and bandwidth. Also it
allows the tests to be modified and the hashes updated to reflect the changes
without having to modify the external images.


Running Tests
^^^^^^^^^^^^^

Once tests are written with either baseline images or a hash library to compare
against, the tests can be run with::

    pytest --mpl

and the tests will pass if the images are the same. If you omit the
``--mpl`` option, the tests will run but will only check that the code
runs without checking the output images.


Generating a Failure Summary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By specifying the ``--mpl-generate-summary=html`` CLI argument a HTML summary
page will be generated showing the baseline, diff and result image for each
failing test. If no baseline images are configured, just the result images will
be displayed.

Options
-------

Tolerance
^^^^^^^^^

The RMS tolerance for the image comparison (which defaults to 2) can be
specified in the ``mpl_image_compare`` decorator with the ``tolerance``
argument:

.. code:: python

    @pytest.mark.mpl_image_compare(tolerance=20)
    def test_image():
        ...

Savefig options
^^^^^^^^^^^^^^^

You can pass keyword arguments to ``savefig`` by using
``savefig_kwargs`` in the ``mpl_image_compare`` decorator:

.. code:: python

    @pytest.mark.mpl_image_compare(savefig_kwargs={'dpi':300})
    def test_image():
        ...

Baseline images
^^^^^^^^^^^^^^^

The baseline directory (which defaults to ``baseline`` ) and the
filename of the plot (which defaults to the name of the test with a
``.png`` suffix) can be customized with the ``baseline_dir`` and
``filename`` arguments in the ``mpl_image_compare`` decorator:

.. code:: python

    @pytest.mark.mpl_image_compare(baseline_dir='baseline_images',
                                   filename='other_name.png')
    def test_image():
        ...

The baseline directory in the decorator above will be interpreted as
being relative to the test file. Note that the baseline directory can
also be a URL (which should start with ``http://`` or ``https://`` and
end in a slash). If you want to specify mirrors, set ``baseline_dir`` to
a comma-separated list of URLs (real commas in the URL should be encoded
as ``%2C``).

Finally, you can also set a custom baseline directory globally when
running tests by running ``pytest`` with::

    pytest --mpl --mpl-baseline-path=baseline_images

This directory will be interpreted as being relative to where the tests
are run. In addition, if both this option and the ``baseline_dir``
option in the ``mpl_image_compare`` decorator are used, the one in the
decorator takes precedence.

Base style
^^^^^^^^^^

By default, tests will be run using the Matplotlib 'classic' style
(ignoring any locally defined RC parameters). This can be overridden by
using the ``style`` argument:

.. code:: python

    @pytest.mark.mpl_image_compare(style='fivethirtyeight')
    def test_image():
        ...

Package version dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Different versions of Matplotlib and FreeType may result in slightly
different images. When testing on multiple platforms or as part of a
pipeline, it is important to ensure that the versions of these
packages match the versions used to generate the images used for
comparison. It can be useful to pin versions of Matplotlib and FreeType
so as to avoid automatic updates that fail tests.

Removing text
^^^^^^^^^^^^^

If you are running a test for which you are not interested in comparing
the text labels, you can use the ``remove_text`` argument to the
decorator:

.. code:: python

    @pytest.mark.mpl_image_compare(remove_text=True)
    def test_image():
        ...

This will make the test insensitive to changes in e.g. the freetype
library.

Test failure example
--------------------

If the images produced by the tests are correct, then the test will
pass, but if they are not, the test will fail with a message similar to
the following::

    E               Exception: Error: Image files did not match.
    E                 RMS Value: 142.2287807767823
    E                 Expected:
    E                   /var/folders/zy/t1l3sx310d3d6p0kyxqzlrnr0000gr/T/tmp4h4oxr7y/baseline-coords_overlay_auto_coord_meta.png
    E                 Actual:
    E                   /var/folders/zy/t1l3sx310d3d6p0kyxqzlrnr0000gr/T/tmp4h4oxr7y/coords_overlay_auto_coord_meta.png
    E                 Difference:
    E                   /var/folders/zy/t1l3sx310d3d6p0kyxqzlrnr0000gr/T/tmp4h4oxr7y/coords_overlay_auto_coord_meta-failed-diff.png
    E                 Tolerance:
    E                   10

The image paths included in the exception are then available for
inspection:

+----------------+----------------+-------------+
| Expected       | Actual         | Difference  |
+================+================+=============+
| |expected|     | |actual|       | |diff|      |
+----------------+----------------+-------------+

In this case, the differences are very clear, while in some cases it may
be necessary to use the difference image, or blink the expected and
actual images, in order to see what changed.

The default tolerance is 2, which is very strict. In some cases, you may
want to relax this to account for differences in fonts across different
systems.

By default, the expected, actual and difference files are written to a
temporary directory with a non-deterministic path. If you want to instead
write them to a specific directory, you can use::

    pytest --mpl --mpl-results-path=results

The ``results`` directory will then contain one sub-directory per test, and each
sub-directory will contain the three files mentioned above. If you are using a
continuous integration service, you can then use the option to upload artifacts
to upload these results to somewhere where you can view them. For more
information, see:

* `Uploading artifacts on Travis-CI <https://docs.travis-ci.com/user/uploading-artifacts/>`_
* `Build Artifacts (CircleCI) <https://circleci.com/docs/1.0/build-artifacts/>`_
* `Packaging Artifacts (AppVeyor) <https://www.appveyor.com/docs/packaging-artifacts/>`_

Running the tests for pytest-mpl
--------------------------------

If you are contributing some changes and want to run the tests, first
install the latest version of the plugin then do::

    cd tests
    pytest --mpl

The reason for having to install the plugin first is to ensure that the
plugin is correctly loaded as part of the test suite.

.. |expected| image:: images/baseline-coords_overlay_auto_coord_meta.png
.. |actual| image:: images/coords_overlay_auto_coord_meta.png
.. |diff| image:: images/coords_overlay_auto_coord_meta-failed-diff.png
