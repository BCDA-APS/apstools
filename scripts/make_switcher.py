"""
Generate ``docs/source/_static/switcher.json`` from git tags.

Pruning rule
------------
- ``dev`` entry always included first (points to ``dev/`` on gh-pages).
- All patches for the **current** (highest) ``major.minor``.
- Only the **latest patch** for every older ``major.minor``.

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
    """Return all final release version tags sorted newest-first.

    Excludes pre-release tags (alpha, beta, rc) and the old date-based
    tags (e.g. ``2019.0321.1``) that pre-date the ``1.x.y`` scheme.
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
        if v.is_prerelease or v.is_devrelease:
            continue  # skip rc, alpha, beta, dev tags
        if v.major == 0 or v.epoch != 0:
            continue  # skip 0.x.y and old date-based epoch tags
        # skip old date-style tags (major >= 2019)
        if v.major >= 2019:
            continue
        tags.append(t)
    return tags


def prune(tags):
    """
    Apply the pruning rule and return the ordered list of version strings
    to include in the switcher (newest first).

    - All patches for the highest major.minor.
    - Latest patch only for every older major.minor.
    """
    if not tags:
        return []

    parsed = [(t, Version(t)) for t in tags]
    # highest major.minor
    current_minor = (parsed[0][1].major, parsed[0][1].minor)

    kept = []
    seen_minor = set()
    for tag, v in parsed:
        minor_key = (v.major, v.minor)
        if minor_key == current_minor:
            kept.append(tag)  # keep all patches for current minor
        elif minor_key not in seen_minor:
            kept.append(tag)  # keep only latest patch for older minors
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
    latest_tag = versions[0] if versions else None

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
