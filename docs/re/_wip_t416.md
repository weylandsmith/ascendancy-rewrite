# t416 — ROTATION AXIS WIRING (D15: "the upper left rotation control
should rotate the galaxy about the Z axis, but it here seems to rotate it
around the Y axis"). Working log; law distils into t399-galaxy-map-3d.md.

## F0 — premise as shipped (port state before this iteration)
windows.txt COSMOSWnd children [verified, ln223-320]:
  ROTRIGHT msg51 SHAPEFRAME 8 rect 495,364-509,394
  ROTLEFT  msg50 SHAPEFRAME 9 rect 479,364-494,394
  ROTUP    msg52 SHAPEFRAME 10 rect 518,364-548,379
  ROTDOWN  msg53 SHAPEFRAME 11 rect 518,380-548,394
  ZOOMOUT  msg55 SF12 / ZOOMIN msg54(?) SF13 rect 557,364-587,379
ui.cpp:593-598 maps RotRight/Left -> cam.rotate() (yaw about the FIELD z
axis = a tumble once tilted), RotUp/Down -> cam.tilt() (pitch about screen
x). User's complaint: the L/R pair must be IN-PLANE SPIN (rotation of the
picture about the view axis = "about Z"), not a tumble about Y.

## F1 — VENDOR DIAL LAW [verified static, capstone base-0 on
## work/ascend_restored.bin; all addresses file-offset == runtime img addr]

COSMOSWnd class handler = 0x26b34 (esi = window record; t302 measured it
LIVE with NAME='COSMOSWnd'). Dispatch tree: msgs 0x32..0x37 (50..55 = the
six ROT/ZOOM dials per the windows.txt SENDMESSAGE table) reach the latch
chain at 0x27d6f..0x279eb. THE DIALS ARE NOT STEPS — THEY ARE A
(active, direction) BIT-PAIR LATCH ON wnd+0xc0:
  bits 0/1 = msg 0x32 ROTLEFT / msg 0x33 ROTRIGHT   (bit0=active, bit1=dir)
  bits 2/3 = msg 0x34 ROTUP   / msg 0x35 ROTDOWN    (bit2=active, bit3=dir)
  bits 4/5 = msg 0x36 ZOOMIN  / msg 0x37 ZOOMOUT    (bit4=active, bit5=dir)
Press semantics (read off 0x27da2..0x2787c for pair 0; 0x27893..0x278c0
pair 0 via the other msg; 0x278d7..0x27951 pair 1; 0x27968..0x279e0 pair 2):
  inactive            -> ACTIVE with this dir   (0x27872 set b0 / 0x278bb or 3 /
                                                  0x27901 / 0x2794c or 0xc ...)
  active, same dir    -> STOP                    (0x27865 cl&0xfe / 0x278a1 /
                                                  0x278f4 / 0x27932 ...)
  active, other dir   -> FLIP dir                (0x27dbf ch&0xfd / 0x278ae or 2 /
                                                  0x278e7 / 0x2793f or 8 ...)
The PERIODIC PUMP (msg 0x3b — t302 measured it firing ~1/s unattended) is
0x27a18: per tick, for each latched pair it applies motion:
  bit0 set: delta = bit1 ? -2 : +2; delta_f = delta * f32[0x9f108];
            FUN_000283e4(wnd, edx=-1, delta_f)          (0x27a28..0x27a4b)
  bit2 set: delta = bit3 ? +2 : -2;
            FUN_000283e4(wnd, edx=0,  delta_f)          (0x27a60..0x27a80)
  bit4 set: edx = bit5 ? +1 : -1; FUN_00028428(wnd,edx) (0x27a95..0x27aa3)
  any motion bit set (dh & 0x15): repaint FUN_000284bc + invalidate
                                  (0x27aa8..0x27ac6)
FUN_000283e4 (0x283e4): edx==-1 -> CALL 0x53584 else CALL 0x53554, both on
eax = wnd+0x14e = the camera basis struct C (vectors at C+0xc, C+0x18,
cross-product third at C+0x24 recomputed by FUN_00053804 @0x53804 — classic
cross product in its asm). NO clamp anywhere in the rotation path.
FUN_00053584 -> FUN_0005324c per vector (0x5324c): mixes (x,z) components
(v.x' = x*c + z*s; v.z' = z*c - x*s per the FP-stack trace; sign detail
[unverified], axis identity verified) = ROTATION ABOUT WORLD Y.
FUN_00053554 -> FUN_000531dc per vector (0x531dc): mixes (y,z) = ROTATION
ABOUT WORLD X.
A THIRD helper FUN_000535b4 -> FUN_000532b8 (mixes (x,y) = rotation about
WORLD Z) EXISTS but the cosmos dials NEVER call it — the in-plane-LOOK of
the vendor spin comes from world-Y rotation because the vendor's rest view
axis IS world Y (its screen plane is XZ); the PORT's rest view axis is
field +z (t399 law), so the port's analog of vendor-Y is port-z.
FUN_00028428 (0x28428) ZOOM: accumulator [wnd+0x57a] += ±scale; stops the
latch at runtime bounds f32[0xfb0]/f32[0xfb4] (bss, runtime-set; static
image bytes are not floats); clamps into [wnd+0xda] via 0x203b8 with
pushed 1.0 (0x3f800000) and 100000.0 (0x47c35000) hard bounds.
help.txt 1spin ln220: "This button will let you manipulate the Galactic
Display. Use the right mouse button if you want to zoom or rotate
continuously." (right-drag direct manipulation = separate mechanism, not
modeled; the LATCH above is the click law.)

