# t400 — RAIL, SPECIES FLAGS, TITLE HOVER, FRAME TEXTURE (law)

Hand-authored (t400 iteration, 2026-11-15). Nothing regenerates this file
(gate regenerates only loader/research/gizmos/economy/modules/attribution
names). WIP trail: docs/re/_wip_t400.md (S1–S14, kept).

Measurement bases (all pinned, in-repo or user-supplied):
- USER original galaxy map: scratchpad/galaxymap-original.png (642x481).
- Self-captured strategic map: docs/assets/refcap/original-strategic-map.png
  (640x480; capture shift +40 rows vs logical game coords, t386 law).
- Title menu: docs/assets/refcap/original-title-menu.png; title palette =
  rewrite/tests/data/title_palette_t386.tsv (t386 law).
- Table: extracted/ascend00/windows.txt. Registration:
  scripts/t398_palette_register.py (mean |diff| over game.pal-converted
  pixels).

## 1. Rail icon placement [VERIFIED]

windows.txt state-1 rail buttons each carry
`SHAPEITEM 1 data\1starmap.shp <frame> 109 0` =
`<enabled> <lib> <frame> <dx> <dy>`; all four iconed rows: Status k5,
Ships k4, Research k3, Special Ability k7. dx=109, dy=0.

Law: icon blits at (rect.x0 + dx, rect.y0 + dy) — 474+109 = 583, matching
the measured icon left edge 584/585 (±2 capture noise). Icons are RIGHT of
the label at NATIVE size (the "wrong size" D11 complaint reproduced
against pushed build 5373c66, which drew vector rects — not a scale law).
Vertical: faces 20–30 px tall in 30-px buttons; measured tops sit at
button-centre minus h/2 (registration tops 130/175/213/248 vs button
centres 145/184/223/262). The port paints railIconPos() =
{x0+109, (y0+y1)/2 − h/2} (ui/hudlayout.h; pinned exactly in
test_rail_t400.cpp after a top-align mutant slipped a tolerance pin).

RACES and Intelligence rows have NO SHAPEITEM (grep: SHAPEITEM exists
only ×4 1starmap rail + ×3 3cfgnew) — their content is code-drawn (§2).

## 2. Species-row flags [geometry VERIFIED; race-selection law = SEAM]

Species row shows TWO small portraits right of the label (user original +
vision read). Measured content run x521..552, boxes 13–14 px wide × ~24,
pitch ~19, label ink ends x516. raceflag.shp = 21 records EXACTLY 14x24
— unique in the corpus at that size×count (census all .shp). Frame index
== specnum [inferred: 21==21 + smraceNN sibling pattern]. raceflag's
dominant colour is EXACTLY (12,32,48) = the rail button fill, so flags
blit seamlessly onto the rail.

Port law (declared, not vendor-cited): left slot (521,288,534,311) =
player species flag (human specnum −1 → left slot left EMPTY — honest),
right slot (540,288,553,311) = first AI specnum, vertical-centred y.
NAMED SEAM: which TWO races the vendor shows. Decider: live witness with
a known player species (the original's own shot cannot resolve it —
registration of 21 frames against one flag of unknown identity is
vacuous, conflicts 55–98).

## 3. Title hover [VERIFIED fill law; bevel structure = SEAM]

Pinned title shot, bands at rect-centre+40 (t386 closure law): six of
seven buttons are EXACTLY {fill (0,0,8), ink (215,215,215)} (t390 law);
PLAYTUTORIAL — the button the cursor was on — has fill (0,28,36) EXACTLY
9691 px + ink 113 px. (0,28,36) is not in game.pal; it IS reachable
through the title TSV (title-family teals (85,142,142)×473, (0,16,20),
(36,73,77), (0,24,28), (48,93,97), (0,8,0) are consecutive vendor columns
of the same GIF palette). windows.txt has NO hover/hot/focus-state field
(grep MOUSEFOCUS|HIGHLIGHT|HOT|BUTTONSTATE|FOCUSCOLOR = 0 usable hits) —
the hover fill is CODE, consistent with the code-drawn species flags.

