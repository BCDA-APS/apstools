#!/usr/bin/env pytest

from ..apsbss import main
from ..apsbss import getCurrentCycle
import sys


def test_myoutput(capsys): # or use "capfd" for fd-level
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
    sys.argv = [
        sys.argv[0],
        "list",
    ]
    main()
    out, err = capsys.readouterr()
    assert getCurrentCycle() in str(out)
    assert err.strip() == ""


def test_cycle_blank(capsys):
    sys.argv = [
        sys.argv[0],
        "list",
        "--cycle",
        "",
    ]
    main()
    out, err = capsys.readouterr()
    assert getCurrentCycle() in str(out)
    assert err.strip() == ""


def test_cycle_now(capsys):
    sys.argv = [
        sys.argv[0],
        "list",
        "--cycle",
        "now",
    ]
    main()
    out, err = capsys.readouterr()
    assert getCurrentCycle() in str(out)
    assert err.strip() == ""


def test_cycle_previous(capsys):
    sys.argv = [
        sys.argv[0],
        "list",
        "--cycle",
        "previous",
    ]
    main()
    out, err = capsys.readouterr()
    assert "tba" in str(out)
    assert err.strip() == ""


def test_cycle_future(capsys):
    sys.argv = [
        sys.argv[0],
        "list",
        "--cycle",
        "future",
    ]
    main()
    out, err = capsys.readouterr()
    assert "tba" in str(out)
    assert err.strip() == ""


def test_cycle_by_name(capsys):
    sys.argv = [
        sys.argv[0],
        "list",
        "--cycle",
        "2020-2",
    ]
    main()
    out, err = capsys.readouterr()
    assert "2020-2" in str(out)
    assert err.strip() == ""
