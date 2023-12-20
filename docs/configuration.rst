.. title:: Configuration

#############
Configuration
#############

This section defines all the ``pytest-mpl`` configuration options.

There are three ways to configure the plugin:

1. Passing kwargs to the ``pytest.mark.mpl_image_compare`` decorator (kwarg)
2. Passing options to pytest from the command line (CLI)
3. Setting INI options in pytest configuration files (INI)

The CLI and INI options are global, and will apply to all tests.
The kwarg options are local, and will only apply to the test function that they are specified in.

If set, the kwarg options will override the equivalent CLI and INI options.
Furthermore, CLI options will override equivalent INI options.

See the `pytest documentation <https://docs.pytest.org/en/stable/reference/customize.html>`__ for more information on how to set INI options.

Enabling the plugin
===================

Enable testing
--------------
| **kwarg**: ---
| **CLI**: ``--mpl``
| **INI**: ---
| Default: ``False``

To enable image comparison testing, pass ``--mpl`` when running pytest.

.. code:: bash

   pytest --mpl

By default, this option will enable :doc:`baseline image comparison <image_mode>`.
:doc:`Baseline hash comparison <hash_mode>` can be enabled by configuring the :ref:`hash library configuration option <hash-library>`.

Without this option, the tests will still run.
However, the returned figures will be closed without being compared to a baseline image or hash.

Enable baseline image generation
--------------------------------
| **kwarg**: ---
| **CLI**: ``--mpl-generate-path=<path>``
| **INI**: ---
| Default: ``None``

Baseline images will be generated and saved to the specified directory path, relative to where pytest was run.

.. code:: bash

   pytest --mpl-generate-path=baseline

The baseline directory specified by the :ref:`baseline directory configuration option <baseline-dir>` will be ignored.
However, the filename of the baseline image will still be determined by the :ref:`filename configuration option <filename>` and the :ref:`use full test name configuration option <full-test-name>`.
This option overrides the ``--mpl`` option.

Enable baseline hash generation
-------------------------------
| **kwarg**: ---
| **CLI**: ``--mpl-generate-hash-library=<path>``
| **INI**: ---
| Default: ``None``

Baseline hashes will be generated and saved to the specified JSON file path, relative to where pytest was run.

.. code:: bash

   pytest --mpl-generate-hash-library=hashes.json

Enabling this option will also set the ``--mpl`` option, as it is important to visually inspect the figures before generating baseline hashes.
The hash library specified by the :ref:`hash library configuration option <hash-library>` will be ignored.

Locating baseline images
========================

.. _baseline-dir:

Directory containing baseline images
------------------------------------
| **kwarg**: ``baseline_dir=<path>``
| **CLI**: ``--mpl-baseline-path=<path>``
| **INI**: ``mpl-baseline-path``
| Default: ``baseline/`` *(relative to the test file)*

The directory containing the baseline images that will be compared to the test figures.
The kwarg option (``baseline_dir``) is relative to the test file, while the CLI option (``--mpl-baseline-path``) and INI option (``mpl-baseline-path``) are relative to where pytest was run.
Absolute paths can also be used.
If the directory does not exist, it will be created along with any missing parent directories.

.. code:: bash

   pytest --mpl --mpl-baseline-path=baseline_images

The baseline directory can also be a URL, which should start with ``http://`` or ``https://`` and end in a slash.
Alternative URLs, or mirrors, can be configured by specifying a comma-separated list of URLs.
Baseline images will be searched for in the order that the URLs are specified, and the first successful download will be used.
Real commas in URLs should be encoded as ``%2C``.

.. code:: bash

   pytest --mpl --mpl-baseline-path=https://example.com/baseline/,https://mirror.example.com/baseline/

.. code:: python

    @pytest.mark.mpl_image_compare(baseline_dir="https://example.com/baseline/",
                                   filename="other_name.png")
    def test_plot():
        ...

Whether ``--mpl-baseline-path`` should also be relative to the test file
------------------------------------------------------------------------
| **kwarg**: ---
| **CLI**: ``--mpl-baseline-relative``
| **INI**: ---
| Default: ``False``

