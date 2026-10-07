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
"%d day%s", no data file) — current default 30 turns | BLOCKED 2026-10-07
(static route exhausted: 7 negative probes — string table is runtime-loaded,
no image/cob presence, no static table, .dip has no charge param; docs/
BLOCKED.md) | remaining: obj1 call-edge of the help formatter, or
controlled-mutation capture; default 30 turns stays in force.
OQ-005 | shp | .shp pixel codec (container CLOSED 208/208) | open | W3 ONLY:
exe shape loader via call graph + live image. Blind static sweeps are
FORBIDDEN (docs/REFUTED-ROUTES.md R2). Map currently draws documented
circles.
OQ-006 | audio | sample rate/channel count of 77 headerless .voc + 29 .raw
(current default 22050 mono) | CLOSED 2026-10-07: DEVICE rate = 22050 MEASURED
— open chain PUSH 0x5622 @0x4f690/@0x4f90b -> CALL 0x68816 -> unique edge
0x68882 -> rate setter 0x6e000 stores [obj+0x3c]; constructor default 11025
@0x6df3e always overwritten; docs/re/audio.md §3.1; rewrite cites chain
(ui/audio.cpp, formats/voc.cpp), pin test audio_open_rate_measured_oq006.
Channels: no vendor channels field in the chain; mono-by-convention,
rewrite stereo mixer documented as presentation choice.
OQ-004 | tables | which tables the exe loads; .tsv container grammar | CLOSED
2026-10-06s: docs/re/datafiles.md (pool-relative immediate law, 337 verified
sites; full census w/ referrer addresses; ascend02 .bin/.tsv loaded via RAM
name table @0x250c1c from .cob TOC, NOT via exe literals; .cob grammar
u32 N + N x 50B names + N x u32 offsets, ascend00 54/54 md5 round-trip).
Gate: scripts/cob_probe.py 3i2. Field semantics of the tables stay OQ-010.
OQ-012 | mapgen | (a) new-game size options (labels baked in 3cfgnew.tmp
glyphs) — REMAINING OPEN. (b) CLOSED 2026-10-06o:
pps ~ U{1..5} measured over 250 systems x 5 campaigns (chi2 2.84, 4df,
p~0.58; rewrite uniform_int(1,5) mapgen.cpp:120 verified matching).
(c) CLOSED 2026-10-06p: position law = FIXED RADIUS SHELLS BY TABLE SLOT x
random direction (r(k): 440 k0-25, 365 k26-37, 290 k38-43, 215 k44-46, 140
k47, 65 k48, 50 k49 — exact float identity across 5 campaigns, 0 inversions;
no type/position coupling: rho(u1C,r3)=+0.02, rho(u25,r3)=+0.03 over 250
stars; sub0 rho -0.59 is confounded by k-ordering. No min-separation enforced
(min observed 24.4). Rewrite UPGRADED 2026-10-06q: mapgen.cpp placement =
shell schedule x uniform angle (kShellR mapgen.cpp:93; starCount default
75->50 at mapgen.h:50 + campaign.h:57; rejection sampling + capacity check removed;
test galaxy_positions_follow_measured_shell_law pins radii/populations;
84 tests 0 failed; gate 4b seeded seed-2024 campaign still wins Control t148;
mapgen.md §4.1 rewritten with scale note).
(d) CLOSED 2026-10-06k (extent = stars on sphere r~440, orbit-pair retraction;
superseded/refined by (c) shells) | open | (a): setup-screen live RAM state from
r1ad captures (options UI lives in RAM at pointer-law base).
OQ-013 | rules | restree variant block: field0 (0..4) semantics; main tree
vs variants vs union in play (current default union) | CLOSED 2026-10-06r |
IN PLAY = the 66 MAIN ROWS ONLY; variants are never loaded, field0 is dead
runtime data (file-level meaning still unknown, stated as residue). Evidence:
loader FUN_00046870 (ascend_restored.bin:0x46870..0x46ae9; found via the sole
u32 -> payload-0x85014 'restree.txt' string site at guest-phys 0x205d23;
2 callers: new-game init FUN_00022ce4, save serialize FUN_00046fa0) bounds its
row loop by the count line (66, cap 100) => rows 66..105 never parsed. Census
scripts/r1_restree_law.py over 27 slots x 13 captures (turns 0..9): main 66/66
in every slot, variants 0/40 under both '^' and space spellings (RAM stores
space-substituted names; loader rewrites '^'->0x20 at 0x46a10). resume.gam
holds the same stride-75/66-row table, 4950 B byte-identical to fresh RAM =>
static definition data, not progress. Record map + the MEASURED COST LAW
(runtime u16@+62 = file_cost x (2row-20) for row>10, clamp 65000; reproduced
66/66 from instructions 0x4691d..0x46a15; row 65: 300 -> 33000):
docs/re/research.md §6. REWRITE UPGRADED: Tech::runtimeCost() (research.h),
available() default includeVariants true->false, campaign.cpp charge :283 +
selection :271/:554 on runtimeCost; tests
research_runtime_cost_law_measured + research_variants_are_not_in_play (86
tests 0 fail); gate green; seed-2024 campaign still wins Control t145.
OQ-014 | rules | planitem unknowns: REQUIRES=254 (Interstellar Trucking),
count triple 22/9, the 11x4 + 5x15x2 grids, item FLAG bits | CLOSED
2026-10-07: loader FUN_00037fc0 + checker FUN_0003830c + init FUN_00037d80
decompiled from the restored image; record layout stride 0x28 (IND@0 RES@+1
PROS@+2 MPOP@+3 UPOP@+4 REQUIRES@+5 FLAGS u16@+6 COST u16@+8 name30@+10)
byte-exact 39/39 vs file in 2 captures (item table phys 0x2b5f50, pointer-law
index member = B + 0x82BB0 + X re-derived — naive B+X is 0x88 off). 254 =
DEAD item, not ungated (checker: avail iff req==0xFF || (req<count && owned),
count DAT_00074744==66). 22=SURFACE count (RAM 4/4), XOR placement law
(slot<cells) XOR (item<22) for idx<=30, specials exempt; 9=ORBITAL (rows
22..30). Grid C row sums = size-class surface cells {7,11,23,45,73} — live
+0x18 law 2650/2650 records x 17 captures, cap==cells+10 zero violations;
grid A = per-type terrain mix (FUN_00037d80), grid B = ring/angle ranges
(FUN_000395c4/0x3965c) + neighbour rule; MPOP gates demolition, UPOP gates
start (FUN_0003830c/0x38840); FLAG bits consumer-mapped, bit4 set by NO
shipped row, bit7 no consumer; RAM bit census == file (39/39). Full spec
docs/re/economy.md §4. Rewrite: economy.h requiresAvailable() (gatedBy
deleted), buildPhase gate+surface-cap, attack/defense/drive/bestDriveRange
upgraded; 3 pin tests (89 tests 0 fail); gate green incl. seed-2024 Control
t145. Per-cell planet model NOT in rewrite — terrain/nuke laws documented,
wiring parked (STATE.md).
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
(partial 2026-10-07 t3: col1 = voices-per-band, col2 = ascending band SIZE
CAP with n*col2 region sizing Σ=215000 [verified; file census: 77/86 .voc
resolve, zero >65000, consistent with threshold-band selection by first
c44[i]>=scalar]; earlier "tick delta" and "byte-cap refuted" notes
retracted — see audio.md §3.2 SCALAR IDENTITY. REMAINING: scalar identity
(sample-span vs timer-span; no disp32 writers on tables 0x102a0/0x102a4 —
next probe callers of FUN_0002086c + writer of audio-obj+0x108), VOC
u16@25, race->theme map).

--- closed during v1 (kept here as a one-line index; evidence in archive and
docs/re/): OQ-001 .cob offsets | OQ-002 FLIC codec | OQ-007 CP437 |
OQ-008 loader control-flow model | OQ-009 AI data side | OQ-011 POINTER LAW
(scripts/r1_pointer_law.py 12/12 slots, gate 3q) |
OQ-017 .fnt codec + UI wiring.
