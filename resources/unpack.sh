#!/bin/bash

# file: unpack.sh
# purpose: unpack databroker test data

CAT+=" apstools_test"
CAT+=" usaxs_test"
TMP=/tmp  # TODO: What about Windows?
SRC=$(dirname $(readlink -f $0))

for c in ${CAT}; do
    echo ${SRC}/${c}.zip
    unzip -u ${SRC}/${c}.zip -d ${TMP}
    databroker-unpack inplace  ${TMP}/${c}   ${c}
done

# show all available catalogs
databroker-pack --list

# --------------------------------------------------------------------
# Copy any generated databroker intake YAMLs from the user XDG
# data directory into the active environment's share/intake so that
# Python processes (pytest, coverage, etc.) will find them even if
# HOME/XDG_DATA_HOME differs across steps.
# Place this after the databroker-pack --list call in resources/unpack.sh
# --------------------------------------------------------------------

# Resolve source intake dir (respect XDG_DATA_HOME if set, else fallback)
SRC="${XDG_DATA_HOME:-$HOME/.local/share}/intake"
if [ ! -d "$SRC" ]; then
    echo "No user intake dir found at ${SRC}; skipping catalog copy."
else
    # Find matching databroker YAML files
    shopt -s nullglob
    FILES=( "$SRC"/databroker_unpack_*.yml )
    shopt -u nullglob

    if [ ${#FILES[@]} -eq 0 ]; then
        echo "No databroker_unpack_*.yml files found in ${SRC}; nothing to copy."
    else
        echo "Found ${#FILES[@]} databroker YAML(s) in ${SRC}:"
        for f in "${FILES[@]}"; do echo "  - $f"; done

        # Candidate destinations: common environment prefixes
        DESTS=()
        [ -n "$CONDA_PREFIX" ] && DESTS+=( "$CONDA_PREFIX/share/intake" )
        [ -n "$MAMBA_ROOT_PREFIX" ] && DESTS+=( "$MAMBA_ROOT_PREFIX/share/intake" )
        [ -n "$MICROMAMBA_PREFIX" ] && DESTS+=( "$MICROMAMBA_PREFIX/share/intake" )

        # Also attempt to query intake's configured search paths (if python is available)
        if command -v python >/dev/null 2>&1; then
            # Print each path on its own line and append to DESTS
            while IFS= read -r p; do
                [ -n "$p" ] && DESTS+=( "$p" )
            done < <(python - <<'PY'
try:
    import intake
    for p in intake.catalog_search_path():
        print(p)
except Exception:
    # If intake cannot be imported in this shell, produce nothing
    pass
PY
)
        fi

        # De-duplicate DESTS while preserving order
        uniq_dest=()
        declare -A _seen_dest=()
        for d in "${DESTS[@]}"; do
            [ -z "$d" ] && continue
            if [ -z "${_seen_dest[$d]:-}" ]; then
                _seen_dest[$d]=1
                uniq_dest+=( "$d" )
            fi
        done

        # Copy files to each destination
        for d in "${uniq_dest[@]}"; do
            if [ -z "$d" ]; then
                continue
            fi
            mkdir -p "$d" || { echo "Warning: failed to create $d"; continue; }
            for f in "${FILES[@]}"; do
                if cp -v "$f" "$d"/; then
                    : # success message already printed by cp -v
                else
                    echo "Warning: failed to copy $f -> $d" >&2
                fi
            done
        done

        echo "Catalog YAML copy complete."
    fi
fi
