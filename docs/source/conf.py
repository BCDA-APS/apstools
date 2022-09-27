# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

from importlib.metadata import version
import configparser
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path().absolute().parent.parent))
import apstools

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

root_path = pathlib.Path(__file__).parent.parent.parent
parser = configparser.ConfigParser()
parser.read(root_path / "setup.cfg")
metadata = parser["metadata"]

project = metadata["name"]
copyright = metadata["copyright"]
author = metadata["author"]
description = metadata["description"]
rst_prolog = f".. |author| replace:: {author}"

# -- Special handling for version numbers ------------------------------------
# https://github.com/pypa/setuptools_scm#usage-from-sphinx

release = version(project)
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = """
    sphinx.ext.autodoc
    sphinx.ext.autosummary
    sphinx.ext.coverage
    sphinx.ext.githubpages
    sphinx.ext.inheritance_diagram
    sphinx.ext.mathjax
    sphinx.ext.todo
    sphinx.ext.viewcode
    nbsphinx
    myst_parser
""".split()

templates_path = ['_templates']
source_suffix = ['.rst', '.md']
exclude_patterns = ['**.ipynb_checkpoints']

today_fmt = "%Y-%m-%d %H:%M"

# html_theme = 'alabaster'
# html_theme = 'furo'
html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']