If this option is set, the baseline directory specified by ``--mpl-baseline-path`` will be interpreted as being relative to the test file.
This option is only relevant if ``--mpl-baseline-path`` refers to a directory and not a URL.

.. code:: bash

   pytest --mpl --mpl-baseline-path=baseline_images --mpl-baseline-relative

.. _filename:

Filename of the baseline image
------------------------------
| **kwarg**: ``filename=<name>``
| **CLI**: ---
| **INI**: ---
| Default: *name of the test with a file extension suffix*

The filename of the baseline image that will be compared to the test figure.
The default file extension is ``png``, unless overridden by :ref:`savefig_kwargs["format"] <savefig-kwargs>`.
This option has no effect if the :ref:`use full test name configuration option <full-test-name>` is enabled.

.. code:: python

    @pytest.mark.mpl_image_compare(baseline_dir="baseline_images",
                                   filename="other_name.png")
    def test_plot():
        ...

If you specify a filename that has an extension other than ``png``, you must also specify it in :ref:`savefig_kwargs["format"] <savefig-kwargs>`.

.. code:: python

    @pytest.mark.mpl_image_compare(filename="plot.pdf",
                                   savefig_kwargs={"format": "pdf"})
    def test_plot():
        ...

.. _full-test-name:

Whether to include the module name in the filename
--------------------------------------------------
| **kwarg**: ---
| **CLI**: ``--mpl-use-full-test-name``
| **INI**: ``mpl-use-full-test-name``
| Default: ``False``

Whether to include the module name (and class name) in the baseline image filename.

This option is useful if you have multiple tests with the same name in different modules.
Or have multiple tests with the same name in the same module, but in different classes.
If this option is set, the baseline image filename will be ``<module-name>[.<class-name>].<test-name>.<ext>``.
The file extension is the default extension as documented in the :ref:`filename option documentation <filename>`.

Enabling this should ensure baseline image filenames are unique.
The :ref:`filename configuration option <filename>` can also be used to fix the filename of the baseline image.

.. note::

   Filename collisions are permitted.
   This is useful if, for example, you want to verify that two tests produce the same figure.
   However, unexpected collisions should become apparent when the tests are run and failures are reported.

This option overrides the :ref:`filename configuration option <filename>`.

Locating baseline hashes
========================

.. _hash-library:

File containing baseline hashes
-------------------------------
| **kwarg**: ``hash_library=<path>``
| **CLI**: ``--mpl-hash-library=<path>``
| **INI**: ``mpl-hash-library = <path>``
| Default: *no hash comparison*

The file containing the baseline hashes that will be compared to the test figures.
The kwarg option (``hash_library``) is relative to the test file, while the INI option (``mpl-hash-library``) is relative to where pytest was run.
The file must be a JSON file in the same format as one generated by ``--mpl-generate-hash-library``.
If its directory does not exist, it will be created along with any missing parent directories.

.. attention::

   For backwards compatibility, the CLI option (``--mpl-hash-library``) is relative to the test file.
   Also, the CLI option takes precedence over the kwarg option, but the kwarg option takes precedence over the INI option as usual.

Configuring this option disables baseline image comparison.
If you want to enable both hash and baseline image comparison, which we call :doc:`"hybrid mode" <hybrid_mode>`, you must explicitly set the :ref:`baseline directory configuration option <baseline-dir>`.

.. _controlling-sensitivity:

Controlling the sensitivity of the comparison
=============================================

.. rubric:: Package version dependencies

Different versions of Matplotlib and FreeType may result in slightly different images.
When testing on multiple platforms or as part of a pipeline, it is important to ensure that the versions of these packages match the versions used to generate the images and/or hashes used for comparison.
It can be useful to pin versions of Matplotlib and FreeType so as to avoid automatic updates that fail tests.

The ``pytest-mpl`` configuration options in this section allow you to control the sensitivity of the comparison.
Adjusting these options *may* allow tests to pass across a range of Matplotlib and FreeType versions.

