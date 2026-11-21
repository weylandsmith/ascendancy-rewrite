# tA3 TEXT LAW — WIP (STAGE A third law row)

TASK (queue row verbatim): font identity + cell size + baseline + color
classes measured from refcaps ONLY (G5); render a reference string table
at 1:1 and diff glyph metrics (height, advance, weight) vs refcap text
rows; fix the port's text draw to cited metrics. CLOSE: metric diff
within 1px on title + newgame + map button text + pins.

## Inputs (in hand)
- Vendor faces [verified, docs/re/fnt.md]: smfont h=8, bigfont h=11,
  intro h=39; byte-per-pixel, ink 0xF3 solid on sm/big, advance==width,
  no side bearings. Port loads them NATIVE (vendortext.cpp buildFace —
  1px atlas gutter, dst w=gw h=h, no scaling).
- Refcap witnesses: docs/assets/refcap/original-title-menu.png (640x480
  P, shot_row = logical+40 per t392), original-strategic-map.png (640x480
  P), scratchpad/newgame-original.png (643x481 RGBA browser shot — crop
  law im[1:481,1:641], NEVER Athens).
- t392 TITLE text law [banked boot.md §7]: big face both lines, draw
  TOPs y0+8 single / y0+4+y0+18 pair; ink {fill (0,0,8), ink (215,215,215)}.
- D19 seed for map: "button text too small/possibly wrong font".
- Image python: ~/tools/revenv/bin/python (repo .venv has NO PIL).

## Findings

