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
code. Low priority otherwise: rewrite is fresh-start-only. STATUS t50:
UNIFIED BASE pinned (rec = name-0x24 == IL walker, exact); mirror law
refined — 151/151 records byte-identical file vs live EXCEPT u16 +0x11
(single field; banked +0x68/+0x69 pair was this one u16 per-byte;
snapshot-pair delta constant 1472). Measured closed-field shapes: type
+0x14 <-> surface +0x18 bijection {(0,7)(1,11)(2,23)(3,45)(4,73)} 151/151
(upgrades sizeClassFor EVIDENCE to direct-file; rewrite code already
agrees, no change); +0x1a == surface+10 per class; +0x0c 0..49 = star
idx [inferred]; owner byte MIRRORED (8 distinct incl 0xFF). STATUS t53:
LOAD PATH CLOSED (r1mut-20261011-092253: HERMESSEN needle + 123-B verbatim
blob diff — records copied not parsed; pointer fields preserved byte-wise,
not rebuilt; sentinel noise baseline-controlled. r1-savestate.md t53).
Mutation route exhausted for MEANINGS; remaining semantics need play-state
mutation (channel words before turns advance) — parked, low priority
(rewrite fresh-start-only). Still open:
+0x0a/+0x20/+0x4a/+0x55 semantics, counter identity, star join,
packed-entropy. Save-writer string xref route dead round 1 (0x857de
zero refs, byte-pattern 0); one LEA-form probe budget remains. STATUS t80: star->planet JOIN CLOSED
both directions — pointer law star+0x2A/2E/32 u32 P -> planet NAME at
file offset P-2507337 (116/116 RESUME.GAM; banked-base P-K-0x24), and pool
membership u8 name-0x18 == star idx 138/138 incl. the 22 unlinked IV/V
rows (star-idx field t50 [inferred] UPGRADED verified). Star chain 96-B
records: live mirror byte-verbatim (50/50, single 12-B repair window on
Barataria tail) — copied-not-parsed re-confirmed on the star side. One
contiguous stride-123 planet pool 0x8e0e..0xd05c (t75 "0xaae2 chain" =
mid-pool entry, law stands). STILL OPEN: +0x0a/+0x20/+0x4a/+0x55
semantics, counter identity, packed-entropy regions (savegame.md t80).
OQ-021 | victory | end-ctrl threshold: vendor comment "over half" vs same
file's prose "two-thirds" — current default >1/2 | open | t73 dark-zone HIT
(docs/re/score.md): score strings ARE referenced — pool-relative immediates
0xf66/0xf7a at 0x2807b/0x280e7 (t72's zero-ref scan used wrong encoding AND
the site sits in the never-analysed dark zone 0x26b32..0x284bb); score
disproducer LAW percent = TRUNC(100*DAT_000482fb/T), T = hi-u16 DAT_00016143
(total stars, cross-checked vs FUN_00028fc0 stride-0x60 record loop);
presenter = eventwnd.cpp jump-table cluster 0x2c03a..0x2c0b6 (selector byte
mov al,[0x43510] @0x2c01d). Comparator itself: ZERO direct-address writes to
0x43510/0x4350c (8-encoding scan over 0x200..0x82bb0). t75: .gam-capture
route MEASURED DEAD (3 escalating fabrications all count 1/50 — load-side
star bitmaps are colony-derived, not .gam-owner-derived; BLOCKED.md T75
POST-MORTEM); harness itself proven (menu row (318,325) enters campaign).
t76: ALL 10 code readers of the star-owner block DAT_00013bc5 decompiled —
0x3ecb8 = AI attitude scorer, 0x44634 = two-race adjacency, rest UI/counting;
comparator ABSENT from image (confirms 06s at exhaustive scope). Corpus
adjudication: 745 banked slots, 0 with selector armed (idle scripts never
colonize). Now BLOCKED-USER-LEVEL (needs interactive original session with a
real colony past 50%, or original scenario at >50% owned). Default >1/2
stands (campaign.cpp:738 unchanged).
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
offers). RESIDUAL RE UNKNOWN (t77b, docs/re/diplomacy.md §10): the nonzero
relation-state ENUM semantics (which of 1/2/3 = war vs allied in the
session matrix; idle corpus contains ONLY 1, no injected transition) —
same closure class as OQ-021 (interactive original session). Two-party
main-branch law itself stays MEASURED (§7/§8) and implemented. | open |
W-B (option C hybrid): build only when ownership model lands; engine
build additionally awaits the state-enum capture above.
OQ-024 | loop | planet GOVERNOR assignment law (@0x38df0 branch of
FUN_00038ba4: '!' -> PROS += IND>>2, '"' -> RES += IND>>2; S6 line 45 read
+0x54 as a governor byte) | CLOSED t45 | FULL STATIC MEASUREMENT
(income-law.md S14): branch pinned verbatim from raw disasm incl. operand
resolution — the [0x743b9]>>0x18 "constant" IS item-table UPOP(35)
(row base 0x73e40+35*0x28=0x743b8; runtime value 1, 32/32 saves via
pointer law); accumulator identity cross-verified by the three doubler
blocks; exhaustive writer census (scripts/r1_0x54_writer_sweep.py: 23
writes/130 reads/61 SIB, zero XCHG/POP) shows the ONLY trigger path is
activator @0x38b26 storing the activated item id — queue+selected are the
SAME field, and 0/2810 corpus records (484 saves, r1_governor_census.py)
hold 33/34/35: the original only fires after a cell-SELECT of a special,
which our captures never contain — the static+corpus+runtime triple IS
the closing measurement. Code site: PlanetState::governor +
storedProsFor/storedResFor/usedPopFor branches (campaign.cpp/.h), pinned
by campaign_governor_law_t45; branch inert by default so timelines
unchanged (2024 Control t777 / 42 Extinct t583 / 13 Control t593).
OQ-025 | mapgen | star-position law at NON-default density | CLOSED
2026-10-12 t79 MEASUREMENT: the t78 3537/4950 "non-shell-slot" reading was
a MEASUREMENT BUG (2D hypot(x,y) is the xy-PROJECTION of a sphere point —
disc-scattered by geometry, not by the generator). Correct law, measured
on 3D radius r3=hypot(x,y,z) at name-0x14 with records gated idx==k +
planet-pointer-on-grid, in-play = chain head cut at slot DAT T: shell
radii FIXED (440,365,290,215,140,65,50) at every size; populations follow
the halving law (shell0 = T//2+1, then halve the remainder, shell6 keeps
the tail): T=15 -> 8/3/2/1/1, T=25 -> 13/6/3/1/1/1, T=50 -> 26/12/6/3/1/
1/1 (reproduces the 2026-10-06p battery table EXACTLY), T=75 -> 38/18/9/
5/2/1/2, T=100 -> 51/24/12/6/3/2/2; zero monotonicity violations in all
five arms (scripts/r1_t79_pos.py, runs r1size-{041459,042719,043229,
044658,045501} + r1deep-230146 control). Evidence mapgen.md §OQ-025; code
site: shellRadiiFor(n) rewrite/src/game/mapgen.cpp replaces the i%50 wrap
(measured wrong for T>50); test galaxy_density_ladder_matches_measured_
sizes pins per-size shell runs (108 tests 0 failed) | CLOSED |
Tail-residue note: gated chains exceed DAT T at low densities (records
stay allocated past the in-play cut — consistent with the t78 caveat).
OQ-020 | abilities | charge time for the 14 charged SA_ abilities (vendor
"%d day%s", no data file) — current default 30 turns | BLOCKED 2026-10-07
(static route exhausted: 7 negative probes — string table is runtime-loaded,
no image/cob presence, no static table, .dip has no charge param; docs/
BLOCKED.md) | T57b: ITEM ability supply side CLOSED verbatim (FUN_00039b6c + raw asm
slot-writer chain 0x38fc8..0x39003: top-up OR word+2 hi |= p3, p3=7
MissileBase/ShortWhopper, 8 LongWhopper, 0 TractorBeam (write skipped);
EBX 45/45/90/200 + p4 land in adjacent unattributed slots).
ITEM-table flag&4 population == exactly those 4 rows [verified battery]
— the ledger's '14 SA_' is the SPECIES-ability pool, separate object.
Decrement period still unmeasured: corpus census zero flag&4 slots
(T49 law); capture-gated. Default 30 turns stays (no rewrite code path).
income-law.md T57b;
T57c: USE path located (FUN_00039c10 tail 0x39ec4..0x39eeb: use=1 only,
counter=word+2 hi [SAR8 @0x39d61], write word+2 |= (c-1)<<8 OR-semantics
HAZARD flagged — top-up OR in FUN_00038f68 may make the per-use write a
no-op/mask, monotone-ammo reading NOT decidable statically; EBX-out 45/45/
90/200 consumer LOCATED = range gate x32 vs distance (0x39cae..0x39d40);
p4-out gates counter read; parallel countdown dword at ability-object+0x70.
Amass-wait formula UNMEASURED — OQ-020 stays OPEN, nothing wired.
remaining: obj1 call-edge of the help formatter, or
controlled-mutation capture; default 30 turns stays in force.
OQ-005 | shp | .shp shape-library codec (container CLOSED 208/208; grammar
CLOSED t61-t69; dims-location residue open) | open | CLOSED PORTION, cited:
control-byte grammar verbatim from raw asm FUN_0005caac 0x5cca3..0x5ce77
(shp.md S9); blit 5-arg law + stream=PAY+(tsz|u64dir[k-1])+0x18 (S12/S14);
runtime table UNIFORM delta{sel0:8, k>=1:24} zero exceptions across 4
verbatim-cached libs x 43 selectors (live-RAM S17, scripts/r1_shp_ramtable.py);
rows x-unbounded write-clamp, 2xH rows = appended animation frames. CODE SITE:
rewrite/src/formats/shp.{h,cpp} ShapeLibrary (container laws enforced,
blit-faithful clamp, dst-untouched transparency, 4096 dims cap: garbage dims
reported not allocated) + tests/test_shp.cpp; corpus MEASURED 208 libs/1557
recs/1484 decode-pass/185 clean (floors 1477/176 from scripts/r1_shp_unifiedlaw.
py). OPEN residue BLOCKED-USER-LEVEL (docs/BLOCKED.md t68): 80 records/31 files
(planind+3cfgnew span-undersized, cos_star simple-format, stragglers) + non-
verbatim .tmp/1starmap cached heads: in-record DIMS-FIELD LOCATION unknown;
closure class = human-verifiable drawn frame (R13 blocks self-verification);
blind sweeps FORBIDDEN (R2). Map draws documented circles; ShapeLibrary is a
validation asset (option C).
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
superseded/refined by (c) shells). (a) CLOSED 2026-10-12 t78 MEASUREMENT:
GALAXY_MORE (setup rect 7,381..122,472 -> (64,426)) cycles five densities —
Average T=50 / Dense 75 / Very Dense 100 / Vacuous 15 / Sparse 25 -> wraps
to Average (r1size-{033341,040859,041459,042719,043229,044658,045501};
T via pointer law DAT_00016143>>16 anchor-vote reader scripts/r1_t78_read.py;
labels via screenshot crops). Evidence mapgen.md OQ-012(a) section; code
site: --stars knob main.cpp (Options::stars -> MapConfig::starCount),
default 50 re-cited mapgen.h; test galaxy_density_ladder_matches_measured_sizes
pins sizes+connectedness+r<=441 envelope (108 tests 0 failed) | CLOSED (a-d) |
Non-default-T position law split out as OQ-025 (measured non-shell-slot at
T=100: 3537/4950 slot-radius inversions vs 0/1225 at T=50; KS against
uniform-in-disc NOT rejected (D=0.078 < crit 0.136), uniform-RADIUS
rejected (D=0.226) — lead only, n=1). Harness caveat banked: the stride-96
NAME-anchored chain walk runs past the LIVE run at low T (Vacuous 043229
slot 41: chain 100 vs slot DAT T=15, idx==k even past 15 — consistent with
either name-pool text or allocated-but-dead records; r1_star_table banked
tail-garbage precedent). t79 extractor MUST gate each record with the LIVE
test (planet-pointer slot name-prefix == star name, r1_star_table.py law)
and cross-check live count against the slot's own DAT_00016143>>16.
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
campaign_build_queue_law_oq016); POP-CAP LAW t29/t31/t33
closed-by-decompile+FULL-corpus ledger, t33-REPLACED numbers (466 saves x
every planet = 72066 samples, slot array at stored-ptr+0x88): recalc
+0x4a = clamp(0..100, +0x55 + MPOP sum over ALL active slots — Colony
Base INCLUDED, flags&4 skip is a measured no-op (rows 17/28/29/30 mpop=0))
holds 72066/72066 100.00%; the t31/t32 "+2 residual" and the skip-CB
model-C preference were HARNESS ARTEFACTS of the missing +0x88 offset
(income-law.md T33; old t31 numbers RETRACTED); +0x55 world-gen seed law
nb//3+5 verified instruction-level @0x37f84..0x37f9e (nb = non-barren
SURFACE cells counted by the 0x37e30 generation loop) AND on the corrected
array 98.6% corpus / 98.63% first-save-per-world (residual = scenario/
preset-row worlds via FUN_00037fc0, not replay noise — generation-state
claim RETRACTED, the array IS the generation output); Lush Growth
Bomb (item 37) completion = +10 once (+0x66 flag, 0x39212..0x39229) — rewrite buildPhase/constructor
REWIRED (capBase/surfaceCells seeded per star, storedCapFor() replaces
constant-25 default, pin test campaign_pop_cap_seed_law_oq016); t29b
terrain-mutation CLOSED by 40k consecutive-save sample census: surface
base classes change ONLY via item-36 Terraforming completion law + the
world-gen |8 rock event (rng%7==0 @0x37f5c); all remaining save-to-save
"class changes" coincide 1:1 with the slot-array pointer moving
(extraction aliasing, not gameplay writes); rng 0x7824f CORRECTED to
0..32767 (`SHR 16; AND 0x7FFF` @0x78269) — seed draw law is barren iff
rng < scaled(w0) @0x37e51..0x37ea4 with cumulative class chain
@0x37eb7..0x37ee0 [verified instruction-level] — t29b's preset-row ->
observed-histogram REFUTATION IS ITSELF RETRACTED t35 (the 51%-barren-on-
row-0 reading was the raw-array misalignment; corrected-array battery:
barren% tracks w0 monotonically on every row — row0/100 -> 99.997% pred/
98.9% meas, 40 -> 41.3/37.8/40.3%, 20 -> ~21%, 0 -> 0.7/0.2%; terrain
GENERATED not authored, 410 names multi-hash across runs) — T36 CLOSED
terrain GENERATION LAW end-to-end (call-site 0x23a64..0x23b49: size =
rng%5, row = rng%11 — captures are normal-mode draws (row hist uniform
0..10 incl 0, absent from special-mode table); header 0x37d80: +0x18 sums
0x744a8, +0x1a=+0x18+10, row clamp>=0xb->2; draw chain @0x37eb7 barren
test FIRST (seed counts exactly chain cells), cumulative scaled sums
(w*32768-w)/100, orbital ring class 1 WITHOUT drawing; classes 5..7
never occur, rock |8 separate): rewrite ctor GENERATES cellClasses per
planet through the identical integer chain on the banked LCG, capBase
= nb/3+5 of the generated grid, pin test extended (ring +10 all-1,
classes {0..4}|8, capBase exact) — rock bit CLOSED t38 (per-PLANET
rng%7 event, k-th item = k-th NON-rock cell, capBase = pre-mark count
VERIFIED 20-0, +0x1c = empty buildable count 71762/72066, class bonuses
CLOSED t37/t38 via cellClasses + T35 gating + rock-skip; income-law.md
T38); completion-law branches CLOSED t39 (rock-consume AND 0xF7 +
slot stays empty @0x39164; Terraform->class1 / Automation |=2 / LGB
+0x55+=10 branch table banked income-law.md T39b; pop==0 clears Colony
Base, 2 weak samples T39c; world-restart artifact filter T39d) — NUKE
LAW capture-gated -> docs/BLOCKED.md (Phase Bomb gizmo 70: static dead
ends T39e, zero device events in 13 runs, default NOT modelled, one-
run closing route written); HOME-PLACEMENT CLOSED t40 + DRAW MECHANISM
CLOSED t42 (one home/empire,
pop 2, Colony Base ONLY 153/157, CB cell = picker-uniform over non-rock
surface cells incl. barren (t42; the t40 rank 2..70 envelope was a
nonbarren-filter artifact, rank0/1 0/72 residual unpinned, never orbital), CB-class channel words == accumulator
153/157 incl. class4 RES0 gating re-confirmation, RES word 0 157/157 ->
colonyChannel grant is IND-compressed-only; scripts/
r1_home_placement.py; rewrite ctor + channel guard + pins) — built-item
CELL SELECTION stays open (T40(6): never |8 verified, prefix-from-0
refuted 0/2720, scenario scatter; rewrite lowest-free is a documented
default); COLONISED-PLANET ITEMS CLOSED t41 (every in-run colonisation
arrives with exactly one active Colony Base — 2 same-world earliest-
owned observations + 2720/2720 owned records corpus-wide carry a CB; pop
:=2, cap==seed+2 exact; dt-diff method found no flips (capture cadence),
earliest-observation method resolved; scripts/r1_colony_items.py; rewrite
seedColonyBaseColony + member worldLcg_); CB-CELL DRAW CLOSED t42 (picker
FUN_0003875c uniform among checker-legal empties; CB legal on all non-rock
surface incl. barren — income-law.md S12, KS PASS 72 homes; rewrite
drawCbCell); BUILT-ITEM CELL LAW CLOSED t43 (picker ignores caller slot —
all 16 EBX=0 build sites are uniform draws; rule G active-neighbour adjacency
CONFIRMED 0/362 final-state violations on continuous-x hex geometry from
fingerprint-anchored runtime tables — income-law.md S13; rewrite
drawItemCell); CARGO-SLOT CHAIN CLOSED t44 (placement = EVENT 4 +0xae
from EVENT 8 FUN_0003a880 coord->slot converter, rule-G re-gated — income-law.md
S13.5); AI LANDING-COORD CHOOSER OPEN -> docs/BLOCKED.md (dispatch-site
recipe banked; rewrite default = picker draw, observation-consistent);
PER-TURN BRACKET LAWS t56 (r1ad-20261011-110013 turns 0..8, full-151
window): channel words +0x44/46/48 are RATES not stockpiles (unchanged
8 turns idle, all worlds); growth tick measured at turn resolution —
player world counter +=1/turn == stored PROS, AI worlds +=2 (PROS+1 alien
term) 40/40 — t24 law re-verified fresh; AI homes queue at first End Turn
(0xFFFF->id, cell c1c -1 co-occurrence 4/4, ids banked un-named), player
home never queues. income-law.md T56; rewrite model structurally matches,
no code change. REMAINING: extreme-row leak MECHANISM FOUND t54, attribution open —
FUN_000238e8 copies 21+21 preset dwords (DAT_00088f90 weights 2..4,
DAT_00088fe4 1..10) into the per-planet gen buffer when control field 0x45
matches (income-law.md T54); T54b CLOSED file-provenance: tables are
COMPILED image constants (zero corpus signature hits), scenario-FILE
override hypothesis REFUTED — attribution is guard-field semantics only,
statics exhausted, rides t51 step 2 (fresh-scenario grid correlation).
Row0 98.9 vs 99.997, row10 c1 1.6 vs 0.006 unchanged. +2/+2 residual minutiae RESOLVED t33
(the paired +-2 class, the skip-CB model-C preference, and the live-RAM
read requirement are all VOID — one wrong array offset; rewrite UPGRADED
to model DIS incl-Colony-Base, income-law.md T33); DISPLAY-WORD LAWS t34
closed-by-stored-word measurement (2720 owned samples, full 466-save
corpus): +0x44 = max(1, trunc((v+1)^0.85)) 97.98% (banker's-round pow85
REFUTED at 56.99%; raw ties on this small-v corpus, compression law for
large v = S6 battery 138/139), +0x46 = raw accumulator 2720/2720,
+0x48 = max(1, PROS - pop>>2) 94.82% (decompile 0-clamp 40.99%); rewrite
storedProsFor REWIRED to the +0x48 word law (sole consumer needClassFor/
FUN_0003fec4; GROWTH INPUT CLOSED t37b: counter += stored +0x48 VERDICT
via scripts/r1_pros_growth.py turn-disciplined battery — raw eliminated
(Feculon II +3 vs cap-2), gated eliminated (5 rich-world GD rows), disp
0 losses; t24 raw reading was a tie capture, income-law.md T37b), harness
r1_income_law.py pow85->trunc + floor-1 words, now EXITS 0 (5/5 all
channels x 2 captures); residual 3+8 planet-names ⊆ seed-failure names =
preset-vs-generated boundary (income-law.md T34). Governor @+0x54 branch
never fires in corpus (byte always queue id) -> OQ-024 |
income law docs/re/income-law.md S6..S10; harness scripts/r1_income_
channels.py; chase-capture law = deep-schedule End-Turn clicks 511:67
every 15s, save ring read by MTIME. Governor @+0x54 CLOSED t45 (S14:
same field as queue; fires only on special-item cell-SELECT; 0/2810). T56: fresh-run AI opening queue = Agriplot (+0x54=0x01) 4/4 thin; word
+0x52 = CELL INDEX not item id (corpus 0..59>39, income-law T56). T58: LIVE queue chain observed to completion at 52 turns — Tonklinus
queued Transport Tubes (id 21 COST 10, completed ~obs20) then re-queued
Agriplot; 3 others held Agriplot; cheap-first pattern (not uniform-random,
consistent t28 selector); player never queued. income-law.md T58. RECALC
RESIDUAL CLOSED t71 (income-law.md T71, measured): byte-exact FUN_00038ba4
recompute reproduces stored +0x44/46/48 at EVERY timeline point (ck001/
020/060/100 of the 52-turn run, incl. across the Transport-Tubes completion)
AND on .gam-RESTORED slots (r1mut run) — 5/5 x all; the t55b acc=(0,0) vs
stored=(1,1) "open recalc term" and S6 52/139 score were harness-era
artifacts (pre-t33 raw reads), not original behaviour; species-modifier and
outside-recalc-init candidates have NO support; load-time staleness refuted
for observable values. Code site: rewrite/src/game/campaign.cpp channel
chain (lines 27/53/543 implement, pin campaign_channel_law_oq016); harness
r1_income_law.py --slot now searches ck/ AND save/ (t71 fix).
OQ-019 | ships | per-ship design model (hull+gizmo inventory), sugar-cube->
hop scale, vendor Ship::init_global_gizmos cost hack, Orbital Docks effect
| open | t15 PARTIAL: gizmo record law MEASURED (docs/re/ships.md §6:
FUN_00049074, stride 0x6a x 76 == file census exact, RESREQ BITMASK +0x33,
cat-switch copies Level->+0x52/56/5e/62 and generator Power->+0x66, cat>4
vendor error; design-screen edges + shp/tmp assets banked). Remaining: cost
hack (+0x46 writers), sugar-cube scale (+0x5e readers), per-ship inventory
(ship.bin law), Orbital Docks — per STATE second leg. STATUS t49: cost-hack
CLOSED re-confirmed t47 (generalized sweep, §9/§13); inventory law CLOSED
t46 (landed ship = active item-23 ring row, §10); Orbital Docks readers
banked t47-48 (upkeep/propulsion/range/step/fuel laws §12-13 — drives
RANGE=STEP=0, executor has NO drive->distance term). sugar-cube scale BLOCKED-USER-LEVEL t58: idle corpus zero ship activity
ever (t49 §14: 2260 slot-pair obs 0 state-4) AND scripted fresh campaign
to turn 52 zero too (t58: 565 slot obs, 0 state-4/0 owned/0 moved, 0
item-23 landings) — NO save-observable route contains flight; closure
needs original-hardware/manual-gameplay capture. Default [1,3]+immediate
arrival stands NOT contradicted.
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
