#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# R1 DEEPER CAPTURE (STATE.md NEXT ACTION 2026-10-05k): drive the ORIGINAL
# game past its title screen under dosbox-x using the coordinates
# scripts/ref_capture.sh / docs/re/refcap.md prove clickable, so the
# autosave law (docs/re/r1-savestate.md) writes save states that carry
# loaded game DATA, not just title-screen state. Slot-diff early(title) vs
# late(in-game) is the evidence source for OQ-003/010/015/016: pointer-law
# decode d = rv - P0 resolves absolute pointers even in pages the static
# restore never touched.
#
# SAFETY: identical invariants to r1_savestate.sh — scratch copy only,
# stdin=/dev/null, -time-limit hard bound, kill only `pkill -x dosbox-x`,
# Xvfb killed by tracked PID, logs size-capped. Clicks are synthetic
# button1 via tools/xsend (refcap gate proves dosbox-x honours them).
#
# Env: DISPNO(93) BOOT(180) BOOT_WAIT(15) DEEP_BYTES(100000) SHOT_PERIOD(0=off)
#      SCHEDULE="sec:x:y;sec:x:y;..."  window-relative click points (law:
#      root = window + 40; default 293 window = 333 root = New Game,
#      confirmed via deep_census newgame.txt strings 2026-10-05k).
# Exit: 0 = payload anchored AND deep (>= DEEP_BYTES changed title->last)
#       1 = ran but shallow / negative      2 = harness error
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
BOOT="${BOOT:-180}"
BOOT_WAIT="${BOOT_WAIT:-15}"
DISP="${DISPNO:-93}"
DEEP_BYTES="${DEEP_BYTES:-100000}"
# BASELINE LAW (measured 2026-10-05k, twice): first autosave lands ~62 s
# after Xvfb start; a click before that leaves NO pre-click slot and the
# diff is post-vs-post = false shallow. Default click t=75 keeps a title-
# screen baseline AND the setup screen loads within the run window.
SCHEDULE="${SCHEDULE:-75:318:293}"
# VERIFY_NEEDLE: a byte string proven unique to the TARGET screen and absent
# before the click (e.g. 'cosmic exiles' = newgame.txt race blurbs, measured
# 2026-10-05k). Synthetic clicks are FLAKY against dosbox-x (run1 landed,
# run2 warped but no button event fired): after each scheduled click we
# re-click on a 11 s cadence (autosave=10 law gives one save per check) and
# STOP as soon as the needle shows up in the newest slot — so a screen that
# already transitioned receives at most the one click that triggered it.
# NOTE `${VAR-default}` NOT `${VAR:-default}`: an EXPLICIT empty needle must
# mean "no needle check" (the :- form silently resurrects the default and the
# baseline guard then fires a false exit 2 — hit 2026-10-06).
VERIFY_NEEDLE="${VERIFY_NEEDLE-cosmic exiles}"
MAX_EXTRA_CLICKS="${MAX_EXTRA_CLICKS:-5}"
OUT="$ROOT/work/r1/r1deep-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" || exit 2
SCRATCH="$ROOT/work/r1/game"

command -v Xvfb >/dev/null && command -v import >/dev/null || { echo "MISSING Xvfb/import"; exit 2; }
command -v dosbox-x >/dev/null || { echo "MISSING dosbox-x"; exit 2; }
[ -x "$ROOT/tools/xsend" ] || { echo "MISSING tools/xsend (gate 4c builds it)"; exit 2; }

pkill -x dosbox-x 2>/dev/null && sleep 1
[ -f "$SCRATCH/ascend.exe" ] || {
  mkdir -p "$SCRATCH/data" || exit 2
  cp -a "$ROOT/game/." "$SCRATCH/" || exit 2
  cp -a "$ROOT/extracted/ascend00/." "$SCRATCH/" 2>/dev/null
  cp -a "$ROOT/extracted/ascend02/data/." "$SCRATCH/data/" 2>/dev/null
}

Xvfb ":$DISP" -screen 0 640x480x24 >"$OUT/xvfb.out" 2>&1 &
XV=$!
sleep 1

# conf law measured in r1_savestate.sh: captures=$OUT/caps -> states land in
# $OUT/save; autosave=10 41-60 fires every 10 s across the whole measured
# boot (slots 41..60 rotate): 6 saves per 60 s.
CONF="$OUT/r1deep.conf"
cat > "$CONF" <<EOF
[dosbox]
machine=svga_s3
memsize=16
captures=$OUT/caps
autosave=10 41-60
saveremark=false
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C $SCRATCH
C:
ASCEND.EXE
EOF

DISPLAY=":$DISP" timeout -s KILL $((BOOT + 40)) dosbox-x -conf "$CONF" -nogui \
  -time-limit "$BOOT" </dev/null >"$OUT/dosbox.out" 2>&1 &
DB=$!

shot() { DISPLAY=":$DISP" import -window root "$OUT/shot-$(printf %02d $1).png" 2>/dev/null; }

