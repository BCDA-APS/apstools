@ECHO OFF

REM post this project to PyPI


python setup.py sdist bdist_wheel upload
