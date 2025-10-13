#!/bin/bash

# List of documentation versions to keep.
# (should include all versions in switcher.json)
# Adding future versions will capture that version
# once it appears in the downloaded gh-pages branch.


# versions (typically release tags) to be kept if they exist
versions=

# drop docs for these versions
# versions+=" 1.6.6"
# versions+=" 1.6.8"
# versions+=" 1.6.9"
# versions+=" 1.6.11"  # no docs for this version
# versions+=" 1.6.12"  # no docs for this version
# versions+=" 1.6.10"
# versions+=" 1.6.13"
# versions+=" 1.6.14"
# versions+=" 1.6.15"
# versions+=" 1.6.16"
# versions+=" 1.7.4"

# existing versions
versions+=" 1.6.17"
versions+=" 1.6.18"
versions+=" 1.6.19"
versions+=" 1.6.20"
versions+=" 1.7.0"
versions+=" 1.7.1"
versions+=" 1.7.2"
versions+=" 1.7.3"
versions+=" 1.7.6"
versions+=" 1.7.7"
versions+=" 1.7.8"
versions+=" 1.7.9"

# future versions (release tags that are expected)
versions+=" 1.7.10"
versions+=" 1.7.11"
versions+=" 1.7.12"

export versions

# update file `docs/source/_static/switcher.json` before each new release
