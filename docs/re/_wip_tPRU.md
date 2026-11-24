# _wip_tPRU — tPR-U USER GRADE PACKAGE PR1 (research screen), 2026-11-24

Purpose: the D26 research-screen attribution question ("does the port LOOK
like the vendor tree now that the geometry machine is shipped") is answerable
only by a human side-by-side. This iteration produced the package; NO law was
changed, NO code shipped, NO OQ row moved.

## P0 SITTING CHECK (ran FIRST)
`python3 scripts/r1_t85g_sitting.py` exit 0 — newest trusted turn-change rows
unchanged (relation snapshots t1250.., battle-window diffs identical in shape
to the banked t1253/1254 sitting). No new user sitting => the stale NEXT
ACTION (tPR-U) stands. 45,227 trusted rows replayed.

## P1 PORT SHOT (real capture, not synthetic)
`OUT=/tmp/tpru_shots bash scripts/tRSB1_witness.sh` VERDICT PASS:
choreography RESUME(318,335) -> RESEARCH rail(553,223) -> dolly-out 2x
(578,449) -> click RE-DERIVED from the app's own log line "ui research center
6 397 240 available" -> "ui research study Xenobiology"; panel-green 0->690;
local-change leg 563 px. Shots: /tmp/tpru_shots/before.png, after.png.
after.png is the OURS half of the package.

## P2 VENDOR REFERENCE (no re-capture — REFUTED route class respected)
work/screens/t252/research_open_game.png (640x480, turn 1255 per
work/screens/t252/_state.json, step "research_open" click 553,223 — the same
rail the witness uses). Vision + pixel census of the field:
- 3 disks visible (one orange with a PICTURE inside at ~(250,182) full-frame,
  two blue), lines running off the TOP edge. Vendor field bg = pure black
  (0,0,0) — 97.7% of a 60x440 sample strip is exactly black.
- vendor orange ring comps: (238,155)-(262,210) + (265,155)-(296,210) — the
  orange ring is SPLIT into two comps by the picture inside; outer extent
  ~59x56. vendor blue ring extent 60 px wide (comp 179..238 includes its line).
- vendor dim-line mean RGB (9.3,31.5,81.6); bright-blue line pixels mean
  (83.2,124.8,174).

## P3 PORT MEASUREMENTS (same probes on /tmp/tpru_shots/after.png)
- ring comps: THREE full rings at 60x58/59 (centres (89,255), (412,255),
  (250,354)) + one clipped at the bottom edge (195,454)-(248,471). So the
  port's ring RENDER size == vendor's 60 px. [verified, both sides measured]
- port dim-line mean RGB (9.5,32.5,90.8); bright-blue (79.7,155.7,198.7) —
  same family as vendor, slightly hotter.
- port field bg = SINGLE flat fill RGB(16,16,24) (26400/26400 px of a
  60x440 strip). Vendor = (0,0,0). MEASURED DIFFERENCE, graded as item 5.
- zero gold-ish px on the clicked disk ((383,226)-(442,284) ring mean
  (79.5,162.2,203.9) = the blue frame). The "gold selected rim" label from
  P10 (0x5caac named "gold-rim path" in _wip_tRSV1 P3/P5) is an INFERRED
  name, never witnessed — the package does not claim it (checklist item 6
  asks the user to judge ring-colour meaning instead).

## P4 ART-FILE CROSS-CHECK (free, from the banked shp law)
resring.shp directory parsed with the unified law (magic '1.10', count u32@4,
starts 0x10+8k): N=4 records; bbox quads k1..k3 = (-30,-30,29,29) => dims
60x60 by the bbox-diff law. The port blits these 1:1 UNSCALED and they MEASURE
60 px on screen — the "29x29" note in research.md S8(f)/_wip P3 is the
record-header reading; the MEASURED on-file bbox says 60x60, and the rendered
result agrees with the vendor's 60 px rings. [verified this iteration: file
offsets 56/1200/2363/3532, bbox at rec+8]
NOTE: this does not re-open any closed row; it aligns a side-note with
measurement. research.md S8(f) "4 records 29x29" -> dims pair reading there
was the header, not the bbox; corrected in P6.

## P4b SEAM TRSV1c-E — DRAWN RING CENTRE OFFSET +15,+15 (measured)
The app logged the node centre (the projection word == the hit centre, the
P11 blit/hit word identity) at (397,240); the DRAWN ring's bright-pixel bbox
is (383,226)-(442,284), centre (412,255) — offset (+15,+15). Arithmetic: the
port blits at (x-14, y-14) (the 29x29 centring assumption, ui.cpp "NODES"
block) and blitShape draws the record with bbox top-left at the blit point,
so a 60x60 bbox (-30,-30,29,29) lands its CENTRE at (x-14+30, y-14+30) =
(x+16, y+16) — matching the measured +15 (chop/round). The vendor passes the
projected word DIRECTLY to the blitter (0x1fc34 x=word+0x5f1 sar16), so under
the word-identity law the vendor's drawn centre and hit centre share the
word; OURS do not. The +-24 hit square absorbs it (witness still PASSes),
but the drawn disk sits 15 px off its clickable centre. SEAM TRSV1c-E named
for the follow-up: re-derive the vendor blitter's anchor semantics (does
FUN_0001fc34/0x5caac shift by the bbox, or is the projected word itself the
top-left?) before touching the offset — do NOT blindly change x-14 to x-30
without the anchor law.

## P5 PACKAGE ARTIFACTS (the deliverables)
- scripts/tPRU_composite.py (new, hand-authored): crops both shots to the
  RESWIN interior (8,46)-(476,472) = 468x426, 2x NEAREST side-by-side + 3x
  zoom strips + on-image plain-language checklist. PIL sanity asserts
  (dims, nonblank, fields differ). Run output:
  `SANITY dims=(468, 426)x2 ours_mean=20.70 vendor_mean=1.01
  differing_px_frac=1.000` -> SAVED scratchpad/PR-usergrade.png 1882x2676.
  Vision-verified: checklist legible, panels labelled, no overlap.
- scratchpad/PR-checklist.txt — 6 graded items: (1) disk size 60 vs 60,
  (2) how much tree fits / camera feel, (3) line colour gradient direction,
  (4) inside-disk picture KNOWN-MISSING (seam TRSV1-C), (5) bg black vs
  16/16/24, (6) ring-colour MEANING (never witnessed either side). t441 has
  NO "research" region table (REGIONS = newgame, planetslist only), so the
  task's "verify with t441 or PIL sanity" resolved to the PIL leg — cited.
- Nothing regenerates these files (scratchpad/ is not a gate-generator
  target; _wip_* are hand-authored per the BLOCKED.md traps).

## P6 RESEARCH.md SIDE-NOTE AMENDMENT (banked this iteration)
S8(f) "4 records 29x29" amended to cite the MEASURED bbox quad (-30,-30,
29,29 => 60x60 by the bbox-diff law, offsets 56/1200/2363/3532) and the
rendered 60 px agreement on both sides. The 29x29 was the dims-pair-at-
header reading; blit is 1:1 either way (0x5caac row-RLE unscaled — unchanged
law), and the port's blit centre (x-14,y-14) still centres a 60 px record on
the projected point only if the record is drawn from its bbox — the port
renders 60 px rings, matching vendor, so the shipped behaviour is right; the
(x-14) offset comment is what the 29x29 note was standing on.

## P7 LEDGER
No OQ row touched. The research screen tracks no open row (open=[016,019]
unchanged). Honest negative under strict-close: this iteration MOVED an
attribution question to the human ruling queue; it closed nothing.
