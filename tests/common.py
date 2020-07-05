
"""
Common methods for unit tests.

.. autosummary::
   
   ~Capture_stderr
   ~Capture_stdout
"""

from io import StringIO
import sys


class Capture_stdout(list):     # lgtm [py/missing-equals]

    """
    Capture all printed output (to stdout) into list.
    
    # https://stackoverflow.com/questions/16571150
    # how-to-capture-stdout-output-from-a-python-function-call
    """

    def __enter__(self):
        sys.stdout.flush()
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


class Capture_stderr(list):     # lgtm [py/missing-equals]

    """Capture stderr into list."""

    def __enter__(self):
        sys.stderr.flush()
        self._stderr = sys.stderr
        sys.stderr = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stderr = self._stderr
