# tPF5-A — INDICATOR-POPUP FRAME LIB (D28 item 9 last leg) — WIP

Assignment: STATE.md NEXT ACTION tPF5-A. STATIC ROUTE, zero guest boot,
budget <=4 probes. Predecessor constraint data: _wip_tOQ19-audit.md A7
(the four tiles PLRES/PLIND/PLPRO/PLPOP carry SHAPEFRAME -1) and
_wip_tPF5.md P7 (the named-open seam).

## P0 — OPEN SITE + FRAME-LIB SOURCE [verified disasm this session]

The msg-50 popup builder is FUN_0x3db80 (already the tPL-B2 law site). Its
PROLOGUE — before the key switch at 0x3dc50/0x28fb8 — resolves the frame lib:

    3dbb3  mov  eax, 0x9f10c            ; shape-cache struct (inline in DSEG)
    3dbb8  xor  edx, edx
    3dbbc  mov  dx, word ptr [0x6fd8e]  ; <<< THE FRAME-LIB ID = WORD ds:0x6fd8e
    3dbc5  call 0x1fc34                 ; (ctx=eax, id=edx) -> shape record
    3dbca  push eax                     ; record handed to the popup composer

So the answer to "which lib does the indicator path push" is NOT a per-widget
word (A7 confirmed: SHAPEFRAME -1 x4) and NOT the tPF-4 default row lib
(WORD ds:0x6fd80). It is the SEPARATE slot ds:0x6fd8e — a slot no earlier
census read (tPF-4 read 0x6fd80/0x6fd90/92/94/9c + the 0x6fd60 race table;
ui-runtime.md:778-780 lists 0x6fd44/0x6fd52/0x6fd96/0x6fd9a — 0x6fd8e is in
NONE of those lists).

Resolver 0x1fc34 verified this session (0x1fc34..0x1fd0f):
  esi := eax (ctx), edi := edx (id); bound check id < 0xc8 (0x1fc62);
  per-id flag word read at [esi + id*0x32 + 0x7cd], sar 0x18, must be != 0
  (the "is this id loaded/counted" gate 0x1fc8d..0x1fc99);
  record pointer = [esi + id*4] if non-null (0x1fcaf), else the registry
  entry lea ebp,[esi+0x7d0]; add eax(id*0x32) at 0x1fcd3/0x1fcd9 — i.e.
  ctx + 0x7d0 + id*0x32, the SAME join tPF-4 used (shp.md S2 registry-name
  law: cp437, NUL-terminated).
Because ctx is the ADDRESS of the inline DSEG struct 0x9f10c (not a heap
pointer), both the id slot AND the registry name string are statically
readable from a banked save under the pointer law (ds D -> linear 0x242000+D
-> Memory offset + H). This is a cited live-RAM measurement, not a guess.

## P1 — ID + NAME MEASUREMENT (scripts/tPF5A_indlib.py)

(see script output appended below)
## P1 — ID + NAME MEASURED [verified scripts/tPF5A_indlib.py, this session]

    saves ok=60/60   (three independent banks: bank-play-20261111-t377,
                     bank-t285-restored-t1086, bank-t438-ring-2200)
    ds:0x6fd8e (indicator-popup frame id): {37: 60}
    ds:0x6fd80 (tPF-4 row default, control leg): {30: 20 -> 30: 60}
    registry id 37 -> 'data\help.shp'   flag>>24 = 100   x60

ANSWER TO THE NAMED-OPEN SEAM: the msg-50 indicator popup's frame lib is
data\help.shp — the SAME file the planet-tile popup's frame identity names
(tPF-2d D8, MEASURED pixelwise: k0 extents == tile popup rect, transparent
rows 217..247 == the button-band constants 0x151/0x16f). D28 item 9's
"which lib" question therefore resolves to "same answer as the tile popup",
and A7's SHAPEFRAME -1 x4 is fully explained: these four tiles carry no frame
WORD because their popup's frame comes from the 0x6fd8e slot, not the file.

## P1b — SECOND, INDEPENDENT SITE FOR THE SAME SLOT [verified disasm]

