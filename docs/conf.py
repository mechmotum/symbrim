# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

# Add source folder to path for autodoc
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "BRiM"
copyright = "2023, Timo Stienstra"  # noqa: A001
author = "Timo Stienstra"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinxcontrib.bibtex",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

napoleon_numpy_docstring = True
napoleon_custom_sections = [("Explanation", "notes_style")]

intersphinx_mapping = {
    "sympy": ("https://docs.sympy.org/dev/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "symmeplot": ("https://tjstienstra.github.io/symmeplot/", None),
}

bibtex_bibfiles = ["references.bib"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