.. _tolerance:

RMS tolerance
-------------
| **kwarg**: ``tolerance=<value>``
| **CLI**: ``--mpl-default-tolerance=<value>``
| **INI**: ``mpl-default-tolerance = <value>``
| Default: ``2``

The maximum RMS difference between the result image and the baseline image before the test fails.
The specified tolerance value can be a float or an integer between 0 and 255.

.. code:: python

    @pytest.mark.mpl_image_compare(tolerance=20)
    def test_plot():
        ...

.. rubric:: How the RMS difference is calculated

Result images and baseline images are *always* converted to PNG files before comparison.
Each are read as an array of RGBA pixels (or just RGB if fully opaque) with values between 0 and 255.
If the result image and the baseline image have different aspect ratios, the test will always fail.
The RMS difference is calculated as the square root of the mean of the squared differences between the result image and the baseline image.
If the RMS difference is greater than the tolerance, the test will fail.

Whether to make metadata deterministic
--------------------------------------
| **kwarg**: ``deterministic=<bool>``
| **CLI**: ``--mpl-deterministic`` or ``--mpl-no-deterministic``
| **INI**: ``mpl-deterministic = <bool>``
| Default: ``True`` (PNG: ``False``)

Whether to make the image file metadata deterministic.

By default, Matplotlib does not produce deterministic output that will have a consistent hash every time it is run, or over different Matplotlib versions.
Depending on the file format, enabling this option does a number of things such as, e.g., setting the creation date in the metadata to be constant, and avoids hard-coding the Matplotlib version in the file.
Supported formats for deterministic metadata are ``"eps"``, ``"pdf"``, ``"png"``, and ``"svg"``.

.. code:: python

    @pytest.mark.mpl_image_compare(deterministic=True)
    def test_plot():
        ...

By default, ``pytest-mpl`` will save and compare figures in PNG format.
However, it is possible to set the format to use by setting, e.g., ``savefig_kwargs={"format": "pdf"}`` when configuring the :ref:`savefig_kwargs configuration option <savefig-kwargs>`.
Note that Ghostscript is required to be installed for comparing PDF and EPS figures, while Inkscape is required for SVG comparison.

.. note::

    A future major release of ``pytest-mpl`` will generate deterministic PNG files by default.
    It is recommended to explicitly set this configuration option to avoid hashes changing.

Whether to remove titles and axis tick labels
---------------------------------------------
| **kwargs**: ``remove_text=<bool>``
| **CLI**: ---
| **INI**: ---
| Default: ``False``

Enabling this option will remove titles and axis tick labels from the figure before saving and comparing.
This will make the test less sensitive to changes in the FreeType library version.
This feature, provided by :func:`matplotlib.testing.decorators.remove_ticks_and_titles`, will not remove any other text such as axis labels and annotations.

.. code:: python

    @pytest.mark.mpl_image_compare(remove_text=True)
    def test_plot():
        ...

Modifying the figure before saving
==================================

.. _savefig-kwargs:

Matplotlib savefig kwargs
-------------------------
| **kwarg**: ``savefig_kwargs=<dict>``
| **CLI**: ---
| **INI**: ---
| Default: ``{}``

A dictionary of keyword arguments to pass to :func:`matplotlib.pyplot.savefig`.

.. code:: python

    @pytest.mark.mpl_image_compare(savefig_kwargs={"dpi": 300})
    def test_plot():
        ...

Matplotlib style
----------------
| **kwarg**: ``style=<name>``
| **CLI**: ``--mpl-default-style=<name>``
| **INI**: ``mpl-default-style = <name>``
| Default: ``"classic"``

The Matplotlib style to use when saving the figure.
See the :func:`matplotlib.style.context` ``style`` documentation for the options available.
``pytest-mpl`` will ignore any locally defined :class:`~matplotlib.RcParams`.

.. code:: python

    @pytest.mark.mpl_image_compare(style="fivethirtyeight")
    def test_plot():
        ...

