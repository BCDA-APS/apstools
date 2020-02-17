
"""
prints document contents

.. autosummary::
   
   ~document_contents_callback
"""

__all__ = ["document_contents_callback",]


import logging
logger = logging.getLogger(__name__)


def document_contents_callback(key, doc):
    """
    prints document contents -- use for diagnosing a document stream
    """
    print(key)
    for k, v in doc.items():
        print(f"\t{k}\t{v}")
