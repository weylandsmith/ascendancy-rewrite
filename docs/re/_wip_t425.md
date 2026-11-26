# t425 — GALAXY MAP CONTROLS + LIVENESS (cycle 1). Working log.
Task rows: (a) dial SPIN LAW supersede t416 latch model; (b) 3-of-8
lower-right buttons dead; (c) player FILTER buttons missing art; (d) corner
Exit popup drawn but inert.

## F0 — premise + control inventory [verified]
windows.txt COSMOSWnd children (extracted/ascend00/windows.txt ln223-415,
tr -d '\r'): SIX dials ROTRIGHT msg51 / ROTLEFT msg50 / ROTUP msg52 /
ROTDOWN msg53 / ZOOMOUT msg55 / ZOOMIN msg54 ALL with SENDPARAM1 999;
FOUR toggle/center buttons CENTERHOLO msg56 / TOGLANES msg57(BUTTONSTATE 1)
/ TOGSHIPS msg58(BS 1) / TOGEMPIRE msg60(BS 0) / TOGCOLONIES msg61(BS 1)
SENDPARAM1 0. (That's 11 children total in the cluster.)
D17 verbatim grade item: "galaxy dial rotates continuously on click (ours)
but original does not".

## F1 — DIAL SPIN LAW: LATCH IS GATED ON SENDPARAM1 == 50..55 [verified static]
COSMOSWnd handler 0x26b34 dispatch (capstone base-0 work/ascend_restored.bin,
work/t425_dispatch.txt): msgs 0x1b..0x3a -> 0x27d2a region; msg 0x3b (timer
pump) -> 0x27a18; msgs 0x3c/0x3d -> 0x27cce; msg 0x3e -> 0x27824;
msg 0x3f -> 0x27ad2; msg 0x42 -> 0x27b87; default -> parent 0x336b4.

0x27d6f (reached for msgs 0x32..0x38 via 0x27d2a cmp-chain):
  0x27d79  cmp dword [esi+0x39], -1 ; je 0x27d90
  0x27d7f-0x27d8b  ebx=0x2ec edx=0xef0 eax=0 call 0x2a428   (sound/aux seam)
  0x27d90  edx = dword[esp+0x36] sar 0x10   (param1 high word — the
           SENDPARAM1 the button sends)
  0x27d99  cmp edx, 0x32 ; jne 0x27887      <<< GATE: latch runs ONLY param1==50
  0x27da2..0x27dc5  pair-0 latch law on byte[esi+0xc0]:
        bit0=0            -> or 1, and 0xfd  (ACTIVE dir=0)
        bit0=1,bit1=0     -> and 0xfe        (STOP: same-dir click toggles off)
        bit0=1,bit1=1     -> and 0xfd        (FLIP dir to 0)
  0x27882  mov eax, 1                        (fallthrough ONLY when gated in)
  then sequential cmp chain for the other params (0x27887 msg-cmp 0x33,
  0x278d7 pair1 0x34, 0x27922 0x35, 0x27968 0x36, 0x279b1 0x37) — each block
  is entered by its param cmp, each ends `mov eax,<bitmask>`; the msg-cmps
  are a SECONDARY discriminator, the PARAM is what selects the pair block.
  After the chain (0x279eb): cmp dword[esp+0x10],4 ; jne skip;
  push 0; ecx=0x3f; ebx=1; push eax; edx=[esi+0x41]; eax=0x7a35c; call 0x5669c.

DECISIVE CONSEQUENCE: the six dial buttons send SENDPARAM1=999 (windows.txt
above). 999 != 50..55, so a BUTTON CLICK on a dial NEVER touches the latch
byte [esi+0xc0]. The latch is driven ONLY by senders that use param1 in
50..55 — i.e. the direct-manipulation path (help.txt 1spin ln220: "Use the
right mouse button if you want to zoom or rotate continuously"). The t416
model (click = latch toggle, pump = continuous spin) is REFUTED for clicks —
exactly matching the user's live observation ("original does not [spin on
click]").
## F2 — LANDED (code + pins + witness, cycle 1)
(a) CADENCE: kSpinTickMs 250 -> 1000 [t302-measured ~1/s; cam3d.h comment
    cites the witness lines]. Latch law itself STANDS (F1b correction —
    the gate is on the msg id; t416's model was right, its CADENCE was 4x
    fast). Feel verdict still belongs to the D16 q5 live row (not closed).
(b) THREE DEAD BUTTONS ROUTED (ui.cpp): TOGSHIPS -> shipsOn (transit-fleet
    pips at from/target midpoints, kOwnerRgb); TOGCOLONIES -> coloniesOn
    (ownership tinting); TOGEMPIRE -> empireOn (owner-coloured re-strike
    of single-owner lanes; starts OFF per BUTTONSTATE 0). Printed-only
    seam REMOVED. Witness: one printf line carries all four layer bits.
(c) RACE FILTER (msg 62 law): raceVisibleMask (init 0xff), click on slot i
    XORs (1<<i) [windows.txt bit column == 1<<slot, verified]; consumer
    hides that owner's stars + fleet pips; slot square dims to half
    luminance (shape+luminance redundancy, CVD law). FILTER ART SEAM
    (named, honest): vendor slot faces k20..k50 are 16x16 solid swatches
    (indices 16,19 / 20,23 / ... / 49,52 measured this session) that
    decode DARK in static game.pal ((18,10,19) at idx 20), while the
    refcap slot reads (89,24,56) — a RUNTIME palette/ramp NOT in the
    static file (nearest static entry (63,39,41) idx 229, delta 1126).
    Blitting raw would paint near-black; port keeps CVD-safe kOwnerRgb
    fills + luminance encoding. The (89,24,56) runtime ramp source is the
    open sub-question (t348-style runtime-pal suspicion corroborates).
(d) CORNER POPUP CLICK: doEscape factored (t409 modal precedence + t410
    chain + quit-at-bottom, verbatim text moved, not rewritten); click
    inside exitPopupRect (recomputed at click point) fires it.
PINS: tests/test_mapctl_t425.cpp x4 (toggle defaults vs BUTTONSTATE; the
4 cluster msgs/frames verbatim; RACE bit column + rect law + gap inert;
popup geometry all-four-corners). Suite 427/0/0.
WITNESS scripts/t425_mapctl_witness.sh PASS: log sequence
lanes1/ships1/colonies1/empire0 -> 4 flips -> "0 0 0 1"; race slot5 ->
mask 0xef; slot5 lum 137.0 -> 68.5 while slot1 198.5 -> 198.5 (mask
touches ONLY the clicked slot); field stays non-empty (1348 px); corner
click 10,10 logs + process EXITS. Shots work/r1/loop/t425_{base,after}.png.
SEAMS (named): S-a ships layer = transit midpoints (port's entire ship
state, campaign.h:284 — no per-ship positions exist to hide/show);
S-b filter->owner mapping slot i == owner i [inferred from kOwnerRgb
order + 7-row table; the vendor's race-index->owner-index chain was NOT
traced this cycle]; S-c empire overlay = single-owner lane re-strike
(port lane model has no fill region to tint); S-d popup click = Escape
chain (the glyph names it; no vendor capture of the corner probe, t419
law unchanged).
NEXT PROBE (cycle 2): runtime-palette ramp for (89,24,56); filter->race
index chain (0x27258 consumer reads stride-0x1ee race records — trace the
race->owner map); D16 q5 live dial-feel verdict.

## F1b — GATE IS ON THE MSG ID, NOT PARAM1 (self-correction) [verified static]
EARLIER DRAFT CLAIM RETRACTED: [esp+0x36] is NOT param1. The handler frame
stores the msg word at esp+0x38 (0x26b3c `mov word ptr [esp+0x38],dx`), so
the MISALIGNED dword read at esp+0x36 shifted right 0x10 == word[esp+0x38]
== THE MSG ID. PROOF: the default path 0x26b8f does exactly this read,
sar 0x10, and passes edx to the PARENT dispatcher 0x336b4 — which dispatches
on dx (cmp dx,7/0xe/0xf/0xc9/0xca). So the latch gate 0x27d99 `cmp edx,0x32`
and the chain cmps 0x33/0x34/0x35/0x36/0x37 select pairs BY MESSAGE ID, as
t416 originally modeled. The dial buttons send SENDMESSAGE 50..55 — the gate
PASSES. t416's latch-on-click model STANDS at the gate level; the D17 live
observation ("original does not spin continuously on click") is NOT yet
explained statically. Candidate: pump cadence — msg 0x3b measured PERIODIC
~1/s (t302 live witness, docs/re/_wip_t302.md ln88-90,138,148-154), delta
2 deg/tick => 2 DEG/SEC, ~1 px/s on-screen: plausibly "does not spin" to a
human eye, vs the port's kSpinTickMs=250 (8 deg/s). NOT a closure (strict-
close): cadence upgrade 250->1000 ms is measurement-backed (t302); the
feel verdict belongs to the D16 q5 live row.
Register law at handler entry (from sender 0x56ad4 + 0x2f4f0 site):
eax = window, edx = msg id, ecx = SENDPARAM1, ebx = SENDPARAM2. The tail
0x279eb `cmp dword ptr [esp+0x10],4` therefore tests PARAM2 == 4 (prologue
0x26b41 stored ebx at esp+0x10) — only param2==4 senders self-notify via
msg 0x3f (param = the single-bit mask 1/4/0x10 set this press). Buttons
(ship SENDPARAM2 0) do not self-notify.
msg 0x3f (0x27ad2): [esi+0xc0] &= ~param2 (mask-clear variant of the stop).
FULL MSG MAP OF 0x26b34 (tree 0x26b4b..0x26b89 + 0x27d2a + 0x27cce):
  26 -> 0x271da  store byte[esi+0xd9]=param1 low byte
  27..55 -> 0x27d6f latch chain (dials; sound 0x2a428 ebx=0x2ec edx=0xef0
       when dword[win+0x39] != -1 first)
  56 CENTERHOLO -> 0x27b02: call 0x26a9c (RECENTER camera) + 0x284bc repaint
  57 TOGLANES -> 0x27b58: TOGGLE dword[esi+0xc4] (0 <-> -1) + repaint
  58 TOGSHIPS -> 0x27d40 (fallthrough of 0x27d36 cmp): TOGGLE dword[esi+0xc8]
  59 -> 0x27a18 PUMP (2deg pairs + zoom, repaint)
  60 TOGEMPIRE -> 0x27cce jbe 0x27b29: TOGGLE dword[esi+0x58a]
  61 TOGCOLONIES -> 0x27cce fallthrough: TOGGLE dword[esi+0xd0] AND TOGGLE
       dword[esi+0xcc] (two fields, verbatim)
  62 RACECONTROLS -> 0x27824: byte[esi+0xd8] ^= bit(dl=param2 low byte)? NO:
       bit set -> CLEAR it, bit clear -> SET it (toggle), then repaint.
       RACE<N>CONTROL table verbatim (windows.txt ln428-435): NUMCONTROLS 7;
       rows bit,x0,449,x1,465,0,FRAME = 1/479/495/20, 2/501/517/25,
       4/523/539/30, 8/545/561/35, 16/567/583/40, 32/589/605/45, 64/611/627/50
       (SHAPEFILE 0 = 1starmap; strip frame 19; strip rect 474,442-632,472).
  63 -> 0x27ad2 mask-clear latch;  66 -> 0x27b87; default -> parent 0x336b4.
