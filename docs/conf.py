"""Sphinx configuration."""

project = "Amber Input File Generator"
author = "Timothy Click"
copyright = "2025, Timothy Click"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