(F1 FACE IDENTITY — .fnt tables re-cited this iteration [verified]:
sm H=8 cap-ink rows 0..6 (7 rows), lower 2..7; big H=11 cap-ink rows
0..9 (10 rows), lower 3..10; advance==width; A sm6/big8, I w4, 1 w4,
space sm4/big5. Ink alphabet exactly {0xF3} both faces (script-measured).

F1b MAP RAIL LAW [measured, original-strategic-map.png]: capture shift
law for GAMEPLAY refcaps = root row = window row + 40 (refcap.md:18,110;
CONFIRMED this iteration — the RACES rect (474,286)-(632,316) white-text
band sits at ROOT rows 328..338, i.e. window 288..298). Ink band 11 rows
(328..338), 7 glyph runs starting 477: run widths/rows EXACTLY the
bigfont extents — 'S' ink 7w x rows rel 0..9, 'p' rel 3..10, 'e' 3..9,
'i' 1w rel 0..9. Advance-sum bigfont "Species" = 40 (8+6+6+6+2+6+6);
refcap first..last ink 477..515, cell box 476..515 = 40px [verified].
TEXTITEM verbatim "0 Species 0 2 2" -> dy=2, draw TOP = y0+2 = window
288 = root 328 == MEASURED ink top EXACTLY. VERDICT: rail button text =
BIGFACE at y0+dy, x = x0+2 (first glyph cell x0+1..; 'S' ink starts
x0+3=477). smfont REFUTED at this site (7-row caps vs measured 11-row
band; template match sm 0.27 / bg 0.32 raw-ink at wrong y-window, then
exact-extent census decisive). PORT DEFECT CONFIRMED: ui.cpp:1388 draws
railLabel with large=FALSE at rr.y+8 — D19 "button text too small" is
exactly this.)
(F2 NEWGAME LABELS [measured on scratchpad/newgame-original.png, crop
law screen=image-1 applied; template match = vendor-face ink pixels all
bright, score=hit/tot]: "Star Density" bg 0.815 (sm 0.207 REFUTED) at
screen (31,392); "Atmosphere" bg 0.846 (sm 0.303) at (282,392);
"Species" bg 0.798 centred PLAYERS_MORE at (168,392); "Player Color" bg
0.878 (sm 0.444) at (403,394). TEXTITEM dy=10 predicts y=391 for the
three GALAXY/PLAYERS/DIFFICULTY labels — measured 392 on ALL THREE
(consistent +1 = browser-window capture offset, law stays y0+dy: the
map refcap rail hit dy=2 EXACTLY, root=window+40). Centre law holds:
x0 = rect centre - adv/2 within 1px on all four (rects 7..122,
131..246, 255..370, 379..493; advs 66/40/61/65 bigface).
"Begin New Game" bg 0.877 (sm 0.402) at (523,455) — kBeginLabelTop=455
ALREADY CORRECT top; centring already correct; FACE was the defect.
Player Species header ink band rows 15..24 (10-row caps = BIGFACE;
t401 bank said 16..25 = pre-crop-law row, now corrected to 15).
Species name (green, race-name text) ink rows 17..26, x394..428 —
10-row caps = BIGFACE, 35px ink box (bigface advance of a 7-glyph name
+ last-glyph no-side-bearing). GREEN ink (0,113,56) core/(0,142,69)
bright — kLore already matches.
FONT-FIELD LAW [inferred from 5 verbatim TEXTITEMs + measurements]:
fields 0 (rail), 2 (pair hints, newgame labels), 3 (title singles) ALL
render the BIG face — t392 measured font-2 hint == bigface 27px span;
this iteration font-0 rail + font-2 labels measured bigface. smfont is
NOT a TEXTITEM face (body-text windows territory — summary/lore
pending F3).
PORT DEFECTS CONFIRMED (face=FALSE where vendor=BIG): ui.cpp:1388 rail
labels (+x also: law draw x = x0+2, port rr.x+6); title.cpp:815 newgame
control labels (+y: law y0+10, port y0+12); title.cpp:564 species name;
title.cpp:570 Player Species header (top also 16->15); title.cpp:963
Begin label (width computed smface -> centring off by adv diff).
(F3 BASELINE LAW, all sites [measured]: draw-TOP = ink-top (caps row 0),
TEXTITEM sites draw TOP = y0+dy VERBATIM — map refcap rail dy=2 hit
EXACTLY (root=window+40). Browser shots drift per-window: newgame
browser +1 (three labels all 392 vs law 391), galaxymap browser -1
(three rails 248/209/287 vs law 249/210/288). LAW = windows.txt dy;
browser deltas are capture noise, NOT law.
Non-TEXTITEM newgame sites (browser shot, crop law applied): species
name ink rows 17..26 (bigface; kNameTop 18->17), Player Species header
15..24 (kHeaderTop 16->15), Begin New Game 455..464 (kBeginLabelTop 455
ALREADY CORRECT). Summary block: "Star Cluster" bg 0.867 (sm 0.424
REFUTED) fit y=326, "Species" bg 0.807 y=339, "Atmosphere" y=351 ->
kSummaryTop 327->326, pitch 13 CONFIRMED (12..14 fits). LORE: 'the'
sm 0.632 > bg 0.469 and bands are 8-row = SM face — port sm draw
CORRECT; pitch 11 CONFIRMED (bands 265,276,287); lore ink top 265 vs
port draw kLoreBox.y0=258 = 7px too high -> new kLoreTextTop=265.
RAIL x LAW: 'S' cell origin x=476 = rect.x0+2 (S ink starts at gx=1 in
cell) -> draw x = x0+2 (port rr.x+6 wrong; icon fallback tx fiddling
obsolete — icon at x0+109 clears even the widest big label 71px).
COLOUR CLASSES [measured]: map refcap (palette-exact) rail ink
(255,255,255) core 260px — game.pal white; port kText (235,235,235) =
port invention -> 255. Title ink (215,215,215) t392 [verified, title
palette — DO NOT touch]. Newgame label core (255,255,255) on browser
shot (browser blends edges to (225,227,229)/(164,171,177) — core is the
(F4 IMPLEMENTED LAW (decisions): TITLE untouched (t392 verified, palette
differs). New constants: hudlayout kRailLabelDx=2 kRailLabelDy=2
(measured cell origin x0+2, TEXTITEM dy=2 exact-hit); menulaw
kControlLabelDy=10 (TEXTITEM verbatim), kLoreTextTop=265 (measured ink
top; port drew 258), kNameTop 18->17, kHeaderTop 16->15, kSummaryTop
327->326 (pitch 13 confirmed 326/339/352). Faces -> BIG: rail labels,
control labels, Player Color label (measured (403,394) big 0.878, centred
within 1px, y=y0+13), species name, header, summary (Star Cluster big
0.817 vs sm 0.276), Begin label. LORE stays SM (measured sm>bg, 8-row
bands). Colour classes: map rail ink (255,255,255) palette-exact -> new
kRailInk; newgame white core (255,255,255) browser 1:1 -> new
kNewgameInk (port kInk 215 = title-palette class, wrong on game.pal
screens); green name core (0,106,51)/(0,149,71) family of kLore
(0,142,69) — keep kLore (ring-pinned). kText 235 NOT globally changed
(26 campaign sites, some unpinned; scope = tA3 sites only).

(F5 WITNESS GREEN [run this iteration]: scripts/r1_tA3_capture.sh
(Title -> FRESHGAME 318,295 -> Begin 566,422 -> intro advance 320,240,
scratch saves /tmp/tA3_saves, 640x480 Xvfb) + scripts/r1_tA3_witness.py
(vendor faces parsed from .fnt; ours side checked at EXACT law
positions, vendor side best-fit +-2 for the banked capture drift;
dynamic-word sites SKIP on the vendor side per the tA1-CONT
different-campaign-state contract). RESULTS: ours-newgame 6/6 PASS
(big iou 0.935-1.000 vs sm 0.15-0.26 — the render draws the law
exactly: cell (31,391) "Star Density" full bigface); ours-map 5/5 PASS
(1.000 all rails); vendor-newgame static sites 3/3 PASS (0.785-0.809
big vs 0.265-0.304 sm); vendor-map 5/5 PASS (1.000 big vs 0.24-0.37
sm). CLOSE term met: ours-vs-law metric diff = 0 px at every site
(<=1px required); title = t392 row-for-row (unchanged this iteration).
CENTRE LAW CORRECTED mid-run: cell x = (x0+x1)/2 - adv/2 (NOT
(x0+x1+1)/2): fits 5/6 measured exactly (Player Color law 404 vs
measured 403 = within the 1px close term). Pins
rewrite/tests/test_textlaw_tA3.cpp x3 (constants, verbatim labels,
centre law) registered in CMakeLists; 475 tests 0 failed.

(F6 MUTATION CAMPAIGN [honest record, two runs]: scripts/r1_ta3_mutate.py,
12 mutants — 8 constant mutants caught by run_tests pins, 4 draw-site
mutants (rail face->sm, rail ink->235, control face->sm, begin ink->
title white) caught by the live witness (core255 frac 0.000 / sm-beats-
big flips). PITFALL BANKED: a foreground mutate run hit the 420 s tool
timeout and was KILLED mid-mutant, leaving M5 applied; the next run
snapshotted that poisoned tree (M7 ANCHOR-ERROR + a phantom summary-top
failure in every later result line). Recovery: restore from /tmp/
ta3_snap, rebuild, suite green; M7 re-run ALONE on a green tree =
CAUGHT. Clean-run evidence: M1-M5 CAUGHT (green run 2), M7 CAUGHT
(isolated green run), M6+M8-M12 CAUGHT (contaminated run 1 — their
catcher lines are the EXPECTED specific pins/witness flips; the poison
only added a second, unrelated failure line, so the catches stand).
AFTER-RESTORE verified: build 0, 475 tests 0 failed, md5 restore checks
passed (script aborts on mismatch). Guard ADDED to the script:
snapshot() refuses to launch on a non-green suite.)

CLOSE VERDICT: metric diff ours-vs-law = 0 px at all 11 ours-side sites
(<=1px required); title untouched (t392 row-for-row stands). tA3 CLOSED;
PHASE-17 Stage A (tA1+tA2+tA3) COMPLETE.
