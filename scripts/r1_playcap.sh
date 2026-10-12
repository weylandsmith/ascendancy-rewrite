#!/usr/bin/env bash
# r1_playcap.sh — USER-FACED original-game capture session (t82).
#
# PURPOSE: the three remaining user-level blocks (OQ-021 victory selector,
# OQ-023 relation-state enum, OQ-010 combat application) all close from ONE
# played session of the ORIGINAL game with the autosave ring running:
#   play a few turns, colonize past half the galaxy, declare war / make
#   peace, fight ONE battle, then quit normally (or let the time-limit end).
# The slot ring under $OUT/save is the evidence; an offline analyzer (this
# script's tail, or scripts/r1_t75_read.py + relation/ship diffs) reads it.
# NOTHING is scripted: no injection, no synthetic clicks — real play only.
#
# SAFETY (docs/BLOCKED.md invariants): runs ONLY against the scratch copy
# work/r1/game (game/ is never mounted); -time-limit hard bound (generous
# default, override TL=seconds); pkill -x dosbox-x only; bounded output dir.
# This session is INTERACTIVE by design (you watch the screen); the
# headless-invariant applies to the agent's automated capture runs, not to
# a human playing on their own display.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRATCH="$ROOT/work/r1/game"
OUT="$ROOT/work/r1/playcap-$(date +%Y%m%d-%H%M%S)"
TL="${TL:-1500}"                       # seconds of play; default 25 min
DISPLAY="${DISPLAY:-:0}"               # your screen
command -v dosbox-x >/dev/null || { echo "dosbox-x not found"; exit 2; }
[ -f "$SCRATCH/ascend.exe" ] || { echo "scratch build missing"; exit 2; }
mkdir -p "$OUT/save"

cleanup() { pkill -x dosbox-x 2>/dev/null || true; }
trap cleanup EXIT

CONF="$OUT/playcap.conf"
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
nosound=false
[autoexec]
MOUNT C $SCRATCH
C:
ASCEND.EXE
EOF

echo "playcap: scratch=$SCRATCH out=$OUT TL=${TL}s display=$DISPLAY"
echo "playcap: autosave ring 41-60 (every 10 min of play + on save)."
echo "playcap: to close OQ-021 colonize past 50% of stars (T=50 -> 26)."
echo "playcap: to close OQ-023 declare war AND propose/join alliance, then End Turn."
echo "playcap: to close OQ-010 let two fleets exchange fire once, then End Turn."
DISPLAY="$DISPLAY" timeout -s KILL $((TL + 30)) dosbox-x -conf "$CONF" -nogui \
  -time-limit "$TL" >"$OUT/dosbox.out" 2>&1 &
DB=$!
wait $DB || true

SLOTS=$(ls "$OUT/save"/*.sav 2>/dev/null | wc -l)
echo "playcap: slots captured = $SLOTS"
if [ "$SLOTS" -gt 0 ]; then
  # instant offline readout while the session is fresh: counted stars +
  # relation-state census over the ring (failures are non-fatal advisories)
  python3 - "$OUT" "$ROOT" <<'PY' || echo "playcap: offline analyzer hit an issue; slots still banked for offline work"
import os, struct as st, sys, sys as _s, zipfile
out, root = sys.argv[1], sys.argv[2]
_s.path.insert(0, os.path.join(root, "scripts"))
from r1_sav_scan import build_anchors, find_base
from r1_income_law import find_records
pay = open(os.path.join(root, "work", "ascend_payload.bin"), "rb").read()
anch = build_anchors(pay)
best = None
for f in sorted(os.listdir(os.path.join(out, "save"))):
    if not f.endswith(".sav"):
        continue
    m = zipfile.ZipFile(os.path.join(out, "save", f)).read("Memory")
    v, _ = find_base(m, anch)
    if not v:
        print(f"  {f}: no base")
        continue
    P0 = v.most_common(1)[0][0]
    def g16(X):
        return st.unpack_from("<H", m, P0 + 0x82bb0 + X)[0]
    tot = g16(0x16143) >> 16
    stars = sum(1 for r in find_records(m) if m[r[0] + 0x57] != 0xFF)
    print(f"  {f}: T={tot} owned-records={stars} "
          f"scored-stars(DAT_482fb)={g16(0x482FB)} "
          f"selector(DAT_43510)={g16(0x43510)} rank(DAT_4350c)={g16(0x4350C)}")
    best = (f, tot, stars)
if best:
    print(f"playcap: last slot {best[0]} T={best[1]} owned={best[2]} "
          f"(OQ-021 closes when scored-stars pass the tested fraction and "
          f"selector state is banked; all readings above are the evidence)")
PY
fi
echo "playcap: done. Evidence lives in $OUT — tell the assistant this path."
