#!/usr/bin/env bash
# r1_t75_run.sh — OQ-021 threshold-discriminating capture (t75).
# Inject 29/50 star ownership (52..58% band: fires >1/2; 2/3 class survives)
# into the SCRATCH RESUME.GAM via scripts/r1_t75_inject.py, boot, resume,
# verify HERMESSEN needle, then End-Turn (511,67) up to ENDTURNS times at
# 30 s cadence (t56 law: flaky first try, reliable at 25s+). Analysis is
# OFFLINE: DAT_000482fb trajectory + DAT_00043510 selector per slot via
# corollary idx (score.md S2). Fire => >1/2. No fire across all slots =>
# threshold class is above this band (2/3).
#
# SAFETY (docs/BLOCKED.md invariants): scratch copy only (game/ never mounted),
# stdin /dev/null, -time-limit hard bound, pkill -x dosbox-x only, Xvfb tracked
# PID, .gam restored on exit, outputs size-capped.
# Env: BOOT(140) DISPNO(94) ENDTURNS(4)
# Exit: 0 = resume confirmed AND >=1 end-turn click delivered
#       1 = ran but resume/click unconfirmed   2 = harness error
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
BOOT="${BOOT:-140}"
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
slot_mem() {
  local f
  f=$(ls -t "$OUT"/save/*.sav 2>/dev/null | head -1)
  [ -n "$f" ] || return 1
  python3 - "$f" <<'PY'
import sys, zipfile
try: sys.stdout.buffer.write(zipfile.ZipFile(sys.argv[1]).read("Memory"))
except Exception: sys.exit(1)
PY
}
has_needle() { slot_mem | grep -aq "$1"; }

T0=$(date +%s); i=1
CLICKED=""; NEXT_CLICK=$((T0 + 70)); NEXT_CHECK=$((T0 + 80)); EXTRA_LEFT=5
ENDS_DONE=0
while kill -0 "$DB" 2>/dev/null; do
  NOW=$(date +%s)
  if [ "$CLICKED" != "ok" ]; then
    if [ -z "$CLICKED" ] && [ "$NOW" -ge "$NEXT_CLICK" ]; then
      shot $i; i=$((i+1))
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 333 >>"$OUT/click.log" 2>&1
      CLICKED="pending"; NEXT_CHECK=$((NOW + 12))
    elif [ "$CLICKED" = "pending" ] && [ "$NOW" -ge "$NEXT_CHECK" ]; then
      if has_needle HERMESSEN; then
        echo "verify: HERMESSEN in newest slot — resume load CONFIRMED" >>"$OUT/click.log"
        CLICKED="ok"; NEXT_END=$((NOW + 15))
      elif [ "$EXTRA_LEFT" -gt 0 ]; then
        DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 333 >>"$OUT/click.log" 2>&1
        EXTRA_LEFT=$((EXTRA_LEFT-1)); NEXT_CHECK=$((NOW + 12))
      fi
    fi
  else
    if [ "$ENDS_DONE" -lt "$ENDTURNS" ] && [ "$NOW" -ge "${NEXT_END:-99999999999}" ]; then
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 511 67 >>"$OUT/click.log" 2>&1
      ENDS_DONE=$((ENDS_DONE+1))
      echo "end-turn click $ENDS_DONE at t=${NOW}s" >>"$OUT/click.log"
      NEXT_END=$((NOW + 30))
      [ "$ENDS_DONE" -eq "$ENDTURNS" ] && { sleep 45; shot $i; i=$((i+1)); }
    fi
  fi
  sleep 5
done

head -c 65536 "$OUT/dosbox.out" > "$OUT/dosbox.out.trim" 2>/dev/null && mv "$OUT/dosbox.out.trim" "$OUT/dosbox.out"
echo "run=$OUT slots=$(ls "$OUT/save" 2>/dev/null | wc -l) resume=$CLICKED endturns=$ENDS_DONE"
if [ "$CLICKED" = "ok" ] && [ "$ENDS_DONE" -ge 1 ]; then
  python3 "$ROOT/scripts/r1_t75_read.py" "$OUT" > "$OUT/analysis.log" 2>&1
  echo "analysis rc=$? (see $OUT/analysis.log)"; exit 0
fi
exit 1