.. note::

   It is recommended to use the ``"default"`` style for new code.

   .. code:: python

      @pytest.mark.mpl_image_compare(style="default")
      def test_plot():
          ...

   The ``"classic"`` style (which ``pytest-mpl`` currently uses by default) was the default style for Matplotlib versions prior to 2.0.
   A future major release of ``pytest-mpl`` *may* change the default style to ``"default"``.

Matplotlib backend
------------------
| **kwarg**: ``backend=<name>``
| **CLI**: ``--mpl-default-backend=<name>``
| **INI**: ``mpl-default-backend = <name>``
| Default: ``"agg"``

The Matplotlib backend to use when saving the figure.
See the :ref:`Matplotlib backend documentation <matplotlib:backends>` for the options available.
``pytest-mpl`` will ignore any locally defined :class:`~matplotlib.RcParams`.

Recording test results
======================

.. _results-path:

Directory to write testing artifacts to
---------------------------------------
| **kwarg**: ---
| **CLI**: ``--mpl-results-path=<path>``
| **INI**: ``mpl-results-path = <path>``
| Default: *temporary directory*

The directory to write result images and test summary reports to.
The path is relative to where pytest was run.
Absolute paths are also supported.
If the directory does not exist, it will be created along with any missing parent directories.

.. _results-always:

Whether to save result images for passing tests
-----------------------------------------------
| **kwarg**: ---
| **CLI**: ``--mpl-results-always``
| **INI**: ``mpl-results-always = <bool>``
| Default: ``False`` (``True`` if generating a HTML summary)

By default, result images are only saved for tests that fail.
Enabling this option will force result images to be saved for all tests, even for tests that pass.

When this option is enabled, and some hash comparison tests are performed, a hash library containing all the result hashes will also be saved to the root of the results directory.
The filename will be extracted from ``--mpl-generate-hash-library``, ``--mpl-hash-library``, or ``hash_library=`` in that order.

This option is applied automatically when generating a HTML summary.

.. rubric:: Relevance to "hybrid mode"

When in :doc:`"hybrid mode" <hybrid_mode>`, a baseline image comparison is only performed if the test fails hash comparison.
However, enabling this option will force a comparison to the baseline image even if the test passes hash comparison.
This option is useful for always *comparing* the result images against the baseline images, while only *assessing* the tests against the hash library.
This secondary comparison will **not** affect the success status of the test, but any failures (including diff images) will be included in generated summary reports.

Some projects store their baseline images in a separate repository, and only keep the baseline hash library in the main repository.
This means that they cannot update the baseline images until after the PR is merged.
Enabling this option allows them to ensure the hashes are correct before merging the PR, but also see how the PR affects the baseline images, as the diff images will always be shown in the HTML summary.

.. _generate-summary:

Generate test summaries
-----------------------
| **kwarg**: ---
| **CLI**: ``--mpl-generate-summary={html,json,basic-html}``
| **INI**: ``mpl-generate-summary = {html,json,basic-html}``
| Default: ``None``

This option specifies the format of the test summary report to generate, if any.
Multiple options can be specified comma-separated.
The available options are:

``html``
    Generate a HTML summary report showing the test result, log entry and generated result image.
    Results can be searched and filtered.
    When in the (default) image comparison mode, the baseline image, diff image and RMS difference (if any), and RMS tolerance of each test will also be shown.
    When in the hash comparison mode, the baseline hash and result hash will also be shown.
    When in hybrid mode, all of these are included.
``json``
    Generate a JSON summary report.
    This format includes the same information as the HTML summary, but is more suitable for automated processing.
``basic-html``
    Generate a HTML summary report with a simplified layout.
    This format does not include any JavaScript or need internet access to load web resources.

Summary reports can also be produced when generating baseline images and hash libraries.
The summaries will be written to the :ref:`results directory <results-path>`.
When generating a HTML summary, the ``--mpl-results-always`` option is automatically applied.
Therefore images for passing tests will also be shown.

For examples of how the summary reports look in different operating modes, see:

* :doc:`image_mode`
* :doc:`hash_mode`
* :doc:`hybrid_mode`
