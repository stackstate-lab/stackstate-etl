#!/bin/bash
set -eu

die () { echo "ERROR: $*" >&2; exit 2; }

for cmd in pdoc3; do
    command -v "$cmd" >/dev/null ||
        die "Missing $cmd; \`pip install $cmd\`"
done

pip install importlib_metadata==4.11.3

DOCROOT="$(dirname "$(readlink -f "$0")")"
BUILDROOT="$DOCROOT/build"

echo
echo 'Building API reference docs'
echo
mkdir -p "$BUILDROOT"
rm -r "$BUILDROOT" 2>/dev/null || true
pushd "$DOCROOT/.." >/dev/null
pdoc3 --html \
     ${IS_RELEASE:+--template-dir "$DOCROOT/pdoc_template"} \
     --output-dir "$BUILDROOT" \
     stackstate_etl
popd >/dev/null

echo
echo "All good. Docs in: $BUILDROOT"
echo
echo "    file://$BUILDROOT/pdoc/index.html"
echo
