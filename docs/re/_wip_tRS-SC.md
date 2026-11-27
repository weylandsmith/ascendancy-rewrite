# _wip_tRS-SC — D32-L4: research up/down buttons = SCROLL not zoom (2026-11-27)

USER VERBATIM (docs/DECISIONS.md D32): "the up/down buttons on the
research screen are supposed to scroll up and down, not zoom in and out."

## P0 STATE OF THE PORT (read this iteration)
- rewrite/src/ui/researchview.h:166 ResCam: posZ=-150 rest, yawDeg; press
  pair law 0x47b44..0x47c42 (tPF-7a corrected table) — press/release legs
  verified, NOT the suspect.
- ResCam::tick (researchview.cpp:296-303): move pair (latchMove 1/2) does
  posZ -/+ kDollyStep(1.0). researchview.h comment itself states
  "RESMOVEUP SHRINKS the tree" — i.e. the port's move pair is a DOLLY =
  scale change = what the user calls zoom.
- Projection (researchview.cpp:220-260): vX = X cos - Z sin, vY = Y,
  vZ = X sin + Z cos - posZ; sx = focal*vX/vZ+0.5+235, sy = focal*vY/vZ+240.
  Geometry (researchTreeGeometry 0x472d4..): per depth column k: Y=30k+
  15*(i&1), X/Z = R*sin/cos(acc) with R in {4,23}. So the tree is a helix
  whose AXIS is world Y (Y spans 0..~510) while X/Z span only +-23.
  => dolly along world Z scales the fan (zoom-like) — the user's complaint.