INIT 0x2718c..0x271b4: c4=c8=cc=d0=0xffffffff, byte d8=0xff (all VISIBLE).
d8 CONSUMER (star draw loop 0x27258..0x272ac): per race idx i 0..6 test
(1<<i) in the d8 copy; zero -> skip that race's records (stride 0x1ee table
at 0x12fd6/0x12e19) => d8 = RACE VISIBILITY MASK. Paint snapshot 0x29514
copies c0,c4,0x58a,c8,cc,d0,d4,d8,d9 into the scene-render param frame.
msg 0x3f (0x27ad2): eax=ebx; not eax; edx=[esi+0xc0]; and edx,eax;
  ebx=0x3f; [esi+0xc0]=edx — clears latch bits EXCEPT bit0?? (scratch:
  ebx semantics = msg param; full-clear variant at 0x279f2 when param==4).
OPEN: which msg does a plain button press actually deliver (0x32 with
param1=999 => NO-OP for dials) — does the vendor dial click do ANYTHING?
Next: trace 0x27d6f fallthrough tail + msg 0x32 default; and check whether
buttons with SENDPARAM1 999 get 0x32 at all (button engine 0x56xxx).

## F3 — CYCLE 2 S-e: THE RUNTIME-RAMP PREMISE IS REFUTED (two compounding
## cycle-1 errors) [measured this session, scripts/t425b_face_census.py]
ERROR 1 (wrong rect). The (89,24,56) refcap reading is NOT the race strip.
original-strategic-map.png rows are GAME rows + 40 (palette.md S4 law: "game
coords = root rows - 40", refcap.md S1). The RACECONTROLS strip is game
y 442..472 -> png rows 482..512 = OUTSIDE the 640x480 png: NO refcap shows
the race slots. The maroon blobs cycle 1 measured are the THREE
BUTTONSTATE-1 toggle buttons (TOGLANES/TOGSHIPS/TOGCOLONIES, windows.txt
X0 479/557/596 y403..433 -> png 443..473; connected-component bbox of idx80
gives EXACTLY x 479-509, 557-587, 596-626 + the TOGEMPIRE slot x518-548
which is NAVY (12,32,48) = idx 242 — the BUTTONSTATE-0 button).
BONUS LAW from that: TYPE-25 button face = SHAPEFRAME 15/16/17/18 (1starmap)
circle glyph over fill idx80 (maroon, ON) vs idx242 (navy, OFF) — vision
confirmed 3 maroon + 1 navy at exactly the BUTTONSTATE 1/1/0/1 pattern.
ERROR 2 (missing conversion). (89,24,56) IS in game.pal: idx 80 raw
(22,6,14), converted via c=(v<<2)|(v>>4) = (89,24,56) EXACT (palette.md S2).
Cycle 1 compared refcap pixels against the RAW 6-bit table ("(18,10,19) at
idx 20") — a units error. palette.md S3 already refuted any runtime palette
for this screen: the strategic-map shot is 307200/307200 px inside the
CONVERTED table. No runtime ramp exists to find.

## F4 — THE REAL FACE LAW (scripts/t425b_face_census.py, 1starmap.shp,
## row-walk = t399_digit_faces.py grammar) [measured]
The seven slot faces are NOT solid swatches: each is 16x16, exactly TWO
opaque indices + transparent skip, 80 px dark tone + 51 px bright tone
(a glyph), and both indices decode fine through static game.pal:
  k20 slot1 idx16(0,85,40)/idx19(0,170,81)      GREEN
  k25 slot2 idx20(73,40,77)/idx23(158,81,174)    PURPLE
  k30 slot3 idx24(166,101,4)/idx27(255,235,97)   YELLOW
  k35 slot4 idx28(186,65,89)/idx31(239,154,174)  PINK
  k40 slot5 idx32(65,56,40)/idx35(121,105,69)    BROWN
  k45 slot6 idx36(20,56,93)/idx39(36,117,207)    BLUE
  k50 slot7 idx40(117,48,4)/idx43(235,121,4)     ORANGE
  (stride frame k19 = 158x30 strip backdrop, idx200/0/196 — not a swatch)
Cycle 1's "indices 16,19/20,23/../49,52" enumeration was off for the later
slots (k30 is 24/27, not 24/23; k50 is 40/43, not 49/52).
CONSEQUENCE for the port: the honest fix is to paint each slot's OWN face
(frame 20+5i) through the converted game.pal — the hues above ARE the
per-slot colours; the CVD-safe kOwnerRgb fill was a placeholder for a seam
that does not exist. (Face glyph shape census: next section.)

## F5 — FACE FAMILY LAW + THE OUTLINE LAW (help.txt) [measured]
Full census of 1starmap k20..k54 (scripts/t425b_face_census.py): every slot
i (0-based) owns a FAMILY OF FIVE records at base = 20 + 5i:
  base+0  16x16  dark tone + bright tone, NO outline        (windows.txt
                                                            SHAPEFRAME col)
  base+1  16x16  BRIGHTER dark tone + same bright tone
  base+2  17x17  base+0 glyph + idx103 OUTLINE (190,255,255), 28 px
  base+3  17x17  base+1 glyph + idx103 outline
  base+4  16x16  GREY variant: idx0 (0,0,0) + idx6 (97,97,97)
Tone pairs per slot: 16/19, 20/23, 24/27, 28/31, 32/35, 36/39, 40/43
(brighter variants 18/19, 22/23, ...). All seven glyphs are STRUCTURALLY
IDENTICAL (pixel-class compare) — only the palette pair differs, so the slot
colour IS the species colour and the glyph is a fixed mark.
DECISIVE SEMANTICS from the vendor's own help (extracted/ascend00/help.txt
ln361-373, HELPINDEX rcontrol == the RACECONTROLS HELPINDEX, verbatim):
  "This group of colored buttons is used to filter Galactic Display
   information by species. @@Only information pertaining to the species
   whose colors are OUTLINED will be displayed."
=> VISIBLE slot = the OUTLINED frame (base+2/+3), FILTERED slot = the GREY
   frame (base+4). The port's "half luminance" encoding is superseded by
   cited vendor art. (dark vs bright variant inside the outlined pair is a
   named residual — no static site resolves it; k22/k23 differ only in tone.)

## F6 — S-f TRACE + HONEST NEGATIVE [measured static + live-RAM census]
(i) The d8 consumer at 0x29976..0x29998 (star paint) does:
      dl = [esp+0x54] (running bit 1<<i)  AND  cl = [win+0xd8]  -> skip if 0
      al = byte [ebp + 0x12e18]           ; race-record byte +2
      edx = 0x13 + 4*al - 3 = 0x10 + 4*al ; then add ebx ([esp+0x38]) -> push
    so the vendor's per-race COLOUR is DATA-DRIVEN (race record byte +2),
    NOT "slot i == owner i". The filter is an AND on the same byte-indexed
    race row, i.e. filter slot i filters RACE ROW i.
(ii) LIVE-RAM census (scripts/t425b_race_colour.py + t425b_race_probe.py,
    pointer law B+0x82bb0+X, B=0x1bf4d8, 20 slots work/r1/playcap/save):
    row base VALIDATED by independent anchors — byte +0 == race index i for
    rows 0..4 (rows 5,6 = 0xFF absent), relation-diagonal word [+0x1b2+2i]
    == 0 on every row, [0x13b98]=4 (races present), [0x7458e]=0 (local race).
    byte+2 = [0, 1, 6, 2, 1] for races 0..4 — NON-INJECTIVE, so byte +2 is
    NOT a 7-way colour permutation of the slot ramp and the paint-site table
    at [esp+0x38] is NOT resolved (also: the loop bound at 0x29957 is 0xd82,
    which is 7*0x1ee + 0x40 — the row-walk origin of THAT loop differs from
    the 0x12e16 base used by the diplo/AI sites; unresolved).
VERDICT: S-f stays OPEN (strict-close: no cited colour-permutation law). The
port's slot i == owner index i mapping is UNCHANGED and the seam note must
say "vendor colour index is data-driven (byte +2), permutation unresolved".

## F7 — CYCLE 3: THE FOUR CIRCLES ARE THE TOGGLE BUTTONS THEMSELVES (cycle-2
## geometry claim REFUTED) [measured this session, scripts/t425c_circle_census.py
## + t425c_button_measure.py + t425c_face_diff.py + t425c_shift_sweep.py]

(i) GEOMETRY. The four circles are NOT inside the race strip and are NOT at
pitch 44. windows.txt verbatim: TOGLANES 479,403..509,433 f15 msg57 BS1;
TOGEMPIRE 518,403..548,433 f16 msg60 BS0; TOGSHIPS 557,403..587,433 f17
msg58 BS1; TOGCOLONIES 596,403..626,433 f18 BS1 msg61 — pitch 39, row ABOVE
the strip. The cycle-2 "x 479,523,567,611 pitch 44" numbers are RACE1/3/5/7
x0s (pitch 22 x2) — a mis-attribution. Native vision on the 4x corner crop
confirms: row (a) 4 small buttons (spin/zoom cluster row), row (b) FOUR ROUND
BLUE-RINGED buttons at x 479/518/557/596, row (c) the maroon strip.

(ii) PAINT LAW +1y. Shift sweep (-3..3): best exact-match for k15/k16/k17/k18
is at dx+0 dy+1 with 71.9/71.4/71.4/81.9% and CONSISTENT index->colour
correspondence (TOGCOLONIES: 34/45 indices >90% consistent; k109/k106/k107
100% consistent). => the vendor blits the SHAPEFRAME at rect.y0+1 (art top
row lands on png row 404, face bottom row 433). The residual 18-28% is
concentrated on idx242->idx103 (ring highlight over face bg) — see (iii).
The race faces k20..k39 match 0.0-1.0% at EVERY offset: the refcap race slots
are NOT the static faces (consistent with the t425b finding; this now has a
number).

(iii) OPEN SUB-QUESTIONS at handoff: (A) the idx242->103 residual — is the
ring partly overpainted (hover/pressed state) or is it the starfield speckle
showing through? (B) the STRIP backdrop in the refcap is conv idx80
(89,24,56) maroon 1900px, NOT k19's idx200 (12,12,16) — k19 exact-match 0.3%.
The strip's runtime colour source is UNKOWN (race colour? remap? different
record?). NOT yet the port's problem unless the port paints k19 there (it
does — ui.cpp step 4) — check the port shot.

