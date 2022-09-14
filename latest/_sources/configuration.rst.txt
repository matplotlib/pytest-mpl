.. title:: Configuration

#############
Configuration
#############

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

This directory will be interpreted as being relative to where pytest
is run. However, if the ``--mpl-baseline-relative`` option is also
included, this directory will be interpreted as being relative to
the current test directory.
In addition, if both this option and the ``baseline_dir``
option in the ``mpl_image_compare`` decorator are used, the one in the
decorator takes precedence.

Results always
^^^^^^^^^^^^^^

By default, result images are only saved for tests that fail.
Passing ``--mpl-results-always`` to pytest will force result images
to be saved for all tests, even for tests that pass.

When in **hybrid mode**, even if a test passes hash comparison,
a comparison to the baseline image will also be carried out,
with the baseline image and diff image (if image comparison fails)
saved for all tests. This secondary comparison will not affect
the success status of the test.

This option is useful for always *comparing* the result images against
the baseline images, while only *assessing* the tests against the
hash library.
If you only update your baseline images after merging a PR, this
option means that the generated summary will always show how the
PR affects the baseline images, with the success status of each
test (based on the hash library) also shown in the generated
summary. This option is applied automatically when generating
a HTML summary.

When the ``--mpl-results-always`` option is active, and some hash
comparison tests are performed, a hash library containing all the
result hashes will also be saved to the root of the results directory.
The filename will be extracted from ``--mpl-generate-hash-library``,
``--mpl-hash-library`` or ``hash_library=`` in that order.

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

.. |expected| image:: images/baseline-coords_overlay_auto_coord_meta.png
.. |actual| image:: images/coords_overlay_auto_coord_meta.png
.. |diff| image:: images/coords_overlay_auto_coord_meta-failed-diff.png
