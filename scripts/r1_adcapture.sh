#!/usr/bin/env bash
# R1 ADAPTIVE CAPTURE (STATE.md NEXT ACTION 2026-10-06c): same invariants and
# boot law as r1_deepcapture.sh, BUT the game keeps running while an outer
# driver (the loop session) reads screenshots, clicks live, and checkpoints.
# Why: new campaigns generate random maps, so a static SCHEDULE cannot target
# a planet (refuted 2026-10-06c: scheduled in-game clicks hit empty space);
# and the 41..60 autosave ring is CYCLIC — past 20 saves mtime order is NOT
# run order. This harness therefore COPIES the newest slot into ck/ckNNN.sav
# at every checkpoint, giving a linear, rotation-proof timeline.
#
# Protocol (outer driver writes commands, script acts on its 10 s tick):
#   touch $OUT/cmd_shot            -> screenshot current screen
#   echo "X Y" > $OUT/cmd_click    -> xsend button1 at window coords, then
#                                     checkpoint immediately after
#   touch $OUT/cmd_ck              -> checkpoint only
# All command files are consumed (deleted) after acting; results appended to
# $OUT/click.log and turn line printed into $OUT/turns.log (slot,turn,time).
#
# SAFETY: identical to deepcapture (scratch copy, stdin=/dev/null,
# -time-limit, pkill -x dosbox-x only, logs bounded).
# Env: DISPNO(93) BOOT(420) BOOT_WAIT(15) SCHEDULE (same syntax as deep;
#      needle-verify ONLY until first campaign entry; after that clicks are
#      driver-controlled).
# Exit: 0 run finished with >=1 checkpoint; 2 harness error.
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
BOOT="${BOOT:-600}"
BOOT_WAIT="${BOOT_WAIT:-15}"
DISP="${DISPNO:-93}"
SCHEDULE="${SCHEDULE:-75:318:293;100:600:440}"
VERIFY_NEEDLE="${VERIFY_NEEDLE-cosmic exiles}"
MAX_EXTRA_CLICKS="${MAX_EXTRA_CLICKS:-5}"
OUT="$ROOT/work/r1/r1ad-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT/ck" || exit 2
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

CONF="$OUT/r1ad.conf"
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

