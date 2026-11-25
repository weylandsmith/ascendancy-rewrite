
# _wip_tPF2c.md — POPUP DERIVATION CITATION AUDIT (D30 binding, 2026-11-25)

User verbatim: "derive the popup drawing behavior from reverse engineering,
rather than guesses or approximation." Per-property citation REQUIRED for:
windows.txt entry, named SHP record for the mineral frame, string-table ids,
button records + labels, build-list row art-source law. Any shipped tPF-2
property that was eyeballed from refcaps must be NAMED and RE-DERIVED.

AUDIT TABLE (status at session start, from _wip_tPF2.md):
- title/body strings + ids (#75..#83, #89..#93, #30/#57/#60): CITED
  (objdump 0x3de5a..0x3e2c8, getter law t96). OK.
- popup RECT (wrec+10..wrec+0x145/+0xcf law, _wip_tPLB2.md:158): CITED. OK.
- PLSQUARE window entry (ln1519, rect 152,120-487,375, SHAPEFRAME 0,
  SENDMESSAGE 1): CITED verbatim from extracted/ascend00/windows.txt. OK.
- BUTTON SET GATE (Build+Cancel iff empty-surface+active-neighbour):
  [inferred] from refcap + planet.txt info02 — NAMED GAP #1 (behaviour,
  not geometry; the F3 honest negative stands: key=3 arm statically
  invisible, t333 law).
- button RECTS: OURS (y1+2..+30 strip, left-quarter Build) — PORT DEFAULT.
  NAMED GAP #2. NEW LEAD THIS SESSION: windows.txt has REAL button records
  PLSQBUT0..5 (TYPE 0, PARENT PLSQUARE, ln1622-1707) — the vendor popup
  buttons are winmgr children, NOT a painted strip. PLSQBUT5 carries
  SENDMESSAGE 55; PLSQBUT0..4 SENDMESSAGE 0.
- POPUP FRAME ART (mineral frame): NOT DERIVED — port paints no frame art
  (vector only?). NAMED GAP #3. Lead: PLSQUARE SHAPEFRAME 0; the
  SHAPEFRAME->widget-lib-per-TYPE table is chrome.md open item (b)
  ("exact table not yet cited").
- PLANLIST row art source (record==itemIdx "t428 1:1 law"): _wip_t428.md
  grep shows F9 = the TYPE-29 panel strip 1:1, NOT the row art. The row
  art-source law may be MISATTRIBUTED. NAMED GAP #4.
- PLANLIST entry itself: ln1503 TYPE 10 rect 120,120-520,420 SHAPEFRAME 7
  — CITED verbatim this session; our indicatorPopupRect(162,130..477,327)
  is the PLSQUARE-derived popup, while PLANLIST vendor rect is DIFFERENT
  (120,120-520,420) — check what the port uses for the list window.
- teal band colour rgb(16,69,77) + pitch 72: refcap-MEASURED at one scale;
  named seams stand (F8 tail).

