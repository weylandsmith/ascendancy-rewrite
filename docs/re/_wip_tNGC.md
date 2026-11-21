# tNGC WIP — NEW GAME CONTENT GATE (PHASE-17) — in progress

## T0 — trigger + state checks [verified this session]
- DECISIONS.md: no USER: lines after D19 (awk over lines>496 empty);
  d1page find -newermt 2026-11-21 empty; HEAD cfee170 2026-11-21 11:08.
  Assignment stands: tNG-C.
- Sitting test scripts/t368_ring_turn.py: 20/20 saves turn=1086 -> NO new
  sitting; r1_t85g_sitting NOT run.
- Ghidra :8089 UP (check_connection OK, ascend_restored.bin 1143 fns).
  0x526b4/0x52174 are GAP territory (no Ghidra fn) -> capstone
  scripts/t442_disasm.py; dumps: work/tNGC_paint526b4.asm (0x526b4..0x52f60),
  work/tNGC_paint_head.asm (0x52100..0x526b4).

## F1 — STATE-3 PAINT ARCHITECTURE [verified disasm]
- Paint chain: 0x52114 (head; sole caller of 0x526b4 at 0x52174) ->
  0x526b4 (body+event dispatcher; its 0x52eb arm 0x528eb is the
  msg-dispatcher t423 cited). ebp = window object throughout ("ebp+4" =
  window surface passed as blit arg5).
- Shape-cache law (banked shp.md S410): fetch = FUN_0001fc34(cache 0x9f10c,
  slot=u16 ds:[0x6fdXX], sel=record idx); name fetch = FUN_0001fe20(0x9f10c,
  edx=name-string-ptr) -> u16 record idx (0xffff = miss).
- LIB SLOTS READ BY THE PAINTER [verified]:
  0x6fd98 = DESC portrait lib (t423c3 stretch site);
  0x6fd96 = ring lib (0x5287a);
  0x6fd86 = SECOND native blit lib (0x522dc);
  0x6fd84 = chips slot (t423c3 SS12) + planet-disc fetch 0x52366 uses
  0x9f10c with slot from FUN_0001fe20 name-fetch result cx (see F3).

## F2 — WINDOW FIELDS (ebp) [verified head 0x522bc..0x52530]
- +0xb1 hiword = SELECTOR A (portrait word idx 0x6fd98; ALSO the planet
  size-index input, see F3; bounds check `cmp 0x15 / jl assert shapefile?`
  at 0x523b1 -> value < 0x15 = 21 max).
- +0xb3 hiword = SELECTOR B (lib 0x6fd86 word + 0x6fd98 word + name-filed
  record); byte [0x891c1 + selB] read at 0x5244e into a draw-list struct.
- +0xb5 word = PLAYER COLOUR idx (chip click 0x529d2 arm: x in 379..493,
  y in 420..440 -> ax=(x-0x17b)>>4 -> STORE word[ebp+0xb5]; then
  FUN_000232ec(0x12e10,...) reassign + vtable repaint [win+0xa7]+0xc)
  — CONFIRMS t423c3 SS10 chip law incl. the field.
- +0xb7 word, +0xb9 word = indices into static u32 tables staged on stack
  at paint time (0x52475 loop 5 words from getter 0x9b base; 0x524b1 loop
  0x15 words from 0xa3; literals 0x11/0x145/0x144/0x172 at 0x524c8) ->
  3 args into FUN_00076c79 with getter 0xa8 (0x5253b). [identity of those
  tables = OPEN, likely wheel/density params]

## F3 — PLANET DISC INDEX LAW (D19 seed #2) [verified asm 0x5231d..0x52389 + field law F7]
FIELD PAIRING LAW (F7): every "dword[win+0xbN]; sar 16" read == word
[win+0xbN+2]. TRUE FIELDS: +0xb3 SELECTED RACE ROW; +0xb5 player-colour idx;
+0xb7 DENSITY idx; +0xb9 SPECIES count; +0xbb ATMOSPHERE idx.
  5231d edx = imm 0x2ba1 --pool-rel--> payload 0x85751 "DATA\\smhome.shp";
        call 0x1fe20(cache 0x9f10c, name) -> cx = slot for smhome lib
  5234b push 0xcd (y=205) ; 52356 push 0x48 (x=72)
  52358 mov eax,[ebp+0xb1]; sar 0x10 = word[+0xb3] = SELECTED RACE ROW
  52366 call 0x1fc34(0x9f10c, slot=cx, sel=race row) ; 5236d call 0x5caac
        NATIVE 1:1 onto surface [ebp+4]
  => DESC planet art = smhome.shp k<race row>, NOT planets.shp-size-index.
  Bounds 0x523a8..0x523c2: word[+0xb3] >= 0x15 (21) -> assert status.cpp:
  21 race records. 0x5237f: call 0x53dd8(eax=surface, ecx=byte[0x7458e]=
  LOCAL player race) = raceflag palette-ramp blit (t427 family) on DESC.
