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
OQ-022 | audio | music span-vs-check contradiction: player FUN_00059c70
validates opened-file span CMP EAX,0x1d4d0 (@0x59cc5, error 0x1047 if above)
and reads 0x1d4c0-byte blocks (@0x59cef), yet theme00.raw span == 8,191,719
in ck005 | CLOSED 2026-10-07 t8 as "engine INACTIVE in captured states"
(docs/re/audio.md §3.4, decision-rule executed on FUN_000598fc head):
head disasm shows name composed into static buffer DS:0xa200c then a guard
([obj+0x48a6]==-1 || [obj+0x48aa]==-1 -> RET 0 @0x59984) that PRECEDES the
0x1d4d0-checked call @0x59987; buffer DS:0xa200c all-zeros in ALL 10 banked
saves (pointer law), tune selector DAT_00010ba0 == 0 in all saves. No
captured run ever feeds theme00 (or any name) to the checked open — the
"contradiction" cannot occur in observed states. EXPLICIT NON-CLAIM: what
serves menu music in the original remains unmapped (candidates: the startup
29-track load + an unmapped raw-play path); no rewrite default depends on
it — playMusic() loads theme00.raw directly == observed vendor state
(rewrite/src/ui/audio.cpp, comment cites §3.4). SPAN LAW byproduct CLOSED
(docs/re/datafiles.md §5: key/val overrides DAT_00010a74/0x10b82 count
[DAT_00010b96]=3, 3/3 exact disk sizes, cross-archive negatives repaired).
OQ-023 | dip | rewrite AI emits only the two-party threshold branch; original
additionally sends TRADE (DA 4/5/6) on turn%NEG_PLAYER_TURNS cadence behind
ownership share/multiple gates and THIRD-PARTY messages (DA 10, 7, 9 under
roll<80) — law MEASURED §9 (t14), engine NOT built (needs star/
lane/tech ownership tables in rewrite + UI affordance for incoming trade
offers). | open | W-B (option C hybrid): build only when ownership model
lands; no RE unknowns remain for this item.
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
docs/re/economy.md §4 [spec prose lost to probe regen; REBUILT with
re-verified predicates at docs/re/income-law.md §4, t25]. Rewrite: economy.h requiresAvailable() (gatedBy
deleted), buildPhase gate+surface-cap, attack/defense/drive/bestDriveRange
upgraded; 3 pin tests (89 tests 0 fail); gate green incl. seed-2024 Control
t145. Per-cell planet model NOT in rewrite — terrain/nuke laws documented,
wiring parked (STATE.md).
OQ-015 | dip | DA_ template selection order | CLOSED 2026-10-08 (t12-t14):
full chain MEASURED — chooser FUN_00044a44 return == ACTIONS pool idx (file
order, docs/re/diplomacy.md §7); DIPVALUES field map via positional loader
FUN_00044290 (§8, pool-base law verified); trade gates + cadence REKEY (§9:
turn % NEG_PLAYER_TURNS == 0; rungs BREAK_ALLIANCE+10 / BREAK_ALLIANCE /
START_ATTITUDE+20 vs attitude; share/multiple floors 0.9/2.0, 0.9/1.6,
0.85/1.7; min counts 5/3/5; state==3 auto-pass); %token sources CODE-
confirmed (§5). Code sites: rewrite/src/game/diplomacy.cpp decideDipAction
upgraded to STRICT thresholds (t13) + §9 scope comment (t14). Pins:
dip_action_chooser_law_oq015_t12, dip_strict_threshold_oq015_t13,
dip_trade_predicate_bytes_oq015_t14 (95 tests 0 fail). %token table CLOSED
2026-10-06g (regex census 22/22 files: exactly %m %y %s %t). Trade/third-
party offer ENGINE wiring in rewrite = build work with law in hand ->
OQ-023 (not an RE unknown).
OQ-016 | loop | campaign per-turn constants: income formula, pop growth
curve/cap, starting items, build order, expansion cadence, home placement
| open (sub-laws CLOSED: income channel law 138/139 battery + t22 pin test
campaign_channel_law_oq016; POP GROWTH CURVE t24 closed-by-measurement
pop==+0x42 UPOP dots, counter-threshold-50, colonise :=2, alien +1-boost
[verified chase capture r1deep-20261007-224831 slots 45->46]; BUILD QUEUE
+ FULL AI SELECTOR LAW t28 closed-by-decompile+live-match: queue 1/planet,
acc += stored IND while pending (0x39005), complete acc>=COST (0x390a3),
selector on queue-empty planets only (caller 0x3ead6), candidates surface
rows 0..21 minus Colony Base, first ABSENT picked immediately unless
COST/IND>=70 aborts scan to best PRESENT (need-class column FUN_0003fec4,
d66 roll; income-law.md S9) — rewrite buildPhase REWIRED (pendingItem/
buildAcc, instant ind_ deduction removed) + pin test
campaign_build_queue_law_oq016); POP-CAP SEED LAW t29
closed-by-decompile+40318-sample-ledger: capBase = nonbarren_surface/3 + 5
written to +0x55 AND +0x4a at world-gen (0x37f84..0x37f9e), nonbarren ~
Binomial(ncells, 1-w0) with MEASURED preset table 0x744f4 {100,50,20,0,40,
20,40,20,40,20,0} and cell counts 0x744a8 row sums {7,11,23,45,73} (live
+0x18 exact); recalc +0x4a = clamp(0..100, capBase + MPOP sum skipping
flags&4 AND Colony Base) holds 38772/40318, residual purely +2 on 39
planets (open minutiae); Lush Growth Bomb (item 37) completion = capBase
+10 once (+0x66 flag, 0x39212..0x39229) — rewrite buildPhase/constructor
REWIRED (capBase/surfaceCells seeded per star, storedCapFor() replaces
constant-25 default, pin test campaign_pop_cap_seed_law_oq016); t29b
terrain-mutation CLOSED by 40k consecutive-save sample census: surface
base classes change ONLY via item-36 Terraforming completion law + the
world-gen |8 rock event (rng%7==0 @0x37f5c); all remaining save-to-save
"class changes" coincide 1:1 with the slot-array pointer moving
(extraction aliasing, not gameplay writes); rng 0x7824f CORRECTED to
0..32767 (`SHR 16; AND 0x7FFF` @0x78269) — seed draw law is barren iff
rng < scaled(w0) @0x37e51..0x37ea4 with cumulative class chain
@0x37eb7..0x37ee0 [verified instruction-level] — BUT the preset-row ->
observed-histogram mapping is REFUTED (13-run first-save battery, ~70k
cells: preset 0 row [100,0,0,0] predicts all-barren yet preset-0 planets
show 51% barren; no monotone reading of 0x744f4 fits, so the generation
row is NOT the save-time +0x16 row) — per-cell terrain SHAPE therefore
stays OPEN and rewrite does NOT model cell classes — REMAINING: terrain
weight-row provenance (scenario data-file lift), nuke event law,
home-placement verification, +2 residual minutiae) |
income law docs/re/income-law.md S6..S10; harness scripts/r1_income_
channels.py; chase-capture law = deep-schedule End-Turn clicks 511:67
every 15s, save ring read by MTIME.
OQ-019 | ships | per-ship design model (hull+gizmo inventory), sugar-cube->
hop scale, vendor Ship::init_global_gizmos cost hack, Orbital Docks effect
| open | t15 PARTIAL: gizmo record law MEASURED (docs/re/ships.md §6:
FUN_00049074, stride 0x6a x 76 == file census exact, RESREQ BITMASK +0x33,
cat-switch copies Level->+0x52/56/5e/62 and generator Power->+0x66, cat>4
vendor error; design-screen edges + shp/tmp assets banked). Remaining: cost
hack (+0x46 writers), sugar-cube scale (+0x5e readers), per-ship inventory
(ship.bin law), Orbital Docks — per STATE second leg.
OQ-018 | audio | soundfx.txt header pairs semantics (2/10000, 3/45000,
1/65000); VOC u16@25=0x0911 + six zero bytes @36; race->theme mapping |
CLOSED 2026-10-07 (all three sub-questions measured). (1) Header pairs:
col1=voices/band, col2=size threshold; play path bands by FILE SIZE via
span table; ck005 proof 327/328 spans == disk sizes; voiceBand() + test
audio_voice_band_law_oq018. (2) VOC header byte map 15/15: ver@20 0x1A,
type@24 0x1F, u16@25==0x0911 CONSTANT, u16@27==size-31, u32@30 rate
(22050x14 + bullet.voc 11025/stereo), bytes36..41 reserved zero; audio.md
§2.1; voc.cpp field pins. (3) race->theme map DOES NOT EXIST: global tune
selector DAT_00010ba0 has exactly ONE writer image-wide (0x21309, MOV
-1 under option gate inside music.txt loader FUN_00020fd4; get_xrefs_to
census 14 refs/1 write + SIB-aware 89/C7 store scan of state fields
+0x48a6/+0x48aa: only 0/-1 state stores); DAT reads 0 in all banked saves
(ck005/ck010 x5 runs) == music.txt track 0 == theme00.raw — the path
playMusic() takes (audio.cpp init cited); test audio_tune_selector_oq018
pins both sites; audio.md §3.3. Discovered follow-up filed as OQ-022.

--- closed during v1 (kept here as a one-line index; evidence in archive and
docs/re/): OQ-001 .cob offsets | OQ-002 FLIC codec | OQ-007 CP437 |
OQ-008 loader control-flow model | OQ-009 AI data side | OQ-011 POINTER LAW
(scripts/r1_pointer_law.py 12/12 slots, gate 3q) |
OQ-017 .fnt codec + UI wiring.
