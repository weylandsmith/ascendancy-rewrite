# _wip_tPF2d.md — POPUP LAW SHIP (tPF-2d, 2026-11-25)

Assignment: docs/STATE.md NEXT tPF-2d. Ship what tPF-2c proved (C1-C11 in
_wip_tPF2c.md — NOT re-derived here), close the three named residues:
(1) 0x744a0 label-registry base (live-RAM witness), (2) help.shp k0 frame
identity (pixelwise), (3) TYPE-14 lib-binding site; plus PLANLIST paint fn
0x3cbb4 row-art citation, and the C6 button-law PORT replacing the invented
y1+2..+30 strip.

## P0 — SITTING CHECK (ran FIRST, RC=0)
work/r1/tPF2d_pre_sitting.out: trusted turn-change rows 45,227, newest
t=1335 — byte-identical class to the tPF-3 standing baseline. No user
sitting; stale assignment stood. Production ring untouched.

## D1 — LABEL REGISTRY LIVE RESOLVED FROM BANKED SAVES (no capture needed)
scripts/tPF2d_label_registry.py on work/r1/bank-play-20261111-t377 (20 saves,
BDA-H per save; law: ds-disp D -> linear 0x242000+D -> member +H; t440 pattern).
MEASURED, unanimous 20/20:
 - ds:0x744a0..0x74524 is NOT a pointer array (small u16/u8-ish values
   0x70504, 0x20302, ...). C11's "0x744a0 is the registry base" hypothesis is
   REFUTED by direct measurement.
 - THE POINTER ARRAY IS ds:0x74528: slot 0 = 0x3 (the indicator key, tPLB2 law
   re-confirmed: key overwrites registry slot 0), slots +1..+23 = u32 pointers
   0x2530a8, 0x2530ad, 0x2530b3, 0x2530ba, 0x2530c0, 0x2530c9, 0x2530ce,
   0x2530d9, 0x2530e3, 0x2530e8, 0x2530f0, 0x2530fd, 0x253104, 0x25310e,
   0x253116, 0x25311d, 0x253128, 0x25312f, 0x25313d, 0x253145, 0x25314b,
   0x253157, 0x25315d at ds:0x7452c..0x74588 — 23 pointers, strings live in the
   RUNTIME game-data heap (0x2530xx), not the payload span (getter pool copies).
 - Adjacent heap text at 0x74590/0x745a4 = 'Minions'/'Somev...' inline — the
   0x7458c+ region is string DATA, not table.
OPEN FOLLOW-UP: the consumer read at 0x3d5db must address 0x74528-family, not
literal 0x744a0 — disassembling 0x3d5db NOW to settle the exact id->slot law.

## D2 — ID->LABEL MAP RESOLVED (D1 decode fixed: heap pointers are RAW linear,
## member = linear + H; the 0x242000-subtract form applies ONLY to static disps)
scripts/tPF2d_label_registry.py RC=0, 20/20 saves unanimous (bank-play-20261111-
t377; work/r1/tPF2d_reg_t377.out + .json). THE TABLE (u32 ptr at ds:0x744a0+id*4):
  35 Tiny  36 Small  37 Medium  38 Large  39 Enormous  40 Husk  41 Primordial
  42 Congenial  43 Eden  44 Mineral  45 Supermineral  46 Chapel  47 Cathedral
  48 Special  49 Tycoon  50 Cornucopia  51 Cancel  52 Create Colony  53 Abandon
  54 Build  55 Leave Orbit  56 Refit  57 Invade  58 Automate
