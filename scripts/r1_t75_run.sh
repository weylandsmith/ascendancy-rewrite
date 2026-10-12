#!/usr/bin/env bash
# r1_t75_run.sh — OQ-021 threshold-discriminating capture (t75, rev2).
# Inject 29/50 star ownership (58% band: fires >1/2; >=2/3 survives) into the
# SCRATCH RESUME.GAM via scripts/r1_t75_inject.py, boot, click MENU ROW
# "Return to Current Game" at (318,372) [measured from shot-02 panel pixel
# bands: rows 252 PlayIntro / 294 Tutorial / 334 NewGame / 372 Return / 410
# Load / 450 Save — an earlier rev clicked y=333 = NEW GAME: wrong screen,
# campaign never entered], detect entry via the r1ad GRID-HASH LAW (first
# autosave lands ~62 s; entry = grid hash != baseline), then End-Turn
# (511,67) ENDTURNS times at 30 s (t56 law). Strong resume needle = owned
# planet count 78 in RAM via IL.find_records (HERMESSEN text is in RAM at
# boot from the .gam either way — weak, rev1 false-verified on it).
# Analysis is OFFLINE (scripts/r1_t75_read.py).
#
# SAFETY (docs/BLOCKED.md invariants): scratch copy only (game/ never mounted),
# stdin /dev/null, -time-limit hard bound, pkill -x dosbox-x only, Xvfb tracked
# PID, .gam restored on exit (incl. any New-Game side state), outputs capped.
# Env: BOOT=380 DISPNO(94) ENDTURNS(4)
# Exit: 0 = entry confirmed AND >=1 end-turn delivered   1 = unconfirmed  2 = harness error
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
BOOT="${BOOT:-380}"
DISP="${DISPNO:-94}"
ENDTURNS="${ENDTURNS:-4}"
OUT="$ROOT/work/r1/r1thr-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" || exit 2
SCRATCH="$ROOT/work/r1/game"

command -v Xvfb >/dev/null || { echo "MISSING Xvfb"; exit 2; }
command -v dosbox-x >/dev/null || { echo "MISSING dosbox-x"; exit 2; }
[ -x "$ROOT/tools/xsend" ] || { echo "MISSING tools/xsend"; exit 2; }
[ -f "$SCRATCH/ascend.exe" ] || { echo "MISSING scratch build"; exit 2; }

pkill -x dosbox-x 2>/dev/null && sleep 1
python3 "$ROOT/scripts/r1_t75_inject.py" "$SCRATCH/RESUME.GAM" > "$OUT/inject.log" 2>&1 || exit 2
cat "$OUT/inject.log"

cleanup() {
  kill "$XV" 2>/dev/null
  pkill -x dosbox-x 2>/dev/null
  python3 "$ROOT/scripts/r1_t75_inject.py" "$SCRATCH/RESUME.GAM" --restore >>"$OUT/inject.log" 2>&1
}
trap cleanup EXIT

Xvfb ":$DISP" -screen 0 640x480x24 >"$OUT/xvfb.out" 2>&1 &
XV=$!
sleep 1

CONF="$OUT/r1thr.conf"
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

TL=$((BOOT + ENDTURNS * 35 + 60))
DISPLAY=":$DISP" timeout -s KILL $((TL + 20)) dosbox-x -conf "$CONF" -nogui \
  -time-limit "$TL" </dev/null >"$OUT/dosbox.out" 2>&1 &
DB=$!

