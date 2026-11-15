# t400 WIP — RAIL + CLUSTER + HOVER LAW (D11)

Session start frame (pre-probe):
- Assignment: STATE.md NEXT t400. Tree clean at 619f2e2 (t399). Page server
  live on 8613 (pid 646702). Ring max_turn=1254 (no new sitting; timeline
  untouched since Nov 12 — r1_t85g_sitting.py NOT run).
- D11 lines (DECISIONS.md 11:37) for this row: rail icons greyscale/wrong
  size/wrong side; species-button icons missing entirely; bottom-right
  cluster bg art + little icons missing; TITLE hover highlight missing.
- Greyscale half is ALREADY closed mechanically by t398 (game.pal law,
  palette.md §3-§6) — t400 owes GEOMETRY (side/size), the cluster, and
  HOVER.
- Port state: ui.cpp rail draw paints icon at rr.x+4 (LEFT of label) —
  palette.md §4 already measured vendor icon x=584/585 = RIGHT of label.
  mapchrome.h holds kTurnCount/kOvalSlots/kMapCtl cluster rects (t394).

S1 RAIL GEOMETRY [verified, t398 registration + external vision of
scratchpad/galaxymap-original.png]: icon LEFT edge x=584/585, icon TOP =
button y0+3 (rows: k5@130->y133, k4@175->178, k3@213->216, k7@248->251).
584-474 = 110 and 585-474 = 111 bracket the SHAPEITEM dy field 109 —
[draft law] item coords are ABSOLUTE game coords, dy=109 imprecise/other-
space. All five icons sit RIGHT of the label. Port paints rr.x+4 = the
D11 "wrong side" defect. Sizes: records 43-45 px wide vs vendor shot icon
~20-14 px?? — vision estimate 20x10 is a rough eyeball; registration
measured k5 44x27 FITS the shot at (585,130) with 97% px within 12 of
game.pal-conv, so NATIVE 1:1 size is the law ("wrong size" complaint =
user ran pre-t394 build 5373c66 which drew vector rects, not a scale law).
S2 RACES ROW [verified table]: RACES TYPE 5 WINITEMS 1, Intelligence
WINITEMS 0 — NO SHAPEITEM anywhere for them (grep: SHAPEITEM exists only
x4 1starmap rail + x3 3cfgnew). Yet the original shows TWO small square
portraits right of "Species". => the portraits are CODE-drawn, not
windows.txt-driven. [draft] = per-race sprites (COSMOSWnd SHIP_SHAPES law
shows code-drawn sprites exist; smrace*.shp = 49-px sprites per t386).
Which two races = t400 open question.
S3 TITLE HOVER [verified census on pinned original-title-menu.png, centre
bands rect-centre+40]: six of seven buttons are EXACTLY {(0,0,8) fill,
(215,215,215) ink} (t390 band-closure law); PLAYTUTORIAL (the button the
mouse was over when the shot was taken) is a DIFFERENT FILL (0,28,36) +
ink + greys {93,146} (bevel-ish) + teal-family other-colours {(85,142,142)
473px, (0,16,20), (36,73,77), (0,24,28), (48,93,97), (0,8,0)}.
=> HOVER LAW EXISTS as data: the hovered button's fill changes to
(0,28,36). Neither colour is in game.pal (title palette = TSV). Next:
which TSV index maps to (0,28,36); whether 0opening.shp holds a highlight
strip record.
S4 CLUSTER [external vision, crop x470-642,y355-478]: buttons sit in a
TEXTURED mottled dark blue-grey PANEL with light bevel dividers (bg art
exists); button faces carry RED/YELLOW glyph glyphs (double arrows,
triangle, star/crosshair, orbital circles with dots); bottom strip = SEVEN
coloured squares (green yellow purple brown/olive pink-red blue orange —
the RACECONTROLS slots, matches kRaceSlots 7x16x16). Our port already
blits k8..k18 faces (t394) — the missing piece per user (running pushed
5373c66, pre-t394) may already be fixed locally; the PANEL behind is the
open question: candidates (a) a 1starmap bg record, (b) state-1 TYPE-100
shapefile, (c) starfield showing through gaps.

