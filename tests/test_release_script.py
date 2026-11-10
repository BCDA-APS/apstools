import importlib
import sys
from contextlib import nullcontext as does_not_raise
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

release = importlib.import_module("scripts.release")


CHANGES_SAMPLE = """Change History
##############

History of changes in the *apstools* project.

..
   1.7.10
   ******

   Release expected by 2026-05-01.

   Enhancements
   ------------

   Fixes
   -----

   Maintenance
   -----------

..
   1.7.11
   ******

   Release expected by 2026-06-01.

   Enhancements
   ------------

   Fixes
   -----

   Maintenance
   -----------

1.7.9
*****

Released 2025-10-13.
"""


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(
                text=CHANGES_SAMPLE,
                expected_versions=["1.7.10", "1.7.11"],
            ),
            does_not_raise(),
            id="find-both-commented-sections",
        ),
    ],
)
def test_split_commented_sections(parms, context):
    with context:
        sections = release.split_commented_sections(parms["text"])
        assert [release.upcoming_version(section) for section in sections] == parms["expected_versions"]


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(
                text=CHANGES_SAMPLE,
                expected_version="1.7.11",
            ),
            does_not_raise(),
            id="pick-later-upcoming-section",
        ),
        pytest.param(
            dict(
                text=CHANGES_SAMPLE.replace(
                    "..\n   1.7.11\n   ******\n\n   Release expected by 2026-06-01.\n\n   Enhancements\n   ------------\n\n   Fixes\n   -----\n\n   Maintenance\n   -----------\n\n",
                    "",
                ),
                expected_version=None,
            ),
            does_not_raise(),
            id="no-later-upcoming-section",
        ),
    ],
)
def test_next_upcoming_section(parms, context):
    with context:
        section = release.next_upcoming_section(parms["text"])
        if parms["expected_version"] is None:
            assert section is None
        else:
            assert release.upcoming_version(section) == parms["expected_version"]


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(
                text="1.7.9\n*****\n\nReleased 2025-10-13.\n",
                new_section=release.new_commented_section("1.7.11", "2026-05-01"),
                expected_prefix="..\n   1.7.11\n   ******\n\n   Release expected by 2026-05-01.\n",
            ),
            does_not_raise(),
            id="insert-explicit-section-verbatim",
        ),
    ],
)
def test_insert_new_section(parms, context):
    with context:
        text = release.insert_new_section(parms["text"], parms["new_section"])
        assert text.startswith(parms["expected_prefix"])


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(
                version_str="1.7.13",
                expected="1.7.14",
            ),
            does_not_raise(),
            id="bump-patch-version",
        ),
        pytest.param(
            dict(
                version_str="1.8.0",
                expected="1.8.1",
            ),
            does_not_raise(),
            id="bump-patch-from-minor-release",
        ),
    ],
)
def test_next_micro_version(parms, context):
    with context:
        result = release.next_micro_version(parms["version_str"])
        assert result == parms["expected"]


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(
                release_date="2026-11-03",
                days_ahead=30,
                expected="2026-12-03",
            ),
            does_not_raise(),
            id="30-days-ahead-from-release",
        ),
        pytest.param(
            dict(
                release_date="2026-11-03",
                days_ahead=1,
                expected="2026-11-04",
            ),
            does_not_raise(),
            id="1-day-ahead-from-release",
        ),
    ],
)
def test_next_milestone_date(parms, context):
    with context:
        result = release.next_milestone_date(parms["release_date"], days_ahead=parms["days_ahead"])
        assert result == parms["expected"]


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(
                rc_tag="1.7.10rc2",
                changes_text=CHANGES_SAMPLE,
                expected_message="Would preserve next section for: 1.7.11",
            ),
            does_not_raise(),
            id="dry-run-preserves-staged-patch-release",
        ),
    ],
)
def test_cmd_final_dry_run_preserves_existing_next_section(parms, context, monkeypatch, capsys):
    with context:
        monkeypatch.setattr(release, "assert_clean", lambda: None)
        monkeypatch.setattr(release, "assert_main", lambda: None)
        monkeypatch.setattr(release, "latest_rc_tag", lambda: parms["rc_tag"])
        monkeypatch.setattr(release, "read_changes", lambda: parms["changes_text"])

        release.cmd_final(dry_run=True)

        output = capsys.readouterr().out
        assert parms["expected_message"] in output


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(
                rc_tag="1.7.10rc1",
                changes_text=CHANGES_SAMPLE.replace(
                    "..\n   1.7.11\n   ******\n\n   Release expected by 2026-06-01.\n\n   Enhancements\n   ------------\n\n   Fixes\n   -----\n\n   Maintenance\n   -----------\n\n",
                    "",
                ),
                expected_message="Would auto-generate new section for: 1.7.11",
            ),
            does_not_raise(),
            id="dry-run-auto-generates-next-section-when-missing",
        ),
    ],
)
def test_cmd_final_dry_run_generates_next_section_when_missing(parms, context, monkeypatch, capsys):
    with context:
        monkeypatch.setattr(release, "assert_clean", lambda: None)
        monkeypatch.setattr(release, "assert_main", lambda: None)
        monkeypatch.setattr(release, "latest_rc_tag", lambda: parms["rc_tag"])
        monkeypatch.setattr(release, "read_changes", lambda: parms["changes_text"])

        release.cmd_final(dry_run=True)

        output = capsys.readouterr().out
        # When no next section exists, the dry-run should indicate it will auto-generate the next version
        assert parms["expected_message"] in output
