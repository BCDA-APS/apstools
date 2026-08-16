# Awaitable Devices Using *ophyd-async*

The devices defined here are subject to change. Feedback is welcome.

This folder contains **experimental** devices written using the
*ophyd-async* library instead of classic (threaded) *ophyd*. Using
*ophyd-async* requires installing apstools with the ``[async]``
extra. As such, it should not be imported from the rest of *apstools*
without making *ophyd_async* a default dependency.