(strings live in the runtime heap 0x2530a8..0x253164, NOT the payload span —
why the static scan found nothing; slot 34 (ds:0x74528) currently reads 0x3 =
the INDICATOR KEY clobbering a pointer slot (tPLB2 law re-confirmed live:
0x3d3a1 `mov esi,[0x74528]` IS reading registry slot 34 as the key).
CONSEQUENCES:
 - C11 RESOLVED: 0x744a0 IS the registry base; 0x74528 is base+0x88 INSIDE it.
   fn 0x3d2a0's "three loops" all write this ONE table (ids 35..58 window).
 - C9 RESOLVED: the naive static.txt map was wrong; the live table says
   id 54='Build' (the 54-loop refcap button FITS), 51='Cancel' (always-append
   dismiss leg FITS), 57='Invade' + 52='Create Colony' + 55='Leave Orbit' +
   56='Refit' are the SHIP legs, 53='Abandon' + 58='Automate' the OCCUPIED-
   cell legs (58 gated by checker(item 35=Automation, cell) — campaign.h:
   item 35 IS the Automation governor item, coherent).
 - ids 35..50 = planet SIZE+ATMOSPHERE+SOIL words (Tiny..Cornucopia = the
   indicator-popup words, ds:0x74528-key dispatch family).

## D3 — CONSUMER GEOMETRY CORRECTED BY DIRECT DISASSEMBLY (0x3d60e..0x3d67e)
Per button (loop over id array; edi = remaining count divisor):
  rec+0x4 = x (cursor, starts 0xa0=160)      rec+0x8 = 0x151 = 337 CONSTANT
  w = (0x1df - x) / remaining;  x_next = x + w, CLAMPED to 0x1df (0x3d636)
  rec+0xc = x (same x)                        rec+0x10 = 0x16f = 367 CONSTANT
  rec+0x45(u16) = id (SENDMESSAGE leg)        label = raw copy of 0x744a0[id]
  n == count == 1 -> SPECIAL path 0x3d684: getter(0x1e=30) = 'OK' single button.
=> C6's "rec+8 = x+1, rec+0xc = hiword(ebp-6)" is SUPERSEDED (ebp-6 hiword is
a call arg to 0x56ca4 at 0x3d64f, not a store). THE BUTTON BAND IS ABSOLUTE
SCREEN: y 337..367, x from 160 even-spread to 479. The PLSQBUT template rects
are overwritten per this law.

## D4 — COMPOSITION LEGS RE-READ VERBATIM (0x3d397..0x3d58e, work/r1/tPF2d_comp.txt)
Gate: key==3 (ds:0x74528 slot-34-as-key). cl = cell item (0xff empty, 0x17=23
ship-family item).
 - EMPTY (0xff) 0x3d550: loop ecx 0..0x26 (skip cl==5), append 54 ONCE PER
   checker(0x3830c, item=ecx, cell=widget+0xab) PASS.
 - SHIP (0x17) 0x3d3ce: automated bit [cell4+2]&1 && owner checks; appends
   52 (0x34), 57 (0x39 'Invade'), ALWAYS 55 (0x37 'Leave Orbit'), 56 (0x38).
 - NON-EMPTY NON-SHIP 0x3d506: item!=5 -> append 53 'Abandon'; then 0x3d51d
   checker(0x3830c, ARG 0x23=35, cell) PASS -> append 58 'Automate'.
 - ALL paths merge 0x3d591: append 51 'Cancel'.

## D5 — CONSUMER LAW CORROBORATED PIXELWISE ON THE REF CAPS (this session)
Bright-pixel census of scratchpad/original-planet-screen-*.png (512x398 ->
640x480 scale): button-band border rows y=335 (top) and y=371..373 (bottom)
span x 153..481; label text rows y=348..356.
 - Build/Cancel cap: text clusters centre ~233 and ~400; LAW x=[160,319]+
   [319,479] centres 239.5/399 — MATCH (text drawn centred in each button).
 - OK cap: text centre ~318.5; LAW single-button x=[160,479] centre 319.5 —
   MATCH. AND the n==1 special path 0x3d684 (cmp count,1; getter(0x1e=30))
   explains WHY the non-buildable popup reads 'OK' even though the id array
   is [51] ('Cancel'): SINGLE BUTTON -> LABEL IS getter(30) REGARDLESS of id.
 - Band y 337..367 (rec+8/rec+0x10) sits INSIDE the border rows 335/371: the
   button band is the popup's bottom strip — the popup rect itself is the
   help.shp frame; buttons are absolute-screen y 337..367, NOT relative to
   the text rect. Our planetPopupRect.y1+2..+30 strip was wrong in kind.

