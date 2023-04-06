.. title:: Basic Usage

###########
Basic Usage
###########

For each figure to test, the reference image is subtracted from the generated image, and the RMS of the residual is compared to a user-specified tolerance. If the residual is too large, the test will fail (this is implemented using helper functions from ``matplotlib.testing``).

.. _image-comparison-mode:

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

.. _hash-comparison-mode:

With a Hash Library
^^^^^^^^^^^^^^^^^^^

Instead of comparing to baseline images, you can instead compare against a JSON
library of SHA-256 hashes. This has the advantage of not having to check baseline
images into the repository with the tests, or download them from a remote
source.

The hash library can be generated with
``--mpl-generate-hash-library=path_to_file.json``. The hash library to be used
can either be specified via the ``--mpl-hash-library=`` command line argument,
or via the ``hash_library=`` keyword argument to the
``@pytest.mark.mpl_image_compare`` decorator.

When generating a hash library, the tests will also be run as usual against the
existing hash library specified by ``--mpl-hash-library`` or the keyword argument.
However, generating baseline images will always result in the tests being skipped.

.. _hybrid-mode:

Hybrid Mode: Hashes and Images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to configure both hashes and baseline images. In this scenario
only the hash comparison can determine the test result. If the hash comparison
fails, the test will fail, however a comparison to the baseline image will be
carried out so the actual difference can be seen. If the hash comparison passes,
the comparison to the baseline image is skipped (unless **results always** is
configured).

This is especially useful if the baseline images are external to the repository
containing the tests, and are accessed via HTTP. In this situation, if the hashes
match, the baseline images won't be retrieved, saving time and bandwidth. Also, it
allows the tests to be modified and the hashes updated to reflect the changes
without having to modify the external images.


Running Tests
^^^^^^^^^^^^^

Once tests are written with baseline images, a hash library, or both to compare
against, the tests can be run with::

    pytest --mpl

and the tests will pass if the images are the same. If you omit the
``--mpl`` option, the tests will run but will only check that the code
runs, without checking the output images.

If pytest-mpl is not installed, the image comparison tests will cause pytest
to show a warning, ``PytestReturnNotNoneWarning``. Installing pytest-mpl will
solve this issue. Alternativly, the image comparison tests can be deselected
by running pytest with ``-m "not mpl_image_compare"``.
