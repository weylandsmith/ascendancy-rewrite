# OPEN QUESTIONS — live closeout ledger (v2, strict-close)

Statuses: open | CLOSED. Nothing else. A question closes ONLY with cited
evidence (Ghidra address / extracted-file offset / pointer-law guest-phys
measurement from a named capture) + the rewrite site upgraded + docs/re/
updated + a gate or test pin. FINAL-DEFAULT is not closing (docs/GOAL.txt).
v1 full evidence text for every row: archive/ralph-v1/OPEN-QUESTIONS.md.
Do-not-retry prohibitions: docs/REFUTED-ROUTES.md.

Format: ID | area | question | status | what closes it (in-hand route)

OQ-010 | rules | combat damage APPLICATION: hit probability, shield
subtract-vs-absorb, overkill, firing order | open | W1: click-diff capture
turn-boundary deltas (turn counter u16 phys 0x254e10), then Ghidra xrefs on
the reader/writer functions (attribution: batmode/cosmos ranges,
work/attribution.tsv). Device constants are already data-verified (gizmos
damage 1..13, shields 1..5) — the application code is the target. Static
route bounded 2026-10-06: payload has ZERO disp32 accesses at orbit offsets
+0x57/+0x5f (scan: 2 bogus hits, both outside code ranges); shape tie found
(FUN_00025604 stride-constant table 0x60/0x7b/0x27 == live-measured record
families, docs/re/r1-savestate.md).
OQ-003 | gam | .gam full record map + field meanings; packed entropy regions
| open | W1 joint: planet records already joined file<->live RAM 151/151
(stride 123); STAR TABLE + ORBIT LAWS closed 2026-10-06 map the neighbourhood
(star stride 96 name-anchored, planet ptrs star-name+0x2A -> planet-name-0x24,
single-owner law, orbit pair planet-name+0x57/+0x5f); field semantics fall
out of controlled-mutation diffs (settle/capture turns), then the save writer
code. Low priority otherwise: rewrite is fresh-start-only.
OQ-021 | victory | end-ctrl threshold: vendor comment "over half" vs same
file's prose "two-thirds" — current default >1/2 | open | W2: find the
constant/comparison near the victory check in code (ghp5 functions_full.tsv,
gsystem attribution). A RAM measurement of a live galaxy at the trigger
boundary corroborates.
OQ-020 | abilities | charge time for the 14 charged SA_ abilities (vendor
"%d day%s", no data file) — current default 30 turns | open | W2: locate the
formatting/argument site in code (help text lives in help.txt L1829 et al.;
the value is a runtime constant).
OQ-005 | shp | .shp pixel codec (container CLOSED 208/208) | open | W3 ONLY:
exe shape loader via call graph + live image. Blind static sweeps are
FORBIDDEN (docs/REFUTED-ROUTES.md R2). Map currently draws documented
circles.
OQ-006 | audio | sample rate/channel count of 77 headerless .voc + 29 .raw
(current default 22050 mono) | open | W3: exe audio-init constant, or
dosbox measurement of output cadence.
OQ-004 | tables | which tables the exe loads; .tsv container grammar | open
| W3: trace the open-file thunk once entry points are pinned via live-image
call graph (no .cob strings in exe — the installer unpacks; loader.md §5).
OQ-012 | mapgen | (a) new-game size options (labels baked in 3cfgnew.tmp
glyphs) (b) pps distribution shape beyond uniform 1..5 (c) star type vs
position (d) logical map extent | open | W2: read the new-game screen's
live RAM state (deep capture stops there by design); (b)/(c) from a captured
fresh galaxy vs generator controls.
OQ-013 | rules | restree variant block: field0 (0..4) semantics; main tree
vs variants vs union in play (current default union) | open | W2: which
research rows are live in fresh-campaign RAM; research-screen code path.
OQ-014 | rules | planitem unknowns: REQUIRES=254 (Interstellar Trucking),
count triple 22/9, the 11x4 + 5x15x2 grids, item FLAG bits (current: 254
ungated; grids parsed-unused) | open | W2/W3: grid consumers in code +
controlled economy diffs.
OQ-015 | dip | DA_ template selection order (%token table CLOSED 2026-10-06g:
exhaustive regex over 22/22 .dip files yields exactly %m %y %s %t — no other
tokens exist) | open | W4: race module (20 E1 sites) — dialogue selection
loop in code (obj1 call-edge route, same class as OQ-021(b)).
OQ-016 | loop | campaign per-turn constants: income formula, pop growth
curve/cap, starting items, build order, expansion cadence, home placement
(all currently documented defaults in campaign.cpp) | open | W2: controlled
multi-turn RAM diffs on an idle empire (deep capture + NEXTTURN cadence law
75:318:293;115:600:440) isolate each channel; corroborate against
planitem/turnloop anchors.
OQ-019 | ships | per-ship design model (hull+gizmo inventory), sugar-cube->
hop scale, vendor Ship::init_global_gizmos cost hack, Orbital Docks effect
| open | W3: ship design screen code + its data reads (live image).
OQ-018 | audio | soundfx.txt header pairs semantics (2/10000, 3/45000,
1/65000); VOC u16@25=0x0911 + six zero bytes @36; race->theme mapping | open
| W3: audio init + theme selection code paths.

--- closed during v1 (kept here as a one-line index; evidence in archive and
docs/re/): OQ-001 .cob offsets | OQ-002 FLIC codec | OQ-007 CP437 |
OQ-008 loader control-flow model | OQ-009 AI data side | OQ-011 POINTER LAW
(scripts/r1_pointer_law.py 12/12 slots, gate 3q) |
OQ-017 .fnt codec + UI wiring.