shot() { DISPLAY=":$DISP" import -window root "$OUT/shot-$(printf %02d $1).png" 2>/dev/null; }
newest() { ls -t "$OUT"/save/*.sav 2>/dev/null | head -1; }
grid_hash() {
  local f="$1"
  [ -n "$f" ] || return 1
  python3 - "$f" "$ROOT/work/ascend_payload.bin" <<'PY'
import sys, zipfile, hashlib
sys.path.insert(0, "scripts")
from r1_sav_scan import build_anchors, find_base
pay = open(sys.argv[2], "rb").read()
try:
    mem = zipfile.ZipFile(sys.argv[1]).read("Memory")
except Exception:
    print(""); sys.exit(0)   # slot mid-write: UNKNOWN, retry next tick (r1ad law)
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
owned_planets() {
  local f
  f=$(newest)
  [ -n "$f" ] || return 1
  python3 - "$f" <<'PY'
import sys, zipfile
sys.path.insert(0, "scripts")
import r1_income_law as IL
try:
    mem = zipfile.ZipFile(sys.argv[1]).read("Memory")
except Exception:
    sys.exit(1)
print(sum(1 for r in IL.find_records(mem) if mem[r[0] + 0x57] == 0))
PY
}

T0=$(date +%s); i=1
BASELINE=""; ENTERED=0
CLICK_LEFT=6; NEXT_CLICK=$((T0 + 75)); LAST_FIRE=0
ENDS_DONE=0; NEXT_END=0
# Entry law for REV3: grid-hash churn was measured on the NEW-GAME flow only,
# and owned planets are RAM-visible at title (world boots from .gam) — neither
# gates a RESUME. Adjudication is POST-HOC in r1_t75_read.py: counting a
# player star count (DAT_482fb >= injected) only happens in-campaign, so
# end-turns fire optimistically from t>=150 and the slots tell the truth.
while kill -0 "$DB" 2>/dev/null; do
  NOW=$(date +%s); REL=$((NOW - T0))
  f=$(newest)
  if [ -z "$BASELINE" ] && [ "$REL" -ge 10 ] && [ -n "$f" ]; then
    BASELINE=$(grid_hash "$f")
    if [ -n "$BASELINE" ] && [ "$BASELINE" != "NOBASE" ]; then
      echo "baseline grid $BASELINE at t=$REL" >>"$OUT/click.log"
    else
      BASELINE=""    # mid-write/NOBASE: retry next tick (r1ad law)
    fi
  fi
  if [ "$ENTERED" -eq 0 ] && [ -n "$BASELINE" ] && [ "$BASELINE" != "NOBASE" ] && [ -n "$f" ]; then
    CUR=$(grid_hash "$f")
    if [ -n "$CUR" ] && [ "$CUR" != "NOBASE" ] && [ "$CUR" != "$BASELINE" ]; then
      echo "grid churn at t=$REL ($BASELINE -> $CUR) [informational]" >>"$OUT/click.log"
      ENTERED=1
    fi
  fi
  if [ "$REL" -ge "$NEXT_CLICK" ] && [ "$NOW" -ge $((LAST_FIRE + 12)) ]; then
    [ "$LAST_FIRE" -eq 0 ] && { shot $i; i=$((i+1)); }
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 372 >>"$OUT/click.log" 2>&1
    echo "resume-click (318,372) left=$CLICK_LEFT at t=$REL" >>"$OUT/click.log"
    CLICK_LEFT=$((CLICK_LEFT-1)); LAST_FIRE=$NOW
    if [ "$CLICK_LEFT" -le 0 ]; then NEXT_CLICK=99999999999; else NEXT_CLICK=$((NOW + 15)); fi
  fi
  if [ "$ENDS_DONE" -lt "$ENDTURNS" ] && [ "$NOW" -ge "${NEXT_END:-$((T0 + 150))}" ] \
     && [ "$NOW" -ge $((LAST_FIRE + 20)) ]; then
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 511 67 >>"$OUT/click.log" 2>&1
    ENDS_DONE=$((ENDS_DONE+1))
    echo "end-turn click $ENDS_DONE at t=$REL" >>"$OUT/click.log"
    NEXT_END=$((NOW + 30))
    [ "$ENDS_DONE" -eq "$ENDTURNS" ] && { sleep 45; shot $i; i=$((i+1)); }
  fi
  sleep 5
done

head -c 65536 "$OUT/dosbox.out" > "$OUT/dosbox.out.trim" 2>/dev/null && mv "$OUT/dosbox.out.trim" "$OUT/dosbox.out"
echo "run=$OUT slots=$(ls "$OUT/save" 2>/dev/null | wc -l) churn=$ENTERED endturns=$ENDS_DONE"
if [ "$ENDS_DONE" -ge 1 ]; then
  python3 "$ROOT/scripts/r1_t75_read.py" "$OUT" > "$OUT/analysis.log" 2>&1
  RC=$?
  echo "analysis rc=$RC (see $OUT/analysis.log)"; exit "$RC"
fi
exit 1
