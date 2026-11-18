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