Byte census of the 3-byte displacement 8e fd 06 (ds:0x6fd8e) over
work/ascend_restored.bin: SIX sites, 0x431d, 0x61c4, 0x98a6, 0x341b7,
0x3dbbf, 0x559ed. The two that matter:

  0x3dbbf  (inside the msg-50 builder FUN_0x3db80, BEFORE the key switch at
            0x3dc50 `cmp eax,4 / ja 0x3e4db / jmp [eax*4+0x28fb8]`) — so the
            frame-lib read is KEY-INDEPENDENT: PLRES/PLIND/PLPRO/PLPOP (and
            the unreachable key-3 SQUARE case) all compose their popup from
            the SAME lib. One answer covers all four tiles.
  0x341b5  (a window-record constructor, separate function):
            mov ax, word [0x6fd8e]
            mov word [edx + 0x18], ax    ; lib id -> widget record +0x18
            mov word [edx + 0x1e], 0     ; frame RECORD = 0  (tPF-2d D9's
                                         ; frame-word field, store site
                                         ; 0x341c8 = one of the two
                                         ; "composition" sites D9 named)
  => the popup WINDOW record carries lib=37 (help.shp) + frame record 0
     verbatim. help.shp has EXACTLY 2 records (container read this session:
     count 2, tsz 24, k0 @0x28 dims words 335x255, k1 @0xc234 bbox
     (0,0,171,76)), so record 0 is k0 — the mineral frame D8 identified.
  NO WRITE SITE to ds:0x6fd8e exists (census of c7 05 / a3 / 89 0d / 66 89
  0d with that disp: ZERO) — the value 37 is a static init, which is why it
  is identical in 60/60 saves across three banks.

## P2 — GEOMETRY CONSTRAINT: THE NAIVE BLIT IS REFUTED [measured]
[SUPERSEDED BY P4 — the comparison below paired the frame against the wrong
rect; kept verbatim as the reasoning trail, per WIP discipline.]

The builder's content rect (0x3dbe5..0x3dc34, already cited law) is
(wx+10, wy+10)..(wx+0x145, wy+0xcf) = 316x198 exclusive / 316x198... stated
plainly: width 0x145-10 = 315, height 0xcf-10 = 197 between origins, i.e.
the TEXT/content box. help.shp k0's extents are 336x256 (port loader; raw
dims words 335x255 = the rect-minus-1 parity law). 336 != 316 and 256 != 198,
so the frame is NOT painted 1:1 into the content rect: the frame belongs to
the popup WINDOW record (P1b: rec+0x18/+0x1e) and is painted by the generic
frame-blit path at the window's own rect, while the builder's rect carries
only the queued lines. Consequence: shipping the frame at the indicator
popup REQUIRES the window-rect law (how the popup window's rect is derived
from the clicked widget) — the port has no popup-window object today, it
draws lines into the builder rect (ui.cpp ~3097 shared site). A blit of k0
into the port's existing dim-backing rect would mis-scale the mineral frame
by ~24 rows and ~20 columns. NOT SHIPPED — see TPF5-B.
## P3 — FRAME IS BLIT BY THE BUILDER ITSELF, + CONSUMER LEG [verified disasm]

Reading the builder prologue as a CALL SEQUENCE (not a byte scan):

    3dba1 push 0xf2 / 3dba6 push esi / 3dba7 call 0x5e940   ; queue bookkeeping
    3dbaf/3dbb1/3dbba push 0,0,0
    3dbb3 mov eax, 0x9f10c ; 3dbbc mov dx,[0x6fd8e]
    3dbc5 call 0x1fc34     ; eax = SHAPE RECORD (help.shp k0)
    3dbca push eax         ; arg1 = record
    3dbce push esi         ; arg2 = widget descriptor (widget+4)
    3dbd5 call 0x5caac     ; THE BLIT (shp.md S9/FUN_0005caac)
    3dbda lea esi,[esi+4] ; 3dbe0..3dbe4 5x movsd -> ebp+0x2e  (rect quad:
                          ;   widget+8 = X0, +0xc = Y0 read at 0x3dbe5/0x3dbf1)