S5 SHAPEITEM dx/dy READING [verified]: header "SHAPEITEM 1 data\1starmap.shp
3 109 0" = <enabled> <lib> <frame> <dx> <dy>. dx=109,dy=0 for all four rail
icons; 474+109 = 583 vs measured 584/585 (capture noise ±2). So THE LAW =
icon painted at (rect.x0+dx, rect.y0+dy), NOT centred, NOT left-of-label.
Measured tops vs y0: k5 +0, k4 +6, k3 +5, k7 +1 (registration y noisy at
mean-diff 3-6; dy=0 law + vertical-centre fallback documented as residual).
S6 SPECIES-ROW ICONS [measured geometry + candidate lib]: chromatic ASCII
map of the shot shows the "Species" label ends x~516 and TWO boxes with
content bbox x 521..552 (green box 521-533, purple 540-552), y 288..314 =
13x25 each, pitch ~19. raceflag.shp = 21 records EXACTLY 14x24 (21 races)
— the only lib in the corpus with that shape class at that count
(census all .shp: nothing else 13-14 wide x 24-25 tall x21). Registration
conflicts high (55-98) because the method scores multicolour art against a
region holding a DIFFERENT race's flag — vacuous for small sprites; needs
the frame->race map first. [inferred] frame index == race index (matches
smraceNN pattern; 21==21). Which TWO races the vendor shows = open content
law (player + leader?); port candidate: player race flag left box, second
box NAMED SEAM.
S7 CLUSTER PANEL CANDIDATE: cluster zone x474..632 (159) y~358..433 (76)
vs 1starmap k0 = 158x75 [census]. k0 is the state-1 TYPE-100 lib's first
record; t391 law: k0 IS the full backdrop for 10status/4loadgam. For state
1 the field backdrop is the starfield, so k0 = sidebar PANEL behind the
cluster is the hypothesis. Test = registration at shift (474,358).
S8 TITLE HOVER LAW [measured on pinned original-title-menu.png]: six of
seven button bands are EXACTLY {fill (0,0,8), ink (215,215,215)}; the
PLAYTUTORIAL band (cursor was on it) = fill (0,28,36) + ink + greys
{93,146} + TEAL FAMILY {(85,142,142) x473, (0,16,20), (36,73,77),
(0,24,28), (48,93,97), (0,8,0)} — and those teals are consecutive VENDOR
columns of the t386 TSV (GIF palette!). 0opening.shp = 318x30 + 6x(30x318)
strips (t386); 318x30 = exactly the button rect size. HYPOTHESIS: a
318x30 strip IS the hover face painted through the GIF palette. Test =
register 0opening records at the hovered band (capture y 320..350, x 159).

S9 HOVER LAW REFINED [measured, pinned original-title-menu.png]: hovered
band = fill (0,28,36) EXACTLY 9691 px + ink (215,215,215) 113 + BLACK
x319..330 rows 280..294 + greys (93,93,93)/(146,146,146) at x320 + x326-328
= a VERTICAL bevel structure mid-button. Cursor position cannot be
separated from chrome with ONE hovered sample: the fill change is the law;
the black/grey structure is either the vendor cursor or a hover bevel —
NAMED SEAM (decider: a screenshot with the cursor away from a hovered
button). Port law: hovered title button fills (0,28,36), never the
non-hover (0,0,8).
S10 CLUSTER BG: the mottled texture = game.pal FAMILY {(77,113,117) mode,
(69,105,109), (85,125,125), (89,134,138), (97,146,146), greys (97,97,97)}
— all five teals verified IN game.pal; the texture fills the RIGHT MARGIN
x633-639 AND the sidebar gaps in BOTH independent vendor shots (user
original + our self-captured strategic-map) = a screen-wide dithered
frame/margin texture; no .shp record matches the cluster panel zone
(1starmap k0 158x75 registration at (472,360): 7172 conflicts, 21% in
palette = REFUTED for the panel). Port: deterministic luminance-noise band
x466..639 y0..479 painted through those measured colours BEFORE the
chrome; the noise pattern itself is a PORT CHOICE (named seam), the colour
census + geometry are cited.
S11 SPECIES FLAGS: content run x521..552 (32 px, two boxes + gap), label
ends x516. raceflag.shp 21x(14x24); dominant colour EXACTLY (12,32,48) =
the button fill (self-masking — blits seamlessly). Paint law: box lefts
521 / 540, vertical-centred in the 30 px rect (24 px sprite -> y0+3).
Left box = PLAYER species flag [port law; vendor's two-race law uncited —
NAMED SEAM, decider = a live witness with a known player species]; right
box = first AI specnum (deterministic). frame index == specnum [inferred
from the 21==21 census + smraceNN sibling pattern].

S12 FRAME TEXTURE LAW [measured, BOTH independent vendor shots agree]: the
map screen carries a mottled grey-teal TEXTURE in vertical bands: left
margin x0..6 full height AND the whole right column x466..639 full height
(pinned self-captured original-strategic-map.png: left rows 40..479 = game
0..439 full under the +40 capture shift; user original identical in the
margins and sidebar gaps). The FIELD interior is black (88945/… black px)
— texture is CHROME, outside COSMOSWnd. Colour census of the bands
(pinned): (77,113,117) 14.9% (85,125,125) 8.7 (97,146,146) 8.0
(69,105,109) 7.4 (97,97,97) 7.2 (89,134,138) 6.7 (89,89,89) 6.6
(60,93,97) 5.6 black 4.5 (73,73,85) 4.1 — ALL verified inside game.pal.
SOURCE RECORD: unidentified — 1starmap k0 158x75 REFUTED at the cluster
(7172 conflicts, 21% in palette); no .shp record matches the band extent.
PORT LAW: deterministic hash-noise over the MEASURED colour set with the
measured weights, painted in the measured bands before chrome; the noise
PATTERN is a named seam (decider: vendor screen-record of a pan, or the
identifying record), the GEOMETRY + PALETTE are cited. Witness = census of
our own render (R13-safe): band px >=90% inside game.pal + non-flat.