## D6 — tPF-2c C6's "54-LOOP APPENDS PER BUILDABLE ITEM" IS REFUTED (byte law)
0x3d582..0x3d58e (append 54) FALLS THROUGH to the common tail 0x3d591 — the
loop-back edge 0x3d559 is reachable ONLY from the checker-FAIL path (0x3d580
je 0x3d559) and the skip-5 path. BYTES: 3d582 `8b45 e8 40 c7448584 36000000
8945 e8` then 3d591 `8b45 e8...`. => the empty-cell popup holds AT MOST ONE
54 button: the FIRST checker-legal item (scan order 0..0x26, skip 5), then
51. The -0x7c disp at 0x3d586 vs -0x78 elsewhere = the same array written
index+1 style (-0x7c+(n+1)*4 == -0x78+n*4; count update 0x3d58e identical).
Consequence: the refcap "Build"+"Cancel" popup is EXACTLY [54,51] — the
shipped behaviour of a single Build button was RIGHT for the wrong reason.

## D7 — PORT SHIPPED (code this session)
rewrite/src/ui/planetwin.{h,cpp}: popupButtonLabel (D2 registry words),
popupButtonIds (D6 break law + 53/58 legs + always-51), popupButtonRects
(D3 spread: y 337..367, x0=160, w=(479-x)/remaining, clamp 0x3d636 then +1),
popupButtonText (n==1 -> getter(30) "OK", 0x3d684..0x3d6bf VERBATIM disasm
re-read this session incl. the key!=3 path 0x3d6c1 which builds a SINGLE
full-band 160..479 y337..367 button labelled getter(30) — corroborates).
ui.cpp: arm site composes ids from the cell's ITEM via popupButtonIds with
the checker leg = placementBlock (the port's cited 0x3830c, NOT the tPF-2
adjacency approximation); press arm matches popupButtonRects, per-id
behaviour (54 -> PLANLIST armed [SEAM: vendor per-item pre-filter unrecovered
— single-Build law makes this moot], 53/58 -> refused no-model, 51/OK ->
dismiss); render draws one button per id, label centred (approx width 7px/
char, named seam). indpopups.h SquareInfo.buildable marked SUPERSEDED for
the ui (stays the pinned checker-leg adjacency law).
Pins tests/test_popuplaw_tpf2d.cpp x5 (suite 546->551, 0 failed).
MUTATION-VERIFIED: M1 break->per-item = 2 fail; M2 y300..330+no-clamp = 4
fail; M3 drop OK-path = 2 fail; M4 always-53 = 1 fail; restore = 551/0.

## D8 — help.shp k0 FRAME IDENTITY CONFIRMED PIXELWISE (step 3 CLOSED)
scripts/tPF2d_render_k0.py (+ tPF2d_help_frame.py) decoded help.shp k0 with
the verbatim S9 codec; per-row WRITTEN/TRANSPARENT census (not palette-
dependent):
 - dims 336x256 == popup rect 152,120..487,375 EXACT (C7 parity law).
 - rows 0..216 fully written (frame + starfield interior), rows 217..247
   TRANSPARENT except 16 px per row (the continuing side-frame edges), rows
   248..255 fully written (bottom frame edge).
 - TRANSPARENT BAND rows 217..247 at record origin 152,120 map to LOGICAL
   y 337..367 — the consumer's button constants (rec+8=0x151, rec+0x10=0x16f)
   EXACTLY. The frame art has a purpose-built CUT-OUT for the button band;
   the buttons paint over it (refcap band bg = solid (12,32,48) measured on
   scratchpad crop rows 338..366, distinct from the starfield interior
   (0,0,0)/(12,12,16) census).
 - refcap bottom frame y368..374 teal + k0 rows 248..254 written: agrees.