## F8 — THE TOGGLE STATE PAINT LAW, 900/900 EXACT [measured,
## scripts/t425c_toggle_state_law.py] and the refcap OFFSET CORRECTION

THE OFFSET. docs/assets/refcap/original-strategic-map.png is 640x480 and is
NOT window-relative: png rows 0..39 are PURE BLACK (all 40 rows, verified
A[y].any()==False) and the green TURNCOUNT digits (windows.txt TURNCOUNT
474,7-632,43) measure at png y 52..80. => PNG y = SCREEN y + 40, the refcap.md
S1 root law, for THIS file. (t394's identity-mapping note belongs to the
OTHER shot, scratchpad/galaxymap-original.png 642x481 — the two captures do
not share a mapping law.) Cycle 2's assignment line "ALREADY the window — do
NOT add +40" is REFUTED; cycle 2's own ui.cpp comment ("the strip is at png
rows 482..512, outside the shot") was RIGHT and contradicts the assignment.

WHAT THE FOUR CIRCLES ARE. png rows 443..473 == screen rows 403..433 == the
FOUR LAYER TOGGLES at pitch 39 (x 479 TOGLANES / 518 TOGEMPIRE / 557 TOGSHIPS
/ 596 TOGCOLONIES), SHAPEFRAMEs k15..k18. Not pitch 44, not the race strip.
The row above them (png 404..434 == screen 364..394) is the spin/zoom cluster
(4 columns holding the 7 ROT*/ZOOM*/CENTERHOLO controls). THE RACE STRIP
(screen y 442..472 => png 482..512) IS NOT IN THIS CAPTURE AT ALL — clipped
below the root edge. So this file carries ZERO pixels of the race slots, and
every "refcap slot" reading in t425 (cycle 1) and t425b (cycle 2) was reading
TOGGLE BUTTON pixels at png 449..465.