Law implemented: hovered title button fills kTitleFillHover (0,28,36),
else kTitleFill (0,0,8) — boot.h titleButtonFill(), SDL side via
SDL_GetMouseState (title.cpp). The residual black/grey vertical structure
(x319–330, greys 93/146) in the single hovered sample is either the
vendor cursor or a hover bevel — ONE sample cannot separate them. NAMED
SEAM; decider: a vendor screenshot with the cursor away from any button
while a button is visibly highlighted.

RAIL hover: NO witness exists (map original's cursor sits above the
cluster; no hovered rail button in any pinned shot) and no data law —
rail hover deliberately NOT implemented (seam, same decider class).

## 4. Frame texture [geometry + palette VERIFIED; source record unknown]

The map screen carries a mottled grey-teal TEXTURE in vertical bands:
left margin x0..6 full height, right column x466..639 full height
(incl. sidebar gaps + cluster background). BOTH independent vendor shots
agree (user original margins; pinned capture left rows 40..479 = logical
0..439 under the +40 shift — the capture's own window clips below). The
FIELD interior is black — texture is CHROME, outside COSMOSWnd.

Colour census (pinned bands; ALL verified inside game.pal): (77,113,117)
14.9%, (85,125,125) 8.7, (97,146,146) 8.0, (69,105,109) 7.4, (97,97,97)
7.2, (89,134,138) 6.7, (89,89,89) 6.6, (60,93,97) 5.6, black 4.5,
(73,73,85) 4.1 (weights sum 74; residue → tail set {(48,77,81),
(105,154,154), (81,81,81), (36,56,60)}, also in game.pal).

Source record UNIDENTIFIED: 1starmap k0 (158x75) REFUTED at the cluster
(7172 conflicts, 21% in-palette); no .shp record matches the band extent.
PORT LAW: deterministic splitmix64 hash-noise over the measured colour set
with the measured weights, painted in the measured bands before chrome
(mapchrome.{h,cpp}; no engine-rng consumption). The noise PATTERN is a
named seam (decider: vendor screen-record of a pan, or the identifying
record); geometry + palette are cited.

## 5. Rail fill colour [VERIFIED, palette.md §4]

Rail button fill is (12,32,48), not the port's earlier (40,40,56). race-
flag dominance (§2) corroborates. Applied in ui.cpp rail draw.

## 6. Cluster background [RESOLVED as §4 texture; panel-art hypothesis REFUTED]

D11 "cluster bg art missing" is satisfied by the §4 texture band (the
cluster sits inside x466..639). No separate panel record exists for the
cluster zone (§4 refutation). Small per-button glyphs were shipped t394
(1starmap k8..k18 faces) — the user graded pushed build 5373c66, which
predates t394; local witness re-confirms them (icon-zone chroma, §7).

## 7. Verification (this iteration)

- Pins: rewrite/tests/test_rail_t400.cpp (4 test fns: placement, flags,
  hover, texture). Suite 330 → 334, 0 failed.
- Mutation 6/6 CAUGHT via scripts/t400_mutate.py at checkpoint 4aad600:
  dx→4, top-align (initially MISSED by a tolerance pin — re-scoped to
  exact cy−h/2 then CAUGHT), flag box 14x24→16x16, hover fill→plain,
  texture hash x-only, band trimmed, census colour off-palette.
- Witness PASS (scripts/t400_rail_witness.sh + t400_witness_census.py,
  mechanical census of OUR render — R13-safe): left band 14 colours 100%
  in game.pal (port frame grey (120,120,120) excluded, named); right band
  182 colours 97.9%; rail icon-zone chroma Planets 1128 / Ships 806 /
  Research 984; species flag zone non-flat incl. raceflag green
  (0,170,81); title-hover: hovered LOAD band dominant (0,28,36), other
  bands (0,0,8). Screenshots: work/r1/loop/t400-map.png,
  work/r1/loop/t400-title-hover.png.
- Engine untouched: headless --campaign 120 --seed 1 md5
  6f8281d078447b0dd036e1d27c7c3578 == t399 record.
