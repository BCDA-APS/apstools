"""
Generate ``docs/source/_static/switcher.json`` from git tags.

Pruning rule
------------
- ``dev`` entry always included first (points to ``dev/`` on gh-pages).
- All patches for the **current** (highest) ``major.minor``, including
  the latest rc tag if no final release exists yet for that patch.
- Only the **latest patch** for every older ``major.minor``.
- rc tags are dropped for any patch that has a final (non-rc) release.
- Only the **latest rc** is kept when no final release exists yet.

Run this script locally as part of the release process, then commit
the updated ``switcher.json`` to ``main`` before triggering the docs
deploy workflow::

    python scripts/make_switcher.py
    git add docs/source/_static/switcher.json
    git commit -m "DOC: update switcher.json for <version>"
    git push

"""

import json
import subprocess
from pathlib import Path

from packaging.version import Version

BASE_URL = "https://bcda-aps.github.io/apstools"
SWITCHER_FILE = Path(__file__).parent.parent / "docs" / "source" / "_static" / "switcher.json"


def git_tags():
    """Return all relevant version tags sorted newest-first.

    Includes final releases and rc tags, but excludes:
    - alpha/beta/dev pre-releases
    - 0.x.y tags
    - old date-based tags (major >= 2019)
    """
    result = subprocess.run(
        ["git", "tag", "--sort=-version:refname"],
        capture_output=True,
        text=True,
        check=True,
    )
    tags = []
    for line in result.stdout.splitlines():
        t = line.strip()
        if not t:
            continue
        try:
            v = Version(t)
        except Exception:
            continue  # skip non-PEP-440 tags
        if v.is_devrelease:
            continue
        # keep rc tags but drop alpha/beta
        if v.is_prerelease and v.pre and v.pre[0] in ("a", "b"):
            continue
        if v.major == 0 or v.epoch != 0:
            continue
        if v.major >= 2019:
            continue
        tags.append(t)
    return tags


def prune(tags):
    """
    Apply the pruning rule and return the ordered list of version strings
    to include in the switcher (newest first).

    - All patches for the highest major.minor (final releases only, plus
      the latest rc for any patch that has no final release yet).
    - Latest patch only for every older major.minor (final releases only;
      rc tags for older minors are dropped entirely once a final exists).
    """
    if not tags:
        return []

    parsed = [(t, Version(t)) for t in tags]

    # Collect the set of base versions that have a final (non-rc) release.
    final_bases = set()
    for _, v in parsed:
        if not v.is_prerelease:
            final_bases.add((v.major, v.minor, v.micro))

    # highest major.minor among final releases
    finals = [(t, v) for t, v in parsed if not v.is_prerelease]
    if not finals:
        # all tags are rc — use the highest rc to determine current minor
        current_minor = (parsed[0][1].major, parsed[0][1].minor)
    else:
        current_minor = (finals[0][1].major, finals[0][1].minor)

    kept = []
    seen_minor = set()  # for older minors (final releases only)
    seen_patch_rc = set()  # track latest rc per base version

    for tag, v in parsed:
        minor_key = (v.major, v.minor)
        base = (v.major, v.minor, v.micro)
        is_rc = v.is_prerelease

        if minor_key == current_minor:
            if is_rc:
                # Include latest rc for this patch only if no final exists.
                if base not in final_bases and base not in seen_patch_rc:
                    kept.append(tag)
                    seen_patch_rc.add(base)
                # else: skip — either a final exists or we already have a newer rc
            else:
                kept.append(tag)  # keep all final patches for current minor
        else:
            # Older minor: keep only the latest final patch.
            if not is_rc and minor_key not in seen_minor:
                kept.append(tag)
                seen_minor.add(minor_key)

    return kept


def make_entry(version, latest_tag):
    """Build a single switcher.json entry."""
    is_latest = version == latest_tag
    name = f"{version} (latest)" if is_latest else version
    return {
        "name": name,
        "version": version,
        "url": f"{BASE_URL}/{version}/",
    }


def build_switcher(tags):
    """Return the full switcher list including the dev entry."""
    versions = prune(tags)

    # "latest" is the highest final (non-rc) release only.
    latest_tag = next(
        (v for v in versions if not Version(v).is_prerelease),
        None,
    )

    entries = [
        {
            "name": "development (main branch)",
            "version": "dev",
            "url": f"{BASE_URL}/dev/",
        }
    ]
    for v in versions:
        entries.append(make_entry(v, latest_tag))
    return entries


def main():
    tags = git_tags()
    if not tags:
        print("No version tags found.")
        return

    entries = build_switcher(tags)

    old_text = SWITCHER_FILE.read_text() if SWITCHER_FILE.exists() else ""
    new_text = json.dumps(entries, indent=4) + "\n"

    if new_text == old_text:
        print(f"No changes to {SWITCHER_FILE}")
    else:
        SWITCHER_FILE.write_text(new_text)
        print(f"Updated {SWITCHER_FILE} ({len(entries)} entries)")
        for e in entries:
            print(f"  {e['name']:40s}  {e['url']}")


if __name__ == "__main__":
    main()