THE LAW [verified, 4/4 buttons bit-exact over the full 30x30 face]:
  the vendor blits the SHAPEFRAME at (X0, Y0+40) and substitutes ONE palette
  entry according to the button's state:
      face idx 242 (raw (3,8,12) navy well) -> idx 80 (raw (22,6,14) =
      conv (89,24,56) maroon) when the toggle is ON; left 242 (navy) OFF.
  TOGLANES BS1 -> 900/900 EXACT under 242->80; TOGSHIPS BS1 -> 900/900;
  TOGCOLONIES BS1 -> 900/900; TOGEMPIRE BS0 -> 900/900 under the RAW palette.
  Zero residual pixels on all four. Three independent sources agree on which
  button is which state: windows.txt BUTTONSTATE, the refcap well colour, and
  the handler init 0x2718c (dword win+0xc4/c8/d0 = -1 visible, win+0x58a /
  byte win+0xd8 empire OFF).
NEGATIVE CONTROL: the spin/zoom row is NOT state-painted — the same remap
degrades it 74.6% -> 21.5% (raw match 74.6..94.9%; the residual is cosmos
speckle over the navy well, the t422 chrome effect, not a colour law).
CONSEQUENCE FOR THE PORT: ui.cpp step 3 blits kMapCtl frames RAW, so the port
shows an ON toggle identical to an OFF one — the vendor's only visual layer-
state signal. Fix = well-colour substitution idx242->idx80 for the four
toggles by state.

