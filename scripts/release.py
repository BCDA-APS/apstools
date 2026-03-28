"""
Release helper for apstools.

Usage
-----
Prepare an rc tag (first rc or subsequent rc)::

    python scripts/release.py rc

Promote an rc to a final release::

    python scripts/release.py final

Show what the next version would be without doing anything::

    python scripts/release.py --dry-run rc
    python scripts/release.py --dry-run final

What each command does
----------------------

``rc``
~~~~~~
1. Determine the next rc version from the current state of git tags:
   - If the upcoming release section in ``CHANGES.rst`` has no rc tag yet,
     create ``<next_version>rc1``.
   - If the latest tag is ``<version>rcN``, create ``<version>rc(N+1)``.
2. Tag the repo with the new rc version (e.g. ``1.7.10rc1``).
3. Run ``scripts/make_switcher.py`` to update ``switcher.json``.
4. Commit ``switcher.json`` to main.
5. Push the tag and the commit.

``final``
~~~~~~~~~
1. Determine the final version from the latest rc tag
   (strips the ``rcN`` suffix, e.g. ``1.7.10rc2`` → ``1.7.10``).
2. Uncomment the upcoming release section in ``CHANGES.rst`` and replace
   the "Release expected by …" line with "Released YYYY-MM-DD."
3. Insert a new commented-out section for the next minor version.
4. Run ``scripts/make_switcher.py`` to update ``switcher.json``.
5. Commit ``CHANGES.rst`` and ``switcher.json`` to main.
6. Tag the repo with the final version (e.g. ``1.7.10``).
7. Push the commit and the tag.
8. Print a reminder to trigger the docs deploy workflow.

Prerequisites
-------------
- Run from the repository root on the ``main`` branch.
- No uncommitted changes.
- The upcoming release section in ``CHANGES.rst`` must be commented out
  (indented with ``.. `` as shown in the file header).
"""

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

from packaging.version import Version

ROOT = Path(__file__).parent.parent
CHANGES = ROOT / "CHANGES.rst"


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def run(cmd, check=True, capture=True):
    return subprocess.run(cmd, check=check, capture_output=capture, text=True)


def git_tags():
    """Return all tags sorted newest-first by date."""
    result = run(["git", "tag", "--sort=-creatordate"])
    return [t.strip() for t in result.stdout.splitlines() if t.strip()]


def latest_tag():
    """Return the most recent tag (any kind)."""
    tags = git_tags()
    return tags[0] if tags else None


def latest_rc_tag():
    """Return the most recent rc tag, or None."""
    for t in git_tags():
        try:
            v = Version(t)
            if v.is_prerelease and v.pre and v.pre[0] == "rc":
                return t
        except Exception:
            continue
    return None


def latest_final_tag():
    """Return the most recent final (non-rc) tag, or None."""
    for t in git_tags():
        try:
            v = Version(t)
            if not v.is_prerelease:
                return t
        except Exception:
            continue
    return None


def assert_clean():
    """Exit if there are uncommitted changes."""
    result = run(["git", "status", "--porcelain"])
    if result.stdout.strip():
        print("ERROR: uncommitted changes detected. Commit or stash them first.")
        print(result.stdout)
        sys.exit(1)


def assert_main():
    """Exit if not on the main branch."""
    result = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    branch = result.stdout.strip()
    if branch != "main":
        print(f"ERROR: must be on 'main' branch (currently on '{branch}').")
        sys.exit(1)


# ---------------------------------------------------------------------------
# CHANGES.rst helpers
# ---------------------------------------------------------------------------

# Pattern that marks the start of the upcoming (commented-out) release section.
# Matches lines like:  ..
#                         1.7.10
_COMMENT_BLOCK_RE = re.compile(
    r"^\.\.\n(   \d+\.\d+\.\d+\n   \*+\n\n   Release expected by (\d{4}-\d{2}-\d{2})\..*?)(?=^\d|\Z)",
    re.MULTILINE | re.DOTALL,
)
_UPCOMING_VERSION_RE = re.compile(r"^   (\d+\.\d+\.\d+)\n   \*+", re.MULTILINE)
_EXPECTED_DATE_RE = re.compile(r"   Release expected by \d{4}-\d{2}-\d{2}\.")


