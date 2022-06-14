Testing ``pytest-mpl`` using the ``tests/subtests``
**************************************************

``pytest-mpl`` can output JSON summaries (``--mpl-generate-summary=json``) which contain lots of machine readable information relating to the internal state of the plugin while it was run.
This test module (``test_subtest.py``) runs the test file ``subtest.py`` multiple times with different combinations of
``pytest-mpl`` arguments.
After each test, it compares the outputted JSON summary to a "baseline" JSON summary for that specific combination of arguments (``summaries/*.json``).

These tests are very sensitive to deviations in the documented behaviour of the ``pytest-mpl`` configuration arguments.
And the exact behaviour of each comparison mode (such as images, hashes or both) can be asserted.
If the format of the hash libraries or the baseline summaries are changed, ``test_subtest.py`` and ``helpers.py`` may require modifications.

By using various helper functions defined in ``helpers.py``, the baseline summaries are not specific to the MPL/FreeType versions.
This is implemented through regex in the log output, and by replacing baseline hashes with hashes in a version specific baseline hash library ``hashes/*.json`` and replacing result hashes with hashes in a version specific "baseline" result hash library ``result_hashes/*.json``.
The baseline images used for the image comparison tests are included in ``baseline/*.png``.

Generating baseline data
========================

The baseline image, hashes and summaries are generated automatically without the need to manually set the data which should fail the tests which are expected to fail.
All of the test names should follow the existing convention (e.g., ``test_hdiff_imatch``), including one flag from both of the categories below.
This ensures the script generates the correct baseline data which should achieve the expected test result.
Full details on how the baselines are modified for each case are given below:

**Hash comparison status flags:**

:``hmatch``: Hash comparison must pass, so same hash in baseline and result hash libraries.

:``hdiff``: Hash comparison must fail, so baseline hash is set to the same as the result hash except the first four characters are changed to ``d1ff``.

:``hmissing``: Baseline hash must be missing, so baseline hash is deleted from the baseline hash library but not the result hash library.

**Image comparison status flags:**

:``imatch``: Image comparison must pass, so correct image is included in the baseline directory.

:``idiff``: Image comparison must fail, so baseline image is edited to include a red cross such that the RMS is greater than the tolerance.

:``idiffshape``: Image comparison must fail due to a different shape, so baseline image is resized to be half the generated width and height before saving.

:``imissing``: Baseline image must be missing, so baseline image is deleted from the baseline directory.

Generating for each version of matplotlib
-----------------------------------------

Baseline data should be generated for each version of matplotlib separately.
For each version of matplotlib (defined within the tox environments in ``tox.ini``), follow the three steps in this section. (Only update one version at a time.)

So the baseline data can be recreated easily, do not make any manual adjustments to the generated files.
Instead, updates the functions which generate the baseline data.

To generate the baseline hashes, result hashes and baseline images run the following command.
If you are generating for a new version of matplotlib, create empty files such as ``hashes/mpl39_ft261.json`` and ``result_hashes/mpl39_ft261.json`` so it knows you require hashes for this version.

::

  MPL_UPDATE_BASELINE=1 tox -e <envname>

Make sure this command runs without any failures or errors.
Inspect the generated data to ensure it looks correct, and ``git add``.
Then generate baseline summaries for the baseline hashes and images by running:

::

  MPL_UPDATE_SUMMARY=1 tox -e <envname>

This will update/create baseline summaries in the ``summaries`` directory.
Make sure this command runs without any failures or errors.
It is very important that you check every change made to the baseline summaries as these summaries define how the plugin should be running internally for each test, for each plugin configuration.
If the summaries are correct, ``git add``.

Now run tox normally to ensure the tests pass:

::

  tox -e <envname>

If the tests pass, ``git commit`` the updated baselines.