## F9 — COLLATERAL: t425b's slot readings were toggle pixels [verified]
t425b measured "slot1 (89,24,56) / slot3 navy / slot5 maroon / slot7 maroon"
at png 449..465 x {479,523,567,611}. With the corrected mapping those x are
inside the toggle cells 479..509 / 518..548 / 557..587 / 596..627, and the
colour pattern (maroon, NAVY, maroon, maroon) is exactly BUTTONSTATE 1,0,1,1
== TOGLANES ON, TOGEMPIRE OFF, TOGSHIPS ON, TOGCOLONIES ON. That is a second,
independent confirmation of F8 (and it means the t425b "face family" law has
NO refcap support — it rests on the .shp family structure + help.txt only).

## F10 — SECOND VENDOR SHOT: SLOT GEOMETRY CONFIRMED, SLOT COLOUR IS
## OCCUPANT-DATA (the port's family-colour assumption is a named seam)
## [measured, scripts/t425c_slot_faces.py on scratchpad/galaxymap-original.png]

WHY THIS SHOT MATTERS: it is 642x481 with IDENTITY mapping (t394), so it is
the ONLY vendor capture we have that actually contains the race strip (rows
442..472; its dominant colour is idx200 == 1starmap k19's own backdrop). The
640x480 refcap never showed a slot pixel (F8).

GEOMETRY [verified]: every slot rect matches the +2 (outlined) family member
at dx0/dy0 as the BEST of all five members and all 49 offsets — slot1 k22
62.3%, slot6 k27 52.6%, slot7 k32 61.2%; the +1/+3 bright and +4 grey members
score 1.2..13.8% / 0.0%. So "visible slot == outlined member at the verbatim
rect" holds on real vendor pixels (t425b's help.txt reading survives).

COLOUR [inferred from a blend-degraded capture — see caveat]: the DOMINANT
tone in each rect is an exact game.pal entry, but NOT the family's own pair:
  slot@479 idx16 ✓ | slot@501 idx24 | slot@523 idx20 | slot@545 idx32 |
  slot@567 idx28 | slot@589 idx36 ✓ | slot@611 idx40 ✓
Family pair for slot i is (16+4i, 19+4i), so slots 2<->3 and 4<->5 are
SWAPPED relative to the family order. [inferred] The vendor paints slot i with
the GEOMETRY of family i and the COLOUR PAIR of whichever species occupies
slot i — the same palette-substitution mechanism F8 measures on the toggles.
That is a data-driven slot->colour map, i.e. exactly the S-f colour byte the
t425b probe could not locate. The port's current paint (family base colours,
ui.cpp step 4) is therefore correct only when the save's species order is the
identity — a NAMED SEAM, not a pin (no cited colour-byte source yet).

