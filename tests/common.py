
"""
common methods for unit tests
"""

from io import StringIO
import sys


class Capture_stdout(list):     # lgtm [py/missing-equals]
    '''
    capture all printed output (to stdout) into list
    
    # http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
    '''
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
    '''
    capture stderr into list
    '''
    def __enter__(self):
        sys.stderr.flush()
        self._stderr = sys.stderr
        sys.stderr = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stderr = self._stderr
