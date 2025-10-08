#!/bin/bash

# file: unpack.sh
# purpose: unpack databroker test data

CAT+=" apstools_test"
CAT+=" usaxs_test"
TMP=$(mktemp -d)
SRC=$(dirname $(readlink -f $0))

# If running inside an activated conda/micromamba environment, prefer
# writing user XDG data into the active environment share so that
# intake/databroker will pick up the generated YAMLs from the env.
if [ -n "${CONDA_PREFIX:-}" ]; then
    export XDG_DATA_HOME="$CONDA_PREFIX/share"
    mkdir -p "$XDG_DATA_HOME/intake"
    echo "Set XDG_DATA_HOME -> $XDG_DATA_HOME (intake YAMLs will go to $XDG_DATA_HOME/intake)"
fi

for c in ${CAT}; do
    echo ${SRC}/${c}.zip
    unzip -u ${SRC}/${c}.zip -d ${TMP}
    databroker-unpack inplace  ${TMP}/${c}   ${c}
done

# show all available catalogs
databroker-pack --list

# Verification: print available catalogs and intake search path and
# fail if the same unpack YAML filename appears in more than one search
# path (this indicates duplication which can cause Intake conflicts).
python - <<'PY'
import sys, os, glob
try:
    import databroker
except Exception as e:
    print('databroker not importable:', e, file=sys.stderr)
    sys.exit(0)

print('databroker.catalog entries:', list(databroker.catalog))
# Try to get the intake/databroker search path and preserve order.
paths = []
try:
    sp = databroker.catalog_search_path()
    print('intake/databroker catalog_search_path():', sp)
    paths = list(sp)
except Exception:
    # older/databroker variations
    try:
        from intake import catalog as intake_catalog
        sp = intake_catalog.catalog_search_path()
        print('intake.catalog_search_path():', sp)
        paths = list(sp)
    except Exception:
        paths = []

# Deduplicate search paths while preserving order (some APIs return duplicates)
seen_paths = set()
unique_paths = []
for p in paths:
    if not p:
        continue
    if p not in seen_paths:
        seen_paths.add(p)
        unique_paths.append(p)

# detect duplicate unpack YAML filenames across unique intake search paths
seen = {}
for p in unique_paths:
    if not os.path.isdir(p):
        continue
    for y in glob.glob(os.path.join(p, 'databroker_unpack_*.yml')):
        b = os.path.basename(y)
        seen.setdefault(b, []).append(p)

# Only consider real duplicates when the same YAML file basename exists in
# more than one distinct directory.
dups = {k: v for k, v in seen.items() if len(v) > 1}
if dups:
    print('Duplicate unpack YAML filenames found in multiple intake search paths:', file=sys.stderr)
    for k, v in dups.items():
        print(f'  {k}:', file=sys.stderr)
        for p in v:
            print(f'    - {p}', file=sys.stderr)
    # Exit nonzero so CI fails early and we can inspect
    sys.exit(2)

print('Catalog verification complete.')
PY
