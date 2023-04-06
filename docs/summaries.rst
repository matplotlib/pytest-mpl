.. title:: Summary Reports

###############
Summary Reports
###############

Generating a Test Summary
^^^^^^^^^^^^^^^^^^^^^^^^^

By specifying the ``--mpl-generate-summary=html`` CLI argument, a HTML summary
page will be generated showing the test result, log entry and generated result
image. When in the (default) image comparison mode, the baseline image, diff
image and RMS (if any), and tolerance of each test will also be shown.
When in the hash comparison mode, the baseline hash and result hash will
also be shown. When in hybrid mode, all of these are included.

When generating a HTML summary, the ``--mpl-results-always`` option is
automatically applied (see section below). Therefore images for passing
tests will also be shown.

+---------------+---------------+---------------+
| |html all|    | |html filter| | |html result| |
+---------------+---------------+---------------+

As well as ``html``, ``basic-html`` can be specified for an alternative HTML
summary which does not rely on JavaScript or external resources. A ``json``
summary can also be saved. Multiple options can be specified comma-separated.

.. card:: Image comparison only

    .. code-block:: bash

        pytest --mpl \
          --mpl-results-path=results \
          --mpl-generate-summary=html,json

    :summary:`test_html_images_only`

.. card:: Hash comparison only

    .. code-block:: bash

        pytest --mpl \
          --mpl-hash-library=mpl35_ft261.json \
          --mpl-results-path=results \
          --mpl-generate-summary=html,json

    :summary:`test_html_hashes_only`

.. card:: Hybrid mode: hash and image comparison

    .. code-block:: bash

        pytest --mpl \
          --mpl-hash-library=mpl35_ft261.json \
          --mpl-baseline-path=baseline \
          --mpl-results-path=results \
          --mpl-generate-summary=html,json

    :summary:`test_html`

.. card:: Generating baseline images and hashes (With no testing)

    .. code-block:: bash

        pytest --mpl \
          --mpl-generate-path=baseline \
          --mpl-generate-hash-library=test_hashes.json \
          --mpl-results-path=results \
          --mpl-generate-summary=html,json

    :summary:`test_html_generate`

.. card:: Generating baseline images (With no testing)

    .. code-block:: bash

        pytest --mpl \
          --mpl-generate-path=baseline \
          --mpl-results-path=results \
          --mpl-generate-summary=html,json

    :summary:`test_html_generate_images_only`

.. card:: Generating baseline hashes (With image comparison)

    .. code-block:: bash

        pytest --mpl \
          --mpl-generate-hash-library=test_hashes.json \
          --mpl-results-path=results \
          --mpl-generate-summary=html,json

    :summary:`test_html_generate_hashes_only`

.. card:: Generating baseline hashes (With hash comparison)

    .. code-block:: bash

        pytest --mpl \
          --mpl-generate-hash-library=test_hashes.json \
          --mpl-hash-library=mpl35_ft261.json \
          --mpl-results-path=results \
          --mpl-generate-summary=html,json

    :summary:`test_html_run_generate_hashes_only`

.. card:: Hybrid mode: hash and image comparison

    .. code-block:: bash

        pytest --mpl \
          --mpl-hash-library=mpl35_ft261.json \
          --mpl-baseline-path=baseline \
          --mpl-results-path=results \
          --mpl-generate-summary=basic-html,json

    :summary:`test_basic_html`

.. |html all| image:: images/html_all.png
.. |html filter| image:: images/html_filter.png
.. |html result| image:: images/html_result.png