def read_changes():
    return CHANGES.read_text(encoding="utf-8")


def upcoming_version(text):
    """Return the version string from the commented-out upcoming section."""
    m = _UPCOMING_VERSION_RE.search(text)
    if not m:
        raise ValueError(
            f"Could not find upcoming version section in {CHANGES}.\n"
            "Expected a commented-out block like:\n"
            "..\n"
            "   1.7.10\n"
            "   ******\n"
            "   Release expected by YYYY-MM-DD."
        )
    return m.group(1)


def next_minor_version(version_str):
    """Return the next minor version string, e.g. '1.7.10' → '1.8.0'."""
    v = Version(version_str)
    return f"{v.major}.{v.minor + 1}.0"


def uncomment_release_section(text, version_str, release_date):
    """
    Remove the ``..`` comment wrapper from the upcoming release section and
    replace 'Release expected by …' with 'Released YYYY-MM-DD.'.

    The commented block uses 3-space indentation under ``..``.  Remove the
    leading ``..\\n`` and de-indent each body line by 3 spaces.
    """
    # Find the commented block: starts with "..\n   <version>\n   ***..."
    pattern = re.compile(
        r"\.\.\n((?:   [^\n]*\n|\n)+?)(?=\n\d|\Z)",
        re.DOTALL,
    )

    def replacer(m):
        body = m.group(1)
        # de-indent by 3 spaces
        lines = body.split("\n")
        deindented = []
        for line in lines:
            if line.startswith("   "):
                deindented.append(line[3:])
            else:
                deindented.append(line)
        result = "\n".join(deindented)
        # replace expected date line
        result = _EXPECTED_DATE_RE.sub(f"Released {release_date}.", result)
        return result

    new_text = pattern.sub(replacer, text, count=1)
    return new_text


def new_commented_section(next_version, milestone_date):
    """Return RST text for a new commented-out upcoming release section."""
    stars = "*" * len(next_version)
    return (
        f"..\n"
        f"   {next_version}\n"
        f"   {stars}\n"
        f"\n"
        f"   Release expected by {milestone_date}.\n"
        f"\n"
        f"   Enhancements\n"
        f"   ------------\n"
        f"\n"
        f"   Fixes\n"
        f"   -----\n"
        f"\n"
        f"   Maintenance\n"
        f"   -----------\n"
        f"\n"
    )


def insert_new_section(text, next_version):
    """Insert a new commented-out section at the top of the change history."""
    # Insert just before the first real release heading (e.g. "1.7.9\n*****")
    first_release = re.search(r"^(\d+\.\d+\.\d+\n\*+)", text, re.MULTILINE)
    if not first_release:
        raise ValueError("Could not find first release heading in CHANGES.rst.")
    idx = first_release.start()
    # Use a placeholder date one year from now; maintainer adjusts to milestone
    today = date.today()
    milestone_date = f"{today.year + 1}-{today.month:02d}-01"
    new_section = new_commented_section(next_version, milestone_date)
    return text[:idx] + new_section + text[idx:]


# ---------------------------------------------------------------------------
# make_switcher helper
# ---------------------------------------------------------------------------


def run_make_switcher():
    run(["python", "scripts/make_switcher.py"], capture=False)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_rc(dry_run=False):
    """Tag the next rc version."""
    assert_clean()
    assert_main()

    # Determine next rc version.
    rc_tag = latest_rc_tag()

    # What version does CHANGES.rst say is upcoming?
    text = read_changes()
    up_ver = upcoming_version(text)

    if rc_tag:
        rc_v = Version(rc_tag)
        rc_base = f"{rc_v.major}.{rc_v.minor}.{rc_v.micro}"
        if rc_base == up_ver:
            # Increment rc number.
            new_rc_num = rc_v.pre[1] + 1
            new_tag = f"{up_ver}rc{new_rc_num}"
        else:
            new_tag = f"{up_ver}rc1"
    else:
        new_tag = f"{up_ver}rc1"

    print(f"Next rc tag: {new_tag}")
    if dry_run:
        print("(dry run — no changes made)")
        return

    # Tag.
    run(["git", "tag", new_tag])
    print(f"Tagged: {new_tag}")

    # Update switcher.json.
    run_make_switcher()

    # Commit switcher if changed.
    switcher = ROOT / "docs" / "source" / "_static" / "switcher.json"
    result = run(["git", "diff", "--quiet", str(switcher)], check=False)
    if result.returncode != 0:
        run(["git", "add", str(switcher)], capture=False)
        run(
            ["git", "commit", "-m", f"DOC: update switcher.json for {new_tag}"],
            capture=False,
        )

    # Push tag and commit.
    run(["git", "push", "origin", "main", new_tag], capture=False)
    print(f"\nDone. rc tag {new_tag} pushed.")
    print("CI will publish to PyPI automatically (rc packages are published).")
    print("Watch conda-forge for any issues before running: python scripts/release.py final")