VERDICT: help.shp k0 IS the popup (mineral) frame [inferred->MEASURED: three
independent agrees — extents, structure, cut-out==button-band constants].
FRAME ART SHIP remains GATED on the user's OQ-005 ruling (docs/DECISIONS.md
D1) — the port keeps its vector frame until then; identity banked here.
Port delta: button-band fill recoloured to the MEASURED refcap teal
(12,32,48) (replaces the eyeballed dark navy; label centring unchanged).

## D9 — TYPE-14 FRAME-WORD WRITER LAW (step 4, static census CLOSED)
16-bit store census (66 89 / 66 c7 with disp 0x1e = hiword of dword+0x1c):
11 sites in the code span. THE FRAME-WORD FAMILY:
 - 0x30b8f: init store WORD[rec+0x1e] = 0xffff (with +0x18 = 0xffff) — the
   widget-record DEFAULT (no frame).
 - 0x57e10: the windows.txt SHAPEFRAME parser store (C1 re-confirmed).
 - 0x3a5ed + 0x38ec7: record-copy loops (word fields +0x16..+0x20 verbatim
   copies) — propagation, not composition.
 - 0x32c66/0x32c6e: a dl==1 toggle writing 0/2 (frame slot 0 vs 2) — a
   runtime composition site (fn 0x32c5c, caller-side arg dl).
 - 0x341c8: WORD[edx+0x1e]=0 where edx=[ebp+0x76] (a child widget rec) —
   second composition site.
PLSQUARE carries SHAPEFRAME 0 verbatim (windows.txt ln1519-1527) => the
parser STORES 0 for it; hiword(+0x1c)==0 != -1 => the 0x31004 blit path is
ACTIVE for PLSQUARE with FRAME RECORD 0 — and the help.shp-k0 identity (D8)
supplies what record 0 paints. THE "TYPE-14 lib-binding" QUESTION IS
ANSWERED: no per-type lib table needed — the frame word comes from the file
(SHAPEFRAME), the lib from the 0x1fc34(0x9f10c) path (C2), and PLSQUARE's
binding is 0 = the popup frame record. Remaining seam: WHICH lib the
0x9f10c path resolves for the planet screen (planal vs help) stays
[inferred->help] on D8's three-way pixel agreement.

## D10 — PLANLIST PAINT FN 0x3cbb4: DISPATCH READ, TABLE STATICALLY INVISIBLE
0x3cbb4 fn body: key = widget+0x47 with remap 4->3 (0x3cc1c) and
SENDMESSAGE(hiword +0x43)==0x33 -> 4 (0x3cc33); cmp 4 / ja default 0x3d1bc;
jmp *cs:[edi*4+0x27fe8] (0x3cc9f). THE TABLE IS STATICALLY UNRESOLVABLE:
 - restored bytes at 0x27fe8 are CODE (a movsd run), not pointers;
 - banked saves read 0 at 0x242000+0x27fe8 (4 banks) — table never populated
   in BSS either;
 - no 5-run of plausible rebased targets near the disp.
The cs: segment override + zero-filled runtime slot means the case bodies
are reachable only by walking the FALLTHROUGH chain from 0x3cca4 (the jump
is real at runtime; the table is filled at window registration = a t333-
family runtime write). HONEST NAME: row-art source citation for PLANLIST
stays MISSING; the fn 0x3cbb4 + key law + default 0x3d1bc are now cited
(progress), the 5 case bodies unread. Next iteration: read bodies by
fallthrough walk 0x3cca4..0x3d1bc (no table needed — bodies are sequential
code blocks separated by jmps) OR one debugger stop at 0x3cc9f.
