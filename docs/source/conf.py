# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import configparser
import json
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

gh_org = "BCDA-APS"
project = project
release = apstools.__version__
version = ".".join(release.split(".")[:2])

# fmt: off
switcher_file = "_static/switcher.json"
switcher_json_url = (
    "https://raw.githubusercontent.com/"
    f"{gh_org}/{project}/"
    "main/docs/source"
    f"/{switcher_file}"
)
switcher_version_list = [
    v["version"]  # to match with ``release`` (above)
    for v in json.load(open(switcher_file))
]
# fmt: on

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = """
    IPython.sphinxext.ipython_console_highlighting
    IPython.sphinxext.ipython_directive
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

templates_path = ["_templates"]
source_suffix = [".rst", ".md"]
exclude_patterns = ["**.ipynb_checkpoints"]

today_fmt = "%Y-%m-%d %H:%M"

html_css_files = [
    "css/custom.css",
]
html_static_path = ["_static"]
html_theme = "pydata_sphinx_theme"
# fmt: off
html_theme_options = {
    "navbar_start": ["navbar-logo", "version-switcher"],
    "switcher": {
        "json_url": switcher_json_url,
        "version_match": release if release in switcher_version_list else "dev"
    }
}
# fmt: on

autodoc_mock_imports = """
    bluesky
    dask
    databroker
    databroker_pack
    epics
    h5py
    intake
    numpy
    openpyxl
    ophyd
    pandas
    pint
    psutil
    pyRestTable
    pysumreg
    spec2nexus
    xarray
""".split()