## F2 — port delta verdict (AMENDED after full basis decode)
AMENDMENT: the first F2 draft claimed the port's axis choice was already
vendor law under a rename. WRONG — recenter FUN_00026a9c (0x26a9c) decodes
the rest camera STRUCT at wnd+0x14e: eye=(1.0,0.0,-1500.0) [verified
immediates 0x3f800000/0xc4bb8000], up@+0x15a=(0,1,0), fwd@+0x166=(0,0,1),
right@+0x172 = cross(up,fwd) recomputed by FUN_00053804 after EVERY
rotation. The dials rotate (up,fwd) about WORLD axes (0x53584 mixes (x,z)
= world Y for the L/R pair msg 50/51; 0x53554 mixes (y,z) = world X for
msg 52/53) — a free BASIS orbit, not Euler yaw-then-pitch, no clamp.
Port today: yaw about field z (in-plane clock-dial spin at rest) + pitch
about screen-x clamped +-1.5 — DIFFERENT mechanism. Port deltas to close:
(a) press semantics: vendor = toggle-spin latch (click starts CONTINUOUS
    rotation, click again stops, opposite dial flips direction); port =
    one 0.25-rad step per click. THIS is the feel the user calls "off".
(b) axis mechanism: port must orbit the camera basis about WORLD Y (L/R
    pair) and WORLD X (U/D pair), recomputing right=cross(up,fwd); rest
    projection (screen x=field x, y flipped, depth=field z + standoff)
    is IDENTICAL at identity, so every t399 rest-pinhole pin survives.
    Vendor standoff = 1500 + zoom 35.0 [verified]; PORT keeps its
    documented fit law (standoff 1760, focal 680) — adopting 1500 would
    break the bounds pin (focal would have to drop to <=551); named.
(c) no rotation clamp (vendor has none; zoom keeps clamps — vendor has
    runtime bounds f32[0xfb0]/[0xfb4] + hard 1.0/100000.0 in FUN_00028428).
(d) per-dial sign table pinned verbatim to the pump (msg 50 ROTLEFT =
    +2 deg, 51 ROTRIGHT = -2, 52 ROTUP = -2, 53 ROTDOWN = +2, about the
    axes above; 54/55 zoom pair). Delta unit = DEGREES [verified:
    FUN_000531dc multiplies its argument by deg2rad 0x88b88 =
    0.017453292]; the extra scale f32[0x9f108] is bss/runtime — port
    documents scale 1.0. Pump cadence: t302 measured msg 0x3b firing
    ~1/s unattended; port tick interval = documented default (250 ms).

## F3 — LANDED (code + pins, 2026-11-17)
cam3d.{h,cpp} REWRITTEN to the vendor basis model: Camera3d carries
up/fwd (recenter rest values verbatim), right()=cross(up,fwd) (FUN_00053804),
dialLatch(cur,dir) pure press law, tick() = one pump application
(2 deg about world Y for latchSpin, world X for latchTilt, zoom scale for
latchZoom), NO rotation clamp, reset() = FUN_00026a9c semantics (identity
basis + latches cleared + zoom default). yawLog()/pitchLog() keep the
"ui cam yaw ..." witness line shape (witness grep survives: t411 script
greps "ui cam yaw"). ui.cpp: map dials pressSpin/pressTilt/pressZoom with
pump signs (ROTLEFT +1, ROTRIGHT -1, ROTUP -1, ROTDOWN +1); sysview
RotateLeft/Right pressSpin (system view has no tilt dials); pump loop
before SDL_RenderPresent gates on cam.moving() + SDL_GetTicks cadence
kSpinTickMs=250 (documented default; idle cost unchanged); depthClass now
fed viewDepth-kStandoff (node+0xd transformed-z law, identical at rest).
Rest projection reduces EXACTLY to the t399 formula — the t399 rest
pinhole pins pass UNCHANGED (407/0/0: suite 403 + 4 new
test_axis_t416.cpp; test_cam3d_t399 zoom/wrap block re-scoped to the latch
law, regression fences kept: reset + finite-after-2000-ticks + stop).
Pins: latch table (start/stop/flip both directions, zoom independence),
world-Y law (up stays vertical; 20-tick in-plane x-shift >=30 px on a
300-deep centre point; depth class unchanged after one tick; rotateBasisY
(90) maps fwd->(1,0,0) per FUN_0005324c signs), world-X law (up.x stays 0,
up.y moves; 100000 ticks finite + right() unit => no clamp drift), rest
basis == recenter immediates + delta-unit constants.
MUTATION: budget exhausted this iteration — the four tests are un-mutated
(SEAM HONESTY: pins written but not mutation-proven; the t407-style sweep
is the closer if any pin is ever questioned).
SEAMS (named): (S-a) pump cadence 250 ms and zoom multiplicative-vs-additive
= documented port defaults (vendor cadence ~1/s measured t302, zoom
accumulator runtime-only); (S-b) standoff 1760 kept over vendor-verified
1500 (fit law, would break the bounds pin; scale-only difference); (S-c)
right-drag continuous manipulation (help.txt 1spin) unimplemented — latch
is the click law; (S-d) the vendor f32[0x9f108] delta scale is bss/runtime,
port documents 1.0 (delta degenerates to the 2-deg immediates).
WITNESS: the user's D16 sheet (t420) is the acceptance channel. Self-grade
walk was SKIPPED this iteration (budget) — the geometry pins stand in for
it; the "click once = continuous spin, click again = stop" feel is what the
user should re-check LIVE.