So the frame is painted by the msg-50 builder, at the CLICKED WIDGET
descriptor, BEFORE the key switch (0x3dc50) — one frame answer for all four
tiles, and for the unreachable key-3 case too. The widget record layout
confirmed in-place: +0x8 X0, +0xc Y0 (the rect), +0x18 LIB ID, +0x1e FRAME
RECORD (exactly the fields the 0x341b5 site writes: [rec+0x18]=ds:0x6fd8e,
[rec+0x1e]=0).

THIRD LEG (the display-queue consumer): fn ~0x557xx — the function that
touches display object 0x7d3a2 (0x5587c), allocs a draw record (0x2a4ec),
writes the rect words +0xc/+0x14, then at 0x559e5-0x559fc does the IDENTICAL
`mov eax,0x9f10c / mov dx,[0x6fd8e] / call 0x1fc34 / call 0x5caac` frame blit
(its rect is a centred/derived box: half-difference math 0x557c2..0x557f8
plus an 8px border adjustment `sub esi,8 / add edi,8 / sub eax,8 / add edx,7`
at 0x559b1..0x559ba). ds:0x6fd8e is therefore THE POPUP-FRAME LIB slot for
the whole popup family, not an indicator-only oddity. [inferred from the
three sites: builder 0x3dbbf, record-composer 0x341b5, consumer 0x559ed]

## P4 — GEOMETRY LAW RECONCILED (P2's "naive blit refuted" was WRONG) [verified]

