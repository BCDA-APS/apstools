"""
Update the ending year in copyright notices to the current year.

Handles both patterns used in this repository:

    # :copyright: (c) 2017-2026, UChicago Argonne, LLC   (Python files)
    Copyright (c) 2017-2026, UChicago Argonne, LLC        (LICENSE.txt, etc.)

Usage (called automatically by the pre-commit hook)::

    python scripts/update_copyright.py <file1> [<file2> ...]
"""

import re
import sys
from datetime import datetime

CURRENT_YEAR = str(datetime.now().year)

# Matches all patterns used in this repository:
#   # :copyright: (c) 2017-2026, ...     (Python files)
#   Copyright (c) 2017-2026, ...         (LICENSE.txt, etc.)
#   copyright = "2017-2026, ...          (pyproject.toml)
COPYRIGHT_RE = re.compile(
    r"((?:#\s*:copyright:|Copyright)\s*\(c\)\s*|copyright\s*=\s*\")(\d{4})(-\d{4})?(\s*,)",
    re.IGNORECASE,
)


def _replace(match):
    prefix = match.group(1)
    start_year = match.group(2)
    suffix = match.group(4)
    if start_year == CURRENT_YEAR:
        return f"{prefix}{start_year}{suffix}"
    return f"{prefix}{start_year}-{CURRENT_YEAR}{suffix}"


def update_file(filepath):
    """Return True if the file was modified."""
    text = open(filepath, encoding="utf-8").read()
    new_text = COPYRIGHT_RE.sub(_replace, text)
    if new_text != text:
        open(filepath, "w", encoding="utf-8").write(new_text)
        return True
    return False


if __name__ == "__main__":
    for path in sys.argv[1:]:
        update_file(path)
