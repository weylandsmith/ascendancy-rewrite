#!/usr/bin/env bash
# refcap_gate.sh — end-to-end reference-capture comparison in one run:
#   1. scripts/ref_capture.sh boots the ORIGINAL (dosbox-x + Xvfb), screenshots
#      the title menu, clicks Play Introduction, screenshots the movie.
#   2. scripts/refcap_match.py scores the title shot (--expect not-movie) and
#      EVERY movie shot (--expect movie) against the intro65a union palette
#      (the decode the C++ port is golden-pinned to).
# Requires: Xvfb, ImageMagick(import), dosbox-x, ~/tools/revenv (PIL).
# Exit: 0 all scores as expected; 2 capture or score failure; 3 tools missing.
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
PY="$HOME/tools/revenv/bin/python"
[ -x "$PY" ] || { echo "MISSING $PY (PIL host)"; exit 3; }
for t in Xvfb import dosbox-x; do
  command -v "$t" >/dev/null || { echo "MISSING $t"; exit 3; }
done

# Click "Play Introduction": window sits at root +0+40 (measured via
# xwininfo), band centre of button 1 is root y 252 -> window-relative 212.
export CLICK_X="${CLICK_X:-318}" CLICK_Y="${CLICK_Y:-212}"
export BOOT_WAIT="${BOOT_WAIT:-9}" SHOTS="${SHOTS:-7}"
export INTERVAL_MS="${INTERVAL_MS:-900}" TIME_LIMIT="${TIME_LIMIT:-60}"
OUTDIR=$(bash scripts/ref_capture.sh 2>/dev/null | sed -n 's/^REFCAP OUT=//p' | tail -1)
[ -n "$OUTDIR" ] && [ -d "$OUTDIR" ] || { echo "capture failed"; exit 2; }
echo "captured into $OUTDIR"
ls "$OUTDIR"/frame-*.png >/dev/null 2>&1 || { echo "no frames"; exit 2; }

FAIL=0
# frame-00 is pre-click (title menu); the click fires after frame-01, so
# frame-02+ must be movie (BOOT_WAIT leaves the menu up; click latency 2 s).
if ! "$PY" scripts/refcap_match.py "$OUTDIR/frame-00.png" --expect not-movie; then
  echo "CONTROL VIOLATION: title menu scored as movie"; FAIL=1
fi
movie_ok=0
for f in "$OUTDIR"/frame-0[2-9].png "$OUTDIR"/frame-1*.png; do
  [ -e "$f" ] || continue
  "$PY" scripts/refcap_match.py "$f" --expect movie || FAIL=1
  movie_ok=$((movie_ok + 1))
done
if [ "$movie_ok" -eq 0 ]; then echo "no movie shots scored"; exit 2; fi

if [ "$FAIL" = 0 ]; then
  echo "REFCAP GATE PASS: original movie pixels obey the reference-decode palette law; menu control obeys its negation"
  exit 0
fi
echo "REFCAP GATE FAIL"
exit 2
