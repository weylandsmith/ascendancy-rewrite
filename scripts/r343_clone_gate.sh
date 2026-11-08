#!/usr/bin/env bash
# t343 portability probe: clone the repo from local disk (file://, zero network)
# and run the quality gate in the clone, capturing VERBATIM per-stage output.
# Usage: r343_clone_gate.sh <dest-dir> [run-label]
# Never touches the source tree except as a clone source.
set -u
SRC=$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)
DEST="${1:?dest dir required}"
LABEL="${2:-run1}"
if [ -e "$DEST" ]; then echo "REFUSING: $DEST already exists (fresh clone per run)"; exit 2; fi
OUTDIR="$SRC/work/r343"
mkdir -p "$OUTDIR"
echo "== cloning file://$SRC -> $DEST"
git clone --quiet "file://$SRC" "$DEST" || { echo "CLONE FAILED"; exit 1; }
echo "== clone HEAD: $(git -C "$DEST" rev-parse --short HEAD)"
echo "== clone tree size: $(du -sh "$DEST" | cut -f1)"
cd "$DEST" || exit 1
echo "== gate run ($LABEL) start $(date -Is)"
bash scripts/gate.sh > "$OUTDIR/clone-${LABEL}-gate.out" 2>&1
rc=$?
echo "== gate run ($LABEL) exit=$rc end $(date -Is)"
echo "== stdout/stderr saved: $OUTDIR/clone-${LABEL}-gate.out ($(wc -l < "$OUTDIR/clone-${LABEL}-gate.out") lines)"
# stage-shaped lines only, verbatim
grep -n -E '^\[gate' "$OUTDIR/clone-${LABEL}-gate.out" | sed 's/^/  /' | tail -60
exit "$rc"