P2 compared k0 (336x256) against the BUILDER CONTENT rect and called the
1:1 blit refuted. That comparison was the wrong pair. The content rect is
(wX0+10, wY0+10) .. (wX0+0x145, wY0+0xcf) — a FIXED 316x198 TEXT box inset
10 from the window origin, independent of widget size. The FRAME is blitted
1:1 at the WIDGET ORIGIN (0x3dbd5, descriptor = widget+4). Check against the
tile popup, where both are already cited law (PLSQUARE X0=152 Y0=120,
windows.txt:1523-1526):

    frame  = 152..(152+335) x 120..(120+255) = 152..487 x 120..375
           == PLSQUARE's own widget rect EXACTLY (487-152+1=336, 375-120+1=256)
           == tPF-2d D8's measured k0 extents  [THREE-WAY AGREE]
    text   = 162..477 x 130..327  (inset 10 left/top/right: 487-477=10)
    bottom inset 375-327 = 48 = the button band (D8's cut-out rows 337..367)

=> LAW: popup frame = help.shp k0 blitted 1:1 at (wX0, wY0); text box = the
port's EXISTING indicatorPopupRect (= origin+10 .. origin+0x145/0xcf). The two
are consistent for the tile popup AND predict the indicator tiles: PLRES
X0=7,Y0=7 -> frame 7..342 x 7..262, text 17..332 x 17..214 (left/top/right
insets all 10, bottom inset 48 = band region).
RESIDUE (named, not blocking): PLPOP X0=355 -> frame 355..690 crosses the
640-wide screen by 51 px; the vendor blit clamps (shp.h blit-faithful clamp),
the port clips identically. No flip/re-anchor law exists in any of the three
sites — do NOT invent one (a future user grade may name it; until then the
clip is the faithful reading).

## P5 — SHIP (this iteration): help.shp k0 behind BOTH planet popups

Port site: ui.cpp drew a dim fill + vector outline at the CONTENT rect for
every planet popup (tile and indicator alike) and blitted NO shape anywhere —
the tPF-2d D8 identity was banked but never shipped (it was gated on D1;
research.md S14(f) verbatim: OQ-005 CLOSED t367, "no gate stands on shipping
decoded frame art"). Delta:
  - indpopups.{h,cpp}: `indicatorPopupFrameRect(content)` — pure law fn:
    frame rect = (content.x0-10, content.y0-10, +335, +255) with kIndPopupFrame
    {336,256} cited to help.shp k0 (measured P1/P4).
  - ui.cpp: load extracted/ascend01/data/help.shp next to the other libs; in
    the popup draw block blitShape(lib, 0, frame.x0, frame.y0) BEFORE the
    text; the dim fill stays as the load-failure fallback only.
  - Button band: UNCHANGED (the k0 cut-out is transparent, so the measured
    teal band fill (12,32,48) still shows through exactly as D8 describes).
Pins tests/test_indframe_tpf5a.cpp; mutation campaign scripts/tPF5a_mutate.sh.
## P6 — SHIP VERIFIED: SUITE, MUTATION, RUNTIME WITNESS [measured this session]

DELTA (checkpoint fdf4115 + this landing):
  - indpopups.{h,cpp}: kIndPopupFrameW/H = 336/256 + indicatorPopupFrameRect.
  - ui.cpp: indPopupFrameLib loads extracted/ascend01/data/help.shp beside the
    other libs (refusal prints 'ui popup frame lib refused' and falls back to
    the tPL-B2 dim backing — silent-degrade law); the popup draw block blits
    record 0 at the frame rect BEFORE the text and is NOT gated on
    planetSquarePopup (the builder blits before the key switch, P3).
  - tests/test_indframe_tpf5a.cpp x4 (CMake wired). Suite 631 -> 635, 0 fail.

MUTATION 5/5 CAUGHT (scripts/tPF5a_mutate.py; snapshot-copy revert, md5
verified after restore indpopups.cpp ab9d53f6 / indpopups.h c29c1035 /
ui.cpp 7deb688b; AFTER-RESTORE 635/0/0):
  M1 drop the -10 origin       CAUGHT (4 FAILs incl. the PLSQUARE 152..487 leg)
  M2 size 316x198 (content)    CAUGHT (rect + dims pins; the refuted reading dies)
  M3 drop the blit             CAUGHT (both wiring pins)
  M4 record 0 -> 1             CAUGHT (both wiring pins)
  M5 gate on planetSquarePopup CAUGHT (shared-frame pin)

RUNTIME WITNESS PASS (scripts/tPF5A_witness.sh, seed 5, Xvfb :99, PID-kill):
nav map -> STATUS rail (553,145) -> row 0 (300,100) -> PLRES (60,50); log
carries 'ui planet popup plres (1 lines)' and NO refuse line. CENSUS on the
shot, discriminator = pixels OUTSIDE the old dim-backing rect (the pre-fix
build paints black there; non-black-frac law tPF-11):
    top rows 7..10   x 30..320   = 1.000
    left cols 7..10  x 40..200   = 1.000
    bottom rows 259..262         = 1.000
    control 420..560 x 300..400  = 0.494 (starfield, unchanged)
=> the help.shp k0 mineral frame paints at the WIDGET ORIGIN, 10 px outside
the old backing on all three sampled edges. WITNESS TRAP LEARNED: the map
click 439,331 (ships.md's cited vendor coord) hits NOTHING on the port's seed
5 map — the port's nav law for the planet screen is the tPF5_port STATUS-rail
chain; and the app.log prints the home-star coords, so a witness can
self-locate instead of hard-coding.

## P7 — LEDGER / HONEST NEGATIVE

TPF5-A tracks NO OQ row (tPF-5 P8 law: D28 build-feedback items are not OQ
rows). D28 item 9 (scratchpad/t433-build-feedback.txt:9) closes as
reproduction+fix per the D30/D31 law: symptom = indicator popups carry no
mineral framing; cause = the port never blitted the popup frame lib at all
(the tile popup's help.shp identity was banked tPF-2d but gated, then never
shipped); fix = P6 delta; witness = P6 census. HONEST NEGATIVE: no OQ row
moved — open=[016,019] unchanged, both are USER-RULING work (STATE tOQ19-AUDIT
law). Residues banked, not blocking: (a) the PLPOP right edge crosses x=640
by 51 px and is clipped (faithful: no flip law exists at any of the 3 sites);
(b) the popup WINDOW object itself is still not modelled — the port blits the
frame at the derived rect rather than owning a window record, so any vendor
window-level behaviour (z-order vs the button band, move/refresh) stays
unmodelled; (c) the button band keeps the measured teal fill standing in for
k0's transparent cut-out (D8), unchanged this iteration.
