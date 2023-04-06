# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime
from packaging.version import Version

from pytest_mpl import __version__

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'pytest-mpl'
author = 'Thomas Robitaille'
copyright = '{}, {}'.format(datetime.datetime.now().year, author)

release = __version__
pytest_mpl_version = Version(__version__)
is_release = not (pytest_mpl_version.is_prerelease or pytest_mpl_version.is_devrelease)


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sample_summaries',
    'sphinx.ext.intersphinx',
    'sphinx_design',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
    "matplotlib": ("https://matplotlib.org/stable", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "mpl_sphinx_theme"
html_theme_options = {
    "navbar_links": "absolute",
    "show_prev_next": False,
    "logo": {"link": "https://matplotlib.org/stable/",
             "image_light": "images/logo_light.svg",
             "image_dark": "images/logo_dark.svg"},
    "collapse_navigation": False,
}
html_sidebars = {
    "**": ["mpl_third_party_sidebar.html", "sidebar-nav-bs.html"]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']