CKN=0
CKDIR="$OUT/ck"
checkpoint() {
  local newest tmp
  newest=$(ls -t "$OUT"/save/*.sav 2>/dev/null | head -1)
  [ -n "$newest" ] || return 1
  # VALIDITY GUARD: autosave writes the slot in place; a raw cp can catch it
  # mid-write (hit r1ad-131350 ck001/ck011 -> BadZipFile). Require a readable
  # Memory member TWICE (2 s apart, stable size) before committing the copy.
  tmp="$OUT/.ck.tmp"
  for _try in 1 2 3; do
    if python3 -c '
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1]); print(z.getinfo("Memory").file_size)
' "$newest" > "$tmp" 2>/dev/null; then
      sleep 2
      if python3 -c '
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1]); print(z.getinfo("Memory").file_size)
' "$newest" | cmp -s - "$tmp"; then
        break
      fi
    fi
    sleep 3
    newest=$(ls -t "$OUT"/save/*.sav 2>/dev/null | head -1)
    [ -n "$newest" ] || return 1
  done
  rm -f "$tmp"
  CKN=$((CKN + 1))
  cp "$newest" "$CKDIR/$(printf ck%03d "$CKN").sav"
  echo "$(basename "$newest") -> ck$(printf %03d "$CKN")" >> "$OUT/ck.log"
  # turn counter via per-run base (anchors); H=0x88 law may differ -> derive
  python3 - "$newest" "$ROOT/work/ascend_payload.bin" >> "$OUT/turns.log" <<'PY'
import sys, struct, zipfile
sys.path.insert(0, "scripts")
from r1_sav_scan import build_anchors, find_base
save, needle = sys.argv[1], sys.argv[2]
pay = open(needle, "rb").read()
mem = zipfile.ZipFile(save).read("Memory")
v, _ = find_base(mem, build_anchors(pay))
if not v:
    print(save, "NOBASE")
else:
    H = v.most_common(1)[0][0] - 0x1BF450
    print(save, "turn", struct.unpack_from("<H", mem, 0x254e10 + H)[0])
PY
}

T0=$(date +%s)
DONE_SCHED=""
EXTRA_X=""; EXTRA_Y=""; EXTRA_LEFT=0; NEXT_EXTRA=0
needle_present() {
  local newest_f
  newest_f=$(ls -t "$OUT"/save/*.sav 2>/dev/null | head -1)
  [ -n "$newest_f" ] || return 1
  python3 -c '
import sys, zipfile
needle = sys.argv[2].encode("latin-1")
try:
    mem = zipfile.ZipFile(sys.argv[1]).read("Memory")
except Exception:
    sys.exit(1)
sys.exit(0 if needle in mem else 1)
' "$newest_f" "$VERIFY_NEEDLE"
}

# phase 1: golden tour = two clicks (75: New Game 318,293; 100: start 600,440).
# ENTRY LAW (measured 2026-10-06d): 'cosmic exiles' appears on the SETUP
# screen, NOT campaign-only — it cannot gate campaign entry (hit run
# r1ad-20261006-125117). Reliable discriminator: the planet NAME grid at the
# pointer-law base is RESIDUAL (previous campaign's names) on title/setup and
# gets regenerated with fresh names when the game actually starts. Baseline
# = grid hash at t=10; entered = grid hash CHANGED. While not entered,
# re-fire the start click every 11 s (bounded); if still not in by t=220,
# re-fire the whole tour (bounded to one redo).
grid_hash() {
  python3 - "$1" "$ROOT/work/ascend_payload.bin" <<'PY'
import sys, zipfile, hashlib, re
sys.path.insert(0, "scripts")
from r1_sav_scan import build_anchors, find_base
pay = open(sys.argv[2], "rb").read()
mem = zipfile.ZipFile(sys.argv[1]).read("Memory")
v, _ = find_base(mem, build_anchors(pay))
if not v:
    print("NOBASE")
else:
    H = v.most_common(1)[0][0] - 0x1BF450
    P0 = 0x26d07b
    blob = mem[P0 + H: P0 + H + 123 * 16]
    print(hashlib.md5(blob).hexdigest())
PY
}
BASELINE=""
LAST_FIRE=0
TOUR_REDO=0
T_REDO_START=0
while kill -0 "$DB" 2>/dev/null; do
  NOW=$(( $(date +%s) - T0 ))
  newest=$(ls -t "$OUT"/save/*.sav 2>/dev/null | head -1)
  if [ -z "$BASELINE" ] && [ "$NOW" -ge 10 ] && [ -n "$newest" ]; then
    BASELINE=$(grid_hash "$newest")
    echo "baseline grid $BASELINE at t=$NOW" >>"$OUT/click.log"
  fi
  if [ -n "$BASELINE" ] && [ -n "$newest" ]; then
    CUR=$(grid_hash "$newest")
    # EMPTY output = slot file mid-write (zipfile raises) -> unknown, retry
    # next tick; never treat as 'entered' (hit r1ad-131350: t=20 false break).
    if [ -n "$CUR" ] && [ "$CUR" != "NOBASE" ] && [ "$CUR" != "$BASELINE" ]; then
      echo "campaign ENTERED at t=$NOW (grid $BASELINE -> $CUR)" >>"$OUT/click.log"
      break
    fi
  fi
  if [ "$NOW" -ge "$T_REDO_START" ] && [ "$NOW" -ge $((LAST_FIRE + 11)) ]; then
    if [ "$NOW" -ge 220 ] && [ "$TOUR_REDO" -eq 0 ]; then
      TOUR_REDO=1
      echo "t=$NOW not entered -> whole-tour redo" >>"$OUT/click.log"
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 293 >>"$OUT/click.log" 2>&1
      sleep 12
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 600 440 >>"$OUT/click.log" 2>&1
    elif [ "$NOW" -ge 100 ] || [ "$TOUR_REDO" -eq 1 ]; then
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 600 440 >>"$OUT/click.log" 2>&1
    elif [ "$NOW" -ge 75 ]; then
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 293 >>"$OUT/click.log" 2>&1
    fi
    LAST_FIRE=$NOW
  fi
  sleep 5
done
echo "campaign phase done at t=$(( $(date +%s) - T0 ))s -> entering adaptive phase" >>"$OUT/click.log"
checkpoint || true
DISPLAY=":$DISP" import -window root "$OUT/live-000.png" 2>/dev/null

# adaptive phase: driver drives via command files; checkpoint every tick
while kill -0 "$DB" 2>/dev/null; do
  if [ -f "$OUT/cmd_shot" ]; then
    rm -f "$OUT/cmd_shot"
    DISPLAY=":$DISP" import -window root "$OUT/live-$(printf %03d "$CKN").png" 2>/dev/null
  fi
  if [ -f "$OUT/cmd_click" ]; then
    read -r CX CY < "$OUT/cmd_click" || true
    rm -f "$OUT/cmd_click"
    if [ -n "${CX:-}" ] && [ -n "${CY:-}" ]; then
      checkpoint || true   # pre-click bracket
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" "$CX" "$CY" >>"$OUT/click.log" 2>&1
      sleep 2
      checkpoint || true   # post-click bracket (dialog/state landed)
    fi
  fi
  if [ -f "$OUT/cmd_ck" ]; then
    rm -f "$OUT/cmd_ck"
    checkpoint || true
  fi
  sleep 10
done
checkpoint || true
echo "adaptive phase done; checkpoints=$CKN" >>"$OUT/click.log"
kill "$XV" 2>/dev/null
[ "$CKN" -ge 1 ] && { echo "ADAPTIVE CAPTURE OK ck=$CKN dir=$OUT"; exit 0; }
echo "ADAPTIVE CAPTURE EMPTY"; exit 2