SESSION PLAN (~<=30 probes):
P1 find the windows.txt parser's SHAPEFRAME store offset + the per-TYPE
   widget-lib table (chrome.md (b)) -> closes which SHP record frames the
   popup (GAP #3) and PLANLIST (GAP #4 partial).
P2 live witness: run --ui, click a tile, dump winmgr window list, see if
   PLSQBUT0..5 windows EXIST and their real rects (GAP #2).
P3 re-derive row art source from the PLANLIST paint fn (GAP #4).
Bank after each probe.

## C1 — SHAPEFRAME STORE OFFSET RE-DERIVED [verified asm, this session]
windows.txt parser fn 0x575e4 (winmgr.cpp; strings '..\\winmgr.cpp' 0x85bbe):
keyword-scan chain pins the store offsets by file order:
 - '%s %d' scans push fmt 0x85c69/0x85c6f/0x85c8d; RECT stores
   X0/Y0/X1/Y1 -> rec+8/+0xc/+0x10/+0x14 (0x57d67 add 8 / 0x57d88 add 0xc /
   +0x10 / +0x14 pattern into scanf arg list).
 - SHAPEFRAME store = 0x57e10 'mov %ax,0x1e(%edx)' -> WORD[rec+0x1e].
   (audio.md 6.9 said +0x1e too; independently re-verified.)
 - PARENT-name scan 0x57c41; SENDPARAM1 -> rec+0x3d sentinel (0x57d11),
   WINITEMS -1 -> rec+0xab (0x57d56 movl $-1,0xab(%eax)).
 - TYPE-100 header rows: 0x57cd5 movl $0,0x1a(%edx) + 0x57cdc mov %ax,0x18(%edx)
   = STATENUMBER->u16[rec+0x18], zero u32 at +0x1a (the SHAPEFILE lib id slot).

## C2 — GENERIC WIDGET-FRAME BLIT LAW [verified asm 0x30fb8, sprite draw]
FUN_00030fb8 (sprite/widget paint; shp.md call-chain cites it into
FUN_0005caac):
 - 0x31004 'mov 0x1c(%eax),%eax; sar $0x10' = HIWORD dword[rec+0x1c];
   if != -1: PUSH 0,0,selector; PUSH u16[rec+0x18]; PUSH 0x9f10c;
   CALL FUN_0001fc34 (shape-cache singleton @0x9f10c, shp.md S9); blit via
   0x5caac at widget+4.  *** THIS IS THE SHAPEFRAME DRAW PATH: dword+0x1c
   carries the frame id, word+0x18 the CACHE SLOT (lib). ***
 - else (frame -1): fill path 0x5e940 + text items 0x2fb38 (gated on
   dword[rec+0x5b]/+0x59 hiwords == -1).
 - LIB REGISTRATION [verified fn 0x3a7b0]: PLANETALLOC init path pushes
   fmt 0x84a20 'data\\planal%02d.shp' in a loop ebx=0..10 (0x3a812 cmp 0xb),
   each iteration CALL 0x1f95c(cache 0x9f10c, name) -> 'mov %ax,0x173(%ecx)'
   = PLANETALLOC object+0x173 slot id; the 11 lib files planal00..10.shp
   EXIST extracted/ascend01/data/ (measured).
 - PARSER WIRING GAP [honest negative]: NO static site writes dword[rec+0x1c]
   hiword from WORD[rec+0x1e] (full-image scan of 0x1e-disp reads: only
   esp/ebp locals + the parser store 0x57e10). Composition is RUNTIME:
   winmgr copies the SHAPEFRAME word into the per-window widget record's
   +0x1c hiword + resolves rec+0x18 = cache slot when the STATE matches.
   Consistent with the t333 (2)/(4) composition-invisibility laws.

## C3 — WHICH LIB FRAMES THE POPUP [cited]
- PLSQUARE (windows.txt ln1519 verbatim): TYPE 14 PARENT PLANETALLOC
  STATE "1 17" rect (152,120)-(487,375) SHAPEFRAME 0 SENDMESSAGE 1.
- TYPE 14 has NO TYPE-100 STATENUMBER 14 header row (full STATENUMBER
  census: 0,1,3,7,8,8,13,16,20 only) -> the lib for TYPE-14 widgets can
  only come from the PARENT PLANETALLOC registration: 'data\\planal%02d.shp'
  loop ids 0..10 (C2). Popup frame = planal<slot>.shp record 0 (frame
  convention: SF record indexes the lib; frame 0 = full-window frame per
  t401 3cfgnew-k0 precedent).
- PLANLIST ln1503 verbatim: TYPE 10 rect (120,120)-(520,420) SHAPEFRAME 7
  -> listbox frame via the T10 widget lib (chrome.md (b) 'T10 listbox ->
  listbox.shp' [inferred there]; listbox.shp EXISTS extracted/ascend01/).
- OPEN SUB-QUESTION (C3a): which planalNN slot the PLANETALLOC object
  resolves for the CURRENT race (0x173 is a u16 slot id; per-race mapping
  loop 0..10 hints race index). Decodable via the decode law + dims:
  frame records are the large ones; enumerate planalNN k0 dims.

## C4 — planalNN DIMS MEASURED: the planal hypothesis for the popup frame
## is DEAD as stated (dims don't fit)
planal00..10.shp all n=5: k0=47x47 (span ~7k), k1..k4=399x399 (W-1/H-1 law
-> 400x400 full-screen backdrops, spans 16k..108k rising = globe art per
race). POPUP rect 335x255 fits NONE of them. => the popup frame is NOT a
planal record. listbox.shp = k0/k1 24x24 + k2/k3 14x14 (small widget art).
NEXT: census ALL cache registrations (call 0x1f95c sites + their fmt
strings) to find which lib(s) hold a 335x255-or-parity record, and re-read
the tPLB2 builder for a frame BLIT site inside the popup builder itself.

## C5 — BUTTON COMPOSITION LAW [verified asm 0x3d397..0x3d591, msg-1 leg]
The msg-1 PLANETALLOC handler leg for key==3 (cmp ds:0x74528,3 @0x3d3ae)
BUILDS THE POPUP BUTTON ID ARRAY (u32 ids at ebp-0x78, count at ebp-0x18):
 - item==0xff (empty square): -> 0x3d550 loop (climb to 0x27=39; body at
   0x3d55f inspects the cell item byte; PARTIAL READ — bank remainder).
 - item==0x17 (23=Ship): ship=0x396cc(cell); word[ship+0x47]/0x49 via
   0x49768 (destination/fleet probes); planet-owner [0x43508]+0x57 rules:
   no-dest -> append 52 (0x34); has-dest && owner!=none && owner!=player
   -> append 57 (0x39) "Cancel"; ALWAYS append 55 (0x37); then
   checker(0x3830c, item=0x23=35, cell) && { cell4[+2]& } ;1 && owner==player
   -> append 56 (0x38).
 - item other than ff/17 -> append 53 (0x35).
 - THEN tail 0x3d51d: checker(0x3830c, edx=0x23(35), cell=widget+0xab)
   TRUE -> append 58 (0x3a).  *** 0x23 is the item-id ARG to the build
   checker = the "buildable-at" gate. The D28 "Build" button == checker-
   pass leg id 58 (or 56 ship-branch) — getter(58) TEXT NOT YET READ.
*** CORRECTION VECTOR: our shipped gate "surface+empty+active-neighbour"
was [inferred]; the vendor gate is THIS leg. Remaining: static.txt ids
52..58 labels + the item==0xff loop body + the consumer that paints the
button strip from the id array.

## C6 — POPUP BUTTON COMPOSITION LAW, FULL [verified 0x3d397..0x3d72e]
The msg-1 leg (key==3 gate 0x3d3ae) builds a u32 BUTTON-ID array then a
generic consumer converts it into button records. ID SET:
 51 (0x33) ALWAYS appended (0x3d5a4) — terminator/dismiss leg.
 54 (0x36) EMPTY-CELL path (item==0xff): loop cl=0..0x26 (cl==5 skipped),
   append iff build-checker 0x3830c(item=cl, cell=widget+0xab) passes —
   i.e. ONE BUTTON PER BUILDABLE ITEM TYPE, not a single "Build"!
 56 (0x38) ship-branch: cell4[+2]&1 (automated) && owner==player.
 57 (0x35) appended when item!=0xff && item!=0x17 (generic dismiss).
 52/57(ship)/55/58 ship legs: no-dest->52; enemy-owned->57; ALWAYS 55;
   checker(item=0x23)+owner==player -> 58.
 58 (0x3a) SURFACE path tail (0x3d51d): checker(0x3830c, item ARG 0x23=35,
   cell) TRUE -> append.
*** THE SHIPPED tPF-2 BUTTON LAW IS REFUTED. Our "Build iff surface+
empty+active-neighbour" is an approximation of BOTH the 54-loop (empty
cell: one button per buildable item, checker-driven; the active-neighbour
leg lives INSIDE checker 0x3830c, OQ-014-cited) and the 58 tail. The
refcap's single "Build" button = the 54-loop producing exactly one
buildable item at that stage of the game. getter-ids: 57 Cancel, 58 Create
Colony, 60 Build, 61 Leave Orbit (static.txt measured; 51/52/54/54/55
labels = getter(51..55) READ NEXT ITERATION).
CONSUMER LAW (0x3d591..0x3d67e, cited verbatim):
 - n = count; if n==1 -> special single-button string path 0x21a20(30).
 - per button i: dest = [[widget+0x67]+0x20] (display obj, the 0x7d3aa
   family); label = 0x744a0[id] -> Pascal string copied raw;
   rec+0x45(u16 hiword of +0x43 SENDMESSAGE) = id;
   rec+0x4 = x cursor (start 0xa0=160); width = 479(0x1df) - x, divided by
   remaining count (EVEN SPREAD of the strip); rec+8 = x+1;
   rec+0xc = y = -0x6(ebp) hiword; rec+0x10 = 367 (0x16f);
   font string lookup 0x56ca4(winmgr 0x7a35c, id).
 - THE PLSQBUT0..5 RECTS IN windows.txt (300,160..500,330) ARE TEMPLATE
   DEFAULTS OVERWRITTEN AT RUNTIME — our F3c "strip below text rect" was
   an eyeball; the law is x0=160, full-width even spread, y from ebp-0x6,
   bottom 367.

## C7 — FRAME-ART CANDIDATE [measured dims, identity OPEN]
Full-corpus shp dims census: the ONLY 33x-wide x ~200-320-tall record is
help.shp k0 = 336x256 (extracted/ascend01/data/help.shp). PLSQUARE popup
rect = 335x255 (F3c) => off-by-one parity EXACTLY like the t394 SHAPEFRAME
record dims == rect-minus-1 law. [inferred] help.shp k0 IS the popup
(mineral) frame. NOT YET VERIFIED PIXELWISE — next iteration: decode k0
(codec law r1_shp_decode_law) and diff its border against the refcap
popup border. NOTE PLSQUARE TYPE 14 has NO TYPE-100 header row (census
0,1,3,7,8,13,16,20) — the lib-binding site for TYPE 14 is unrecovered
(honest negative; help.txt/HELPWINDOW association stands in windows.txt
2034).
## C8 — PLANLIST ART SOURCE [gap stands]
dkshipNN k0 315x223 = ship-design screens, NOT list rows. The row-art law
(planitemLib rec==itemIdx) stays [inferred]-cited via t428's 1:1 tile law,
NOT a PLANLIST-paint citation. No PLANLIST paint fn located this session.

## VERDICT tPF-2c (honest negative, strict-close):
NO row closes. The audit LANDED C1-C8: SHAPEFRAME store +0x1e re-verified;
widget-frame blit path 0x31004 (dword+0x1c hiword = frame id, word+0x18 =
cache slot) found; planal-hypothesis KILLED by dims census; button law
FULLY DERIVED and it REFUTES the shipped tPF-2 button gate; frame candidate
help.shp k0 336x256 named (pixelwise check owed); PLANLIST row-art citation
still missing. NEXT tPF-2d: getter(51..56) labels; decode help.shp k0 +
refcap border diff; find TYPE-14 lib-binding site; port the C6 spread law
+ 54-loop; drop the invented strip.

## C9 — BUTTON-ID SEMANTICS CROSS-CHECK [measured id census]
Sites pushing ids 50..64 cluster in fn 0x3d2fe (the msg-1 leg, C5/C6) and
fn 0x3aa0a (a second composition site — the ORBITAL/ship context, ids
50,51,52 + 57-family). The label source is the RUNTIME table 0x744a0[id]
(exactly 2 sites: 0x5d1f, 0x3d5db) — NOT statically the static.txt order.
CAUTION: naive static.txt-index reading maps 51->'Supermineral',
55->'Tycoon' (nonsense as buttons), while 57->'Cancel' fits. So the
0x744a0 table is a POPULATED registry (writer = the same loader family as
0x74528's fills at 0x3d2b4/0x3d2b6 which copy static.txt 41..60 region —
CITE NEXT: find 0x744a0's writer, likely a 20-entry copy of static.txt
41..60 => id 51 = entry 10 of that copy = getter(51) verbatim 'Supermineral'
— if that holds, the vendor's empty-square buttons really are named by
DEV-TYPE words?? No — resolution requires the writer + the refcap button
text (refcap shows 'Build'/'Cancel'). 'Build' IS getter(60) and 'Cancel'
getter(57), and id 57 appended per C6 = Cancel FITS. The 54-loop appends
id 54 ('Special' by naive map) which CANNOT be the refcap 'Build' — so the
consumer's id->string map is NOT static.txt-order-51-biased; 0x744a0's
writer is the decisive probe for tPF-2d.

## C10 — THE LABEL REGISTRY INIT SITE [verified fn 0x3d2a0 verbatim]
Three loops fill u32 PTR arrays via getter 0x21a20(eax=id) storing the
RETURNED POINTER (Pascal/char strings into registries):
 - getter(41..0x28=64)? loop1: ebx=0x29.. while edx!=0x14 -> 21 entries
   getter(41..61) -> 0x74528[0..20] (0x74528..0x74578) — this is why
   ds:0x74528 (the indicator KEY) sits INSIDE a string registry: the key
   overwrites registry slot 0 (a u32 field reused as the key — tPLB2 law).
 - loop2: edx=0x2e..0x39 (12) -> 0x7453c.. hmm store is 0x7453c(%ebx) with
   ebx=4..0x2c -> 0x74540..0x74568: getter(46..57).
 - loop3: ebx=0x39..0x58 edx 4..0x20 -> 0x7456c..0x74588: getter(57..88).
CONSEQUENCE [measured + cited]: the button-label read 0x744a0[id] at
0x3d5db is OUTSIDE every filled span (0x74528+) => 0x744a0 is a DIFFERENT
registry whose writer is NOT in fn 0x3d2a0. Static scan of literal
0x744a0/0x74480..0x744d0 immediates: ZERO writers (only the two reads).
=> id->label map at 0x744a0 is populated RUNTIME by a mechanism statically
invisible (t333 family) OR via a base-register chain; RESOLVE tPF-2d via a
LIVE-RAM witness (pointer law, r1 savestate tooling) dumping 0x74480..0x74590
in a planet-view state, then resolving each u32 pointer to its string.

## C11 — ID->LABEL ARITHMETIC NOTE (for tPF-2d)
0x744a0 + 54*4 = 0x74578 — the LAST slot of loop1's registry span
(0x74528..0x74578 = getter(41..61)). If the registry base is 0x744a0 and
loop1 actually wrote at base+0x28 (i.e. the disp 0x74528 IS base+40), then
0x744a0[id] indexes the SAME arrays with id offsets: 51->getter(51+?)
mapping must be derived from the base identity, NOT guessed. The live-RAM
dump (C10) settles both base and labels in one witness.