def cmd_final(dry_run=False):
    """Promote the latest rc to a final release."""
    assert_clean()
    assert_main()

    rc_tag = latest_rc_tag()
    if not rc_tag:
        print("ERROR: no rc tag found. Run 'python scripts/release.py rc' first.")
        sys.exit(1)

    rc_v = Version(rc_tag)
    final_version = f"{rc_v.major}.{rc_v.minor}.{rc_v.micro}"
    final_tag = final_version  # tag == version string

    print(f"Promoting {rc_tag} → {final_tag}")

    text = read_changes()
    up_ver = upcoming_version(text)
    if up_ver != final_version:
        print(f"ERROR: CHANGES.rst upcoming version ({up_ver}) does not match rc base version ({final_version}).")
        sys.exit(1)

    if dry_run:
        next_ver = next_minor_version(final_version)
        print(f"Would release: {final_tag}")
        print(f"Would create next section for: {next_ver}")
        print("(dry run — no changes made)")
        return

    # 1. Uncomment and datestamp the release section.
    today = date.today().isoformat()
    text = uncomment_release_section(text, final_version, today)

    # 2. Insert new commented section for the next minor.
    next_ver = next_minor_version(final_version)
    text = insert_new_section(text, next_ver)
    CHANGES.write_text(text, encoding="utf-8")
    print(f"Updated {CHANGES.name}")

    # 3. Update switcher.json (tag not yet placed, so rc still appears).
    run_make_switcher()

    # 4. Commit CHANGES.rst + switcher.json.
    switcher = ROOT / "docs" / "source" / "_static" / "switcher.json"
    run(["git", "add", str(CHANGES), str(switcher)], capture=False)
    run(
        [
            "git",
            "commit",
            "-m",
            f"REL: release {final_tag}\n\nUncomment CHANGES.rst, add next section, update switcher.json.",
        ],
        capture=False,
    )

    # 5. Tag the final release.
    run(["git", "tag", final_tag])
    print(f"Tagged: {final_tag}")

    # 6. Re-run switcher now that the final tag exists (drops rc entries).
    run_make_switcher()
    result = run(["git", "diff", "--quiet", str(switcher)], check=False)
    if result.returncode != 0:
        run(["git", "add", str(switcher)], capture=False)
        run(
            ["git", "commit", "-m", f"DOC: update switcher.json after tagging {final_tag}"],
            capture=False,
        )

    # 7. Push.
    run(["git", "push", "origin", "main", final_tag], capture=False)

    print(f"\nDone. Final release {final_tag} tagged and pushed.")
    print("PyPI publish will start automatically via CI.")
    print(
        f"\nNext steps:\n"
        f"  1. Verify the PyPI release: https://pypi.org/project/apstools/{final_tag}/\n"
        f"  2. Update switcher.json and trigger docs deploy:\n"
        f"     gh workflow run docs.yml -f deploy=true\n"
        f"  3. Close the GitHub milestone for {final_tag}.\n"
        f"  4. Create a GitHub release from the {final_tag} tag.\n"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "command",
        choices=["rc", "final"],
        help="'rc' to tag an rc release; 'final' to promote to a final release",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without making any changes",
    )
    args = parser.parse_args()

    if args.command == "rc":
        cmd_rc(dry_run=args.dry_run)
    elif args.command == "final":
        cmd_final(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