- PORTRAIT SITE (head 0x52114): 0x52292 fetch 0x1fc34(0x9f10c,
  slot=g[0x6fd98]) sel=word[+0xb3] (SAME race-row selector) -> NATIVE blit
  (75,85); SECOND fetch 0x522d5 slot=g[0x6fd86] sel=word[+0xb5]
  (player-colour idx) -> NATIVE blit (75,85) SAME position = the colour
  RING over the portrait (racering k<colour>, 53x53 native — t423c3 SS9
  law re-derived from the site). The 0x52834 STRETCH site (t423c3) uses
  [win+0xb1]>>16 = word[+0xb3] too.
- RACE-NAME TEXT 0x523a8..0x52416: base [win+0xaf] stride 200 *race row +
  static table 0x74590 stride 20 *race row -> 0x76c79 text draw.

## F4 — CHIPS [verified 0x529d2 arm + t423c3 SS12]
- Click rect x 379..493 y 420..440 (cmp 0x1a4/0x1d8), idx=(x-379)>>4,
  ONE ROW of 7 -> matches D19 "ONE row of SEVEN chips" (port defect was
  2 rows of solid swatches — port side to verify).

## F7 — FIELD MAP CORRECTED (paired dwords; supersedes F2/F6 field names)
All reads are dword[win+0xbN]>>16 = the UPPER word. TRUE WORD FIELDS:
  word[+0xb3] = SELECTED RACE ROW (stored 0x52d83 arm 0x1c01; read by
    portrait/planet/chip fetches via dword[+0xb1])
  word[+0xb5] = PLAYER COLOUR idx 0..6 (stored chip-click 0x52a11; read
    dword[+0xb3] at ring site + 0x52621 selection compare)
  word[+0xb7] = STAR DENSITY idx 0..4 (inc 0x52db9, wrap==5 -> 0)
  word[+0xb9] = SPECIES COUNT 3..7 (inc 0x52e58, wrap==8 -> 3)
  word[+0xbb] = ATMOSPHERE idx 0..2 (inc 0x52eec, wrap==3 -> 0)
CHILD FRAME LAW (parent writes child+0x72; children array = [win+0x67],
children = GALAXY_MORE/PLAYERS_MORE/DIFFICULTYMORE in msg order):
  child0 (density)   +0x72 = idx VERBATIM      -> 3cfgnew k0..k4
  child1 (species)   +0x72 = COUNT + 2         -> k5..k9 (Five=5 -> k7
     == t401 anchor CONFIRMED: field stores the COUNT not rank)
  child2 (atmosphere)+0x72 = idx + 0xa         -> k10/k11/k12
MSG MAP CORRECTED: ONLY 0x1f5/0x1f7/0x1f9 cycle (MORE buttons; windows.txt
GALAXY_MORE=501 PLAYERS_MORE=503 DIFFICULTYMORE=505); 0x1f6/0x1f8 ->
0x52f49 -> PARENT (inert). No LESS buttons in state 3.

