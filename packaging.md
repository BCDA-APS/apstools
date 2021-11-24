# Packaging Hints

## Pre-release

1. Close all relevant issues and pull requests.
2. Run `git status` and verify
   1. on *main* branch
   2. no uncommitted content
   3. repo is synchronized with *origin*
3. update `CHANGES.rst`

## Tag the new version

Follow [semantic versioning](https://semver.org) principles.

1. empty commit: `git commit --allow-empty -m "REL: X.Y.Z"`
2. make the tag: `git tag -a X.Y.Z`
3. verify version: `python ./setup.py version`
4. push the empty commit: `git push origin main`
5. push the new tag: `git push origin --tags`

## PyPI upload

Packaging for PyPI (`pip` installation) is covered by a GitHub Actions workflow.

## Conda upload

Packaging for Anaconda (`conda` installation) is covered by a GitHub Actions
workflow.

### Conda channels

Builds of this package are uploaded to these conda channels:

* [*aps-anl-tag*](https://anaconda.org/aps-anl-tag) : all releases starting 2021-11-24

<!-- 
* [*aps-anl-dev*](https://anaconda.org/aps-anl-dev) : anything else, such as: pre-release, release candidates, or testing purposes
-->
