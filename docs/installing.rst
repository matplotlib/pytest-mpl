.. title:: Installation Guide

##################
Installation Guide
##################

This plugin is compatible with Python 3.6 and later, and
requires `pytest <http://pytest.org>`__ and
`matplotlib <http://www.matplotlib.org>`__ to be installed.

Using pip
=========

``pytest-mpl`` can be installed with ``pip``:

.. code-block:: bash

    pip install pytest-mpl


Using conda
===========

Installing ``pytest-mpl`` from the ``conda-forge`` channel can be achieved by adding ``conda-forge`` to your channels with:

.. code-block:: bash

    conda config --add channels conda-forge
    conda config --set channel_priority strict

Once the ``conda-forge`` channel has been enabled, ``pytest-mpl`` can be installed with ``conda``:

.. code-block:: bash

    conda install pytest-mpl

or with ``mamba``:

.. code-block:: bash

    mamba install pytest-mpl

It is possible to list all of the versions of ``pytest-mpl`` available on your platform with ``conda``:

.. code-block:: bash

    conda search pytest-mpl --channel conda-forge

or with ``mamba``:

.. code-block:: bash

    mamba search pytest-mpl --channel conda-forge

Alternatively, ``mamba repoquery`` may provide more information:

.. code-block:: bash

    # Search all versions available on your platform:
    mamba repoquery search pytest-mpl --channel conda-forge

    # List packages depending on pytest-mpl:
    mamba repoquery whoneeds pytest-mpl --channel conda-forge

    # List dependencies of pytest-mpl:
    mamba repoquery depends pytest-mpl --channel conda-forge

Installing the development version
==================================

Clone the `pytest-mpl GitHub repository <https://github.com/matplotlib/pytest-mpl>`__, or your own fork of it.
Then install ``pytest-mpl`` using ``pip`` from the root directory of the repo:

.. code-block:: bash

    pip install -e ".[test,docs]"


Troubleshooting
===============

To check that ``pytest-mpl`` has been installed correctly and is recognised by ``pytest``, run:

.. code-block:: bash

    pytest --trace-config