CAPTURE CAVEAT [verified]: this shot is NOT a pure game.pal render — it
contains colours outside the converted table ((95,73,111), (125,121,138)) and
blends like (0,138,66) between conv idx16 (0,85,40) and idx19 (0,170,81). That
is why slot1 tops out at 62.3% rather than 100%, and why the same shot scores
the toggle well law only 37.3%/39.0% (DIRECTION still right: the swap lifts
LANES/SHIPS/COLONIES from 0.1-0.3% and hurts EMPIRE 39.0% -> 0.6%). The
640x480 refcap remains the authoritative exact-diff source (palette.md S3:
307200/307200 px inside the converted pal).


## CORRECTION (tPF-7b, 2026-11-26): the cadence upgrade 250->1000 was NOT
## measurement-backed. The t302 "~1/s" it cited measured OUR POLL LOOP
(census bank windows at ~1 s poll cadence), never the pump — REFUTED at the
pump leg by tNG-S S28 (REFUTED-ROUTES, basis integration 28-33 fires/s) and
independently at the reswin timer by tPF-7 P6. The 1000 ms constant this
session wrote into cam3d.h made the cosmos dials 29x slow (user-visible;
tPF-7b shipped kFireLoopMs=34 + pins + witness). Historical F-block text
above (ln 49, 104-108) kept as the record of what was believed then.
