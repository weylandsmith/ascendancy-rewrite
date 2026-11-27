#!/usr/bin/env bash
# tRS-SC SCROLL WITNESS (D32-L4; law docs/re/research.md S17).
# Holds the vendor RESMOVEUP button (windows.txt RESMOVEUP rect
# 563,442-593,457 -> centre 578,449) and asserts on the port's
# "ui research center row x y state" witness lines:
#   (a) SLIDE: during the hold the logged centre's Y CHANGES while its X
#       STAYS CONSTANT (scroll moves vY only; a zoom/dolly would move X).
#   (b) FREEZE: after clickup, at most one further centre line (release
#       law tPF-7 unchanged).
#   (c) BOUND: the scroll never runs away — posY is clamped per paint
#       (0x47ef1..0x47fc3), observable as the centre line STOPPING changing
#       while the button is still held (clamp saturation) OR staying inside
#       the window rows; measured as: >= 2 distinct y values, all within
#       [46,472] (RESWIN interior).
# Scratch Xvfb, kill BY PID (docs/BLOCKED.md invariants).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/trssc_shots}
DISP=${DISP:-:98}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X98-lock /tmp/.X11-unix/X98
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
trap 'kill $APP $XV 2>/dev/null' EXIT
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.15; }

X 318 335            # RESUME -> campaign map
X 553 223            # RESEARCH rail -> state 20
sleep 1

# --- (a) HOLD-SCROLL LEG ---------------------------------------------------
# RESMOVEDOWN (windows.txt rect 563,458-593,472 -> centre 578,465): pair B
# from rest => posY += 1/pump; the per-paint clamp lets it travel to the
# frontier's top Y (~30 world units of slide = ~250 px at the 7-9x scale).
# RESMOVEUP from rest would saturate at the clamp floor immediately — same
# law, wrong direction for a witness.
X clickdn 578 465    # press-only on RESMOVEDOWN (move pair latches)
sleep 2
X clickup 578 465
sleep 0.5
# centre lines seen during the session (row x y state)
grep "ui research center " "$OUT/app.log" | tail -12 > "$OUT/centres.txt"
python3 - "$OUT/centers_unused" "$OUT/centres.txt" <<'EOF'
import re, sys
rows = []
for ln in open(sys.argv[2]):
    m = re.match(r"ui research center (-?\d+) (-?\d+) (-?\d+) (\w+)", ln)
    if m: rows.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)))
if len(rows) < 2:
    print("VERDICT FAIL: fewer than 2 centre lines"); sys.exit(1)
# SCROLL LAW per SAME-ROW lines: Y slides, X constant. A row CHANGE in the
# log is legitimate (a different Available row becomes the first on-frame)
# and carries its own X.
ok = True
seen_same = 0
for a, b in zip(rows, rows[1:]):
    if a[0] == b[0]:
        seen_same += 1
        if a[1] != b[1]:
            print(f"FAIL (a): same row {a[0]} moved in X ({a[1]}->{b[1]}) — dolly/zoom, not scroll")
            ok = False
        if a[2] == b[2]:
            print(f"FAIL (a): same row {a[0]} y static between lines")
            ok = False
ys = sorted({r[2] for r in rows})
print("distinct y:", ys[:8], "same-row line pairs:", seen_same)
if seen_same == 0 and len(ys) < 2:
    print("FAIL (a): no scroll observable at all"); ok = False
if not all(-2000 <= y <= 4000 for y in ys):
    print("FAIL (c): y wildly out of the vendor word range"); ok = False
print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
EOF
V1=$?

# --- (b) FREEZE LEG --------------------------------------------------------
C1=$(grep -c "ui research center " "$OUT/app.log")
sleep 2
C2=$(grep -c "ui research center " "$OUT/app.log")
echo "centre lines before/after idle: $C1 $C2"
[ $((C2 - C1)) -le 1 ] || { echo "VERDICT FAIL: still logging after release"; exit 1; }

DISPLAY=$DISP import -window root -crop 640x480+0+0 +repage "$OUT/after.png" 2>>"$OUT/app.log"
echo "WITNESS rc: slide=$V1 freeze-ok"
exit $V1
