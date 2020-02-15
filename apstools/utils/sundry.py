
"""
various and sundry utilities, defying further categorization

.. autosummary::
   
   ~cleanupText
   ~itemizer
   ~pairwise
   ~split_quoted_line
   ~text_encode
"""

__all__ = """
    cleanupText
    itemizer
    pairwise
    split_quoted_line
    text_encode
""".split()

import logging
logger = logging.getLogger(__name__)

import re


def cleanupText(text):
    """
    convert text so it can be used as a dictionary key

    Given some input text string, return a clean version
    remove troublesome characters, perhaps other cleanup as well.
    This is best done with regular expression pattern matching.
    """
    pattern = "[a-zA-Z0-9_]"

    def mapper(c):
        if re.match(pattern, c) is not None:
            return c
        return "_"

    return "".join([mapper(c) for c in text])


def itemizer(fmt, items):
    """format a list of items"""
    return [fmt % k for k in items]


def pairwise(iterable):
    """
    break a list (or other iterable) into pairs
    
    ::
    
		s -> (s0, s1), (s2, s3), (s4, s5), ...
		
		In [71]: for item in pairwise("a b c d e fg".split()): 
			...:     print(item) 
			...:                                                                                                                         
		('a', 'b')
		('c', 'd')
		('e', 'fg')
  
    """
    a = iter(iterable)
    return zip(a, a)


def split_quoted_line(line):
    """
    splits a line into words some of which might be quoted

    TESTS::

        FlyScan 0   0   0   blank
        FlyScan 5   2   0   "empty container"
        FlyScan 5   12   0   "even longer name"
        SAXS 0 0 0 blank
        SAXS 0 0 0 "blank"

    RESULTS::

        ['FlyScan', '0', '0', '0', 'blank']
        ['FlyScan', '5', '2', '0', 'empty container']
        ['FlyScan', '5', '12', '0', 'even longer name']
        ['SAXS', '0', '0', '0', 'blank']
        ['SAXS', '0', '0', '0', 'blank']

    """
    parts = []

    # look for open and close quoted parts and combine them
    quoted = False
    multi = None
    for p in line.split():
        if not quoted and p.startswith('"'):   # begin quoted text
            quoted = True
            multi = ""

        if quoted:
            if len(multi) > 0:
                multi += " "
            multi += p
            if p.endswith('"'):     # end quoted text
                quoted = False

        if not quoted:
            if multi is not None:
                parts.append(multi[1:-1])   # remove enclosing quotes
                multi = None
            else:
                parts.append(p)

    return parts


def text_encode(source):
    """encode ``source`` using the default codepoint"""
    return source.encode(errors='ignore')
