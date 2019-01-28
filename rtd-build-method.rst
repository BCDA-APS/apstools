Simulate the RTD build
######################

Documentation builds on ReadTheDocs.io (RTD) are a
challenge when the Python code imports packages
that involve C (or other) language components
that are not already part of the RTD standard
build environment.  RTD has a remedy for such builds,
to use a virtual environment (setting on the *admin*
page of the project).  RTD also supports conda
which greatly simplifies the establishment of a
working code base.

Use a custom Conda Environment
******************************

This project will describe the requirements
for a custom conda environment in which
RTD will build the documentation.

Create the conda environment
============================

If you have not already done this, create a custom 
conda environment.  Call it *toolsdoc*. ::

    conda create -n toolsdoc python=3 sphinx sphinx_rtd_theme
    pip install versioneer

For me, this proposed to install some packages::

    Fetching package metadata .........
    Solving package specifications: .
    
    Package plan for installation in environment /.../anaconda/envs/toolsdoc:
    
    The following NEW packages will be INSTALLED:
    
        cairo:      1.14.8-0     
        fontconfig: 2.12.1-3     
        ...
    Proceed ([y]/n)? 



You can get a list of all conda environments currently
created using this command::

    conda env list

Build docs in the custom conda environment
==========================================

Use the *toolsdoc* custom conda environment,
as created before::

    source activate toolsdoc
    conda install -c lightsource2-tag bluesky ophyd
    cd ~/Documents/eclipse/apstools

Check that the documentation builds with no errors::
 
   cd docs
   make clean
   make html

which produced this output::

   rm -rf build/*
   sphinx-build -b html -d build/doctrees   source build/html
   Running Sphinx v1.5.1
   making output directory...
   loading pickled environment... not yet created
   building [mo]: targets for 0 po files that are out of date
   building [html]: targets for 7 source files that are out of date
   updating environment: 7 added, 0 changed, 0 removed
   ...
   Build finished. The HTML pages are in build/html.

The warnings about "nonlocal image" are acceptable since they refer to the 
project *badges* used in the `README.rst` file.

Build the `.readthedocs.yml` file for RTD
=========================================

Referring to the `RTD instructions for conda 
builds <https://docs.readthedocs.io/en/latest/conda.html>`_, 
create a `.readthedocs.yml` file in the root of the repository
with this content::

   conda:
       file: environment.yml

That's all it needs.  Next, we'll build that `environment.yml` file.

Build the `environment.yml` file for conda
==========================================

Use the `conda instructions <https://conda.io/docs/using/envs.html>`_ 
to create the `environment.yml` file for the project.  Configure
it for the packages you installed in the environment using conda and 
pip.  In short, execute this command line in the root of the project::

   conda env export > environment.yml

To avoid demanding any unecessary requirements, such as specific versions,
it may be desireable to edit this file and specify just those packages
requested by this project and widen the acceptable versions using `*`,
`>=`, `>` or even removing specific version number requirements.
This step may take iteration to fine-tune the requirements for the environment.
Refer to the steps to build the `environment.yml` file 
`by hand <https://conda.io/docs/using/envs.html#create-environment-file-by-hand>`_.

Note: Since the standard conda install of Qt is release 5, it is necessary
to pin, at least, the major version number to 4 for the *toolsdoc* package.

Local Test of the RTD build procedure
*************************************

Tear down the custom conda environment::

    source deactivate
    conda env remove -n toolsdoc

Re-build the project documentation using 
the configuration files that were setup.
This command will create the conda environment 
as described above::

   conda env create -f environment.yml

RTD: use virtual environment
****************************

On RTD, configure the project to build in a virtual environment
and use the `environment.yml` file from the project.

Push to GitHub and test the build by RTD
****************************************

Save all these files, commit, and push to the GitHub master.
Since GH has been configured to notify RTD of any new commits,
the build should be triggered in seconds to start automatically.
Look for it at the project's RTD build pages.