- ui.cpp:1016-1055 click arms: RotLeft/Right->pressRot, MoveUp/Down->
  pressMove, msg ids 50..53 verbatim from windows.txt RESROTLEFT/RIGHT +
  RESMOVEUP/DOWN (extracted/ascend00/windows.txt:1769-1826, all four
  HELPINDEX resmove; help text: "This button will let you manipulate the
  Research Display. Use the right mouse button if you want to move or
  rotate continuously." help.txt resmove block).
- Vendor pump legs RE-READ THIS ITERATION (t442_disasm 0x47c48..0x47d3a):
  rot pair (bits 0x4/0x8): delta +-3.0 x [0x9f108] -> call 0x53504 on
  basis win+0x11f (yaw mix, cosmos 0x5324c law). move pair (bits 0x1/0x2):
  delta +-1.0 x [0x9f108] -> fld/fadd/fstp DIRECTLY on [esi+0xe3] — no
  call, no transform. 0x47a5b init writes [esi+0xe3]=0xc2c80000 = -100.0
  (port rest -150.0 came from 0xc3160000 elsewhere — RE-CHECK which site
  is the reswin rest value).

## P1 OPEN QUESTION
Does the vendor have ANY leg that moves the research display vertically
(a true scroll), e.g. an ARROW-key path in the hotkey dispatcher
(fn 0x54d18 tree 0x54faf) posting a different msg/param, or a reswin msg
arm outside the port's 50..53 set? If NO, the honest negative goes to
docs/re/research.md S16 addendum: vendor up/down ARE the dolly pair
verbatim; the user's "scroll" perception must be explained by the vendor
GEOMETRY (dolly on a Y-axis helix reveals/hides columns vertically) or by
a port axis defect — NOT by inventing a scroll msg.

## FINDINGS LOG
(append as probes land)

## P2 MSG TREE FULLY READ (t442_disasm 0x47aa1..0x47b41) — NO SCROLL MSG EXISTS
reswin handler dispatch tree arms (msg value in ecx):
  <0xc -> redraw(0x47478) | 0xc-0xd -> 0x479e1/0x47a1c: ZOOM-MULTIPLIER legs
    on GLOBAL f32 DAT_0009f108: 0x479e1 (msg 0xc) guards v > qword[0x24fc]
    then v *= f64[0x850b4] (~2?); 0x47a1c (msg 0xd) guards v < f32[0x850a0]
    then v *= f64[0x24f4] (~0.5?) — these are the pump-magnitude hotkeys,
    NOT a display scroll.
  0xe-0x20 NOOP | 0x21 -> 0x47929 CLEAR-ALL-OWNED (ANDs race bit out of every
    record +0xa byte... [0x74743] window) + studied=0xffff | 0x2e -> 0x47828
    SET-ALL-OWNED (debug) | 0x46(70) -> 0x478a0 UN-STUDY current |
  0x47(71) -> 0x47a53: writes [win+0xe3] = 0xc2c80000 = -100.0 + repaint;
  0x48-0x4f, 0x51 -> 0x47a7a: writes [win+0xe3] = 0x49742400 = 1e15 + repaint;
  0x32-0x47 -> 0x479a5 arm (0x32-0x34) | 0x32-0x35 press table (the latch legs).
NO leg writes a pan/scroll word; NO arrow-key alternative exists either:
hotkey dispatcher 0x54d18 (key word [0x484c4]) full tree read — arms toggle
globals 0x660c/0x78863/0x7884b/0xa2048, window mgmt via 0x56e10 (0x19/0x1f),
NONE touches reswin state or posts 50..53/0xc/0xd. CONCLUSION [verified]:
the vendor has NO separate scroll leg — the up/down buttons ARE msg 52/53
(RESMOVEUP/DOWN, windows.txt:1793-1826) latching the [win+0xe3] dolly pair
(bits 0x1/0x2), pumped +-1.0 x DAT_0009f108 into [win+0xe3] (0x47cd0..0x47d12
VERBATIM re-read: fld [esi+0xe3]; fadd delta; fstp [esi+0xe3]).

## P3 FIELD-ROLE CORRECTION FOUND — [win+0xe3] IS POSITION Y, NOT Z (the defect)
CAMERA STRUCT BASE = win+0xab (0x470fe lea eax,[ebp+0xab]; call 0x203b8).
0x203b8 stores: [cam+0x24]=fov30 (win+0xcf), calls 0x203e4 -> [cam+0x28]=focal
(win+0xd3 -- the SAME word the draw pushes at 0x48069!), [cam+0x2c]=near1,
[cam+0x30]=far1e5. Camera POSITION = cam+0x34 = win+0xdf/0xe3/0xe7 (0x20414
negates the triplet for the affine translation t=-pos). INIT 0x4710e-0x47123:
  mov [eax],0 / [eax+4],0 / [eax+8],0xc3160000  ==  x=0, y=0, z=-150.
=> win+0xe3 = POSITION Y (rest 0.0); win+0xe7 = POSITION Z (-150, never
written anywhere else -- grep of the whole reswin asm window shows +0xe7 has
ZERO write sites). The MOVE pair (0x47cd0..0x47d12) adds +-1.0*[0x9f108] to
+0xe3 = A VERTICAL SCROLL, exactly the user's law. The port (researchview.h
ResCam::posZ, tick posZ -/+) dollies the DEPTH = zoom -- the D32-L4 defect.
CORROBORATION: hotkey arms 0x47a53 (msg 0x47) write [win+0xe3] = 0xc2c80000
= -100.0 and 0x47a7a (msgs 0x48-0x4f,0x51) write 0x49742400 = 1e15 then
repaint -- a 'scroll to start / scroll to end' idiom that only makes sense
for a bounded scroll coordinate.
PER-PAINT CLAMP LAW (0x47eac draw fn, block 0x47ef1..0x47fc3 VERBATIM):
min=max=worldY(row0) (win+0x147 == row-0 Y of the world array win+0x143
stride 0xc); for every row PASSING THE 0x46d3c DRAW SCOPE: min=min(Y),
max=max(Y); then posY = clamp(posY, min, max) (0x47f89 fld pos; fcomp min;
jae -> second check; below-min -> min; above-max -> max; mov [ebp+0xe3]).
=> the vendor SCROLLS the camera along the tree's Y axis and CLAMPS it to the
FRONTIER's Y-extent; the tree is a helix along Y (Y=30k+15(i&1), X/Z radius
<=23) so this reads as an up/down list-scroll, NOT zoom.
PROJECTION (0x53374 re-read VERBATIM): word[ebx]=round(focal*vX/vZ+0.5)+235
(arg 0xeb), word[edx]=round(focal*vY/vZ+0.5)+240 (arg 0xf0) -- push order
push esi(Y-words) push edi(X-words) push 0xf0 push 0xeb push [ebp+0xd3]focal
at 0x48035..0x48076; vY = world.y - cam.y ONCE the port passes the right
field (vZ unchanged = X sin + Z cos - (-150)).

## P4 WITNESS + CLOSE (2026-11-27)
Witness rc=0 (log /tmp/trssc_shots/app.log): latch 0 2, row 0 centre
64,240 -> 64,112 monotone (X const 64), release latch 0 0, 0 lines idle.
Mutation cycle M1-M4 ALL CAUGHT, restore md5-ok x4 (md5s in git diff).
Law distilled docs/re/research.md S17(a)-(d). No OQ row (user-defect class,
like tWIN-1); open=[016,019] unchanged. Residues banked: (1) msg 0xc/0xd
pump-multiplier hotkeys ([0x9f108] x f64[0x850b4] / f64[0x24f4], guards
qword[0x24fc]/f32[0x850a0]) are NOT ported — no key binding exists for them
in the port UI; the f64 constants were not decoded (values at ds-relative
pool, unverified). (2) The 0x47a53/0x47a7a scroll-to-end hotkey arms are
likewise unported (no binding). Both are debug/hotkey legs; the BUTTON law
is fully cited.
