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
2. make the tag: `git tag X.Y.Z`
3. verify version: `python ./setup.py version`
4. push the empty commit: `git push`
5. push the new tag: `git push --tags`

## Create Release Notes

1.Create the notes:

   ```bash
   ../../prjemian/condatools/create_release_notes.py \
      --head main \
      ${previous_tag} \
      ${current_milestone_name} \
      ${github_api_token} \
      | tee /tmp/notes.md
   ```

2. Copy `/tmp/notes.md` to the GH wiki, creating a new page.
3. On the GH web site, create the new release.
4. Close the project for this release.
5. Close the milestone for this release.
6. Delete local branches that are merged or discarded.

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