needle_present() {
  # newest autosave slot's Memory member contains $VERIFY_NEEDLE? (member is
  # deflate-defensible; go through zipfile, not grep-on-zip)
  local newest_f
  newest_f=$(ls -t "$OUT"/save/*.sav 2>/dev/null | head -1)
  [ -n "$newest_f" ] || return 1
  python3 -c '
import sys, zipfile, re
needle = sys.argv[2].encode("latin-1")
try:
    mem = zipfile.ZipFile(sys.argv[1]).read("Memory")
except Exception:
    sys.exit(1)
sys.exit(0 if needle in mem else 1)
' "$newest_f" "$VERIFY_NEEDLE"
}

T0=$(date +%s)
sleep 5; shot 0
i=1
DONE_SCHED=""
EXTRA_X=""; EXTRA_Y=""; EXTRA_LEFT=0; NEXT_EXTRA=0
NEXT_PERIODIC=$((T0 + ${SHOT_PERIOD:-0}))
while kill -0 "$DB" 2>/dev/null; do
  NOW=$(( $(date +%s) - T0 ))
  if [ "${SHOT_PERIOD:-0}" -gt 0 ] && [ "$(date +%s)" -ge "$NEXT_PERIODIC" ]; then
    shot $((i)); i=$((i+1)); NEXT_PERIODIC=$((NEXT_PERIODIC + SHOT_PERIOD))
  fi
  # verification-driven retry: needle present = click landed -> stop retrying;
  # absent + past next save window -> re-click the same point (bounded).
  if [ -n "$EXTRA_X" ] && [ "$EXTRA_LEFT" -gt 0 ]; then
    if needle_present; then
      echo "verify: needle present, clicks landed (extra budget left $EXTRA_LEFT)" >>"$OUT/click.log"
      EXTRA_X=""
    elif [ "$(date +%s)" -ge "$NEXT_EXTRA" ]; then
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" "$EXTRA_X" "$EXTRA_Y" >>"$OUT/click.log" 2>&1
      EXTRA_LEFT=$((EXTRA_LEFT - 1)); NEXT_EXTRA=$(( $(date +%s) + 11 ))
    fi
  fi
  IFS=';' read -ra ITEMS <<< "$SCHEDULE"
  for it in "${ITEMS[@]}"; do
    [ -z "$it" ] && continue
    case "$DONE_SCHED" in *"| $it "*) continue;; esac
    T="${it%%:*}"; XY="${it#*:}"; X="${XY%%:*}"; Y="${XY##*:}"
    if [ "$NOW" -ge "$T" ]; then
      shot $((i)); i=$((i+1))
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" "$X" "$Y" >>"$OUT/click.log" 2>&1
      DONE_SCHED="$DONE_SCHED| $it "
      EXTRA_X="$X"; EXTRA_Y="$Y"; EXTRA_LEFT="$MAX_EXTRA_CLICKS"
      NEXT_EXTRA=$(( $(date +%s) + 11 ))
      sleep 2
    fi
  done
  sleep 5
done

kill "$XV" 2>/dev/null
pkill -x dosbox-x 2>/dev/null
head -c 65536 "$OUT/dosbox.out" > "$OUT/dosbox.out.trim" 2>/dev/null && mv "$OUT/dosbox.out.trim" "$OUT/dosbox.out"
echo "run=$OUT slots=$(ls "$OUT/save" 2>/dev/null | wc -l) clicks=$(cat "$OUT/click.log" 2>/dev/null | wc -l)"

[ -d "$OUT/save" ] || { echo "NEGATIVE: no save dir"; exit 1; }

python3 "$ROOT/scripts/r1_sav_scan.py" --run-dir "$OUT" \
  --needle "$ROOT/work/ascend_payload.bin" > "$OUT/scan.log" 2>&1
SC=$?
head -c 2000 "$OUT/scan.log"

"$HOME/tools/revenv/bin/python" "$ROOT/scripts/r1_deep_diff.py" \
  --run-dir "$OUT" --deep-bytes "$DEEP_BYTES" \
  --needle-screen "$VERIFY_NEEDLE" | tee "$OUT/deep_scan.log"
DC=${PIPESTATUS[0]}

# keep the newest frame pair for vision review, drop older frames (bounded tree)
if [ "${KEEP_SHOTS:-0}" != "1" ]; then
  ls -t "$OUT"/shot-*.png 2>/dev/null | tail -n +5 | xargs -r rm -f
fi

if [ "$SC" -eq 0 ] && [ "$DC" -eq 0 ]; then echo "DEEP CAPTURE OK"; exit 0; fi
[ "$SC" -eq 2 ] || [ "$DC" -eq 2 ] && { echo "HARNESS ERROR (scan=$SC deep=$DC)"; exit 2; }
echo "SHALLOW/NEGATIVE (scan=$SC deep=$DC)"
exit 1
