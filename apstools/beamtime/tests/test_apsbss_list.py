#!/usr/bin/env pytest

from ..apsbss import getCurrentCycle
from ..apsbss import main
from .utils import is_aps_workstation
import pytest
import sys


def test_myoutput(capsys):  # or use "capfd" for fd-level
    """Example test capturing stdout and stderr for testing."""
    print("hello")
    sys.stderr.write("world\n")
    out, err = capsys.readouterr()
    assert out == "hello\n"
    assert err == "world\n"
    print("next")
    out, err = capsys.readouterr()
    assert out.strip() == "next"
    assert err.strip() == ""


def test_no_cycle_given(capsys):
    if is_aps_workstation():
        sys.argv = [
            sys.argv[0],
            "list",
            "9-ID-B,C",
        ]
        main()
        out, err = capsys.readouterr()
        assert getCurrentCycle() in str(out)
        assert err.strip() == ""


def test_cycle_all(capsys):
    if is_aps_workstation():
        sys.argv = [
            sys.argv[0],
            "list",
            "9-ID-B,C",
            "--cycle",
            "all",
        ]
        main()
        out, err = capsys.readouterr()
        assert "2020-1" in str(out)
        assert err.strip() == ""


def test_cycle_future(capsys):
    if is_aps_workstation():
        sys.argv = [
            sys.argv[0],
            "list",
            "9-ID-B,C",
            "--cycle",
            "future",
        ]
        main()
        out, err = capsys.readouterr()
        assert "status" in str(out)
        assert err.strip() == ""


def test_cycle_blank(capsys):
    if is_aps_workstation():
        sys.argv = [
            sys.argv[0],
            "list",
            "9-ID-B,C",
            "--cycle",
            "",
        ]
        main()
        out, err = capsys.readouterr()
        assert getCurrentCycle() in str(out)
        assert err.strip() == ""


def test_cycle_by_name(capsys):
    if is_aps_workstation():
        sys.argv = [
            sys.argv[0],
            "list",
            "9-ID-B,C",
            "--cycle",
            "2020-2",
        ]
        main()
        out, err = capsys.readouterr()
        assert "2020-2" in str(out)
        assert err.strip() == ""


def test_cycle_now(capsys):
    if is_aps_workstation():
        sys.argv = [
            sys.argv[0],
            "list",
            "9-ID-B,C",
            "--cycle",
            "now",
        ]
        main()
        out, err = capsys.readouterr()
        assert getCurrentCycle() in str(out)
        assert err.strip() == ""


def test_cycle_not_found():
    if is_aps_workstation():
        sys.argv = [
            sys.argv[0],
            "list",
            "9-ID-B,C",
            "--cycle",
            "not-a-cycle",
        ]
        with pytest.raises(KeyError) as exc:
            main()
        assert "Could not find APS run cycle" in str(exc.value)


def test_cycle_previous(capsys):
    if is_aps_workstation():
        for when in "past previous prior".split():
            sys.argv = [
                sys.argv[0],
                "list",
                "9-ID-B,C",
                "--cycle",
                when,
            ]
            main()
            out, err = capsys.readouterr()
            assert "Approved" in str(out)
            assert err.strip() == ""


def test_cycle_recent(capsys):
    if is_aps_workstation():
        sys.argv = [
            sys.argv[0],
            "list",
            "9-ID-B,C",
            "--cycle",
            "recent",
        ]
        main()
        out, err = capsys.readouterr()
        assert "status" in str(out)
        assert err.strip() == ""
