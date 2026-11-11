#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t53 capture STEP 1 (OQ-003 controlled mutation): boot scratch copy with
# sentinel-injected RESUME.GAM, click "Return to Current Game" (title
# button 4: window (318,333) — golden-save law, docs/re/refcap.md S4),
# collect autosaves. Analysis is OFFLINE afterwards (scripts/
# r1_mutation_read.py); this script only runs the bounded experiment.
#
# SAFETY invariants (docs/BLOCKED.md): scratch copy NEVER mounts game/;
# stdin=/dev/null; -time-limit hard bound; pkill -x dosbox-x only; Xvfb by
# tracked PID; outputs size-capped. Original resume in game/ is never
# touched; scratch RESUME.GAM is restored from .pret53 at exit.
#
# Env: BOOT(140) DISPNO(94)
# Exit: 0 = slots collected AND post-click slot count > pre-click baseline
#       1 = ran but negative    2 = harness error
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
BOOT="${BOOT:-140}"
DISP="${DISPNO:-94}"
OUT="$ROOT/work/r1/r1mut-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" || exit 2
SCRATCH="$ROOT/work/r1/game"

command -v Xvfb >/dev/null || { echo "MISSING Xvfb"; exit 2; }
command -v dosbox-x >/dev/null || { echo "MISSING dosbox-x"; exit 2; }
[ -x "$ROOT/tools/xsend" ] || { echo "MISSING tools/xsend"; exit 2; }
[ -f "$SCRATCH/ascend.exe" ] || { echo "MISSING scratch build (run r1_savestate.sh once)"; exit 2; }

pkill -x dosbox-x 2>/dev/null && sleep 1
python3 "$ROOT/scripts/r1_mutation_inject.py" "$SCRATCH/RESUME.GAM" > "$OUT/inject.log" 2>&1 || exit 2
cat "$OUT/inject.log"

cleanup() {
  kill "$XV" 2>/dev/null
  pkill -x dosbox-x 2>/dev/null
  python3 "$ROOT/scripts/r1_mutation_inject.py" "$SCRATCH/RESUME.GAM" --restore >>"$OUT/inject.log" 2>&1
}
trap cleanup EXIT

Xvfb ":$DISP" -screen 0 640x480x24 >"$OUT/xvfb.out" 2>&1 &
XV=$!
sleep 1

CONF="$OUT/r1mut.conf"
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
slot_mem() { # newest slot Memory -> stdout
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
CLICKED="" NEXT_CLICK=$((T0 + 70)) NEXT_CHECK=$((T0 + 80)) EXTRA_LEFT=5
while kill -0 "$DB" 2>/dev/null; do
  NOW=$(($(date +%s) - T0))
  if [ -z "$CLICKED" ] && [ "$(date +%s)" -ge "$NEXT_CLICK" ]; then
    shot $i; i=$((i+1))
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 333 >>"$OUT/click.log" 2>&1
    NEXT_CLICK=$(( $(date +%s) + 11 ))
    CLICKED="pending"
  fi
  if [ "$CLICKED" = "pending" ] && [ "$(date +%s)" -ge "$NEXT_CHECK" ]; then
    if has_needle HERMESSEN; then
      echo "verify: HERMESSEN in newest slot — resume load CONFIRMED (extra left $EXTRA_LEFT)" >>"$OUT/click.log"
      CLICKED="ok"
    elif [ "$EXTRA_LEFT" -gt 0 ] && [ "$(date +%s)" -ge "$NEXT_CLICK" ]; then
      DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 333 >>"$OUT/click.log" 2>&1
      EXTRA_LEFT=$((EXTRA_LEFT-1))
    fi
    NEXT_CHECK=$(( $(date +%s) + 10 ))
  fi
  sleep 5
done

head -c 65536 "$OUT/dosbox.out" > "$OUT/dosbox.out.trim" 2>/dev/null && mv "$OUT/dosbox.out.trim" "$OUT/dosbox.out"
echo "run=$OUT slots=$(ls "$OUT/save" 2>/dev/null | wc -l) clicks=$(cat "$OUT/click.log" 2>/dev/null | wc -l) resume=$CLICKED"
[ -d "$OUT/save" ] || { echo "NEGATIVE: no save dir"; exit 1; }
if [ "$CLICKED" = "ok" ]; then
  python3 "$ROOT/scripts/r1_sav_scan.py" --run-dir "$OUT" \
    --needle "$ROOT/work/ascend_payload.bin" > "$OUT/scan.log" 2>&1
  echo "anchor rc=$? (see $OUT/scan.log)"; exit 0
fi
exit 1
