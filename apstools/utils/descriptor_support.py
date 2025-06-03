"""
Parsing descriptor documents
++++++++++++++++++++++++++++

.. autosummary::

   ~get_stream_data_map
"""

import logging

logger = logging.getLogger(__name__)


def get_stream_data_map(
    start_detectors: list[str],
    start_motors: list[str],
    descriptor: dict,
    report_unknown: bool = False,
) -> dict[str, list[str]]:
    """
    Return the names of the run's detector and motor signals.

    This function is used when processing the descriptor document of a run.

    PARAMETERS

    start_detectors: list[str]
        List of detectors provided to the plan (reported in start document).
    start_motors: list[str]
        List of motors provided to the plan (reported in start document).
    descriptor: dict
        The bluesky run 'descriptor' document published by the RunEngine.
    report_unknown: bool
        Should this function raise a KeyError if a signal is not found?
        Default: ``False``

    RETURNS

    Dictionary with keys: 'detectors', 'motors', 'unassigned'.
    Values are lists of signal names.

    (new in release 1.7.4)
    """
    assignments: dict[str, list[str]] = dict(
        detectors=[],
        motors=[],
        # By default, all data_keys are not assigned as motor or detector.
        unassigned=list(descriptor["data_keys"]),
    )

    # Look at the plan arguments for principle detectors and motors.
    hinted_keys: dict = descriptor.get("hints", {})
    for part, keys in dict(detectors=start_detectors, motors=start_motors).items():
        for key in keys:  # Cherry-pick any hinted or named parts.
            candidates: list[str] = []
            hinted_key_fields = hinted_keys.get(key, {}).get("fields", [])
            if len(hinted_key_fields) > 0:
                # hinted fields take priority
                candidates += hinted_key_fields

            elif key in descriptor.get("object_keys", {}):
                # The key might be an object which has one or more fields (like
                # a motor or a scaler). The optional 'object_keys' provides the
                # field list for an object.
                candidates += descriptor["object_keys"][key]

            elif key in descriptor["data_keys"]:
                # Final test: is the key known, at all?
                candidates.append(key)

            elif report_unknown:
                raise KeyError(f"{key!r} unknown in {part!r} list")

            for item in candidates:  # Reassign the candidates ...
                if item in assignments["unassigned"]:  # ... not already assigned.
                    assignments["unassigned"].remove(item)
                    assignments[part].append(item)

    return assignments