## F8 — CHIP ROW LAW [verified head 0x5258d..0x52647]
Per-frame staged rect seed: ebx=0x17d ecx=0x18b (x, x+14), fixed y pair
(esp+0x120)=0x1b1=433, (esp+0x128)=0x1cf=463.
LOOP si=0..6 (SEVEN chips, pitch 16):
  rect = (381+16i, 433, 395+16i, 463)  [14x30]
  record = FUN_0001fc34(0x9f10c, slot=word[0x6fd84], sel=word[+0xb3])
    -> the SELECTED RACE ROW's chip record (same emblem, tint per chip)
  call 0x53ee0(record, ecx=edi=0, eax=&rect, pushes chip idx + edi)
    = tinted native blit (t423c3: ramp pal[byte*4+0x13-k])
  IF si == word[+0xb5] (player's own colour): EXTRA call 0x2fe04 with
    idx 0xf3 (pal 243 WHITE), ecx=0xe, rect -> selection marker on that chip.
AFTER LOOP: FUN_00055208(0x7a35c, 0x17b,0x1ed,0x1a4,0x1d8) = Player^Color
window update-rect (x379..493 y420..472 verbatim).
=> D19 chip defect ROOT CAUSE: port paints SOLID FILLED RECTS
(kPlayerChipRgb); vendor blits the race EMBLEM record TINTED, one row of
seven, white marker on the selected chip. LIB for slot word[0x6fd84]:
writer hunt NEXT (not in boot table).

## F9 — DESC PANEL ART LAWS (the tNG-C headline) [verified]
Surface = NEWGAMEWND (windows.txt X0=334 Y0=12); 0x5caac(surface, lib,
recIdx, x, y) draws record content at window+(x,y)+bbox(L,T)
[5caac.c:42-46: param_2 = lib + 8*recIdx + 8; dest = bbox + param_4/5].
- PORTRAIT: smrace k<word[+0xb3] race row> at (75,85) -> content screen
  (359,47) 100x100. PORT MATCHES (kDescRingCentre-based).
- RING: 0x522d5 fetch slot word[0x6fd86] (=racering), sel=word[+0xb5]
  player colour, blit (75,85) -> ring centre screen (408,96). PORT (409,97)
  matches +-1.
- PLANET (D19 seed #2 CLOSED): 0x5231d name-fetch "DATA\\smhome.shp"
  (payload 0x85751), 0x5caac(surface, smhome, recIdx=word[+0xb3], 0x48,
  0xcd) -> bbox (-24,-26,27,25) -> content screen (382,191) 52x52 NATIVE.
  = smhome k<SELECTED RACE ROW>. NOT planets.shp, NOT size-index.
  Bounds assert cmp 0x15 (21 recs) at 0x523b1 == smhome/raceflag count 21.
  PORT DEFECT: planets.shp k[(sel%11)*5+1] at (401,218)-centre (invented
  biome mapping, named seam t414) — REPLACED.
- CREST: 0x5237f 0x53dd8(surface, ecx=byte[0x7458e]=LOCAL PLAYER race) =
  raceflag k<player race> on DESC. PORT DEFECT: draws k<selIndex>
  (selected race) at kDescCrestRect — index fix cited; the dest of the
  2-arg blit stays the port's measured kDescCrestRect (named caveat).

## F9b — WHEEL LAWS CONFIRMED (no port delta)
newgameWheelFrame(menulaw.cpp:240) bijection == child+0x72 law (F7):
density rank k0..k4, species COUNT+2 k5..k9 (Five=k7 anchor), atmosphere
+10 k10/k11/k12. Wrap laws vendor-verbatim: density 0..4, species 3..7
(wrap 8->3), atmosphere 0..2 (wrap 3->0) — port cycles already match
(densityIdx%5, species 3..7, atmosphere%3).

## F10 — CHIP LAW FULLY PINNED [verified asm + decompile + refcap census]
- 0x53ee0 decompile (Ghidra): rewrites FOUR palette slots 0x10..0x13 :=
  0x10+4k .. 0x13+4k (loop eax 0..3), then FUN_0005cf96 = tinted blit.
  So chip k = raceflag record with palette slots 16-19 remapped to the
  colour-family-k ramp pal[16+4k..19+4k]. LIB = raceflag.shp (21 recs,
  15x25, ink indices subset {16,17,17,19} + navy 242 [census k0/k3/k5]).
- Rect law (head 0x5258d seed + loop): chip i rect =
  (381+16i, 433)..(395+16i, 463); blit rect top-anchored; 7 chips; ALL
  SEVEN show the SAME emblem = raceflag k<word[+0xb3] SELECTED race row>
  in family i's tint.
- SELECTED chip (i == word[+0xb5]): FUN_0002fe04 (decompile: 4 x
  FUN_0005bf71 = hline/vline family) draws a 1-px WHITE (0xf3=pal243)
  FRAME 14x24 (ecx=0xe, push 0x18) around the chip.
- REF WITNESS scratchpad/newgame-original.png census (x381+16i windows,
  y433..463): chip i brightest ink EXACTLY pal[4i+19] for i=1..6
  ((158,81,174),(255,235,97),(239,154,174),(121,105,69),(36,117,207),
  (235,121,4)); chip0 = green family + white frame x28 px (player colour
  0 selected in that shot). Navy (12,32,48) = 191/465 px per window.
- PORT DEFECTS: solid kPlayerChipRgb rects (no emblem, no tint law, no
  frame); replace with raceflag ramp blit + white frame.

## F11 — BEGIN PANEL STARFIELD = SHRUNK-FIELD ANSWER (D19 open question)
Arm region body 0x52787..0x5282f [verified disasm]: per item ebx: x =
(word[ebx+3] hiword)/5 + 5, y = (word[ebx+5] hiword)/5 + 5 (idiv dword
[esp+0x18]=5 at 0x527a4/0x527c9, add eax,5), sprite class ecx from value
test (>0 -> 1; <=-220 (0xdc) -> 2; else 0), record [eax+0xab] via 0x5caac.
=> ANSWER: SHRUNK VOLUME (full-field coords /5 into the panel), NOT a
same-field-scaled render. Port t423 SS4 law = N=kDensityStarCounts[idx]
points volume-placed — directionally right (N tied to density), exact
/5-grid law is a NAMED refinement (Begin starfield is a D19 seed; full
per-sprite law owed by tNG-B/tNG-C CONT if the user-grade still shows it).

## F12 — 0x52389 crest call = RACELIST row0 flag, NOT DESC crest
ebx=0xc1 edx=0x6b set at 0x52372..0x52377 -> window-rel (193,107) =
screen (527,119) = INSIDE RACELIST (x502..632 y45..372) row0 slot. The
DESC crest site is therefore NOT this call; port's kDescCrestRect law
(t426 family) stays, index question stays a named caveat (do not touch).

## F13 — CYCLE-2 IMPLEMENTATION MEASUREMENTS (tNG-C2 session) [verified]
- smhome.shp census under the PORT's OWN bbox-diff law (scripts read via
  formats/shp.h layout: k>=1 bbox quad at rec+0x08): 21 records, EVERY one
  L,T,R,B = (-24,-26,27,25) -> content 52x52, placement (L,T). The "CANON
  27x25" u32-pair at rec+0x10 is the R,B half (tA1 refutation re-confirmed).
  Vendor blit 0x5234b/0x52356 pushes (0x48,0xcd)=(72,205) win-rel; window
  X0=334 Y0=12 -> dest = (334+72-24, 12+205-26) = screen (382,191).
- raceflag.shp census: 21 recs, bbox quad (0,0,14,24) -> 15x25 content,
  (L,T)=(0,0) (blit dest == rect corner verbatim).
- REFCAP re-measure scratchpad/newgame-original.png (browser law [1:481,
  1:641]): chip i brightest ink == pal[4i+19] EXACT for i=1..6 (chip0
  brightest = WHITE frame pixel; frame law). Chip strip content bbox
  (380,428)-(495,464) n=1814 (NAVY detector). Planet zone content bbox
  (381,191)-(433,241) n=1840 = 53x51 (52x52 content + 1px antialiasing
  drift; +-6 tol covers it). Vendor frame: 28 white px in (382,434)..
  (395,459) for chip0 (the selected chip in that shot).
- FRAME GEOMETRY: task law rect (382+16i,434)..(395+16i,459) (14x26
  outline). F10's "ecx=0xe push 0x18" read is ambiguous (14x24 vs 15x25);
  the refcap white-px positions sit on the task-law outline, so the task
  law is what ships. Named caveat: interior frame style (single hline/
  vline family FUN_0005bf71) not pixel-diffed against a rect-outline draw.
- FRAME REFINED [verified px census, tNG-C2]: white pixels are EXACTLY two
  hlines y=434 and y=458, x 381..395 (30 px, chip0 selected). The vertical
  edges x381/x395 rows 435..457 are NOT white: left (164,171,177), right
  (225,227,229) (the chrome-noise grey family, 22+1 px each). Emblem
  content occupies rows 433..457 (per-row content census: 433 = 108 px,
  458 = 109 = bottom hline, 459+ = panel navy). FUN_0002fe04 decompile =
  4 x FUN_0005bf71 (argparse ambiguous, unaff_EBX) — consistent with
  2 hlines + 2 vlines, colours not statically decidable. SHIPPED LAW:
  top/bottom WHITE hlines (381+16i..395+16i @ 434 and 458), left vline
  (164,171,177) x=381+16i y435..457, right vline (225,227,229)
  x=395+16i y435..457. The t401 chip constants (X0=384, rows 434..459)
  are SUPERSEDED (tA3 raw-row drift class: emblem content starts 433).
- raceflag ink census (walk law, k3/k5): ink {16:22-48, 17:28-40,
  18:9-37, 19:114-145} + navy 242:124-174 + strays (k3: 151x8, 196x1).
  Ramp shift 4k applies ONLY to {16,17,18,19}; 242 and strays render
  through their own pal entries.
- Port law constants (menulaw.h): kChipRowX0=381 pitch 16 rect 15x31
  (381+16i,433)..(395+16i,463); ramp slots {16,17,18,19}; chip i maps
  slot 19 -> pal[4i+19]; navy 242 untouched; frame pal 243 WHITE.

## F5 — WHEEL DISPATCHER arms [verified 0x528eb..0x52945]
- msg dx: <0x1f5 -> 0x52f59 ; 0x1f5..0x1f8 -> 0x52db9 ; 0x1f9 -> 0x52eec ;
  0x1fa -> fallthrough ; 0x1c01 -> 0x52d6c ; else parent 0x336b4.
- 0x52678 = Begin-button click-blocker gate: click dead IF
  dword[0x484ec] in (0x1f6,0x278) AND dword[0x484f0] in (0x17d,0x1d8)
  (Begin panel region x502..472? y381..472 — matches tA2 kBeginPanelVisual).

## F6 — WHEEL STATE + FRAME LAW [verified arms 0x52db9/0x52e58/0x52eec]
WINDOW FIELDS see F7 (paired dwords — the F6-first-draft field names here
are superseded; the arm STRUCTURE below stands).
- DENSITY arm (msgs 0x1f5/1f6/1f8): word[win+0xb5]++ ; IF idx==5 -> wrap 0
  ; setter FUN_000226e4(0x12e10, density=eax[esp+edx*4-2]...) ; map win
  FUN_00028fc0 ; repaint self ; child[0] = [win+0x67]: child->obj+0x72 =
  density VERBATIM ; child repaint. (0x1f8 arm: cmp word[+0xb5]==5 wrap —
  the same arm reached thrice; the stack-table read is the density VALUE
  {15,25,50,75,100} for the SETTER, the SHAPE idx stored to child+0x72 is
  the RAW COUNTER.)
- SPECIES arm (0x1f7, via 0x52f49 cmp): word[win+0xb7]++ ; IF ==5 -> wrap 0
  (FOUR options 0..3 visible? NO: wrap at 5 -> 0..4? cmp imm 5 jne skip ->
  wraps after value 4->5 -> reset 0: FIVE states) ; setter
  FUN_00022ce4(0x12e10, A=+0xb1, count=+0xb7) ; child[1] = [[win+0x67]+4]:
  child->obj+0x72 = count + 2 ; repaint. => species wheel frame = idx+2
  CONFIRMS t423 SS2 k(count+2).
- ATMOSPHERE arm (0x1f9): word[win+0xbb]++ (NOTE: increments +0xbb, the
  field AFTER atmosphere — see caveat) ; IF word[win+0xb9]==3 -> word[+0xbb]
  =0 ; repaint self ; child[2] = [[win+0x67]+8]: child->obj+0x72 =
  atm_idx + 0xa ; repaint. => atmosphere frames = k10/k11/k12 EXACTLY
  (idx 0,1,2 + 10) — THREE options, hostile = idx 2 = k12 = the D19
  correct reference. PEACEFUL/NEUTRAL sliver defect = port drawing wrong
  frame or double-blit, NOT a vendor feature.
  CAVEAT: the +0xbb inc with +0xb9 wrap test reads oddly; [eax+0xb9] where
  eax=eax-at-entry (dispatcher sets ebp=eax at 0x528f2) — same window. The
  wrap law AS CODED: atm counter lives +0xb9; +0xbb is a shadow/pair word.

- CHILD WINDOW LAW (new, generalises t423 SS2): the three wheel widgets are
  children [win+0x67][0..2]; the PARENT writes each child's +0x72 = shape
  record idx (density verbatim, species +2, atmosphere +10); child paint =
  generic shapeitem paint drawing ITS +0x72 record from its bound lib.
  windows.txt shows k0 for all wheels because +0x72 is RUNTIME-set.
- 0x1c01 arm (0x52d6c): species-list row click — if [eax+0xb1] hiword !=
  clicked: word[win+0xb3] = clicked ; setter FUN_00022ce4(0x12e10,
  +0xb1, +0xb7) ; repaint. (SELECTOR A/B PAIR semantics OPEN.)
- PLANET arm region starts 0x52f59 (cmp dx,2 jb 0x52f88 ...) — NEXT probe.

## F14 — CYCLE-2 CLOSE-OUT RECORD [tNG-C2, executed 2026-11-21]
IMPLEMENTED: smhomeLib DESC planet (title.cpp, kDescPlanetCentre {406,217});
blitShapePalRamp + chipInkSlot (vendortext.cpp); chip row = 7 raceflag ramp
blits + selected-chip frame (white hlines 434/458, grey vlines 435..457);
t401 chip constants superseded; kPlayerChipRgb REMOVED (the D19 "2 rows of
solid swatches" defect root). HARNESS: t441 desc-planet cited
("fixed",(52,52)) rect widened (377,188,436,246) + playercolor-chiprow
region (tight-to-content law rect (381,433,491,458); the task's padded rect
saturated the NAVY detector — banked pitfall). PINS:
rewrite/tests/test_newgame_content_tNGC.cpp x4 all ok; ctest suite green
(0 failed). WITNESS scripts/r1_tNGC_chip_witness.py: vendor 7/7 + ours 7/7
chip ramp law PASS, framed-chip-count==1 both sides, planet 51x51 vendor /
51x50 ours (52+-2 law) PASS; t441_screen_diff newgame 18/18 PASS incl the
two new regions. MUTATION 10/10 CAUGHT (launched on a GREEN suite per the
launch guard; M1 chipx0, M2 chipy, M3 ramp-shift, M4 ramp-domain,
M5/M6 frame rows, M7 planet-anchor, M8 species-domain = tests-class;
M10 family-zero, M11 frame-off = witness-class; AFTER-RESTORE tree
md5-clean, git status shows only docs edits). PITFALLS ADDED: (i) ctest
substring trap — "0 tests failed
out of 1" CONTAINS "tests failed"; launch guard must use exit code only
(caught itself, tree never mutated); (ii) framed-chip brightest-ink test is
frame-polluted on BOTH sides -> presence-of-pal[4i+19] check (vendor 7 px
vs ours 67 px — count parity is NOT law; the vendor's chip0 emblem decodes
sparser than the port's k0 walk produces, open sub-question logged here,
NOT a gate failure). MUTATION: scripts/r1_tNGC_mutate.py, table M1..M8 +
M10..M11 (no M9 by design).

## F15 — tNG-C3 CYCLE 3 (G1 side-by-side pass + Begin starfield law) [in progress]
Trigger check: no USER: lines after D19 in DECISIONS.md; ring turn 1086 on
tail saves (53/54.sav) = no new sitting; pid 1182156 alive. Assignment =
STATE.md defect list (1) wheel ghost sliver (2) density/species extraneous
art (3) Begin starfield SHRUNK-VOLUME law + green ring (4) chip-grey probe.
### F15-4 CHIP-GREY PROBE [CLOSED as measured-position law, 2026-11-21]
Pixel diff ours(t412 shot, post-tNGC2 build) vs refcap, chip0 zone:
LEFT vline x=381 rows 435..456 EXACT (164,171,177) both sides; RIGHT
vline x=395 rows 435..456 EXACT (225,227,229) both sides. Row 457 is the
sole diff row: vendor (221,224,226)/(244,245,245) = emblem-content bleed
into the frame bottom corner; our painter keeps the vline to 457 uniform.
=> shipped measured-position law (white hlines 434/458 + grey vlines
435..457) is PIXEL-TRUE on the chrome; no chrome-family lookup needed.
Static source question (button chrome vs FUN_0002fe04 args) stays
undecidable and is IRRELEVANT to the port now — measurement closed it.
### F15-1/2 G1 PASS wheel panels [in progress]
t412 shot atmosphere value=1: best-shift pixel agreement panel interiors
(408..466) vs refcap: atmos 91.4% @(-2,-1), density 93.6% @(1,-1),
species 80.0% @(1,0) (species CONTENT differs by setting: our 7 chips vs
vendor ~5 — not a defect class). Vision pass: no ghost sliver / stray
white line visible on atmos k11 panel in current build; diffs distributed
across disc (gradient/antialias class), NOT a clip-edge band.
### F15-1 ATMOSPHERE STATE CENSUS (current build, scripts/tNGC3_atm_shot.sh)
Ours cycled k10->k11->k12 (app.log msg 505 x2): content bbox
k10 x284..345 (W=62!) y411..459; k11 x288..336 (W=49); k12 x290..336
(W=47). WHITEISH (min>150) px: k10 24 px rows 431..437 ONLY; k11 0; k12
0. => THE DEFECT REPRODUCES on OUR k10: a bright-blue horizontal LENS
BAND rows ~431..437 extending ~13 px past the disc both sides with stray
dashes at x284/x344 — this is the D19 "ghost sliver + stray white line"
family (user saw it on peaceful/neutral pre-tNGC2; now only k10). k11
(pixel-compared vs refcap: 91.4% agreement @( -2,-1), diffs = gradient
dither class) and k12 are CLEAN. Next: k10 stream walk autopsy vs codec.
### F15-1 VERDICT (defect 1 + 2): GHOST SLIVER / EXTRAOUS ART NOT IN CURRENT BUILD
(a) STRAM-DECODE PROOF (scripts/tNGC3_wheel_decode.py): the k11 stream
(88x79) GENUINELY CONTAINS the bright-blue lens band (pal 98/251/252/254
runs rows ~20..33) and the (190,255,255)=pal103 eye highlights; the k10
stream the same family. The lens + highlights are VENDOR ART, not a port
artifact.
(b) PIXEL PROOF vs refcap (atmosphere panel, ours k11 vs vendor): BOTH
sides show the lens tips extending beyond the disc (vendor rows 430/431
content x282..343 vs disc-only x289..337; ours rows 433/434 x284..345 vs
disc-only x293..338) and BOTH show the pal-103 white highlight clusters
(ours x304..306/x322..323 rows 431..437; vendor x302..304/x320..321 rows
429..436) — SAME features, offset ours = vendor + (+2,+2).
(c) RESIDUE = ANCHOR OFFSET, not double-blit: disc-extent centres ours vs
vendor: atmos k11 (315.5,435) vs (313,433.5) = +2.5,+1.5; density k2
(64,436) vs (65,435) = -1,+1; species bbox ours (160..214) vs vendor
(161..215) = -1,0 (content differs by setting: ours k9 seven-player vs
vendor k7, not comparable beyond extent). kWheelBlitTop=408 / x=cxp-28 is
within 1-2 px on all three panels; the D19 "art drifts between options /
next-disc sliver / stray white line" class does NOT reproduce on the
post-tNGC2 build (all three atmos states captured: whiteish-px census 0
below-disc rows 460..471 on ours AND vendor; per-state bboxes consistent).
HONEST NEGATIVE: defects 1/2 closed-as-not-reproducing (the D19 witness
pre-dates the t401/t414/tNGC2 wheel fixes); no code change shipped for
them this cycle; the 1-2px anchor offsets are banked here and are
tNG-U (user-grade) polish, NOT tNG-C defects.
### F15-3 BEGIN STARFIELD LAW, FULL DISASM RE-READ (0x526f0..0x5282f) [verified]
Loop head 0x526f0: 0x52678 click-blocker gate; 0x55208 lookup -> obj;
COUNT = word[obj+0x572] (galaxy star count — DENSITY setting feeds the
galaxy, hence "tied to density"); record stride 0x172 (add esi,0x172);
record ptrs deref'd from [esi].
POSITION LAW: x = (hiword dword[rec+5])/5 + 5, y = (hiword dword[rec+3])/5
+ 5 (idiv 5 at 0x527b1/0x527c9) — raw MAP coords shrunk, NO rotation in
position (rotation [0x2bf3] + trig 0x76e08 feeds CLASS only, via fistp
into esp+0x20; ah=byte[rec+4] high != 0 SKIPS the class recompute, ecx
keeps last value).
CLASS LAW CORRECTION (supersedes F11!): 0x52817 pre-sets ecx=3;
cmp eax,0xdc jle 0x52787 -> else 0x5282d xor ecx,ecx. At 0x52787:
eax>0 -> 1; eax<=-220 -> jle keeps ecx=3; else 2. FOUR-WAY:
  eax>220 -> cls 0 ; 0<eax<=220 -> 1 ; -220<eax<=0 -> 2 ; eax<=-220 -> 3.
(F11's "value>0->1, <=-220->2, else 0" was a misread of the jle target.)
SPRITE LAW: rec = 4* dword[ebp] + cls (0x527d1 shl 2); lib handle
dword[obj+0xab]; blit 0x5caac. Panel extent: x,y<=~130x100 fits
kBeginPanelVisual 131x92 = the D19 "starfield" IS this shrunk draw.
BEGIN RING MEASURED (refcap): centre (600,417.5), OUTER diam 57
(green runs x572..575 / x625..628 at y418; rows 389..393 / 442..446 at
x601) BAND 4-5 px, colour (0,113,56) family + bevel ring at inner edge
(576..579 greys/teals). Ours: 1-px circle r28 centre kBeginEmblemCentre.
### F15-3b BEGIN PANEL COORD READING + RING GEOMETRY [verified]
COORD LAW REFINED: the /5+5 inputs are S16 HIWORDS of dwords[rec+3]/
[rec+5] = the vendor MAP PIXEL coords (x 0..639, y 0..479): /5+5 maps
0..639 -> 5..133 (panel width 131) and 0..479 -> 5..101 (height 92).
=> the Begin starfield = the FULL galaxy map shrunk 5x into the panel,
positions STATIC (rotation drives only the sprite class), panel origin =
kBeginPanelVisual (502,381) + (mx/5+5, my/5+5), clipped at the panel.
REFCAP BEGIN PANEL FACTS: left band x503..570 holds BOTH the grey hash
dots (families (225,227,229)/(164,171,177)/(103,116,126)/white) AND
COLOURED star px ((60,40,16),(65,4,6),(20,52,117),(164,90,7)) — the
starfield is ADDED to the dots, not a replacement. RING: centre
(600,417.5), OUTER diam 57 (x572..628 y418; rows 389..393/442..446 at
x=601), BAND 5 px, radial rungs top (10,46,51)/(0,142,69)/(0,124,61)/
(0,113,56)/(8,82,43), bottom (0,153,74)/(0,153,74)/(0,142,69)/(0,110,54)/
(5,65,43) — bevel: bright outer edge on the BOTTOM, dark inner edge.
CLASS LAW (four-way, supersedes F11): v>220->0, 0<v<=220->1,
-220<v<=0->2, v<=-220->3; v from trig(z_angle + accumulator) (0x76e08),
accumulator [0x2bf3]; byte[rec+4] high set skips recompute.
IMPLEMENT (this cycle): (i) Begin panel starfield = every galaxy star
(count law word[obj+0x572] == stars.size()), pos = origin+(mx/5+5,
my/5+5) with mx=my from OUR 1024-grid scaled *640/1024, clip panel;
sprite cos_star rec 4*K+cls, K=0 named seam (same as map screen);
rotation formula for v [inferred] (plane rotation of (x,z)); (ii) ring =
annulus r in [23.5,29] about (600,417.5), 5 radial rung colours with
top/bottom asymmetry per census. Dots KEPT (vendor has them).
### F15-3c BEGIN STARFIELD + RING IMPLEMENTED [tNG-C3, verified by build+shot]
title.cpp Begin panel: (i) starfield block (c) draws EVERY galaxy star
pos = beginStarPos (menulaw.h pure law: 502+(x*640/1024)/5+5,
381+(y*480/1024)/5+5, clip kBeginPanelVisual), sprite cos_star rec cls
(K=0 named seam), FOUR-WAY class law beginStarClass (v>220->0, 0<v<=220
->1, -220<v<=0->2, <=-220->3); draw order = dots -> STARFIELD -> ring ->
portrait (refcap: no star px over the emblem). (ii) ring = annulus r in
[23.5,29] about (600,417.5), 5 radial rung colours kRingTop/kRingBot
blended by vertical position (census F15-3b); 1-px kLore circle DELETED.
(iii) portrait = blitShapeCircular clipR=23 about the hole (native 100x100
smrace at centre overflowed the ring before — vision pass caught it).
WITNESS: green-mass begin panel ours 933 vs vendor 847 (was 332 vs 847 —
defect class CLOSED, residue = rung blend lands some near-green px);
side-by-side vision: ring thickness/position/hole-clip = match; star
COLOURS differ by galaxy seed (cos_star k1..k3 blue vs k4..k7 warm — the
K byte [ebp] selects the colour family; K=0 seam named, same as map).
PURE-LAW PINS added to menulaw.h (beginStarPos/beginStarClass/beginRingAt);
ctest 0 failed. ROTATION: class-only spin (beginYaw) per cited law; the
vendor accumulator [0x2bf3] value is a named seam.
### F15 CLOSE-OUT SUMMARY (tNG-C3, D18 cap reached — no tNG-C4)
(1) atmosphere sliver: NOT REPRODUCING post-tNGC2 (F15-1; lens band +
white highlights are vendor art present on BOTH sides; residue = 1-2px
anchor offsets -> tNG-U polish). (2) density/species extraneous art: NOT
REPRODUCING (93.6%/80% pixel agreement; species content differs by
setting, not defect). (3) Begin starfield + thick beveled ring: CLOSED
with cited law implemented + witness (F15-3c). (4) chip-grey probe:
CLOSED as measured-position law — vlines pixel-EXACT rows 435..456
(F15-4). Fold list for tNG-B/tNG-U: 1-2px wheel anchor offsets; chip0
row-457 frame/emblem corner bleed; Begin K-family seam (which cos_star
colour family per race); vendor starfield class-rotation accumulator
[0x2bf3]; species-desc vendor 5-chip vs ours 7 (content setting).
