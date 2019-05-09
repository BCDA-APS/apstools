# Packaging Hints

## PyPI upload

Preceed the wildcard with tag text (`apstools-1.1.1*`)::

	python setup.py sdist bdist_wheel
	twine upload dist/*

## Conda upload

In the upload command below, use the text reported 
at (near) the end of a successful conda build.

	conda build ./conda-recipe/
	anaconda upload -u aps-anl-tag /home/mintadmin/Apps/anaconda/conda-bld/noarch/apstools-1.1.1-py_0.tar.bz2

* `aps-anl-tag` production releases
* `aps-anl-dev` anything else, such as: pre-release, release candidates, or testing purposes
