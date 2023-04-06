.. title:: pytest-mpl documentation

.. module:: pytest-mpl

.. toctree::
    :hidden:

    installing
    usage
    configuration
    summaries

##################################
pytest-mpl |release| documentation
##################################

``pytest-mpl`` is a `pytest <https://docs.pytest.org>`__ plugin to facilitate image comparison for `Matplotlib <http://www.matplotlib.org>`__ figures.

For each figure to test, an image is generated and then subtracted from an existing reference image.
If the RMS of the residual is larger than a user-specified tolerance, the test will fail.
Alternatively, the generated image can be hashed and compared to an expected value.

************
Installation
************

.. grid:: 1 1 2 2

    .. grid-item::

        Install using `pip <https://pypi.org/project/pytest-mpl>`__:

        .. code-block:: bash

            pip install pytest-mpl

    .. grid-item::

        Install from `conda-forge <https://github.com/conda-forge/pytest-mpl-feedstock#installing-pytest-mpl>`__ using `conda <https://docs.continuum.io/anaconda/>`__:

        .. code-block:: bash

            conda install pytest-mpl

Further details are available in the :doc:`Installation Guide <installing>`.


******************
Learning resources
******************

.. grid:: 1 1 2 2

    .. grid-item-card::
        :padding: 2

        Tutorials
        ^^^

        - :doc:`Basic usage <usage>`

    .. grid-item-card::
        :padding: 2

        How-tos
        ^^^


    .. grid-item-card::
        :padding: 2

        Understand how pytest-mpl works
        ^^^


    .. grid-item-card::
        :padding: 2

        Reference
        ^^^

        - :doc:`Configuration <configuration>`
        - :doc:`Summary Reports <summaries>`


************
Contributing
************

pytest-mpl is a community project maintained for and by its users.
There are many ways you can help!

- Report a bug or request a feature `on GitHub <https://github.com/matplotlib/pytest-mpl/issues>`__
- Improve the documentation or code
