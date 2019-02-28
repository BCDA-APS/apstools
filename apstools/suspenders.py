
"""

(bluesky) custom support for pausing a running plan

.. autosummary::
   
    ~SuspendWhenChanged

"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

from bluesky.suspenders import SuspenderBase


class SuspendWhenChanged(SuspenderBase):
    """
    Bluesky suspender
    
    Suspend when the monitored value deviates from the expected.
    Only resume if allowed AND when monitored equals expected.
    Default expected value is current value when object is created.
    
    USAGE::

        # pause if this value changes in our session
        # note: this suspender is designed to require Bluesky restart if value changes
        suspend_instrument_in_use = SuspendWhenChanged(instrument_in_use)
        RE.install_suspender(suspend_instrument_in_use)

    """
    # see: http://nsls-ii.github.io/bluesky/_modules/bluesky/suspenders.html#SuspendCeil
    
    def __init__(self, signal, *, 
                expected_value=None,
                allow_resume=False,
                sleep=0, pre_plan=None, post_plan=None, tripped_message='',
                **kwargs):
        
        self.expected_value = expected_value or signal.value
        self.allow_resume = allow_resume
        super().__init__(signal, 
            sleep=sleep, 
            pre_plan=pre_plan, 
            post_plan=post_plan, 
            tripped_message=tripped_message,
            **kwargs)

    def _should_suspend(self, value):
        return value != self.expected_value

    def _should_resume(self, value):
        return self.allow_resume and value == self.expected_value

    def _get_justification(self):
        if not self.tripped:
            return ''

        just = 'Signal {}, got "{}", expected "{}"'.format(
            self._sig.name,
            self._sig.get(),
            self.expected_value)
        if not self.allow_resume:
            just += '.  '
            just += '"RE.abort()" to finalize current data streams (if any)'
            just += ' and then restart bluesky session to clear this.'
        return ': '.join(s for s in (just, self._tripped_message)
                         if s)

