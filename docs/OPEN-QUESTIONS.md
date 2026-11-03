# OPEN QUESTIONS — live closeout ledger (v2, strict-close)

Statuses: open | CLOSED. Nothing else. A question closes ONLY with cited
evidence (Ghidra address / extracted-file offset / pointer-law guest-phys
measurement from a named capture) + the rewrite site upgraded + docs/re/
updated + a gate or test pin. FINAL-DEFAULT is not closing (docs/GOAL.txt).
v1 full evidence text for every row: archive/ralph-v1/OPEN-QUESTIONS.md.
Do-not-retry prohibitions: docs/REFUTED-ROUTES.md.

Format: ID | area | question | status | what closes it (in-hand route)

OQ-010 | rules | combat damage APPLICATION: hit probability, shield
subtract-vs-absorb, overkill, firing order | CLOSED t89 (all four named legs
cited + rewrite code site changed + 109-test pin; see STATUS t89 at row end and
docs/re/combat.md S2d..S2j) | W1: click-diff capture
turn-boundary deltas (turn counter u16 phys 0x254e10), then Ghidra xrefs on
the reader/writer functions (attribution: batmode/cosmos ranges,
work/attribution.tsv). Device constants are already data-verified (gizmos
damage 1..13, shields 1..5) — the application code is the target. Static
route bounded 2026-10-06: payload has ZERO disp32 accesses at orbit offsets
+0x57/+0x5f (scan: 2 bogus hits, both outside code ranges); shape tie found
(FUN_00025604 stride-constant table 0x60/0x7b/0x27 == live-measured record
families, docs/re/r1-savestate.md). STATUS t85b (first long original-game
capture banked: turns 37..1131, war on Minions t887): combat RAN 244 turns
but autosaves sample turn boundaries only, so mid-resolution damage never
lands in a sample. t85b also fixed the combat analyzer to STREAM the 4.3 GB
jsonl (measured 290 MB peak; the load-everything version was OOM-killed on
this data). STATUS t85c (CORRECTION + testimony): the t85b "ZERO AI-ship
events" claim was a FILTER ARTIFACT — it discarded free-record owners
(65535), which is exactly what a destroyed ship record looks like at the
next boundary sample. Corrected presence-law census (scripts/
r1_t85c_focus.py): 9 owner->free DELETIONS banked — 4 Minion-owneed
(slot12 t888 = the war-declaration boundary itself, slot8 t902, slot5
t910, slot0 t1018) and 5 player-owned — plus slot flips (0<->2) that are
free+realloc between samples, not captures. Player testimony CONSISTENT:
"Minions only had one ship for me to destroy, it didn't shoot back" —
Minions fielded exactly 4 ships in 1100 turns (slots 0,5,8,12) and all
four died in the war window; zero-shot-back matches a crewed-population/
power edge. Deletion-vs-turn-boundary correlation is now banked, but the
damage APPLICATION law itself (hit prob, shields, shields vs power) is
still unseen; closing route unchanged (in-battle recording or static
application-code site). STATUS t85g (t1253 sitting, FIRST mid-turn damage
frames banked): MAJOR ADVANCE, still open. MEASURED both-sides field law:
ship +0x8c = INTEGRITY (design constants d2/d4/d6=20, d12=40 at peace;
volley-step decrements 20>12->4>0 observed on 9 Ungooma slots; death at
+0x8c==0 then owner->free per presence law), +0x88 = MOVES (decrements
1..2/sample, recharges at boundary, never feeds death). Return fire
VERIFIED: player slot14 40>38>36>34 same frames ("fired back once or
twice" = exactly this). STATIC: exhaustive write census of [reg+0x8c]
finds ONE subtract in the image — 0x4d1ea sub [esi+0x8c],[edi+0x4a] inside
combat loop 0x4d075..0x4d20e: per-target distance-squared (shooter xyz
+0x9e, cross-confirms xyz law) vs attacker field [edi+0x3a]<<5, in-range
-> call 0x4b740 -> integrity subtract. Damage values vary per hit (steps
{16,8,12,13,7,4,3}) so [edi+0x4a] is a per-shot combat-object value
(ship records read +0x4a=0 at boundary). UNSEEN: shields subtract-vs-
absorb (candidate: inside 0x4b740), hit probability, firing order. Next:
static decode 0x4b740 + 0x4d075 body (docs/re/combat.md S2). Evidence:
scripts/r1_t85g_sitting.py + r1_t85g2_slots.py over live-timeline.jsonl
t1244..1254; rewrite combatPhase stays the documented aggregate default
(OQ-010 unclosed => no code change). STATUS t86 (W6-A1 static, no capture):
SHIELD-LAYER IDENTITY CLOSED — [reg+0x90] writer census
(scripts/r1_t86_write_census.py, objdump-verified; control: re-finds the
0x4d1ea +0x8c subtract among 10) shows +0x90 charged from CAT==1 (shield)
gizmo Level field design[+0x56] at 0x49f15/0x4a71f, zeroed at fire-loop entry
0x4a6a6 and by flag [ship+0x9c]&8 at 0x4a73a, +0x88 = gizmo-power sum via
0x4a99c (init 0x4a76c). MAJOR CORRECTION to t85g S2: [edi+...] is the static
GIZMO/DESIGN table 0x7650c + 0x6a*current_gizmo (EDI set at 0x4cddc; table
names byte-verified in slot-48 RAM: Mass Barrage Gun..Hyperfuel), NOT a
battle-built attacker snapshot; 0x4d075/0x4d1ea are cases of gizmo-mode
dispatcher 0x4cd90. Damage per hit = design[+0x4a] (no roll at that site).
STILL OPEN: hit probability, firing order, 0x43a4c star-defense contribution,
exact gizmos.txt column->+0x4a map (t86 check matched 1/76 on a strict
5-field equality — see combat.md S2d caveats; power/range/level legs verified
weapon-side, level verified shield-side). No rewrite change (strict-close).
STATUS t87 (W6-A2 static, no capture): COLUMN MAP CLOSED 76/76 + TWO
IDENTITY CORRECTIONS. Tool scripts/r1_t87_gizmo_table.py: loader
FUN_00049074 store sites + runtime join (save/50.sav B=0x1bf4d8, member=
B+0x82bb0+X) -> file cols Cat/Power/Range/Level/NumUses/Industry/Special1/
Special2/ResReq/flags == design +0x32/+0x36/+0x3a/+0x3e/+0x42/+0x46/+0x4a/
+0x4e/+0x35/+0x33, ALL 76 rows + 76/76 names (exit 0). CORRECTION: +0x4a =
FILE Special1 NOT Industry (t86 75/75 coincidence); Cat jump table 0x344b0
copies Level->derived +0x56 (shields) etc. Case table decoded (combat.md
S2f): dispatcher 0x4cd90 = SPECIAL-GIZMO ACTIVATION (13 singleton cases,
cl==active gizmo id: 0x24 Recaller, 0x26 Smart Bomb AT-WAR-gated area
0x4b740, 0x2e Catapult xyz-negate, 0x35 Cannibalizer self-damage, 0x3a
Repair clamp at NEW field +0x98=max integrity, 0x41 Replenisher restores
NumUses slot[+1], 0x45 Invulnerablizer sets +0x9c bit 0x10 (the absorb-null
flag identity), 0x48 Self Destructotron = the t85g "combat loop" 0x4d075,
0x4b Hyperfuel +40 moves; mode==1 charges power first at 0x4d594). CAT-0
guns have NO case here => generic gun fire is in the other 0x4b740 callers
(0x4bb56 nearest, t88). 0x43a4c identity CLOSED: NOT star defense — the
DIPLOMACY-ON-ATTACK handler (attitude -= 10*(word[0x13bc4]+1), doubled if
state==3, at-war returns 0, sets attacked-bitmap bit at
[[edi+2]>>16+0x48304]). Row STAYS OPEN (strict-close): hit probability still
no roll seen, firing order = caller 0x4a3c4 chain + generic-gun caller
0x4bb56 undecoded. No rewrite change.
STATUS t88 (W6-A3 static, no capture): GENERIC VOLLEY PATH FOUND, FIRING
ORDER CLOSED, HIT PROBABILITY ANSWERED BY CITED ABSENCE. 0x4bb56 is inside
cat-0 handler 0x4b8e4 (prologue verified; sole caller 0x4a3a0 in dispatcher
0x4a360, which t87 mislabelled: it CATEGORY-dispatches design[+0x32] ->
cat0 0x4b8e4 / cat1 0x4c794 / cat2 0x4ca50 / cat5 0x4cd90, and DEC slot[+1]
NumUses at 0x4a390 on mode==1). FIRING ORDER: loop 0x4a5c1 iterates ship
gizmo slots +0xab stride 7 in STORED order, fires EVERY cat-0 weapon
(set [ship+0x63], call 0x49f28->0x4a360); stance setter 0x4a55c writes
[ship+0x67]/[ship+0x68]=target. Gun law (combat.md S2g): same-system gate
(+0x58==4 && +0x59 equal), range gate dist<=design[+0x3a]<<5 (+0x9c&4
doubles), damage=design[+0x52] (derived Level), 0x4b740 two-layer clamped
absorb shield+0x90 then hull+0x8c, death 0x49d2c, power charged at 0x4c614.
HIT ROLL MEASURED NEGATIVE: zero rng edges in [0x4a360,0x4f097), LCG
constant unique 0x7825b, full-body reads of 0x4b8e4/0x4b740 show no
comparison of a random value — damage is deterministic per shot (matches
t85g steps 40>38>36>34). Row STAYS OPEN (strict-close): closure needs the
rewrite combatPhase UPGRADE at a cited code site (next task t89). Tool
scripts/r1_t88_caller_census.py exit 0.
STATUS t88a (audit pass, same day): S2g INSTRUCTION-RE-VERIFIED (dispatcher
0x4a360, gate 0x49f28, volley loop 0x4a5c1, gun handler 0x4b8e4 gates +
damage select + call 0x4bb56, hit path 0x4b740 whole body — all literal,
combat.md S2h) + census tool re-run RC=0. NEW: COMMIT LAW CLOSED — of the
13 callers of 0x49f28 exactly TWO pass mode==1 (0x25560 gun-commit, 0x25570
->0x39c10 ability-commit, both inside player-command-exec 0x2547c after the
0x41260 movement resolver; ah>=4 = assert trap 0x2a438); every AI-attack and
volley path is a mode-0 dry-run (no DEC uses, no power charge). Self-destruct
sites 0x4d191/0x4d2dd pass the dispatcher's mode variable (0x4d2dd gated
at-war [edx+0x12fd6]==2). Row STAYS OPEN: all named residuals answered by
cited absence/measurement, contract closure still needs the rewrite
combatPhase code-site change (t89). STATUS t89a (scoping pass, no code
change — session budget exhausted mid-task, docs/BLOCKED.md t89a): the
"does the rewrite have a combat phase" gate PASSED — Campaign::combatPhase
exists rewrite/src/game/campaign.cpp:1247-1322 (advance() :1376); upgrade
target = attackScore :1204-1224 / defenseScore :1226-1240 + the noise draws
:1275/:1305-1306. Aggregate-model constraints and the exact honest delta
(SUM-of-Levels volley replacing MAX per 0x4a5c1 every-weapon law; noise =
uncited v1 abstraction vs S2g measured-negative determinism — removal
re-diverts rng_ and requires PLAYTHROUGH regeneration), full scoping in
docs/re/combat.md S2i. Row STAYS OPEN (strict-close: the code-site change
plus its pinning test is the closing measurement). STATUS t89 (CODE task,
CLOSED same session): all four named legs carried to the rewrite at cited
code sites — attackScore volley = SUM researched cat-0 Levels NumUses!=0
(0x4a5c1 every-weapon law + design[+0x52]==Level t87 map) replacing v1 MAX;
defenseScore = HULL layer only (pop/10 + fortify), the v1 shield-addend
refuted by hit-path 0x4b740 (shields never join the defense total, they
clamped-absorb at 0x4b7c4..0x4b7d1 and spill); combatPhase noise draws
REMOVED per the measured-negative hit roll (S2g/S2h) — capture iff
volley - MIN(volley, shieldChargesFor(b)) > defenseScore; shield charges =
SUM researched cat-1 Levels (charge law 0x49f15). Sites:
rewrite/src/game/campaign.cpp (attackScore/defenseScore/shieldChargesFor/
setAllTechs/combatPhase) + campaign.h (absorbSplit mirrors 0x4b7c4 clamp) +
tests TEST(campaign_combat_law_oq010) (file sums 49/16 re-extracted,
full-vs-no-tech volley delta == 49, absorb/clamp/spill edges, seed
determinism 40 FFA turns). MEASURED closing evidence: 109 tests 0 failed;
rng_ re-diversion regenerated timelines — 2024 Control t777, 42 Extinct
t581, 13 Extinct t503, 1/2 Control t842/t677, all FINITE in the 1200 gate
budget; PLAYTHROUGH.md regenerated (stale 600 echo-literal fixed). Caveats
carried: aggregate model only (S2i) — per-ship slots, same-system gate
0x4b982, range gate 0x4ba57, per-shot power accounting NOT modelled; a
per-ship model (OQ-019) must re-use S2d..S2h literally.
OQ-003 | gam | .gam full record map + field meanings; packed entropy regions
| CLOSED t181 2026-10-28 (measured disclaim; was the row's own decision option
"let the three-class diff run first") | W1 joint: planet records already joined file<->live RAM 151/151
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
STATUS t81: counter identity + two field meanings CLOSED by measurement —
growth law revalidated 90/90 owned transitions over the full 20-slot
r1deep timeline (model incl. alien +1 at PROS<4; scripts banked), live
global votes DAT_000066e4=50 (20/20) and DAT_0007458e=0, and the +0x4a
equation re-measured: +0x4a = POPULATION CAP (clamp targets @0x393f0/
@0x38f03), +0x55 = natural-population SEED (uniform +2 residue = the
banked event-50 bonus, L622). +0x0a gets an explicit UNMAPPED verdict
(seed-band bytes churn live even unowned; not read by recalc). OQ-003
residue now = packed-entropy regions only (star-map heads class, shared
with OQ-005 blocked closure). Rewrite growth block already implements
this law exactly — evidence upgraded, no code change (income-law.md t81).
PLAIN (t179): The save-file format is decoded; the only unread parts are
byte regions that look random. Working theory: the save writer copies dirty
memory, so some regions are leftover uninitialized RAM, not game data. The
test (no play needed): compare the same region across title-screen boot slots
(before any game exists), fresh-game saves, and long campaign saves - data
that only stabilizes after play is play-initialized; churn in all three
classes is true residue and gets disclaimed. Recent player saves also help if
captured through the watcher in straddling pairs (one save before, one after a
state-change turn). Low priority: the rewrite starts games fresh and never
loads originals. DECISION OPTIONS: accept "unknown, disclaimed" as closure,
or let the three-class diff run first (queued t181).
STATUS t181: THREE-CLASS DIFF RUN — CLOSED BY MEASURED DISCLAIM.
scripts/r1_t181_banddiff.py (exit 0) locates every save block in live RAM
(multi-block image: per-region deltas 0x2b6718/0x25676f/0x263fb1/0x276b0c/
0x2d3a0e; file==boot 100% per region) then diffs classes at the LOCATED
addresses: ENTROPY-BAND boot-vs-played 432/2048 = 21.1% stable while HEADER
99.5 / S-TABLE 93.8 / POOL 87.2 / BLOCK11200 100.0 (play-counter deltas
0xffffff00 x22, 0x02000000 x21 arithmetic); baseline oct14 slot at the band's
address (member 0x2e7a0e) reads 0/16 nonzero; band deltas between same-world
saves are asymmetric-zeros (54/34) at identical offsets; not compressed
(0/2316 blocks >=6.8 b/B, max 5.60); float-shape REFUTED (13%/9% sane f32 vs
3-5% pool control). Game runs without it x3: golden resume.gam band span =
133 nonzero bytes yet boots (golden tour §), RESUME-014 EOF 0x12753 has no
band region yet played, tail varies 776..14,561 nonzero by session.
EVIDENCE docs/re/savegame.md §t181 (class table + probe-bug correction:
mem.find(b'') artifacts WITHDRAWN; title slots DO carry the on-disk world —
0x25996f/0x25a76f located needles). What the scratch WAS stays UNNAMED
(live-UI-trace class; the disclaim does not depend on it — non-claim banked).
CODE SITE: rewrite unchanged — fresh-start-only row, nothing loads originals.
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
stands (campaign.cpp:738 unchanged). STATUS t85b: the first
long played capture (turns 37..1131, player at 27 systems_any / 26
systems_full at the end) banked DAT_482fb every slot and the selector
NEVER armed — DAT_482fb max 23/50, so >1/2 on DAT_482fb is CONSISTENT
(never contradicted), while systems_full crossing without arming shows
systems_full is NOT the comparator variable. Full census docs/re/score.md
S6. STATUS t85c (testimony): player confirms NO Control-victory screen
ever appeared, through t1131 — CONSISTENT with >1/2 on DAT_482fb (max
23/50 = 46%, never crossed). The score-screen percent discriminator is
DEAD: the player UI has no score screen (buttons = Planets/Ships/
Research/Special Ability/Species; the disproducer is an internal
readout gated by the nougat.lf file-probe flag, docs/re/score.md S7/S8). Replacement closer:
continue the live campaign past boundary DAT_482fb >= 25 and observe
whether the 0x2c01d end-ctrl arm fires — banked max is 23 and the player
is still expanding, so this may close passively during normal play.
STATUS t85g: passive test continues; NEW NEGATIVE DATA sharpens the
comparator hunt. DAT_482fb OSCILLATES independently of territory:
t1157=8 -> t1158=14 -> t1170=12 -> t1186=15 -> t1238=12 -> t1251=13 ->
t1254=14 while systems_full is monotonically 26..32 and systems_any
28..36; score==systems_full matched 0/786 trusted rows t>=1250. The
variable is NOT a territory count and can go DOWN without losing a
system (t1151 10 -> t1157 8 with no systems loss: candidate drivers =
fleet losses [t1157 window had ship deaths], economy, or a rolling
window). Passive capture keeps banking it every slot; a DECLARATIVE test
exists now that nougat.lf is live: press C on the starmap (debug State-
of-Galaxy, docs/re/debugflags.md S t85f) and read PERCENT CONTROLLED —
that prints the comparator's own formula output 100*DAT_482fb/T.
STATUS t187 (2026-10-28 LIVE sitting, rows t1255..1335): passive test
continues with NEW HIGHS and still no arming — DAT_482fb 14->15->16->21
(T=50; systems_full=34, systems_any=36 same rows), selector_byte 0 in
every trusted row (45140 pts, docs/re/score.md S8). 68% full-system share
with zero arming re-confirms systems_full-is-not-the-variable at a new
operating point. Boundary test is 4 units away (>=25); row STAYS OPEN —
if a Control-victory screen appears in this sitting, bank it IMMEDIATELY,
that is the closing measurement.
STATUS t189b (merge of pairing-session findings 2026-10-29): the 14->21 drift
the player saw is REAL and is NOT any systems count — same frames t1253..1335
score_stars walks 14,15,12,16,21,19,22 (goes DOWN too) while systems_any=36
and systems_full=34 are dead flat (player saw 14->21 and 36 planets: both
match). DAT_482fb tracks something oscillating +-several per turn despite
constant ownership; untested candidates: per-star "percent controlled"
aggregates, production-weighted counts, or a value recomputed only when the
'c' overlay opens (player opened it on different turns -> saw different
numbers). t187's falsification of systems_full as comparator re-confirmed at
a second operating point. RESIDUE REFINED: not just the threshold — the
DISPLAYED count itself needs its producing write-site pinned (comparator
sweep within the new window against per-star control fields per
scripts/r1_slot.py, if in watcher schema).
STATUS t212 (2026-10-30, static exhaustion of the write-site): (a) the
aicode.md P7 "producer" writes WORD [0x48300] (0x2519b/0x25217/0x25225), a
DIFFERENT slot from the displayed dword [0x482fb..0x482fe] — no alias
(the doc's own caveat confirmed); that block is moreover gated [0x10ba0]==-1
(never fires in banked play) and is a debug-dump-with-counter (calls 0x77ece
+ printf-family 0x7865a per iteration). (b) WRITER CENSUS = ZERO writes to
0x482fb..0x482fe across THREE independent instruments with positive controls:
capstone disp32+imm pass obj0 (scripts/r212_ref_census.py, controls 0x28074/
0x280be/0x2519b/0x25008 found); DECODER-FREE raw image scan (pattern fb 82
04 00 = EXACTLY 4 hits: 2 relocation-table + the 2 presenter disp fields
0x28075/0x280c0 — rules out decode desync); live-RAM pointer scan 60.sav
(every dword pointing into 0x482f0..0x48310 is a relocated operand field of a
KNOWN instruction, byte-exact per scripts/r212_code_identity.py) + forward
trace of all 145 immediate-loaded data-segment bases in [0x47f00,0x48b00)
(scripts/r212_base_disp.py, 140,156 insns, zero [reg+disp] stores into the
window). (c) CONCLUSION: the 12..22 oscillation is produced by a RUNTIME-
COMPUTED store address (scaled-index / memory-loaded base / rep-span /
register-transient class) — not statically enumerable; the decisive
instrument is a dosbox-x-class write watchpoint, i.e. the SAME interactive
session the comparator-firing test already needs. Also banked: at V==1 saves,
byte[star+0x15]==0 on all rows (r212_predicate_corr.py, 90 trusted saves) —
aicode P7's owner-bit label for +0x15 stays [unverified] and join-FAILS
against V; current ring is the new-game ring (V=0, 4 nonzero +0x15).
Full detail docs/re/_wip_t212.md S1..S7 + score.md S9. STATUS t214
(2026-10-30, no-sitting iteration): trigger-A re-verified byte-identical
(scripts/r214_triage.py RC=0: ns-mtime/size/tail-md5 all equal baselines, zero
dosbox-class processes, zero new saves anywhere) — the mid-campaign V>1 witness
and the comparator-firing ask both stay UNOBSERVABLE this iteration, nothing
re-censused (t212 law). NEW instrument-health result banked
docs/re/_wip_t214.md S2..S7: four live watcher instances share the capture dir;
raw timeline rows are writer-multiplicity-inflated (4.26x overall, up to 12x
locally, factor drifts over the capture life) while ALL banked counts
(t187 x1115, t189 68-sustained, 28k trusted obs) were produced through
r1_stream.observations(trust=True) and verified safe — duplicate (file,mtime_ns)
groups carry ZERO content conflicts (tail-1200 audit), so no restatement is
needed; future sittings get scripts/r214_triage.py as a pre-mining gate. STATUS t215
(2026-10-31, no-sitting iteration): trigger-A re-verified byte-identical
(r214_triage.py RC=0) plus a NEW independent axis — newest .sav/.gam under
/home/hrethric (1409 files, no date filter) is playcap/save/60.sav 2026-10-29
13:22, i.e. the save the last sitting ended on, and zero saves modified since
2026-10-29 18:00 — so "watcher died and hid a sitting" is independently
excluded, not just assumed. WRITER POPULATION MEASURED (docs/re/_wip_t215.md S2,
/proc/<pid>/fd census): EXACTLY four processes hold live-timeline.jsonl open
(27774 + orphans 260988/290953/292085, all --no-exit; wrapper 27772 holds no
writer fd) — t214's process-presence inference is now a direct fd-level fact,
and the retirement ask (supervised-session decision) stands upgraded. STATUS t251
(2026-11-01, witness mining, scripts/r1_t251_mine.py): WITNESS (b) LANDS —
t212's roots (r1sav-*/r1deep-*/playcap ring) MISSED work/r1/bank-*: bank-t1254
ALL 20 slots (turn 1254) hold V=23 with NINE byte[star+0x15] nonzero rows
[2,6,12,16,21,22,28,33,44]; bank-t251-live1255 (turn 1255) V=14 with TEN
nonzero rows. SEMANTIC NON-JOIN MEASURED on real mid-campaign slots: V != ownP
(23 vs 9; 14 vs 9), V != occ (14 vs 10), V==systems_full 238/45,227 trusted
slots (0%), V==systems_any 4,970 (10%) — the displayed count is NOT any +0x15
bitset count. P7 label SETTLED: star row 2 holds +0x15==0x3 (TWO races set) at
both turns — +0x15 is not a single-owner bit (t206's vision-byte reading stands).
The 9 intra-turn V->0 dips in the trusted run all coincide with session-boundary
slots (wall-clock gaps; the 07:43:50 dip precedes the 07:44 relaunch) = LOAD
artifacts, narrowing the t85b oscillation class (feeds t255). Row STAYS OPEN: play-gated threshold/comparator residue + watchpoint-class writer. STATUS t255
(2026-11-01, drive-corpus behavioural re-probe, scripts/r255d_persession.py +
r255f_traj.py + r255e_semantics.py over the FULL 7.1 GB timeline = 65,380 deduped
rows / 25 sessions / turns 37..1335, PER-SESSION trust; docs/re/score.md S10):
(a) ZERO MID-TURN V CHANGES — V moves only between turn boundaries (39 changes,
0 same-turn); the t189b "recompute when a screen opens" candidate is REFUTED
(t249's controlled screen-open never moved V). (b) V IS NOT SAVE-PERSISTED:
every session's load turn reads V==0 while the slot carries a full active world
(21-41 ships) — NOT title class; the FIRST End-Turn after load recomputes it,
and deterministically: the same loaded state reloaded twice (Oct-31 01:41 and
Nov-1 08:11 restarts of t1086) produced V=23 at t1087 both times. Writer fires
on the turn clock, not the loader — narrows t212's runtime-computed-store class
to the End-Turn recompute path. (c) V != territory at new operating points:
V=23 held t1087..1096 while territory moved; SAME turn t1254 read V=14 (Oct-26
lineage) vs V=23 (Oct-31 lineage), both any=36 — V depends on lineage history.
(d) NO V>=25 row and NO selector arm anywhere in the corpus: the Control-victory
boundary test remains unobserved passively (live rides V=14/t1255). NEXT
discriminator banked: per-owner ship census vs V-change turns (ship_raw banked
in every row); decisive instrument still a write watchpoint on the End-Turn
path. STATUS t258 (2026-11-01, THE BANKED DISCRIMINATOR EXECUTED,
scripts/r258_vdisc.py single pass over 303,625 lines / 53,412 trusted V!=0 rows
/ 25 sessions; docs/re/score.md S11): CANDIDICIDE COMPLETE, SURVIVORS NONE —
of the 38 V-change turn-boundaries vs the 795 V-stable turn-boundary control:
T/rank/selector are corpus-constants; systems_any/full/planets_mine move at
exactly 1/38 change boundaries AND 1-2 stable boundaries (dead both legs —
t85g's non-territory verdict re-proved at full scope); alive ship counts and
ALL 12 per-owner order-kind features move at 2-33/38 AND 3-289 stable (best
correlate A_k4/A_k5 33/38 drowned by 278 false positives — order churn is
ubiquitous, V moves rare). Closed-form aggregate fit on all 53,412 rows dies
too (best P_k4+P_k5+A_k4+A_k5 5,688/53,412 = 10.6% coincidence; first-miss at
t37 V=1 zero-ships). NEW POSITIVE FACTS: 3rd independent determinism witness
(S14/S15 replay t1169->1171 V 14->12->14 exactly); V==0 is a LOAD-CLASS not
turn==0 (33 session-turn pairs at turns 692..1254); shape clues banked —
DOUBLING 11->22 (S07 t911->912) and HALVING 22->11 (S13 t1140->1141) suggest a
floor/threshold over a per-star derived quantity rebuilt per end-turn. The
world-feature space is now MEASURED-CLOSED as an explanation of V: the producer
cannot be identified from banked watcher fields at all. NEXT instrument =
dosbox-x write watchpoint on the End-Turn path + drive past V>=25 (USER ASK in
docs/BLOCKED.md; zero V>=25 rows and zero selector arms in the whole corpus —
the threshold itself remains unobserved). rewrite default >1/2
(campaign.cpp:2093) UNCHANGED, consistent with every banked frame. Row STAYS
OPEN (strict-close). STATUS t259 (2026-11-01): the parked :9 game PROCESS DIED
~15:45:08 unattributed (docs/re/_wip_t259.md S3, docs/BLOCKED.md t259 ADDENDUM)
— passive threshold witness is IMPOSSIBLE until relaunch decision; ask (A) as
literally authored is dead. OFFLINE HANDLE TESTED AND CLOSED t259: banked
savs are full guest RAM (ZIP member "Memory"), but the same-turn-different-V
pair census over ALL 122 banked/ring savs returned NONE (turn set {1086:V0,
1096:V23, 1254:V23, 1255:V14}; scripts/r259_savpair_census.py,
work/r1/t259_savpair.out) — cross-bank diffs are confounded by world movement.
OQ-021 has NO offline residue left: both residues are play/watchpoint-gated.
STATUS t262 (2026-11-02): CENSUS TRIGGER HYPOTHESIS MEASURED-DEAD on the driven
corpus (808+207 turn boundaries, segment-trust law): V moves at 37 boundaries
where the fleet inventory was byte-identical at 27 of them (doubling/halving
included), inventory moves at 121 boundaries with V static, and 18/149
inventory signatures carry MULTIPLE V values in one continuous lineage (worst:
one sig, V in {12,15,16,19,21,22}, turns 1255..1335 driven) — V is NOT a
function of the ship census; producer inputs localized to NON-fleet state
(score.md S13, scripts/r262_census_disc.py + r262_legA.py). Row STAYS OPEN:
threshold still unobserved (driven max V=22@t1301, decayed 21@t1335). | open (threshold
residue = play witness; displayed-count write-site = RESIDUE NOW NARROWED TO
END-TURN RECOMPUTE PATH OVER NON-FLEET STATE (t262 S13), runtime-watchpoint
class; screen-open hypothesis REFUTED t255; banked-world-feature explanations
MEASURED-EXHAUSTED t258; fleet-census trigger MEASURED-DEAD t262) STATUS t269 (2026-11-02, threshold mining, score.md S14,
scripts/r269_vthreshold.py + r269_anom.py): full corpus 71,038 trusted rows —
ZERO V>=25, selector census {0: ALL}, rank census {65535: all but 2 turn-0
title frames} (score evaluator never ran); T census FIRST-BANKED {50: 71023}
with every anomaly a turn-0 setup frame -> captured play is ALL T=50 galaxies,
denominator never variable; distance-to-half = max 46.0% (V=23), strict
majority 3 stars away, systems_any=36>25 with sel=0 re-confirms the semantic
non-join at the threshold neighbourhood; 66 V-change boundaries banked. Row
STAYS OPEN (a trajectory is not a threshold; ENDGAME-window witness still the
closure class) STATUS t272 (2026-11-02, watchpoint session GRANTED and RUN on
scratch — INSTRUMENT MEASURED-DEAD on this box): the installed dosbox-x
2025.02.01+dfsg-3 has no debugger command set at all (zero bpm/bpmw/clrbp/
bplist/breakpoint strings even at -n 2; DEBUGBOX shell internal absent
("Bad command or filename"); GUI has no Debug menu; -break-start accepted and
IGNORED — boots to title; all measured, docs/re/score.md S15,
docs/REFUTED-ROUTES.md t272). The runtime-watchpoint class named as the
write-site closure route DOES NOT EXIST here; alternatives checked same session
(dosbox 0.74 zero debugger strings, no bochs/qemu/valgrind, ptrace dead R4).
Keeper for any future debugger-class run: a title-screen boot does NOT have the
image resident (scripts/r272_scratch_resident.py) — enter a campaign first.
Row STAYS OPEN; live routes = t273 threshold watch (V>=25 event) and the
ENDGAME-window witness; rewrite default >1/2 unchanged | STATUS t273 (2026-11-02, docs/re/score.md S16): FIRST nonzero selector/rank in corpus — the TUTORIAL-lineage segment (648 rows, bank-t273-tutorial645) reads selector=2, rank=1 with V=0 and player owning 3/50 systems: selector=2 is NOT the end-ctrl threshold arm under the file-order reading; selector->arm MAPPING [unverified] (presenter arms re-measured by push-imm scan: 0x2c03a default/0x2c04d xtnc/0x2c064 dest/0x2c07a CAPT (S3 miss)/0x2c092 unit/0x2c0a9 ctrl; jmp-table @0x10173e0 not locatable in payload by arm-dword scan). Campaign lineage: zero V>=25 rows (72,327 rows), selector 0 everywhere; threshold witness STILL absent. Row STAYS OPEN.

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
main-branch law itself stays MEASURED (§7/§8) and implemented.
STATUS t85b: first real transitions banked (docs/re/diplomacy.md §11):
player war-declaration fires the cell 1->2 RECIPROCALLY (both empires,
t887->888, sustained 244 turns) while AI contact fires 0->1 both ways;
alliance proposal shows NO cell change, only attitude +280 on the
PLAYER-side cell. STATUS t85c: player confirms the Orfa NEVER accepted —
and the banked AI-side cell explains it: att[Orfa->Chamachies] peaked 485
and decayed to 451, never crossing Orfa's ACCEPT_ALLIANCE=570, and a
player PROPOSE does not move the AI-side attitude (docs/re/diplomacy.md
§12). WORKING: 2=war, 1=peacetime/no-active-relationship; an accepted
alliance (state-3 candidate) remains capture-gated — a future sitting must
first raise Orfa attitude above 570 by other means, then propose.
STATUS t85g (t1253 sitting): CORRECTION to t85c — a player PROPOSAL DOES
move the AI-side cell (att[Orfa->Chamachies] 487->526, +39); t85c's "+280
player-side only" understated it (the t85c proposal window simply didn't
catch a delta). Acceptance law unchanged: 526 < 570, no alliance, cells
stay 1. Second proposal (this sitting) also declined per player report.
STATE-3 remains UNOBSERVED across 42k trusted rows. Vendor name table
RELNAMES@0x89074 = Unknown/Peace/War/Alliance (debugflags.md t85f)
corroborates the working enum 1=Peace 2=War 3=Alliance — but the CLOSING
measurement still needs a row whose cell actually holds 3. Residual route:
attitude-raising (gifts/trades?) then accept, OR static: writers of the
state byte that store 3 (t85h: scan stores of imm3 into [+0x1c0+idx]).
W-B (option C hybrid): build only when ownership model lands; engine
build additionally awaits the state-enum capture above.
PLAIN (t179): Our rewrite AI only sends war/peace decisions; the original
also sends trade offers and third-party messages. Building the full trade
engine is deferred (option C: build when the ownership model lands). The
narrower open question: we measured relation cells 0=unknown, 1=peace, 2=war
(real transitions banked) but never actually SAW a cell hold 3 (alliance) -
no captured game ever had an alliance accepted (both player proposals fell
below the Orfa's 570 attitude threshold, measured). Vendor debug names
(Unknown/Peace/War/Alliance) corroborate 3=Alliance. Closure routes: play
(raise attitude with gifts, propose, watch the cell) OR the queued static
scan t180: find code that stores the value 3 into a relation-state byte -
named by t85g, never run.

STATUS t187 (2026-10-28 LIVE sitting): FIRST-EVER reciprocal WAR->PEACE
(2->1) banked (declared and made peace within one autosave granularity,
docs/re/diplomacy.md S15) — the enum rung transitions are now 0->1, 1->2,
2->1; state 3 remains UNOBSERVED across 45140 fresh trusted pts (honest
negative, row stays open). NEW: the Orfa AI-side attitude is drifting up
UNATTENDED 526->535 over t1254->1284 (+3 per ~3-4 turns, player-side
att frozen); extrapolated 570-crossing ~t1295-1300. PLAYER ASK banked in
STATE.md: propose alliance to Orfa while playing — an accepted alliance
writes the cell holding 3 and CLOSES this row.

STATUS t180 (2026-10-28, STATIC route RUN — the t85h/t85g-named scan nobody
ran): ANSWER TO "does code store 3 into a relation-state byte" = YES, three
sites, all conditional. tools scripts/r1_t180_state3_writers.py (census,
agrees site-for-site with scripts/r1_t107_writers_full.py 0x1c0 via an
independent encoding+boundary method), scripts/r1_t180_switchtbl.py and
scripts/r1_t180_offer_switch.py (both cs-relative switch tables resolve
15/15 and 13/13 inside their functions using the R13 +0x14bb0 code-object
base). Raw disasm work/r1/t180/code0.txt. Law banked docs/re/diplomacy.md
S13. FINDINGS: FUN_000454a4 (0x454a4..0x45c30, exactly 3 callers 0x36b2f /
0x36c47 / 0x4470e) is the state mutator, dispatched on bl = DA index (cmp
bl,0xe); its cl argument is FUN_00044fc0's VERDICT CODE (caller 0x446d9..
0x4470e: `call 0x44fc0` -> `movsx ecx,al`, out-param -> bl). Case bl=3 gate
`cmp cl,0x4` at 0x4561f -> writes 0x3 to SELF cell 0x4562f AND mirror 0x45641
with attitude +10 both sides; the accept verdict 4 comes from FUN_00044fc0
rung 0x44ffc comparing att[self][other] against WORD [row+0x1d1], and +0x1d1
is ACCEPT_ALLIANCE per the MEASURED S8 field map -> ALLIANCE FORMATION LAW:
cell := 3 both ways iff att > race.ACCEPT_ALLIANCE (S13.2). Case bl=11
(0x45aa3) is a second alliance-shaped channel, gate cl==19 plus att >
(other-10), cl provenance UNRESOLVED. Reader side exhausts the enum at
{0,1,2,3} (23/6/20/23 compare sites) and the three third-party rungs SEMAN-
TICALLY LOCK the meanings: 0x44c1a self==2 AND third==3 -> DA 10
BreakAllianceWithOtherRace; 0x44c71 self==3 AND third==2 -> DA 7
OfferPeaceToOtherRace; 0x44ce0 self==2 AND third==1 -> DA 9
DeclareWarOnOtherRace. Vendor RELNAMES@0x89074 = Unknown/Peace/War/Alliance
(byte-verified in-image this turn; indexed 0x2817b by the `c` state-of-galaxy
displayer) names the same ordering. STRUCTURE BONUS: row law code-confirmed —
`imul ebx,edx,0x1ee` + baked `mov edi/eax,0x12e16` (0x446bf, 0x454d4,
0x2748c), and row-relative [rowbase+other+0x1c0] == absolute
[other+owner*0x1ee+0x12fd6] (0x12e16+0x1c0), so the S10 window law no longer
rests on RAM inference alone; and 0x27476..0x27511 is the SCENARIO SEEDING
writer of state 1 (copies attitude from +0x12feb, skips the player row) — the
static origin of the S11 "pre-war every pair sat at 1" observation.
NOT CLOSED, honestly: the row's own closing measurement is a cell OBSERVED
holding 3, and 42k trusted rows contain none. S13 is instruction-level
derivation from the static image plus semantic locks, corroborated live only
for 1 and 2 — stronger than a default, but not the named observation, so
strict-close holds and the row stays open. WHAT CHANGED: the residual is
downgraded from "semantics unknown / static route unrun" to "mechanism derived,
STATIC ROUTE EXHAUSTED — capture-only". The capture test is now precise rather
than exploratory: raise the target's attitude above ITS OWN ACCEPT_ALLIANCE
(per-race, S8 — the Orfa's 570 was the binding number in the banked campaign)
and propose; expected signal = BOTH cells 3 with +10 attitude, and DA 10
becoming selectable against any empire the acceptor is at war with. Do NOT
re-queue a static scan for this row. Rewrite code site: unchanged —
diplomacy.cpp:227 `!atWar && !allied` is consistent with a single neither-
state, and AcceptAlliance cannot be returned because the original's accept
test lives in the RECEIVER's rung (0x44ffc vs its own +0x1d1) while
decideDipAction takes no incoming-offer parameter; wiring it is the W-B
ownership-model gate, not an RE unknown. The comment at diplomacy.cpp:244
("state changes only on accept") is now cited rather than assumed.
STATUS t188b/t189b (2026-10-29) — THE CLOSING MEASUREMENT IS IN: cell0i=3
AND celli0=3 OBSERVED at t=1335 (wall 23:47:43) with attitude +10/+10
(605->615 player-side, 631->644 AI-side), sustained 68 raw rows; re-run of
scripts/r1_t188_state3_arbiter.py this session RC=0 reproduces frame-for-
frame. Flip comparator = AI-side atti0=631 > Orfa ACCEPT_ALLIANCE=570 —
EXACTLY the t180 static law (0x4562f/0x45641 writes), now corroborated
end-to-end by capture (docs/re/diplomacy.md §16). ENUM IDENTITY
CLOSED BY OBSERVED TRANSITIONS: 2=WAR (t85b reciprocal 1->2, sustained 244
turns), 1=PEACE (t187 reciprocal 2->1), 3=ALLIANCE (this event) — matches
vendor RELNAMES@0x89074 and the §13 third-party semantic locks. The t180
"NOT CLOSED, honestly" paragraph above is SUPERSEDED by this observation;
iter-110's "no cell3 = non-event" pre-check was correct at scan time but
the mid-turn write (§16 methodology law: walk RAW rows) had not yet landed.
| CLOSED 2026-10-29 t189b (observation: live-capture cell==3 both ways
t1335, scripts/r1_t188_state3_arbiter.py RC=0 re-run; law docs/re/
diplomacy.md §13+§16; rewrite code site unchanged, diplomacy.cpp:227/:244
cited; engine-build residual — trade/third-party emitter + receiver-rung
parameter — tracked in docs/PLAN.md A7, NOT an RE unknown) |
POST-CLOSURE ANNOTATION t252 (2026-11-01, LIVE SWEEP 1, ui-runtime.md §6b):
player-side negotiation UI MEASURED live at t1255 — NEGSCREEN opens from the
Species-menu race row (NOT the galaxy sidebar); ALIENDIP renders one dialogue
line (band y 252-262) whose text is the raceNN.dip DR_* section verbatim with
%m/%y substitution (Ungooma "How can we little %m help you?" == race11.dip:173
DR_NoDipResponse); PLAYERDIP renders the option list at ~29 px pitch (bands
329-339/358-367/387-396) and the rendered set is POSTURE-DEPENDENT (observed:
Goodbye / declare-war / propose-alliance). Option #1 click closes the
negotiation back to the species menu, zero turn drift. Row STAYS CLOSED (the
closure evidence is t189b's; this annotation only feeds the A7 engine-build
residual with the receiver-side UI shape).
POST-CLOSURE ANNOTATION t268 (2026-11-02, LIVE SWEEP 3, ui-runtime.md §6d):
option list re-measured on a DIFFERENT campaign state (t1236): FIVE rows
rendered (Goodbye / declare-war / propose-alliance / DA_TradeStarlanes /
DA_TradeStars — player.dip :67/:31/:34/:37/:40 verbatim), bands 329-339/
361-367/390-396/416-425/446-454; Goodbye (file-LAST in ACTIONS) is HOISTED to
render row 1; DA_TradeResearch/OfferPeace/BreakAlliance and all %t third-party
actions filtered out at this posture. Alien line "Uh oh.  What's wrong now?"
== race02.dip:172 DR_NoDipResponse (Orfa) exact. A7-relevant: the trade rows
DA 4/5 the rewrite AI is supposed to emit ARE UI-renderable player-initiated
actions too, and player.dip holds the BASE DIPVALUES table (ACCEPT_ALLIANCE
200) which race files override (Orfa 570 live) — engine must read per-race.
Row STAYS CLOSED (annotation only; no state-enum or law change).
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
(measured wrong for T>50); test galaxy_density_ladder_matches_measured_sizes
pins per-size shell runs (108 tests 0 failed) | CLOSED |
Tail-residue note: gated chains exceed DAT T at low densities (records
stay allocated past the in-play cut — consistent with the t78 caveat).
OQ-026 | visibility | original WITHHIDES fogged lanes and gates fogged stars
— CONSUMER MAPPED t194 (ships.md S23 L9): cosmos list builder FUN_00028fc0
admits lane i iff lane rec+0x20 & viewer_mask(DAT_00089324) != 0 (no entry =>
never drawn by painter FUN_000284bc, never clickable; all 5 builder call
sites are cosmos repaints); viewer setter FUN_00021a84(idx): mask=(idx==0xff?
0xff:1<<idx), ALSO sets [0x7458e] — X_CUR IS THE VIEWER INDEX; star obj
+0x16/+0x17 gate selection/lane-follow in FUN_00028e70 (& DAT_00006774 =
data-seg twin); stars always DRAWN | CLOSED 2026-10-29 t195 | THE ROW'S OWN
closure bar was rewrite implement+pin (set t194); LANDED: rewrite/src/game/
campaign.{h,cpp} visibility layer (laneVis_ = rec+0x20 analog; starLaneVis_/
starSelVis_ = obj +0x16/+0x17 twins kept separate per the differing t193
censuses; viewerMaskFor() == FUN_00021a84 verbatim; laneVisibleTo/
cosmosLanesFor == 0x2914e filter; cosmosStarsFor unconditional == L9 honest
negative; shareLaneVision == FUN_00046354 shape N=rand%(3|6)+1 OR-only,
BIDIRECTIONAL at alliance formation (cited caller 0x45778) + RECEIVE-ONLY
one-shot first-contact leg (cited shape 0x55f6e); shareStarVision ==
FUN_00046524 twin modulus 4|2; init seed = own claim exactly per the t192/
t193 witness law). PIN TEST(campaign_visibility_law_oq026_t195): 25 checks —
mask law {0:1,1:2,5:20,255:255}, init fog pattern, spectator AND (mask-0
lanes stay hidden even under 0xff), receive direction + N envelope, sticky
monotonicity over 30 turns, alliance bidirectional share incl star twin,
SA_KnowStarLanes + SA_KnowHomeWorlds both routes (player species + race
token) — 111 tests 0 fail. MEASURED base (scripts/r1_t194_viewer_mask_
witness.py 20/20 saves; r1_t193_midgame_witness.py censuses) cited ships.md
S23 L5..L10. CODE SITES: campaign.cpp seedVisibility/visibilityPhase/
diplomacyPhase ProposeAlliance branch + species.cpp kNotes rows 3/15 (filed
no-op count 4->2, ability_probe 3m updated); abilities.md §2 rows WIRED.
Residues DOCUMENTED inside the closure (not open laws): init path of the
first 1<<r bits unidentified; twin caller pairing [unverified]; AI-AI share
has no rewrite producer (no AI-AI dip relations — t193 mask-6 class has no
rewrite analog); boot-arg at 0x21408 [unverified regparm]. |
OQ-020 | abilities | charge time for the 14 charged SA_ abilities (vendor
"%d day%s", no data file) — rewrite placeholder was 30 turns | CLOSED t100 | THE
MEASUREMENT (aicode.md §6.4 + docs/re/_wip_t99.md F7-F11): charge period =
cadence word WORD[0x6780 + 2*ability] embedded in ascend.exe — 5:60 6:100
7:62 8:77 9:90 10:150 11:70 12:63 13:66 14:72 16:92 17:100 19:89 20:68;
ZERO exactly at {0..4,15,18,21} == the passive set == exactly !chargedIdx;
live playcap/save/60.sav words == restored FILE 0x89330 byte-exact, ZERO
stores image-wide (constant table; gate 0x43b58 cad>counter rejects,
equality fires EVENT-24 dispatch; reset-on-fire exit T1 0x4400a; UI
countdown cad-counter 0x37b6c). The t57 "static route exhausted" claim was
VOID (route = the W6-A6 ability-cadence engine). CODE SITE: rewrite/src/
game/species.cpp abilityChargeTurns = kCad[21] verbatim table (replaces the
30-turn placeholder); campaign.cpp abilityPhase rewired to the cited
COUNT-UP law (charge_ == row+0x19e: +1/turn, fires iff == cad exactly,
resets 0; T2 0x43fe5 stores 0 at the equality point too — one reset models
both). Pins: TEST(species_charge_split_verified) full 21-word table +
nonzero==charged set; TEST(species_charged_ability_fires_on_schedule) t60
first fire, reset 0, second fire t120 (period == cad); per-ability
activation tests moved to their cadence words (ForcePeace 100,
ShieldPlanets 66, BlockStarLanes 92, MoreMaxPop 72, Cornucopia 150,
StealResearch 63); gate 3m bound 40->65 (HealShips cad 60). Verify tool
scripts/r1_t100_cad_verify.py RC=0 (C++ == FILE leg == LIVE save leg,
item-table-anchored B=0x1bf4d8). 110 tests 0 failed; timeline seeds
unchanged (2024 t737 / 42 t688 / 13 t503, all finite). CAVEAT (out of this
row's scope per T57b's separate-object finding): the ITEM-ability supply/
amass path (FUN_00039b6c/0x39c10 slot word+2) remains an UNATTRIBUTED
decrement-period question — it is the gizmo-slot object, not the SA_
species pool this row's vendor text and table govern. |
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
W3 sanctioned route EXECUTED t83 negative (shp.md W3: all 75 decoder sites
read dims ONLY from the record-start header; cache load = verbatim copy, no
dims transform) — no other reader exists in the image;
closure class = human-verifiable drawn frame (R13 blocks self-verification);
blind sweeps FORBIDDEN (R2). Map draws documented circles; ShapeLibrary is a
validation asset (option C).
PLAIN (t179): The shape/sprite library format is decoded for 1477 of 1557
records; 80 records in 31 files don't fit the law - every reader in the game
reads image size only from the record header, but these 80 have header sizes
that don't match their data. Question: where does the real size come from, or
are these simply broken vendor data? Closure needs human eyes (vision tooling
is down on this deployment; strict-close forbids self-grading). Plan (queued
t182): a dumper renders all 80 as PNGs; the player eyeballs ~20 and rules
"fine" (our size law was too strict - fix the doc) or "garbage" (broken
records - close with evidence). ~30 minutes of human time total. DECISION
OPTIONS: run the dumper, or accept the current validation-asset treatment.
STATUS t182 (2026-10-28): DUMPER SHIPPED — work/r1/shp_png/ (index.txt +
15 validated PNGs: 5 CONTROLS spanning size classes + 10 RESTORED), driver
scripts/r1_t182_pngdump.py + tools/shp_pngdump.cpp over the rewrite's own
ShapeLibrary; palette game.pal labelled UNVERIFIED. MEASURED CORRECTION
(shp.md S18): the ledger script's k==0 V-trial walked from rec instead of
the closed rec+8 law — 10 k==0 records (10status/2savegam/4loadgam/planpro/
planres/smship11/smship15/lgrace07-09-10 rec0) were FALSE FAILs, promoted
with zero demotions; corpus now V 197 + A 1289 + FAIL 71 = 1557, libs clean
186/208. Genuine residue 71 records/28 files (planind 13, 3cfgnew 13,
cos_star 12, stragglers 46). Row stays OPEN — closure = player eyeball of
the packet (R13); packet is ready to rule on.
STATUS t196 (2026-10-29): VISION-ORACLE TRIAGE + SPAN-BOUND ARTIFACT FOUND —
residue re-cut 71 -> 29 FULL-FRAME false FAILs + 16 non-drawable dims words +
26 zero-stream EMPTY slots (1 overlap: 3cfgnew k12 EOF-truncated). MEASURED
(shp.md S20): running the closed S9 grammar from the canonical stream slot at
the canonical dims with NO directory-span bound completes EXACT-H for planind
k0..k12, 3cfgnew k0..k11, 14intel k8, 1starmap k3/k4/k6; the blit
(FUN_0005caac, S12) takes no length arg and has no overrun error code, and the
cache is a verbatim whole-library copy, so the [rec,nxt) bound in
scripts/r1_shp_unifiedlaw.py + rewrite ShapeLibrary::decode() is OUR validator
artifact, not vendor law (same species as the t182 off-by-8 set). For these 29
the dims-location answer is: canonical slots, exactly like every passing
record. What stays OPEN honestly: dims-location for 16 records whose dims word
is non-walkable (cos_star k40..k51 =0, mouse k6/k7, 1starmap k1, sg50expl k9)
— closure class = paint-routine census or player ruling, not file probing —
plus 3cfgnew k12 truncated at file EOF. Vision identifications banked
(work/r1/shp_png/ids.tsv + sheets/): planind = manufacturing gauge ladder
(factory grows +1 tank/level), planres/planpro ladders monotonic k0..k20
(record index = plausible level index; player's ~60-level testimony implies a
compression map, uncited), 3cfgnew = new-game/race-config art, 1starmap =
star-map sprites ("NEXT TURN <ENTER>" verbatim), mouse = cursors + "Exit
<ESC>", planitem = distinct item icons, planets = biome spheres, planal00 =
cratered-surface crops (population-pose hypothesis KILLED). Row status OPEN.
STATUS t197 (2026-10-29): SPAN BOUND REMOVED + LAWS UNIFIED (shp.md S21).
Validator gained X-class (span-free EXACT-H walk): residue re-cut 71 -> 29 X
(false FAILs, now decodable) + 44 real FAILs; dims-gate unification demoted
exactly 2 degenerate walks the vendor blit refuses (mouse k5 W=0, sg64expl k0
H=0xfffffffb). FINAL [measured, pinned gate stage 3c-2 + test_shp floors]:
V196+A1288+X29+FAIL44=1557, clean libs 187/208; Python validator and rewrite
ShapeLibrary::decode() now agree RECORD-EXACT (1513 decode-pass). CODE SITE:
rewrite/src/formats/shp.cpp walkRows bound img.size() + decode() (4096 clamp
kept), pin test shp_span_free_t197; scripts/r1_shp_unifiedlaw.py X tag +
--profiles. Evidence packet regenerated: 44 rendered/44 validated incl. 29
XREC-- full frames (work/r1/shp_png, ids.tsv validator-tagged). Measured
correction to S20: past-span rows PAINT (planind tail 40 distinct indices),
they are desynced next-record bytes, NOT transparent — whether widgets SHOW
those bands is the paint-routine question (gauge-library queue item). Row
stays OPEN: dims-location unknown for the 44 (cos_star k40-51, mouse k5/6/7,
1starmap k1, 3cfgnew k12 EOF-trunc, 26 zero-stream EMPTY + sg*/expl ladder
singles + sg64expl k0); closure class unchanged = player ruling / draw
capture (R13), never file-probing self-grading.
STATUS t198 (2026-10-29): PAINT ROUTINE CENSUS (docs/re/planets-ui.md).
Planet-screen paint body 0x3b96c (planwin.cpp cluster; 12 blit sites cited);
selector switch 0x3cc9f table READ LIVE (41.sav member image_off 0x3cb98 ->
[0x3cca7,0x3cd3b,0x3cdcf,0x3ce39,0x3cefd]). SELECTION CENSUS PARTIAL, cited:
planind records are addressed by gauge selectors 0..20 (law:
clamp0..20(round(IND^0.75)), IND=word [planet+0x44]) -> the 13 X-class
records k0..k12 are ALL WITHIN THE DRAWABLE RANGE, "never-drawable
placeholder" REFUTED for planind; t197's "do widgets show the past-span
bands" question ANSWERED (no clip-rect override; each draw = one complete
record's own stream per the S17 runtime table). 1starmap k3/k4 SELECTED via
windows.txt SHAPEITEM lines (:456/:477), k6 not per those lines; 3cfgnew
only record 0 selected (:612). OPEN remains: cos_star selector semantics at
0x2925c (its k40-51 residue), slot-library identity of gauge/pop cache
globals [0x6fd90/2/4/9c] (zero direct writers found — A3/89 05/C7 05 census
over the whole image), and the 44 dims-unknowns. Row stays OPEN.
STATUS t199 (2026-10-29): REWRITE WIRING OF THE PLANET-UI VIS LAWS (pure
code; no new residue evidence — row stays OPEN on the same residues). The
t198 laws are now CODE: ui::gaugeSelector = clamp0..20(lround(L^0.75)) and
ui::prosSelector = identity-clamp (rewrite/src/ui/layout.{h,cpp}; tie-proof
in planets-ui.md S3 — no integer L^0.75 lands on .5, so lround == the x87
frndint the original used); Campaign::popBands/popBandsFor implements
SEL(i)=1+[i>=used]+[i>=pop] over i<cap verbatim (src/game/campaign.h on the
+0x4c/+0x42/+0x4a analogs usedPopFor/pop/storedCapFor). Pins:
layout_planet_gauge_selector_law_t199 (corpus anchors RES52->19, IND53->20,
IND77->clamp, boundary-exact both sides at all 21 selectors) and
campaign_pop_band_law_t199 (edge-class shapes + independent band histograms
count1==used/count2==pop-used/count3==cap-pop + used<=pop<=cap over seeded
state). Arithmetic correction: planets-ui.md S3's "pow(53,0.75)=20.2" is
19.64 (conclusion unchanged). Id fold into shp.md S22. Rendering stays
blocked on OQ-005 per ui-runtime.md §2 (no vendor sprites, lookalikes
banned) — documented in ui-runtime.md §2a.
STATUS t200 (2026-10-29): COS_STAR SELECTOR SEMANTICS MEASURED — RESIDUE
SHRINKS WITH CITED BOUND (planets-ui.md §6). The STAR_SHAPES paint is
FUN_00029788's star path (blit site 0x298dc — t198's "0x2925c" was the
enclosing function start): LAW SEL = 4*[star_record+0x00] + cls(4-band
ladder on f32[star+0xd]), payload = [wnd+0xab] (corroborated: guest RAM
buffer 0xfd2934 in 60.sav matches cos_star.shp header+dir byte-for-byte).
K = star type index — census scripts/r200_kcensus.py RC=0 over 20 saves x 50
stars: measured set {0,1,2,4,5,6,7,8,9,11,12} subset {0..12}
(hist {0:220,1:60,2:40,4:40,5:160,6:120,7:100,8:20,9:60,11:100,12:80};
types 3/10 absent in these new-game saves; starstat.txt has exactly 13
types). => SEL reach 0..51: the 12 dims-zero residue records k40..k51 ARE
ADDRESSABLE (types 10/11/12 x cls 0..3 — rare star types' pips; a dims-zero
slot blits error -1 @0x5cb2b = draws nothing), while k52..k54 are provably
UNADDRESSABLE by any legal K (need K>=13 > type domain). Honest negative
kept: WHY those slots are empty (vendor defect vs dims-location unknown)
stays unmeasured — row stays OPEN, residue restated as "12 addressable-empty
+ 3 unreachable spares" instead of "44 dims-unknowns incl. cos_star 12".
Also adjudicated: cosmos site 0x2a223 is a relation BADGE blit (SEL 9 =
ALLIANCE, 8 = WAR, -1 = skip; t189 relation-state byte), NOT star art.
STATUS t252 (2026-11-01, LIVE SWEEP 1, docs/re/ui-runtime.md §6a/6b): window-class SHAPEFILE map MEASURED from windows.txt and corroborated live — sidebar button icons ARE 1starmap.shp SHAPEITEM records (frames 3=Research 4=Ships 5=Planets 7=Special), NEGSCREEN class art = 13NEGOT.SHP, research screen = 20RES.SHP, ship design = 8SHIPDES.SHP (9 SHAPEFILE keys total). Screens opened live at t1255 with zero turn drift: RESWIN renders a NODE GRAPH (discovered=blue ring, current=gold) + right panel "Current Project: Accel Energy Replenishment (15 days) Allows Lush Growth Bomb"; pan clicks at RESMOVEUP/DOWN center (570,455) moved ONLY the minimap column (bbox x552-593 y222-469, 472px; 2nd click 0px = edge). These are W3-eyeball identification targets for record-level IDs once the codec exists. Row STAYS OPEN (strict-close): codec still blocked (R2); no record-id fold from this sweep yet.
STATUS t253 (2026-11-01, LIVE SWEEP 2, docs/re/ui-runtime.md §6c): SHIPDESSCREEN's seven tab tiles are pinned to 8SHIPDES.SHP FRAMES BY THE VENDOR FILE (windows.txt SHAPEFRAME: WEAPONS 2, HULL 3, DEFENSES 4, ENGINES 5, SENSORS 6, ENERGY 7, SPECIAL 8; GIZLIST 7, SHIPDESSCREEN 0) AND to seven semantic roles MEASURED live (each tab's GIZLIST == the gizmos.txt category block in file order, 6/6 exact: cat0 weapons/cat1 shields/cat2 drives/cat3 scanners/cat4 generators/cat5 specials). Live art in grid order: explosion / ship silhouette / blue orb | green crystal / magenta vortex / gold cylinder / pink beam+green tip — a ready frame->role target set for the W3 eyeball route. Row STAYS OPEN: this is frame-role identification, NOT a dims-law answer or a drawn-frame ruling; codec remains R2-blocked.
STATUS t254 (2026-11-01, POP-SLOT LIBRARY + PLANITEM RULING, docs/re/shp.md S23 + _wip_t254.md): population-slot icon library IDENTIFIED by cited live-RAM measurement — u16[DAT 0x6fd9c]=44 (bank-t251-live1255/41.sav) -> cache slot 44 PAY=0x435400 verbatim 1.10 copy at +0x88 content-matches 17np.shp EXACT (control slot 41 -> 14intel.shp; slot index == gwshare.txt line - 1); runtime selector table sel 0..8 -> record stream starts 0..8 (9/9, entry+0x18 law). Record IDs (vision 16x + live Vega IV pixel census 37 busy/2 free/1 unpainted cell, capacity-sized array law holds): k1 9x9 sideways red humanoid = BUSY, k2 7x9 front-facing yellow = FREE, k3 8x8 hollow green ring = EMPTY — the player's S19 testimony corroborated record-for-record. Geometry exclusion measured: planets.shp min 11x11 (11 groups x 5-size ladder), planitem min 24x23, planalNN min 47x47 — all EXCLUDED from the 0x0a PLPOP pitch; planets-ui.md S4 corrected in place. PLANITEM ruling CONFIRMED: live PLBUILD icon "Scientist Takeover" (item idx 34) == planitem.shp k34 1:1 MAD 1.5 vs next-best 42.1 (scripts/r1_t254_pi_match.py); per-item ids for the other 39 recs stay contact-sheet folds (t254_B_planitem.png). Row STAYS OPEN (strict-close): the dims-location residue (12 addressable-empty cos_star + 3 spares + stragglers) is UNTOUCHED by this iteration — pop-slot ids are identification-by-context, not a drawn-frame ruling; codec R2-block stands.
STATUS t278 (2026-11-02, RULING PACKAGE, docs/re/shp.md S24 + BLOCKED.md t68 amendment): the user-facing ask is now a DECISION SHEET — work/r1/shp_png/index.txt rebuilt verbatim per the queue row (twin decision-sheet.md; generator scripts/r1_t278_decision_sheet.py; raw census banked index_t278pristine.txt). 88 rows (A=15 already-shown restatements with the Oct-29 quotes verbatim from session msg 40813, B=29 SPAN-FREE full frames w/ bright thumbnails + cited library laws incl. planind drawn-in-play, C=44 FAIL rows w/ span bytes + honest status). Measured decomposition of the 44: 25 zero-byte ladder slots (batch-rulable framing) + 12 cos_star addressable-empty + mouse k6/k7 + 1starmap k1 + sg50expl k9 (invalid dims) + mouse k5 + sg64expl k0 (t197 demotions) + 3cfgnew k12 (EOF-broken). Render-state MEASURED: on-disk PNGs are bright-palette (lgrace10 mean 148, max 255 — t189b fix present); sheets/ contact sheets are DARK-era, flagged in-sheet, regeneration offered not performed. Row STAYS OPEN (strict-close): recommendations are proposals, not rulings (R13); closure = the user's per-row reply or a draw-capture. PITFALL banked: r1_t182_pngdump.py overwrites index.txt on every run — hand content there must be regenerable, hence generator + pristine copy.
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
CODE SITE: rewrite/src/formats/bin_table.h (BinTable::parse, vendor columns
documented as open per OQ-004 scope; consumer main.cpp:151 counts parsed
tables only — no semantics claimed).
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
claim RETRACTED, the array IS the generation output) [t106 UPDATE: the
scenario/preset-row ATTRIBUTION ITSELF IS NOW REFUTED — see the t106
block at the end of this row and income-law.md T106]; Lush Growth
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
r1_income_law.py --slot now searches ck/ AND save/ (t71 fix). t90 AI
TURN-LOOP MAP (W6-A3, docs/re/aicode.md, tool scripts/r1_t90_callgraph.py
RC=0): master turn FUN_00024f24 phase order pinned (income 0x2501c ->
orders 0x25023 -> research 0x2502f -> growth 0x2503c -> cap 0x25056 ->
per-race AI 0x25083/0x250a5 skip-player -> scored-star scan 0x250aa);
build-selector caller-side CONFIRMED (0x3f130 called ONLY from the
queue-empty planet loop 0x3eade, gate [+0x5a]==0 && [+0x54]==0xff — t28
law re-verified); EXPANSION LAW closed-by-decompile for the SELECTION
half: FUN_00040018 = tech-legal candidates (0x46d3c prereq-chain law)
-> preferred-list scan (runtime 0x67be, 11 u32 template) -> rng%100<45
sentinel -> uniform fallback; target stored DAT_00076492[race]
(19-site writer/reader census cited); RESEARCH COMPLETION law cited
(FUN_00046aec: progress = +1/planet gated (govtype 0x13bc4==2 && word
<15) + planet RES word; x1.2 (0x3feb3333 pair); >= cost -> mask +0x4a/+0x4b
set); ship orders FUN_00040178 kind/target +0x58/+0x59 + congregation-
to-nearest-friend via starlane table 0x45beb (0x4aa10) [verified]. STILL
OPEN (rides this row's expansion-cadence + remaining minutiae):
research PICKER CLOSED t91 (W6-A4): field identity 0x74744+0x1d4e ==
DAT_00076492 (turn call site 0x2502f EAX=0x74744; exhaustive disp census —
raw u16 0x1d4e scan 6/6 sites all in FUN_00046aec/0x46e84, disp32 0x76492
19 insn sites, pin tool scripts/r1_t91_picker_census.py RC=0); AI picker ==
FUN_00040018 (value-writers 0x40164 picker + 0x47e34 UI; gate 0x3eb1d calls
it iff target==0xffff): legal-candidate build (skip owned, FUN_00046d3c
prereq chain) -> preferred-list scan (static 0x67be, 23 u16, zero writers)
-> DAT_00074902-bit race rng%100<45 sentinel -2 -> uniform rng — SAME law
as the t90 expansion pick: research + expansion target are ONE per-race
slot. Build-completion path FUN_00046e84 (sole caller 0x39173) GRANTS rng-
chosen legal tech directly (mask +0x4a/4b) and never writes the target word
(aicode.md §3b). rewrite researchPhase uniform pick = delta t92. t92 PASS
(budget-interrupted, honest negative, NO code change): picker body
0x40018..0x40175 fully disassembled — precedence MEASURED-CORRECTED to
sentinel(-2) > FIRST-preferred-member > uniform (guards 0x400fb/0x4010d/
0x4013b, aicode.md §3c); preferred-list membership math: on the 66-main
table only values 1 and 47 can ever match a candidate row; sentinel flag
DAT_00074902 measured LIVE 0x0f (all 4 AI flagged) in playcap 60.sav,
0x00 in r1deep slots (probe self-validated rowcount 66 + row-0 mask);
-2-consumer semantics named residual; full t93 implementation decision +
pin-test spec banked aicode.md §3c. t93 CODE LANDED (picker sub-law
CLOSED-with-code-site): §3c's sentinel model CORRECTED by re-verifying the
disassembly — uniform leg 0x40134 tests chosen>=0, so -2 is OVERWRITTEN
before the 0x40164 store; sentinel skips ONLY the preferred scan (0x400fb),
flag-0x0f shipped AI research uniformly at 100% of pick opportunities,
-2-consumer residual UNREACHABLE (aicode.md §3d). rewrite delta:
campaign.h aiResearchPreferred (tier decision, membership {1,47} §3c math)
+ campaign.cpp researchPhase AI branch = FUN_00040018 tier chain
(row-order candidates cap 32, rng%100<45 roll, preferred-first else
uniform 0x4013f; player path unchanged); TEST
campaign_research_picker_law_oq016 (edges + campaign leg), 110 tests 0
failed; timelines re-measured FINITE <1200: 2024 Control t737 / 42 Extinct
t688 / 13 Extinct t503 / 1 Control t836 / 2 Control t657; PLAYTHROUGH
regenerated. Remaining (row STAYS open, strict-close): order-ENUM numeric
law (W6-A5),
0x43b50 tail + 0x2ef60 case bodies (A6/A7), random-event module P0. t94
W6-A5 MEASUREMENT PASS (honest negative, NO closure): SO name table
dumped (8 names stride 20 @0x88e60, pool-rel 0x62b0+20k); +0x58 store/
reader census 56 verified obj0 sites (new tool r1_t94_order_census.py);
exec semantics cited: kind5=travel-to-star consumed into 4 by 0x21f58,
issuer 0x220a8, {3,1,2}->4 retreat downgrade 0x220f2; UI 6-way dispatch
0x1de40 on jump table 0x8c90 = LE-fixup-encoded, UNDECODED (the named A5
closer: fixup-decode or live pointer-law capture -> case bodies -> name
tie). Numeric->name mapping NOT made; aicode.md §2f-supplement. t95 PASS
(jump table CRACKED, name tie one step short, NO closure): decode law
MEASURED — the table is NOT at member B+0x8c90 (pool data sits there; naive
pointer-law read is silently wrong); the live loader relocated the DISPATCH
jmp disp32 (member B+0x1de53) to 0x1dcc90 == 0x8c90+0x1d4000, and the six
entries at member (disp+136) are case-body runtime addrs img+0x1d4000 in the
sub-0x14bb0 code gap: kind0 0x8dd9 / kind1 0x8f9f / kind2 0x906b / kind3
0x914d / kind4==kind5 0x8dfb (SHARED display tail — consistent with 5->4
collapse). VALIDATED on 3 slots (playcap/41, r1deep-…190330/41, r1deep-…
224831/41), tool scripts/r1_t95_jumptable.py RC=0. All six bodies
disassembled live: each calls string-getter 0x1e0e70 with EAX=index (kind0
3, kind1 4, kind3 8 then 9; kind2/kind4/5 none) then the shared batmode.cpp
tail (fmt '%s %s' star-name + 'POWER %d MOVES %d INTEGRITY %d' via 0x2360c9,
blit 0x1eef88). A5 residual = ONE read: 0x1e0e70's string-table base+stride
(img 0x140e70, normal obj0 law — not in the gap) maps indices->names; NOT
done this session (budget), names NOT tied, row STAYS OPEN (strict-close).
aicode.md §2g. No rewrite change (ANALYSIS-ONLY). t96 CORRECTION PASS (t95's
decode PREMISES refuted by address-law re-check; two sub-laws CLOSED-with-
code-site, row STAYS open): the "fixup-encoded garbage / unreadable gap" was
a member-index artifact — cs-base 0x8c90 == FILE 0x1d840 in the restored
image, where a CLEAN 6-pointer table sits (0x1d989/0x1db4f/0x1dc1b/0x1dcfd/
0x1d9ab/0x1d9ab; live entries = file+P0 exactly, banked law; no fixup decode
needed). Disassembled statically: the dispatcher is the SHIP-PANEL STATUS
text builder, mapping kind->static.txt TEMPLATE (kind0 'Sun %s', kind1
'Planet %s'+[+0x57], kind2 star-name + '\nMoving to Star Lane/Planet' by
+0x5d, kind3 'Star Lane'/'Red Link', kind4==5 tail POWER/MOVES/INTEGRITY)
— IT IS NOT THE ORDER-NAME MAPPING, so t94/t95's named closer was chasing a
wrong target (REFUTED-ROUTES R13). STRING-GETTER LAW CLOSED (FUN_00021a20 +
init FUN_000218b4): getter(n) = nth quoted string of game/static.txt (191
strings, runtime table data-intra 0x10ba8 => P0+0x93758, count ds:P0+0x959bc
live 191 — file order verified live, entry 3='Sun %s'); +0x5d ACT ENUM
census (9 imm sites 0/1/2, pairs +0x5e=act target; display guard cmp 7).
SO-name->kind numeric tie STILL NOT MEASURED: block F 0x88e60 has 8 names +
2 'BAD' (kind domain 0..5 — block indices != kinds [inferred]); sole code
ref 0x1dae5 copies the 200-B block to stack, no [esp+0x10] reader found in
window scan 0x1c000..0x1e500. Banked aicode.md §2g-correction, §2h with 3
named hammers. No rewrite change (ANALYSIS-ONLY). t97 CONSUMER PASS (all 3
hammers executed, honest negative, row STAYS open): helper 0x2fb38 disasm =
Watcom staging scaffolding (byte-writes [obj+0xf3], conditional 0x5e940
call; 106 callers = every string zone), NOT a relocating helper and NOT a
consumer; display fn full extent 0x1d989..0x1df18 has NO reader of the
[esp+0x10] SO slot (act-arms 0x1de9c use [+0x5e]+0x1c/+0x24 names, static
.txt only); 20-stride indexed census (152,831 insns) = 6 sites, all esp-frame
printf arg tables, none pool-backed; pool-rel imm census (t94 blind spot:
static-file form only) found 14 candidates, 13 decode artifacts under
disassembly, 1 real = 0x1dae6 (known copy); LIVE census (playcap/save/60.sav
self-validated): ZERO u32 in 16 MiB RAM points into the relocated block
(P0+0x88e60..+0xc8) in any byte phase; computed-jump table census obj0:
9 sites, the only batmode-zone one is t96's F 0x1d840 status table — no
second kind-keyed table; contrast: dip-state name cluster has 62 imm
referrers (a consumed table looks like THAT). Block's debug-symbol-table
signature is now STRONG but no cited debug-format tie exists in reach, so
strict-close keeps the row open. Next hammer (named): WLINK ID-Info parse
of ascend.exe debug region (LE delta +0x2a50 pinned; raw u32==block-foff
census already NEGATIVE — any tie is object/segment-relative; fetch the
record-layout spec before parsing, format guessed wrong twice). t98 WLINK
VERDICT PASS (spec-first, IBM LX spec rev 11; tool scripts/r1_t98_wlink.py
RC=0, seals: objtab->optab->resname tiling byte-exact, module name 'corn'):
ascend.exe SHIPS WITH NO DEBUG INFO — DEBUG INFO OFF/LEN (header +0x98/
+0x9c) = 0/0 (spec: zero = table absent), zero debugger signatures file-
wide (NB03/NB00/ODIAG/DWARF/OS21001), each SO name occurs exactly ONCE
(the block itself; no nonresident name table DW(le+0x88)=0), no module-
name vocabulary ('.obj' 0). The SO block lies inside the demand-page span
(0x17600..EOF) = plain image data, not a container table; t97c's parse bug
root-caused (DW(le+0x30)=FIXUP SECTION SIZE, not objtab; LE object table
has NO name strings per spec §2.4). CONCLUSION: the name->kind tie is
UNMEASURABLE by any remaining route — A5 component CLOSED as debug-only
identifiers (t97 rule): names survive from a stripped debug build, are
consumed by NOTHING (t97 live+static censuses), and the kind->USER-visible
mapping lives in game/static.txt ONLY (t96 string-getter law). The
index==act-value reading (act domain 0..7 matches 8-name extent) STAYS
[inferred], never measured. Row remains OPEN for its remaining A6/A7
minutiae (0x43b50 tail, 0x2ef60 cases). LE-debug route -> REFUTED-ROUTES
R14. rewrite delta: NONE (ANALYSIS-ONLY). t99 W6-A6 CLOSED THE A6/A7
RESIDUAL ITSELF (aicode.md §6, tool scripts/r1_t99_maint_census.py RC=0):
FUN_00043b50 = per-race SPECIAL-ABILITY CADENCE ENGINE; jump table FILE
0x43b10 (+0x14bb0 law); key row+0x19d = ability number (sole writer 0x4460f
in the RACE%02d.DIP loader); ALL 16 bodies cited and matched 1:1 to
help.txt ability text (5 HealShips .. 20 IndustryBoost, 15/18 NOP);
row+0x19e = counter (+1/turn iff [[row+7]+0x14]&0x80, reset on fire, exact
== cad fires event 24); 0x6780 = CHARGE-DAYS table (feeds OQ-020). Row
STAYS OPEN (strict-close): rewrite deltas unimplemented (t100), event-24
consumer + dx-switch adjudication open. t101 RE-ATTRIBUTION PASS CLOSED
THE §6.4 NOTE (tool scripts/r1_t101_field_verify.py RC=0): vendor panel
arm 0x1da8a..0x1daaf bytes pin [ship+0x88]=POWER, +0x94=MOVES, +0x8c=
INTEGRITY into 'POWER %d MOVES %d INTEGRITY %d' F 0x831c9; the t90 §2e
"race-maintenance legs" (0x43bd0/0x43c0a/0x43c5b) are REFUTED — all three
loops are edx==1 ABILITY bodies (jump table FILE 0x43b10 16/16); per-turn
recharge = FUN_0004a74c [ship+0x88] := trunc([+0x18]*(1+clamp((T-[+0x52])
//100,0,10)/10)) at 0x3e7b0 (T = ds:0x12e10 live 1254) — law verified
25/35 exact + 35/35 bounded live, five zero-POWER war-fleet rows remain
[unverified mechanism] (docs/re/_wip_t101.md F8b). t102 CLOSED THE
EVENT-24 CONSUMER RESIDUAL (aicode.md S7, tool
scripts/r1_t102_event24_verify.py RC=0 five legs): pump FUN_00055ae8
type-switch decoded EXHAUSTIVELY — type 24 (and 10..14/21/22/24/25/>=26)
has NO effect arm (ring-maintenance null, 0x55d02/05/d10 -> 0x55d69);
SPLIT LAW: producer gate race==ds:0x7458e (0x3e7d5..0x3e7e7) == the
0x3eb3c sync-dispatch skip gate — AI races run SA_ bodies SYNCHRONOUSLY
in the FUN_0003e6e0 turn tail, the local race's due-ability event is a
pure EVENTWIN UI refresh, human abilities fire via UI path FUN_00037b6c
dx==1 (0x37cb1, edx=1). F8b drain sites attributed (completion leg
0x41ded ZEROS POWER+MOVES, jump table FILE 0x41244 7/7; five rows =
post-recharge drains with +0x52 ETA re-stamp 5/5 on 59+60.sav) but NOT
capture-observed — direct playcap at order-completion is the closure
path. t103 CLOSED THE DX-SWITCH RESIDUAL (aicode.md S8, tool
scripts/r1_t103_dxswitch_verify.py RC=0 five legs): FUN_00037b6c =
ability-window class-record handler (class pool 0x5d84 file 0x88934, +8
slot, zero rel32 callers; pump FUN_00056b5c / relay FUN_00056ca4 [class+8]
bytes pinned); dx 1|2 = PROBE 0x43b50(row,0) + 'N day(s)' countdown
(static.txt 28/29 singular iff cad-counter==1, 'OK' label), dx 50 && ebx==1
= FIRE 0x43b50(row,1) + abres%02d-from-help.txt result window (aicode S6
'abres at dx==2' expectation REFUTED), else base filter 0x33ff8;
[ui+0xccb]:=2 marker has ZERO readers (disp32 census); FUN_00043b50 reset
direction CITED counter-cad (0x44001) — t100 reset-0 model unaffected.
Positive armer of (msg 50, ebx 1) not provable statically (all 9 pump + 56
relay sites traced; input relay 0x54976 verbatim from DOSBox event record)
— live-UI-trace residual carried. t104 CLOSED THE F8b CAPTURE RESIDUAL
OBSERVATIONALLY (aicode.md S7.4 adjudication, tool
scripts/r1_t104_drain_verify.py RC=0 four legs, pass over the banked
playcap stream 44,928 rows): completion drain OBSERVED executing on
continuous tracked records (4 events, days 369/678/945/1017 owner0 slots
3/14/10/28: POWER +0x88 >0 -> 0 WITH order-state +0x5d cleared 0x3->0 in
one sample pair; POWER restored at the NEXT boundary == FUN_0004a74c);
CONTROL burn class (b5d unchanged, 126) separated. The five static zero-
POWER rows on 59/60.sav are REFUTED as completion drains — all five slots
2/4/11/12/15 DIED mid-t1253 (war turn) and reappeared at t1254 as post-
death free-record reuse (slot4 design 2->4, ETA re-stamped 1257..1264 >
T=1254 per the 0x40e96 stamp law); no recharge-law exception. Row STAYS
OPEN (remaining: per-cell terrain/nuke wiring, home-placement
verification, +2 residual minutiae, scenario-template preset source,
live-UI-trace armer residual). t105 CLOSED the last two aicode.md S6.4
ability-engine residuals [verified, scripts/r1_t105_verify.py RC=0 five
legs]: (a) SA_Cornucopia min key WORD[planet_rec+0x42] IS the population
counter (identity with the t24 CLOSED pop law; body 0x43de4 pinned, pool
0x2b057 stride 123; race-row +0x42 premise in the assignment was FALSE —
pointer garbage, GOVOROM = ability number 10, no GOVOROM race row in the
campaign); (b) the "stride-45 table 0x74782" REFUTED — index math 75*t
byte-pinned, word = restree runtime cost (base 0x74744, cost@+62, live
66/66 vs the OQ-013 law). Row status UNCHANGED (the same open set stands).
t106 REFUTED the scenario-template PRESET-SOURCE attribution for the +0x55
seed residual [verified, six independent measurements, docs/re/income-law.md
T106]: deviations are RUN-LOCAL not NAME-LOCAL (7/15 r1deep runs have zero
deviating planets; 41/424 names ever deviate; none deviates consistently; flat
across +0x16 rows 0.58-3.00% and sizes 1.17-2.76%), FROZEN for the run (single
grid fingerprint + constant d across all 20 saves of the 15-deviation run ->
rules out mid-capture terrain writers and extraction aliasing), NOT array
aliasing (6/322), NOT found in any data file (contiguous slot-block join: DEV
3/29 vs CTRL 12/72 external hits across Memory + restored image + 471-file
corpus; T54b already proved the preset blocks are EXE constants), and
header-INDISTINGUISHABLE from law-holding records (a +0x6b==105
"discriminator" was a single-event artifact, z-test over 8282 records). The
complete corrected word-writer census for +0x55 is FOUR sites — 0x37f9a seed,
0x39224 item-37 +10, 0x44054 owner-scan +2, 0x3a664 planet-record constructor
copy (FUN 0x3a558, callers 0x258dd/0x26044) — none able to store an arbitrary
per-planet value. Residual reading [inferred]: the banked "first saves" are
MID-campaign states (41..56.sav), so a generation-scoped law was audited after
40+ turns of event drift; the +2 scan explains the small positives. TOOL LEG
same turn: r1_t86_write_census.py never prepended the 0x66 operand-size prefix
and desynced its objdump window, so NO 16-bit word write had ever been in its
candidate set — fixed, ~~+0x55 now 12 verified sites (4 word), +0x42 28
(including colonise 0x23cac)~~ [t109 PURGE: those counts were inflated by the
third verifier defect; corrected = +0x55 6 verified / 5 in-code / 4 WORD,
+0x42 23 verified / 19 in-code / 13 WORD, colonise 0x23cac survives —
census-audit.md S2/S9]; r1_t106_writers.py is the boundary-checked
variant. Row STAYS OPEN (remaining: per-cell terrain/nuke wiring, home-
placement verification, +2 residual minutiae, event-dispatch caller of 0x4402a
(capture-class), live-UI-trace armer residual; "scenario-template preset
source" REMOVED as refuted). t107 AUDIT OF CENSUS-CITED CLOSURES
(docs/re/census-audit.md): fixed-tool + NEW full-op tool
(scripts/r1_t107_writers_full.py) re-ran +0x44/46/48/4e/50/52/54/58/5d/66/67/
88/90 — NO closed row falsified (planet-field laws trace to the t23 w16-mask
census, not r1_t86); three in-place doc amendments (combat.md S2d +0x90 14th
writer 0x49307; aicode S6 kind imm-0 0x24a00 + imm-2 0x3ca60; aicode S7.4
third burn path 0x41d80 DEC +0x88). Row status UNCHANGED. t108 RE-AUDIT OF
REMAINING CENSUS CLAIMS + +0x66 ATTRIBUTION (census-audit.md S6-S8): all five
outstanding census-cited claims HOLD under whole-span function-start decode
(0x7458e two-store law, [ui+0xccb] dead marker (store addr corrected
0x37bbb->0x37bb9), FPU-no-+0x67 negative scope-annotated, t88 caller census
re-run green RC=0, diplomacy stride-0x1ee census = retracted RAM-value census,
no tool liability). THIRD tool defect found + fixed: boundary_ok fallback base
== addr self-verified 16-aligned byte-op candidates (27 "+0x66 in-code" sites
-> 15 real) AND objdump wrapped-tail lines broke mid-insn coverage — both
tools patched, controls green. +0x66 flag law now PROVEN COMPLETE: the banked
|=1/|=2 pair (0x39229/0x37f7b) is the only planet-record flag OR-ing in the
image (others = planet template copy 0x3a696, ship-design table 0x490e3/23a
stride 0x6a, stack-locals in shp-cache callers). One phantom citation (0x390a0)
corrected in S3. Row STAYS OPEN (open set unchanged: terrain/nuke wiring, home
placement, +2 minutiae, 0x4402a caller [capture-class], live-UI-trace armer).
t109 COUNT-COLUMN PURGE (census-audit.md S9-S10): S2's inflated per-offset
counts replaced in place with authoritative-rule numbers (full-op in-code:
44:22 46:7 48:10 4e:8 50:13 52:23 54:22 58:32 5d:25 66:15 67:30 88:23 90:14;
WORD counts unchanged on all 13 offsets — phantom load was byte-op-only);
+0x55 FOUR-site word list and all four t107 amendment sites re-verified to
survive the fix verbatim; closing control r1_t108_disp32_audit RC=0 reproduces
S6 exactly. Tool liability (t106/t107/t108) BOUNDED CLOSED; no banked law
changed. Row STAYS OPEN, same residual set — all remaining open rows are
capture/user-gated (no offline static work remains).
t179 CONSOLIDATED STOCK-AI DOSSIER (docs/re/ai-dossier.md, synthesis + verdict,
no ledger movement): the deferred player question ("does the AI defend systems
and choose offensive thrusts or is it haphazard?") is ANSWERED with citations —
policy-driven not plan-driven: cited doctrines (threat-byte shield buying
0x3fc4c/income-law S9, fleet congregation 0x40178, strongest-first 0x40eb4,
retreat-downgrade 0x220f2, sticky orders, Invasion-Module-gated assault) vs the
bounded negative that NO site scores enemies or plans at system level (target
slot DAT_00076492 = research row index; engagement resolver 0x42c60..0x42e6e =
first-eligible in list order, t179 P3 probes; rel32 census: 0x41260 has exactly
2 callers, 0x39894 gate has 8 — t179 P2). Row STAYS OPEN; residuals unchanged
(A5 name tie, P0 event window; OQ-023 state-3 WRITER FOUND t180 —
residual is now the live cell==3 observation only, diplomacy.md §13) — dossier §7 states the
scope of search explicitly. Gap map dossier §8 (17 rows; threat input, demolish
channel, per-ship model = the three big rewrite gaps). STATUS t201 (AI GAP ROW 3 CLOSED, gap row 4 queued t202): THREAT-BYTE INPUT LAW MEASURED + EMERGENCY CHAIN FUN_0003fc4c CITED + REWRITE WIRED — +0x59 = #{ACTIVE slots, item FLAGS bit8} (shields 18/19/26/27) EXACT 2900/2900 corpus records; +0x58 = bit4 set (17/28/29/30) 2880/2900 (20 misses = evaluator self-init 0x3fb3e); recalc FUN_00038ba4 zeroes+derives both every run (tools r201_threat_writers/census/law_verify RC=0). Chain: XenoDig(+0x66 bit1, rock-arm 0x37f7b) > Shield18 (IND>=4,PROS,Shipyard present,freeCells>=3,+0x59<6) > MegaShield19 period tiers 200/225/300/400 VERBATIM 0x3fd73..92, UNSIGNED (day-+0x67)/period > +0x59 @0x3fda1 > Cloaker11 (owner odd, IND>20 STRICT, rng<4) > template MEASURED {12,13,14,15,37}. Rewrite: emergencyChainPick+periodFor+threatFor wired into buildPhase pre-scoring (0x3f4d5 ordering) + pin campaign_emergency_chain_law_t201 (115 tests 0 failed). Row STAYS OPEN (strict-close): gap row 4 (over-pop/min-REQUIRES demolish, t202), chain-C row-operand identity [+ctx7->+2>>16] UNVERIFIED, +0x67 buy-path stamp write-site uncensused-to-hit — all documented ai-dossier.md S10. STATUS t202 (AI GAP ROW 4 — DEMOLISH CHANNEL: LAWS MEASURED, CODE DEFERRED to t202b, docs/re/_wip_t202.md S1..S14): +0x4c USED-POP law MEASURED — UPOP sum over ALL slotted items (excl item23/flags&0x40/slotflag&2) 2760/2900, Automation-bonus shape explains 140 residuals (r202d_usedpop_models.py RC=0; t28 pending-only reading superseded). OVER-CAP branch LIVE: 220/2900 records used==pop==cap fire 0x3f178; victim law CORRECTED from t28 — LARGEST UPOP among MPOP==0 non-Colony-Base cells (0x3f1bb skips MPOP!=0; 0x3f1c1 reads byte+4), ties keep first cell. PRE-TRIAGE GATE 0x3f252 (t28 never banked): triage runs iff emptyNonRock<2 OR (emptyNonRock==emptyBarren AND ability!=BuildOnBlack[diplo+0x19d==2, census {0:19,1:2,2:11,3:0,4:8} 60.sav]). MIN-REQUIRES SWEEP 0x3f354 verbatim (margin cap-pop, 0xFF REQUIRES PARTICIPATES — sentinel 0x1869f never prunes). Tubes 0x3f2c8 stays DEAD-code (mask all-zero t28). t201 caller wiring re-verified FAITHFUL (0xffffffff-on-buy vs 0-on-no-force, S12 — do not "fix"). ZERO demolition event witnesses in ring (honest negative; preconditions measured instead). t202b = pure code + pins per _wip S14. Row STAYS OPEN. STATUS t202b (DEMOLISH CHANNEL CODED + PINNED — gap row 4 GAP->MODELLED): usedPopFor UPGRADED to the measured M4 item-UPOP sum (campaign.h, excl item23/flags&0x40, gov-35 term kept; pin campaign_used_pop_item_sum_t202b). buildPhase AI branch now runs over-cap 0x3f178 (picker overCapDemolishPick: skip CB, skip MPOP!=0, STRICT max UPOP, first-cell ties, UPOP==0 never wins; no-candidate -> skip selector = 0x3f20b assert-return path; recheck used'>=pop -> skip) -> no-free-pop 0x3f220 -> PRE-TRIAGE gate 0x3f252 (runs iff eNR<2 OR eNR==eB && !BuildOnBlack) -> min-REQUIRES sweep 0x3f354 (minRequiresDemolishPick, NO CB skip, 0xFF participates) -> shared gate 0x3f41e (eNR==0 -> skip; eB==eNR && !BB -> skip) -> t201 chain + scorer UNCHANGED. Pins campaign_demolish_pickers_t202b (edge classes incl tie-first-cell, CB-skipped-in-overcap-but-not-sweep, 255-participates) + end-to-end campaign_over_cap_demolish_e2e_t202b (planet at used==pop==cap demollishes one Factory in ONE advance and queues) + campaign_barren_sweep_demolishes_cb_e2e_t202b (eNR==0 triage sweeps the CB: REQUIRES 5 < 255). 119 tests 0 failed. BLAST RADIUS MEASURED: 0x3f220 is now REAL traffic — AI builds serialize behind pop growth (seed 42 first colony t169->t279, seed 2024 Control win t831->t1255, CLI-verified FINITE); three pacing guards widened (campaign_total_owned 220->420 turns, species/ships victory guards 1200->1600) with dated comments — pacing windows, NOT laws. income-law.md S9 OVER-CAP paragraph CORRECTED (largest-MPOP -> largest-UPOP-among-MPOP-0, byte identities cited) + pre-triage gate + sentinel reason folded. Row STAYS OPEN (strict-close): no in-corpus demolition EVENT witness yet; +0x54 word identity mid-game, 0x3f4b8 cmd1-on-tail semantics, M3-shape 140-row discriminator remain [unverified] residues (_wip_t202 S14). STATUS t203 (AI GAP ROW 7 — FREE-TECH GRANT MEASURED + CODED + PINNED, docs/re/_wip_t203.md S1..S4): FUN_00046e84 0x46e84..0x46f9d disassembled VERBATIM (capstone revenv). CALLER GATE SEMANTICS CORRECTED vs dossier S3c: the gate 0x3913b is ITEM-BLIND — key = completing slot byte0 bit3 (the ROCK marker, mapgen drawer 0x37f7b; placement rule D 0x38533..0x38552 legal iff (byte0&8)==(itemIdx==0x26) makes item 38 Xeno Dig the ONLY item ever placeable on rock, so dig-on-rock completion IS the grant trigger); rock branch: byte0 and 0xF7 + slot freed 0x39164 (dig consumes itself) then call 0x46e84; non-rock branch 0x3917a normal activation, NO grant. GRANT LAW: candidates = rows 0..65 MINUS research target word (0x46ee6 [base+race*2+0x1d4e]==DAT_00076492, t91 identity) MINUS owned ([row+0x47]>>0x18 & 1<<race); NO prereq legality call exists in 0x46e84 (calls = assert 0x46ec2 str 0x8504f research.cpp, rng 0x46f23, event 0x46f8c) — dossier S3c 'legal rows' CORRECTED: grants land DEEP, prereqs unmet; rng 0x7824f = 15-bit LCG always >=0 so idiv uniform, empty-guard 0x46f1c precedes the draw (no draw when count==0); mark +0x4a/+0x4b |= 1<<race; TARGET WORD NEVER WRITTEN (sole +0x1d4e ref is the read). Rewrite: freeTechGrantFor (campaign.cpp, rng_ stream documented default — original single-stream draw ORDER unrecoverable), drawItemCell rule-D dig exemption (dig draws draw ONLY from rock cells), buildPhase dig-completion branch (rock clear + item consumed + grant; no-rock fallback = item stands 0x3917a-faithful). Pins test_freetech_t203.cpp x5 (owned+1 per grant/exhaustion -1, target-exclusion, e2e dig-on-rock grants exactly 1, dig-on-nonrock grants 0 + item stands, seeded determinism) — 124 tests 0 failed. BLAST RADIUS: seed 2024 still Control t1255 FINITE, seed 42 Extinct t979 FINITE (CLI, this session). Row STAYS OPEN (strict-close): zero in-corpus GRANT event witnesses (0x55a60 code-0x16 event never observed in ring captures — grant fires rarely: dig-armed AI + completed dig + legal rock); 0x55a60 event-string identity + EDI=0xffffffff quirk unmodelled (cosmetic); rng stream ORDER inside completion tail unverified. STATUS t204 (DIPLOMACY-ON-ATTACK CODED + PINNED — gap row 13 GAP->MODELLED, docs/re/_wip_t204.md + diplomacy.md S17): FUN_00043a4c re-verified VERBATIM 0x43a4c..0x43b0e; TWO LAW CORRECTIONS vs t87 S2f-b: subtrahend key = MOVSX BYTE[0x13bc4] not word (live ==1 in 20/20 playcap saves => d=20, state-3 doubled 40; assignment's '==2 => 30' did NOT reproduce), and the state-3 clamp is a CEILING (0x43ade JLE skips when att<=word[obj+0x1cf]=BREAK_ALLIANCE; slams to line-10 only when STILL above) => firing at an ally GUARANTEES the alliance dies. CALLER CENSUS (E8 byte-pass): EXACTLY {0x39fba,0x3a255 planet-event (esi+0x57 victim, 0xff skips), 0x4b875 combat damage-apply BEFORE the shield/hull subtraction 0x4b87a/0x4b888 — price of FIRING, repelled attacks pay too}; row=VICTIM 0x12e16+0x1ee*r, EDX=attacker; EBX=species record 0x13bc5+0x60*r, bitmap base [dword[edi+2]>>16]. Rewrite: applyAttackDipCost (diplomacy.{h,cpp}) + kAttackDipGovByte=1 + Campaign::attacked_ byte/attackedMarks() mirror of [0x48304] PERMANENT (no clear incl. peace); combatPhase wired at the 0x4b875-position, player-attacker only (two-party projection gap row 12 — AI-AI engagements have no attitude cell, banked). Pins test_diponattack_t204.cpp x4 (battery: at-war guard/gov 0-2 ladder/double/ceiling engage+exact-boundary JLE-skip+d0-still-marks; e2e 340->320 exact + cascade->declare@280->at-war freeze@256; alliance violation -40 -> break same turn; ceiling e2e 520>510 -> 500 -> break) — 128 tests 0 failed; blast radius UNCHANGED (seed 2024 Control t1255, seed 42 Extinct t979). Row STAYS OPEN (strict-close): HONEST NEGATIVE zero in-corpus attack-event witnesses ([0x48304]==0 20/20 saves — nobody fired at a non-at-war power in captured play); [0x13bc4] row identity (species-table base vs standalone) open; planet-event callers unwired (no planet-attack-event model); per-shot stacking vs per-engagement aggregate (S2i pattern divergence). STATUS t205 (TABLE IDENTITY ADJUDICATED — docs/re/_wip_t205.md, tools r205_table_identity/r205b_operand_census/r205c_strided_consumers/r205d_windows RC=0): 0x13bc5+0x60*k k<50 IS the per-STAR runtime table (t200 wins): 36 absolute-base sites on 0x13bc5 vs ZERO strided sites on 0x13bc4 image-wide; live census 20/20 saves rows 0..49 initialised, u32[+0] in {0..12} for ALL 50, boundary == star count 50 (u16[0x16145]) not race count 4; dword[0x13bc5+96k+2]>>16==k (self-handle) 20/20. 0x13bc4 = ABSOLUTE SCALAR global (all 8 refs scalar byte reads incl 0x43a99; zero writers enumerated; gates on ==2 never fire in captured scenarios — semantics need a save where they do). [0x48304] CORRECTED: PER-STAR byte array (byte[0x48304+star_idx] |= 1<<victim), t204's single-byte mirror replaced (attacked_ vector + attackedAt(star); attackedMarks() OR-reduce keeps pin surface; honest negative SURVIVES: full window 0x48304..+0x3f all-zero 20/20). Rewrite: combatPhase marks the engagement star; pin diponattack_mark_is_per_star_t205 — 129 tests 0 failed; blast radius UNCHANGED (seed 2024 Control t1255, seed 42 Extinct t979). Docs corrected in place: diplomacy.md S17.1/17.3, income-law.md S6-caveat(a), ai-dossier S2 para + row11 housekeeping (ForcePeace/CauseWar WIRED; 'Hatred' not a token). Row STAYS OPEN: mark-array consumer law (readers 0x4162f/0x42bd2/0x45e8d/0x4610b/0x46213 + bit-0 pair 0x24e39/0x24e84) unmapped -> t206; zero attack-event witnesses. STATUS t206 (ATTACKED-MARK CONSUMER LAW MEASURED — docs/re/_wip_t206.md + diplomacy.md §18 NEW, tool r206_mark_context_census.py RC=0): the mark byte carries TWO INDEPENDENT channels. VICTIM BITS 1..7 (writer 0x43afa): consumers are the ORDER RESOLVER 0x41260 only — 0x41610..61 owner==player [0x7458e] + unit-at-star -> status byte |=0x20 (under-attack alert); 0x42b7d..e8 same test -> action-availability eligibility (WAR-relation guard 0x42bb1 adjacent) — NO diplo-value/AI/emitter feed; t204's PERMANENT mirror SURVIVES head-on (0x4610b/0x4611c = 'or cl,1' bit-0 OR-set, not decay/transfer; sole victim clear = setup fill 0x25008 in star-init 0x24f24, single caller 0x55f06). BIT 0 = contact/announcement latch never written by the attack handler: 0x45e48 (caller 0x4a90a march body, gate 0x45e93 BEFORE fire-then-latch 0x4611c, event code 3/0x14, 0x55a60 arg 0x7a35c = event-ring game object NOT a string), 0x46144 first-contact establish (relation byte 0->1 PEACE init 0x461a8 + bookkeeping, latch AFTER 0x4623e, codes 8/9), 0x24dd0 (callers 0x55ed0/0x55f98: clears bit0 on ALL stars — bound u16@0x16145 MEASURED 50==star count 20/20, C1 handle-index==0 20/20 — then latches + announces ONE star/Call via event 0x13 iff vision + WAR occupant + [occ+0x88]>0): call-scoped duplicate-notice suppression, NOT permanent. REWRITE NO DELTA (mirror faithful: no per-unit alert layer, no notice queue; pin mark_channels_separate_t206). Gap row 12 residue SHRINKS (bitmap no longer owes the ladder an explanation). Row STAYS OPEN (strict-close): C3 window 0x48304..+0x3f ALL-ZERO 20/20 — zero witnesses for every bit-0 branch (post-first-contact nobody-fires corpus); event-code semantics = ring codes; [0x13bc4] semantics still open. STATUS t207 (PLANET-EVENT CALLERS OF 0x43a4c CLOSED — CALLER THREAD COMPLETE + GUARANTEE-WAR LAW CODED/PINNED, docs/re/_wip_t207.md S1..S7e, windows work/t207_w1..w16, tools r207_disp_cluster.py + r207_opinion_census.py RC=0): E8 full-image census of 0x43a4c EXACTLY {0x39fba,0x3a255,0x4b875} — all three now accounted. 0x39f00..0x3a098 (sole caller 0x4c97f = gizmo-attack shared tail, gated success+mode1+design cat==0 AFTER power subtract 0x4c960) = GUN-BOMBARDMENT path: victim = planet owner byte [esi+0x57] (0xff skips), star = [esi+0xa]>>16, dip price FIRE-AND-FORGET (return discarded 0x39fbf) + planet item-loss tail; rewrite HONEST NO-DELTA (no per-ship bombard channel; item-loss = OQ-019 family). 0x3a174..0x3a4df (callers {0x3d951 race-family [unverified context], 0x42c8e order-resolver t179 invasion leg}) = INVASION/CAPTURE RESOLUTION: slot must be item 0x17 Ship -> 0x396cc maps handle to ship record 0x3a095+0x162*i; attacker = ship owner [ship+0x54]>>16; ability gate [eax*2+0x12fb3] (eax=247a; = diplo-row(a)+0x19d, MEASURED distribution {0,2,11,19} == t202 census — scale-2 ALGEBRA CORRECTION banked S7a) ==0 -> out-param forced 1; on the handler's -1 return: 0x12fdf+494v = row(v)+0x1c9 DECLARE_WAR, 0x12fc8+494v+2a = the attitude cell (NOT the third-party matrix) — GUARANTEE-WAR CLAMP att>DECL -> :=DECL-10 (t180 chooser then declares: invading a non-at-war owner GUARANTEES WAR; 200/200 fresh pairs slam-eligible); defense law invmod vs active-0x12+2*active-0x13, strip 0x49 slots via 0x496e4, deactivate 0x13 via 0x38840, event code 0xd, tail 0x38ba4. Rewrite: guaranteeWarOnInvasion (diplomacy.{h,cpp}) wired at combatPhase capture branch; pins invasion_guarantee_war_battery/cascade/combat_phase x3 — 133 tests 0 failed; BLAST RADIUS UNCHANGED (2024 Control t1255, 42 Extinct t979). Row STAYS OPEN (strict-close): zero in-corpus clamp witnesses (mark window all-zero 20/20); positive e2e pin needs owner-0 guaranteed capture (fixture self-caught: first attempt 320!=280 because no player capture ran); clamp-vs-repel position undetermined statically; out-param semantics + 0x3d951 context open; invasion defense law unmodelled (OQ-019 boundary). STATUS t208 (POSITIVE E2E PIN LANDED + RESIDUE-LINE AMENDMENT, docs/re/_wip_t208.md): t207 residue (a) CLOSED — pin invasion_capture_war_e2e_t208 runs the FULL cascade end-to-end through the wired capture branch: player = SA_SuperMarines via CampaignConfig::playerSpecies -> ability_[kPlayer] (campaign.cpp:234-235 — the ability vector indexes OWNER, hence the new fixture param), industry cleared over the invasion ship-cost gate by NEW header-inline scenario hook setIndustryForTest (campaign.h, mirror of ind_, no production call site, zero semantic delta), one advance(): capture RAN (starOwner(1)==0), handler -20, clamp 320->280, chooser DeclareWar flipped dipState_.atWar and the post-advance cell == 280 - negPlayerTurns/4 EXACTLY (mood(1)==0 carried from t204's 320 pin); without the clamp atWar would stay false (320-neg/4 >= DECL 290 -> act None) — both arms distinguishing. 134 tests 0 failed; BLAST RADIUS UNCHANGED (header-inline hook + test only, t206 no-re-run rule; Control t1255 / Extinct t979 stand). RESIDUE-LINE AMENDMENT (both here and ai-dossier row 13): 'planet-event callers unwired' is STALE — both callers of 0x43a4c are READ (t207): bombard 0x39f00 = honest NO-DELTA (fire-and-forget price; rewrite has no per-ship gunnery channel), invasion 0x3a174 = clamp WIRED at the capture branch with the attempt-time-vs-under-fire position documented as divergence; the residue now shrinks to 'per-ship invasion/bombard channel = OQ-019 family'. Row STAYS OPEN (strict-close): zero in-corpus clamp witnesses; 0x3a174 out-param + 0x3d951 context open; invasion defense law unmodelled (OQ-019 boundary); per-shot stacking vs aggregate. STATUS t209 (LAST TWO STATIC-LAW RESIDUES OF THE 0x3a174 LEG CLOSED — OUT-PARAM CALLER LAW + CLAMP-VS-REPEL POSITION, docs/re/_wip_t209.md S1..S6): E8 re-census callers of 0x3a174 EXACTLY {0x3d951, 0x42c8e}. OUT-PARAM LAW CLOSED: 3rd arg = out-param pointer (EBX->ECX @0x3a17f); sole writer 0x3a35e `mov [ecx],eax` (full-body 284-insn operand pass: zero other [ecx] writes, ecx unrewritten before the store, NO ret in [0x3a174,0x3a35e), assert arms 0x2a428 = vendor reporter never returning); value = defense result [esp+0x14] FORCED 1 iff ability byte (row+0x19d) == 0 witness — t207's [unverified] reading VERIFIED, value also = strip-loop bound (min-1 defense consumption). CALLERS DISAGREE (the finding): engine caller 0x42c8e (order resolver) never pre-inits slot [esp+0x30c], DISCARDS the return (0x42c97 clobbers EAX; 0x42c9c = identity assert 0xbc4), and overwrites the slot @0x42cba with the 0x39894 return — out param DEAD in the engine path; caller 0x3d951 = UI announcement family (context MEASURED, residue (c) closed): reads [ebp-0x24]==1 -> message 0x1c vs 0x1d (0x21a20), ids 0x1fc5/0x1fd3 (0x56d1c), UI words [ecx+0xcb1/0xcb3/0xccc]. CLAMP POSITION CLOSED (the t207 DOCUMENTED DIVERGENCE): clamp 0x3a25a runs AT ATTEMPT TIME — before the defense-score loop even counts (0x3a29e..0x3a325), result select 0x3a327, success/repel branches ONLY at 0x3a45c (invmod > shields -> -1-sentinel tail); caller tail outcome-INDEPENDENT (return discarded, no order/ship-survival branch). => original pays the guarantee-war clamp on a REPELLED invasion too; rewrite capture-branch wiring = documented UNDER-MODEL of the attempt-time law (per-attempt wiring stays OQ-019 BLOCKED-USER; NO semantic change this iteration — campaign.cpp comment amended with cites, blast radius trivially nil). Row STAYS OPEN (strict-close, unchanged honest negatives): zero in-corpus clamp witnesses (mark window all-zero 20/20 — needs user play vs a non-at-war owner); invasion defense law unmodelled (OQ-019); per-shot stacking vs aggregate; [0x13bc4] semantics other-family. STATUS t210 (LAST STATIC RESIDUE OF THE 0x4b875 ATTACK-PRICE LEG CLOSED — STACKING LAW MEASURED, docs/re/_wip_t210.md S1..S6, tool scripts/r210_loop_nesting.py Tarjan-CFG RC=0): STACKING IS REAL but per COMMITTED WEAPON / per VICTIM, NOT per shot. 0x4b740 decodes end-to-end loop-free (every branch forward, single 0x43a4c call 0x4b875 gated cmp [esp+8],1 @0x4b7f1 — mode==1-only RE-CONFIRMED at the gate itself); six direct callers (E8 EXACTLY {0x1a146,0x39d9f,0x3a0b3,0x4bb56,0x4d191,0x4d2dd}, zero thunk sites); nesting: 0x1a146 mode-0 DEAD (xor edx,edx @0x1a13f), 0x3a0b3 acyclic mode-1 (mov edx,1 @0x3a0a9, item-0x17 t204 family), 0x4bb56 = cat0-handler-only E8 site (volley loop 0x4a5c1 calls 0x49f28 with edx=0 @0x4a5ec = dry-run, t88a holds), 0x4d191/0x4d2dd INSIDE loops of cat-5 dispatcher 0x4cd90 (sole caller 0x4a3c4 dispatcher cat5 arm — self-corrected from an earlier literal-only 'indirect' claim): splash per-other-entity 0x4d0a5..0x4d1a4 and per-hostile-alive-power 0x4d2ab..0x4d2fd (owner!=victim @0x4d2be, byte[0x12fd6+494*owner]==2 @0x4d2ca), mode invariant ([esp+0x73c] sole writer 0x4cd9d). COMMIT LAW QUANTIFIED: command-exec 0x2547c loop 0x2550c..0x25527 bound = matched-gizmo count, ONE mode-1 arm per matched gizmo (ah==3 -> gun 0x25560, ah==2 -> ability 0x25570; ah==1 ALSO traps @0x25598 — t88a correction). REWRITE: combatPhase per-engagement charge = DOCUMENTED UNDER-MODEL (under-fires per extra committed weapon at the same victim and per splash victim beyond the first; per-commit conversion crosses the OQ-019 BLOCKED-USER per-ship boundary — no semantic change, same rule as t209 clamp position/t204 volley mapping; campaign.cpp:1935 comment cites). t204 S2 'per shot' mechanism CORRECTED in _wip_t204 amendment + ai-dossier row 13. Row STAYS OPEN (strict-close, unchanged): zero in-corpus clamp witnesses (play-gated); invasion defense law + per-ship channel unmodelled (OQ-019); runtime entity-loop bounds play-gated; [0x13bc4] semantics other-family. STATUS t211 (COMMIT-CHAIN TAIL CLOSED — SECOND-DOOR NEGATIVE + SPLASH BOUND NAMED, docs/re/_wip_t211.md S1..S6, tools r211_probe_a..f RC=0): 0x49f28 dispatch = THREE arms (mov cl,[ship+0x62]; cl==0 -> travel resolver 0x49f54; cl==1 -> attack leg 0x4a360; cl>=2 -> NO call, result 0 via xor @0x49f2f). SECOND DOOR: NO — 0x49f54 entry edges EXACTLY {0x49f37}, callee closure depth-3 (24 fns) ZERO attack-family hits {0x4b740,0x43a4c,0x4cd90,0x4b8e4,0x4a360}, zero indirect edges inside the body; 0x4a360 entry EXACTLY {0x49f45}; scanner validated by reproducing t210's six 0x4b740 callers EXACTLY. The phase-flip block 0x4a350 (mov byte[eax+0x62],1 first insn) is UNBOUND corpus-wide: zero static branch edges (140,156 insns), zero image dwords, zero RAM dwords == P0+0x4a350 (3 saves, t191 binding class; honest negative, NOT claimed dead). cl==1 population = constant writers only (==1 sites 0x415b4/0x423e2/0x4245f/0x43392/0x4340f/0x43843/0x43900/0x4a350/0x4a591; 0x4a591 = the cat-0 volley preamble arms phase=1 then the 0x4a5c9 ring-slot scan dry-runs 0x49f28 edx=0 — the exact t210 dry-run loop, phase set HERE never by travel). SPLASH BOUND NAMED: [esp+0x730]/[esp+0x734] (sole writers 0x4d09e/0x4d2a4) == 4*FUN_00022304([engaging_ship+0x59]) — co-located ship count at the engaging ship's location (ship table 0x3a095+0x162*i i<108 owner!=-1; location key = star record 0x13bc5+96*idx via [[ship+0x59]+0xa]>>16 for kinds 1/2/3, RAW lane handle for kind 4; 0x22304 verbatim 0x22304..0x223a1). Splash multiplier <= N-1 self-skip 0x4d0ac, loop-2 gates owner!=@0x4d2be + byte[0x12fd6+0x1ee*owner]==2@0x4d2ca. REWRITE NO DELTA (OQ-019 boundary — no cited per-commit loop to convert; per-engagement charge stays the documented under-model). Row STAYS OPEN: residue now = zero clamp witnesses (play-gated); invasion defense law + per-ship channel (OQ-019); [0x13bc4] semantics; VALUE-SOURCE of the al-form [ship+0x62] writers 0x15c6d/0x15d98 (whether cl>=2 ever occurs, low priority — the cl>=2 arm no-ops anyway); 0x42211/0x43188 alignment-suspect (t108 law, preceding byte undecodable). STATUS t213 (AL-FORM VALUE-SOURCE CLOSED — MEASURED NEGATIVE, NO >=2 PHASE EXISTS; docs/re/_wip_t213.md S1..S7, tools r213_cfg_15b/r213_probe_a..e RC=0, scanner validated vs t210's six 0x4b740 callers EXACTLY before trusting zeros): BOTH al-forms live in the batcon order-commit dispatcher 0x156d4..0x17c25 (t211's 'UI/setup family' SUPERSEDED; r1-savestate.md:393 Ghidra class batmode/batcon E1; entry indirect — zero E8/jmp callers image-wide, sole dword==0x156d4 at file 0x88408 in a code-address table). SITE 1 0x15c6d: phase local [esp+0x50] has EXACTLY ONE byte-def (0x15c34, bl=1 from 0x15c2c inside the order-init block 0x15c14..0x15c34); CFG cut of 0x15c14 makes 0x15c6d unreachable (641->564 blocks) => phase==1 on EVERY execution; the order-arg codes {5,1,0,2} land in the DAY byte [ship+0x67] via [esp+0x55], never +0x62 (t211 mis-locate corrected). SITE 2 0x15d98: cluster [0x15d36,0x15e7c) in-edges EXACTLY {0x16329->0x15e43 (dead-ends to tail), 0x16378->0x15e23 (phase=1 then jmp tail 0x15e7c — never reaches store), 0x16391->0x15d36, 0x163df->0x15d8f}; both live chains downstream of 0x16385 mov [esp],dh with gate 0x16376 test dh,dh on the ZERO side, and the dl=2 def 0x16361 is straight-line-overwritten by 0x16385 => phase==0 on EVERY execution. 0x16e8b def = separate function 0x16e4c own frame, zero edges into cluster. Together with t211's constant-writer census the static [ship+0x62] writer population is COMPLETE and BINARY {0,1}: the cl>=2 arm at 0x49f28 is defensive dead code in the original; rewrite needs NO >=2 model (no semantic change). 0x42211/0x43188 stay alignment-suspect (excluded, NOT refuted). Row STAYS OPEN (strict-close, unchanged honest negatives): zero in-corpus clamp witnesses (play-gated); invasion defense law + per-ship channel (OQ-019 BLOCKED-USER); [0x13bc4] semantics other-family. STATIC CORPUS FORMALLY EXHAUSTED (t213 S7): remaining residues are play-gated / BLOCKED-USER / watchpoint-class only.
STATUS t214 (2026-10-30): sitting adjudication ran (trigger-A byte-identical,
zero dosbox processes, zero new saves — scripts/r214_triage.py RC=0): the
multi-volley-vs-non-at-war clamp witness did NOT arrive; row unchanged, witness
ask stands. docs/re/_wip_t214.md S1. STATUS t215 (2026-10-31, no-sitting
iteration): trigger-A byte-identical again (r214_triage.py RC=0) + independent
save-axis (newest .sav anywhere == 60.sav 10-29 13:22, zero modified since
10-29 18:00) — witness still UNOBSERVABLE, nothing re-censused (t212 law); row
unchanged, witness ask stands. docs/re/_wip_t215.md S1/S3. STATUS t251
(2026-11-01, drive + witness mining, scripts/r1_t251_mine.py, docs/re/selfplay.md
t251 section): FIRST POSITIVE ATTACK-EVENT WITNESS IN THE CORPUS — t887 (wall
15:12:56->15:18:03, trusted stream): att[Minions][Chamachies] 324->284 EXACTLY
-40 with relation state 1(PEACE)->2(WAR) in the same autosave window and NO
other state/attitude transition in the pair — the t204 price + t208 chooser
cascade observed live (-40 == two committed weapons per t210 stacking). MINUS
(honest): Minions self-declaring with a -40 slam in their own row is not fully
excluded from stream data alone; the t205 per-star VICTIM mark (byte 1<<3) is
ABSENT from every bank (bank-t1254 holds only byte[0x48304+38]==0x1 = the t206
CONTACT latch, first nonzero byte ever seen in that window), so either the fire
path used was not 0x43a4c or the mark law has an unmapped clear. CLAMP witness
(att slamming exactly to DECL-10==280) still ABSENT (284 != 280 — this is the
price, not the clamp). Multi-volley-vs-non-at-war damage channel NARROWED to a
sharp negative: named-owner ship disappearance events 0/45,227 trusted points;
shield-agg(+0x4) decreases 10, all resolvable as slot remap (owner high-u16
0xffff->N) or garbage owners; streak/multi-volley proxies on raw windows are
INVALID (day byte +0x67 churns every turn — t213). Row STAYS OPEN (strict-close):
clamp witness still unobserved; direction attribution needs the watchpoint-class
instrument. docs/re/selfplay.md t251 + docs/re/_wip_t251.md S1..S6.
STATUS t270 (2026-11-02, HOME-PLACEMENT VERIFICATION — mapgen.md t270 section,
KEEPER scripts/r270_homeplace.py RC=0, work/r1/t270_homeplace.out,
docs/re/_wip_t270.md S1..S4): the runtime HOME JOIN is MEASURED and decisive —
DWORD[data 0x12e1d + race*0x1ee] == phys of star-record base(k) (base =
NAME-0x1C, stride 0x60) exactly; at turn>=1 that star's owner byte ==
0x80|(1<<race) AND the race's own planet (t248 NAME+0x33 law) is in its LIVE
list (25/25 observations; production t1086/t1254: Oslo I@25, Philadelphia
II@27, Sarsaparilla I@18). TURN-0 frames carry TEMPLATE RESIDUE pointers
(r5=base+11/r6=base+6 constant across all fresh runs) — trust law extends
t269's turn-0 anomaly class to the race rows. HOME PLACEMENT IS RUN-LOCAL:
11 distinct home-star sets over 11 independent lineages (production banks = 1
lineage); resume.gam's 7-owner signature re-confirmed EXACTLY but matches no
live run — static init, not a template. Home slots span table 0..40 (no shell
constraint; "outer shell" and "lowest id" both REFUTED); min inter-home
184.3..440.7 units (median 358) over 14 lineages. Home PLANET = first
colonisable orbit (varies I..V; t40/t42-consistent). Row STAYS OPEN
(strict-close): the remaining home residue is now precisely the SETUP-TIME
DRAW LAW (which pool the vendor samples and any rejection test — runtime
tables cannot pin it; needs the setup code path or a setup watchpoint), and
the rewrite pickHomeStars() (campaign.cpp:301) is a documented MISMATCH
(deterministic max-min BFS spread, first-home-lowest-id REFUTED) — NOT
upgraded this iteration for lack of a pinned draw law. Star owner-byte bit7
semantics remain UNVERIFIED (t248 masks &0x7f). t271 PER-CELL WIRING SCOPED
AS DECISION (income-law.md T271, keepers r271_cellreach/tfdrill/pendctx RC=0,
1074 saves): cell model shape = slot-indexed KEPT (world-gen classes, rock
event, CB/built-item draws, channel gating, dig consume ALL already wired +
pinned t40..t43/t203); T39b item-36 Terraforming + item-35 Automation
completion branches NOT wired — MEASURED zero-witness class (35: 0 slot-obs
ever; 36: 78 pending-only obs, 0 completions; AI-unreachable by the verbatim
scorer cap rows<22 @0x3f52f + chain sets) -> REFUTED-ROUTES t271 with re-open
conditions; per-slot shield byte write reachable but consumer unmapped (OQ-019
family, no dead state added); nuke law unchanged BLOCKED. NEW OBSERVATION
banked: a pending build reserves its slot (byte1:=item id, word2 bit0 CLEAR)
— pending IS observable in idle-turn ring captures (refines t202b note; +0x4c
M4 untouched). Row STAYS OPEN (strict-close): Phase Bomb capture law, human
build-order minutiae, setup-draw law (t273 seed), shield-byte consumer,
word[+0x16] template source. STATUS t273 (2026-11-02, full-corpus witness harvest, docs/re/selfplay.md t273, scripts/r273_harvest.py+r273_vet.py, work/r1/t273_harvest_full4.out): t251's mine had TWO measurement bugs (owner HANDLE u16@+0x54 read as race index -> its relv filter never filtered; stale-echo row pairs minted phantom deltas) — its '252 non-war candidates' are VOID. Guarded re-run (72,128 pairs, prev_turn adjacency + 120 s gap): 32 hull-decrease hits, 26 AT_WAR, all 6 non-war-labelled rows FAIL the attribution vet (no ship of ANY class within 60 u; min distances 363..1854) => damage-vs-non-at-war-owner STILL ZERO. MULTI-VOLLEY 12 (turn,slot) pairs, ALL in the t1253 AT-WAR battle (filter validated there: slot 14 six hits). SECOND price+cascade witness: Ungooma->Chamachies 477->437 EXACTLY -40 + state 1->2 adjacent pair wall 00:35:35 t1253; t887 re-confirmed; a -28 price fired with NO flip (state 1->1). Clamp target 280 never hit. STATUS t274 (2026-11-02, rewrite/tests/test_econres_t274.cpp + income-law.md T274): income-channel + growth-counter + build-queue + research-tier-chain laws pinned as 4 MUTATION-VERIFIED e2e regression catchers (gate >= -> > CAUGHT via exact cadence t16->t17; growth +1-boost deleted CAUGHT 474 fails; variants-in-play CAUGHT 1270 fails incl. q<66 legality). TWO sim divergences banked, both OPEN: D1 rewrite auto-queues the PLAYER home where T56 says 0xFFFF (documented default, re-trajectory cost); D2 AI opening item Factory 6/6 vs T56 Agriplot 4/4 (n=4 thin; adjudication needs fresh-run selector witnesses, drive class HELD). Fixture-route honest negative: watcher JSON carries NO per-planet economy scalars (keys verified: turn/score/selector/rank/ships/ship_raw/relation/planets_mine only) — per-planet pins run on the seeded sim, not save extraction. Row STAYS OPEN (strict-close). STATUS t280 (2026-11-02, raw body re-read, aicode.md §6.3 amendment E1 + income-law.md S10 closure note): the "+2 event modifier" of the pop-cap seed word +0x55 — previously "no in-code caller found (data/vtable driven)" — HAS ITS CALLER IDENTITY: jump-table case al=9 of the special-ability dispatcher 0x441d8 == SA_MoreMaxPop body 0x4402a (every owned planet, no gates). Rewrite upgraded from the [documented default] +25 post-clamp bonus to the cited capBase += 2 (pin species_more_max_pop_... control differential, mutation-verified). The t31 +2 LEDGER residual (1756/46132) is NOT explained by this body (firing moves +0x55 and +0x4a together) — that residue stays open. Row STAYS OPEN (terrain/nuke, home-placement, template-source sub-items remain). STATUS t281 (2026-11-02, census scripts/r1_t281_w16_census.py RC=0 + raw re-read work/t280_bodies.txt:152): the word[+0x16] sub-item got its FIRST direct measurement — the field PERSISTS in saves UNIFORM over 0..10 across owned AND unowned planet records in two lineages (bank-t1254 145/owned-124, bank-t273-tutorial645 135), i.e. it is the stored world-gen weight-row index (ctor draw rng%11 @0x23a97/aa8), NOT a homeworld marker (t105 §3's one-sample [inferred] reading REFUTED); its ==10 value (preset [0,33,34,33], the zero-barren row) is the skip operand of SA_Cornucopia 0x43de4, now wired verbatim in the rewrite (PlanetState.terrainRow + surface-bound cellClasses repaint {0,1}->{2,3,4}, richPros stand-in DELETED, pin species_cornucopia_repaints_min_pop_colony_t281 mutation-verified both legs). The t29b histogram non-prediction (save-time row does not predict save-time barren%%) STANDS — persistence is not provenance; the generation-side template SOURCE of the row draw stays open. Row STAYS OPEN (strict-close).


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
arrival stands NOT contradicted. STATUS t101 (re-attribution fallout):
the two budget fields are now CITED — MOVES = [ship+0x94], re-granted
each turn to the drive stat sum [ship+0x10] (FUN_0004a658; live == drive
32/35 rows), consumed by travel as RAW float distance (fild/fsub/fistp
0x4a30f..0x4a314 under the mode==1 commit gate); POWER = [ship+0x88]
recharge trunc([+0x18]*(1+age/100-step)). t47's §12/§13 "design-list
pointer / fuel / propulsion" labels RETRACTED to the +0x30 base-offset
artifact (ships.md §12 t101 block — rows 10..15 live-NAMED shields).
Remaining per-ship: the per-turn step CLAMP law (how far a ship walks vs
its MOVES budget — the walk body 0x533e0 + callers) and the build/redesign
inventory path. Row STAYS OPEN.
PLAIN (t179): Ships move by walking raw distance per processing tick (no
hop abstraction - measured). What's unpinned is the UNIT SCALE: the help text
measures drive range in "sugar cubes" (map grid cells), but the conversion
from drive stat to world-units-per-tick was never observed (zero ship flights
in every passive corpus). Player testimony t179 adds structure: two turn
tiers (per-day ship moves, round-robin across ships, orders persist across
days), separate within-system engines vs star-lane drives (stacking multiple
lane drives increases speed - consistent with the cited [ship+0x10] stat-SUM
law), and the Lane Magnetron = one-shot instant lane transit (vendor text
verbatim gizhelp.txt:1173-1181, gizmos.txt row category 5; the kind==5
go-to-star order handler 0x21f58 is cited). Queue t183: static hunt for the
scale factor + the per-day tier (per-star 0x60-stride pass 0x2547c is the
candidate). DECISION OPTIONS: accept default scale [1,3]+immediate arrival as
documented default, or let t183 run first.
STATUS t183 (static hunt RUN, ships.md §17): SCALE MEASURED AT LAST —
travel body FUN_00049f54 walks min(d/160, MOVES[+0x94]) sugar units per
resolver call, steps=max(1,round(walk)) capped by fuel [+0x88] (fuel==steps
burned; MOVES refilled to drive sum EVERY resolver call via 0x3ea08<-
0x412d4); const pool MEASURED live 20/20 saves: 1/160 @0x25ff, 32.0 @0x2603,
5.0 @0x2607, grid quantizer DAT_000895dc=32 (§17 T2/T3). Round-robin is a
MIN-FUEL one-ship-per-call resolver inside the turn loop FUN_00024f24
(0x12e10: 41 xrefs ZERO obj0 writers — no autonomous day-tick found);
lane transit = same walk law gated by lane matrix -1 gradient (§17 T4/T5).
Rewrite default NOT changed this iteration: campaign.cpp:1022 driveHopsFor
[1,3] is the LAUNCH-range default (ships.md §3, separate question); the
per-tick movement layer has no sugar-scale site to upgrade until the live
flight delta pins arrival granularity — row STAYS OPEN
(pending: live consecutive-save flight delta per BLOCKED t48, per-ship
redesign inventory, magnetron identity — index-36 census REFUTES the
Magnetron tie: Disarmer row, §17 T6).
STATUS t184 (static+runtime RUN, ships.md §18): THE LAST OFFLINE RESIDUE —
build/redesign inventory path — CLOSED WITH CITED MEASUREMENT: gizmo ring
rec+0xab stride 7 x25 physical slots {cidx u8, u16, u32}; cap dword[+0x15a]
:= live-table dword(0x6842+2*hull)>>16, hull=byte3[+0x94 design ptr +0xa7];
MEASURED 1234/1234 owned rows across 20/20 saves (scripts/r1_t184_inv_law.py
RC=0, caps {10,15,25}); filled[+0x15e] == occupied-slot count over 0..cap
INCLUSIVE (phantom-slot off-by-one at idx==cap MEASURED 100 rows, vendor
0x49698 bound jg); commit = per-slot cidx adds (scenario builder FUN_00040358
jumptable kits + design-apply FUN_00040d1c race-filtered RNG shuffle + UI
FUN_0004dd50) then FUN_00049acc RE-MATERIALIZE (no record copy ever);
redesign FUN_000497a8 REFUSES iff new hull cap < filled (0x497da). Row
STAYS OPEN on strict-close: ONLY the live flight-delta residue remains
(BLOCKED t48 capture window) plus magnetron identity (t183 census).
STATUS t185 (static RUN, ships.md §19): MAGNETRON IDENTITY CLOSED WITH
CITED MEASUREMENT — (a) loaded design table == gizmos.txt file order
MEASURED 76/76 names x 1368 save members, ZERO mismatches
(scripts/r1_t185_magnetron_census.py RC=0); immediate 0x24 at 0x4159a =
RECALLER (gizhelp.txt:695-699 help-tag gizmo36 too), NOT the Disarmer —
t183's off-by-one corrected; the branch is an emergency auto-recall inside
the movement resolver. (b) THE MAGNETRON USE-SITE FOUND: FUN_0004ca50
(kind-2 target-order dispatcher) case cl==0x3c at 0x4cd5c — Range*32 lane-
distance gate + design flag bit1 + Power burn, placement via 0x220a8 +
0x21f58 (star coords + (0,-200,0) + rng%200 x2, jitter const LIVE -200.0
MEASURED at B+0x82bb0+0xaee), slot rebuild 0x496e4; 0x4a360 guard
decrements the slot use-word iff design[+0x42] != 0 (semantics of col5 NOT
re-derived). §16 item 3 UNMEASURED tie => MEASURED law. Row OQ-019 STILL
OPEN on strict-close: the sole residue is the live flight-delta
arrival-granularity capture (BLOCKED t48); every offline question named on
the row is now closed. NEXT: offline queue EMPTY — re-arm idle, surface
the decision list (OQ-005 eyeball index.txt first).
STATUS t187 (2026-10-28 LIVE sitting — THE FLIGHT CORPUS EXISTS NOW):
state-4 rows OBSERVED for the first time (x1115 in t1255..1335; state5
x584, state3 x717) — the t49/t58 zero-flight corpora argument is
SUPERSEDED; the capture BLOCKED t48 demanded is IN HAND and the sitting
was still live at session end (turns 1335+). Raw regularities banked
docs/re/ships.md S20 (14/28/56-unit-per-turn lane steps paired with
MOVES=6/12; owner-1 4.67=14/3 sub-steps; state4<->5 flips coincide with
[+0x59] order changes AND 1100-2500u position discontinuities whose
frame-law reading is UNVERIFIED — coordinate reframe vs real instant
transit must be disambiguated). t188 TASK: extract the scale law from
scripts/r1_t187_scale.py output + the star table (star f32 coords vs
ship xyz frames) and pin or refute; row stays OPEN until cited.
STATUS t188 (2026-10-29, ships.md S21, cited): frame question ANSWERED
with measurement — the st5 lane coordinates are a LANE-LOCAL frame (pure-
x march, y exactly 0/1, z a fixed multiple of 32 outside the galactic star
extent ±402 read live), the 1100-2500u discontinuities ARE the state/frame
switches (25/27 big-mover rows are 5->4/4->5 flips; zero big steps on
st5->5 rows), and the T1 walk law is MEASURED-NEGATIVE for the march
(MOVES+0x94 and FUEL+0x88 frozen every turn while x+=14/28). New law banked:
lane step = {14, 28, 14/3} units/turn, LANE/ROUTE-scoped not ship-scoped
(one ship slot13: step 14 on lanes z=±1824, step 14/3 on lane z=544 with
d10/MOVES/POW unchanged; slots 13 vs 17 differ ONLY in +0x52 route handle).
Residue keeps the row OPEN (strict-close): which lane-record word carries
the step/divisor is UNMAPPED in code; galactic-frame per-turn transit
distance unmeasurable from this corpus (st4 spans single-turn). Magnetron
exonerated for these rows (rng%200 jitter would break the observed 32-grid
st4 positions).
STATUS t189 (2026-10-29, ships.md S22, cited): THE LANE-STEP WRITER FOUND —
FUN_0004a74c IS the state-5 march body (guard [+0x58]==5 at 0x4a7a6; callers
exactly FUN_0003e6e0 + FUN_00049c14; its prologue at 0x4a76c IS t101's
POWER-recharge site — the two citations are ONE function). Law [verified
disasm 0x4a7a6..0x4a8af]: step0 = float(ship[+0x8]+ship[+0xc]); gate1 byte
[handle+0x23] bit0 -> step *= moffs(0x263b) MEASURED 1/3; gate2 species row
(dword [+0x54]>>16) col 0x12 == 0x12 -> step = max(step,1)*moffs(0x263f)
MEASURED 2.0 (never witnessed firing); x :=
min(x+step, |A-B|), A/B = ptr[handle]/ptr[handle+4] star-coordinate records;
y/z untouched. MEASURED: base law EXACT on every consecutive st5 pair (delta
== step0 or step0/3 to 4dp, ZERO exceptions); step0 words are (14,0)/(0,28) —
S21's 14/28 ARE record fields, NOT MOVES-derived; SLOW pairs live ONLY under
handles 0x258933/cf/f6 (254 pairs, ZERO fast) vs 15 other handles all FAST
(0 slow); slot13 vs slot17 same owner, records byte-identical 0x00..0x27,
opposite speed — handle-gated in play; slot13's ~224 saturation == the
lane_len clamp. THE DIVISOR MEASURED LIVE: pool word = relocated operand
+0x88 (control 32.0 verbatim at 0x2603 law) — 0x263b word reads 0.333333
and 0x263f word 2.000000 in ALL saves 41..60; by branch construction the
HANDLE gate carries the 1/3, the species gate the 2.0. Row STAYS OPEN
(strict-close): gate2 has zero observed witnesses and byte[handle+0x23] /
species-col-0x12 semantics are unmapped (old-game handle bytes destroyed by
the ring rotation).
STATUS t190 (2026-10-29, ships.md S23, cited): THE LANE-RECORD STRUCT AND
byte+0x23 SEMANTICS CLOSED WITH MEASUREMENT — lane record = 39-byte pool
rec (data-seg+0x3337, stride 0x27, cap 148; rec+0/+4 = star-A/star-B OBJECT
ptrs, allocator FUN_00024834 0x248af/0x248b1; +0x23 never initialized);
bit0 has EXACTLY ONE writer image-wide (0x247f7 OR 0x1 inside FUN_0002446c,
the connectivity-BRIDGE creator; never cleared) and MEASURED 20/20 live
new-game saves: +0x23==1 on recs 50..57, ==0 on recs 0..49 (nlanes=58, 50
stars, matrix one-pairs=58; scripts/r1_t190_lane_pool.py RC=0) — bit0 =
"bridge lane, not a real starlane" => THE x1/3 GATE SLOWS BRIDGE LANES;
t189 fast/slow handles congruent to the pool base mod 39 (deltas
39x{5,52,56,57}) = handle identity CONFIRMED, corpus fully explained.
Gate2: species col +0x12 (table img 0x12fb3 stride 0x1ee) has NO 0x12 in
rows 0..23 in ANY of the 20 LIVE tables — stronger non-witness (scenario-
scoped non-claim). t52 matrix-buffer identity tension CLOSED en route (one
100-linear hop matrix at data+0x32ddb == folded DAT_00045beb; FUN_0002351c
loads authored lanes + BFS flood-fills hop counts). Row STAYS OPEN on
strict-close: sole residue = the LIVE st4 in-system per-turn displacement
observation (BLOCKED t48 capture window; dosbox down, ring holds t=0 rows);
byte+0x20 (power-of-two side-field) banked unattributed S23 L5.
Closure path: ONE watcher run dumping st4 world coords + species row during
a known march (the +0x23 window question is answered statically — do NOT
re-open it). STATUS t191 (2026-10-29, cited; ships.md S23 L5 CLOSED,
debugflags.md t191): lane rec+0x20 = PER-EMPIRE LANE-VISIBILITY MASK —
cheat writer 0x273ca (scancode-keyed: cosmos handler 0x26b34, DX==3 keydown,
ECX==0x26='l', nougat.lf-gated; runtime slot member 0x247adc holds P0+0x26b34,
60.sav — static hunts fail because the dispatch table is unrelocated in the
file image), normal-play writers 0x463eb/0x46421 (function 0x46354 share
loop; semantics inferred, flagged), reader = lane-paint loop 0x25aa2..0x25b6d
into painter 0x20c48; NO clear site image-wide = sticky law proven. Row
STAYS OPEN: live-st4 residue unchanged. | open |
STATUS t192 (2026-10-29, ships.md S23 L6, cited): THE rec+0x20 SHARE LAW AND
THE 0x22-GROUP BASES CLOSED WITH MEASUREMENT — (a) FUN_00046354 is a MUTUAL
LANE-VISION SHARE between two empires' diplo rows (party masks 1<<byte[row+0]
and 1<<byte[0x12e16+0x1ee*p2]; t191's "0x12e16 = lanes-shared-at-contact
column" hypothesis DEAD — 0x12e16 is the diplo-row table base), N =
rand%(state==3?6:3)+1 grants/call => ALLIANCE DOUBLES THE SHARE BUDGET;
callers 0x45778 (EBX=0 bidirectional, alliance-formation block) and 0x55f6e
(EBX=-1 receive-only, per-race event loop 0x55f1b..0x55f2e, party-1 = current
player); star twin FUN_00046524 same shape (mod 4/2, star-obj +0x16/+0x17).
(b) MEASURED 20/20 saves (scripts/r1_t192_share_mask_scan.py): the per-race
list [dword(0x12e1d+0x1ee*r)+0x2c+4*i] holds EXCLUSIVELY lane-pool records
(220/220 mod-39 congruent, 0 star, 0 other) and race r's list == EXACTLY
{lanes with rec+0x20 == 1<<r} (100/100 lists, 0 disagreements). Pool +0x20
census {0:940,1:40,2:60,4:40,8:40,16:40}: every visible lane single-bit =>
the share path has ZERO witnesses in the new-game corpus (honest negative;
closing a share-event observation needs a mid-game save where two empires
share a lane). (c) paired mask byte = member B+0x82bb0+0x6774 (payload bytes
0x21aa6 = 88 15 74 67 00 00) == 1<<[0x7458e] 20/20 (weak: idx==0 all saves).
CAVEAT BANKED: 0x22e60 DOES clear rec+0x20 via the per-race list (reachable
only through FUN_00022ce4 <- FUN_000226e4, 4 callers all reading as setup/
new-game paths — 0x24f8f sits before the authored-lane loader 0x2351c, 0x52cb6
next to the [0x7458e] reset 0x52cc6); t191's image-wide-no-clear form is now
CONDITIONAL, the sticky law stands for the cheat/share writers (no inverse of
0x273ca/0x463eb/0x46421 exists). Rewrite surface: NONE (rewrite has no lane-
visibility layer; ships.md L6/debugflags.md flag that abilities.md's "no fog
of war in original" parenthetical is false-of-original — filing disposition
unchanged, justification text queued for the next abilities pass). Row
STAYS OPEN: live-st4 residue unchanged. | open |
STATUS t193 (2026-10-29, ships.md S23 L7/L8, cited): MID-GAME WITNESSES
IN — the Oct-29 12:30..13:22 sitting re-wrote all 20 saves at t=1086
(4 empires, war with Minions): pool +0x20 census {1:160,3:80,6:180,7:220,
11:260,15:260} of 1160 recs = 100/1160 MULTI-BIT (the 0x463eb/0x46421 SHARE
OR HAS FIRED; e.g. 11 = player+Orfa+Minions), per-empire fog 9/8/25/32 of 58
lanes; star twin +0x16/+0x17 multi-bit too; masks md5-static across the
window (no grant fired inside it). t192's LIST=={mask==1<<r} law SUPERSEDED
(0/80 mid-game): per-race lists = OWN claimed lanes (cnt=2, second entry a
t190 BRIDGE lane), subset of nonzero-mask pool. rec+0x21 {0:720,1:440} mid-
game, NOT a function of +0x20 (mask 11 with both values) — writer/semantics
still open (flag). STATIC: t191's 'paint loop 0x25aa2..0x25b6d -> painter
0x20c48' REJECTED — 0x20c48 is an alloc wrapper (FUN_00077b40/0x77b47) and
FUN_00025604 is a state-SNAPSHOT serialiser; NO rec+0x20 UI consumer found
(census: 4 TEST + 18 CMP imm hits, none lane-pool-scoped; Ghidra
search_instructions 98,819 instrs) — visibility-asked consumption moved to
OQ-019's OWN residue re-probed and still NOT falsifiable: 2238 st4
samples in the sitting window, 10 (turn,slot) pairs, ZERO mid-turn
displacement, and the game never left t=1086 (639 rows 12:55:59..13:22:12,
turn advance absent) — the live in-system march needs a sitting that PASSES
turns while a ship is in-system. STATUS t256c (AI GAP ROW 16 DISPOSITION,
docs/re/ai-dossier.md S11 + _wip_t256c.md; tool scripts/r256c_shipstate.py
RC=0 — first full per-ship ORDER-STATE census: 62,762 trusted rows / 25
sessions / t240..1335): live order-kind set is exactly {1..5} (kind 0 ONLY on
dead slots, imm0 0x24a00 law); AI holds kind 2 ZERO times; travel/arrival
pair kind4<->kind5 symmetric 416/416 in self-play (0x220a8/0x21f58); retreat-
downgrade 0x220f2 fired 143x (both owners); Invasion Module 0x49 carriers in
480 distinct ships — every §5/t179 law INPUT is observable in the ORIGINAL
and NONE is representable in the rewrite's transit-only fleet_ vector. Row 16
relabelled GAP->BOUNDARY (aggregate model accepted permanently); this row
(OQ-019) is where the per-ship build lives and it STAYS OPEN (strict-close:
the census informs the boundary, it closes no law; the st4 in-system march
residue unchanged). STATUS t265 (2026-11-02, DRIVE-CORPUS FLIGHT MINING —
docs/re/ships.md S24, _wip_t265.md; tools r265_st4_magnetron.py /
r265_pass2.py / r265_pass3.py / KEEPER r265_keeper.py RC=0 on the t261
production drive 1086->1236, ~150 real turn advances, softlock window
21:38-23:06 excluded): (1) THE t193 st4 RESIDUE ROUTE IS MEASURED-DEAD — 21
multi-row st4 runs spanning >=1 turn advance (longest 150 turns/1014 rows)
have net displacement 0.00 with CONSTANT [+0x59]; every big mover is a 4<->5
frame switch ((4,5)x60+(5,4)x67), zero healthy (4,4,True); st4 = DWELL state,
the in-system march resolves inside one turn boundary and is NOT observable at
10 s ring cadence — finer instrument (watchpoint class) or nothing. (2) t189
LANE-STEP LAW RE-CONFIRMED SECOND CORPUS, ZERO VIOLATIONS: consecutive-turn
st5 |dx| == step0 or step0/3 with step0=float(u16[+0x8]+u16[+0xc])
same-window (2,400+ pairs, 27 handle groups); /3 is lane-scoped not
handle-value-scoped (6 mixed handle values = route re-points + pool recycling,
t190-consistent). (3) TURN-ATOMICITY: same-turn st5 x-delta EXACTLY 0.0 in
17,595 pairs zero exceptions — t187's "4.67 = three sub-steps" reading DEAD
(4.6667 is the single step); entry-x all multiples of step (S21 x=k*step
corroborated). (4) MAGNETRON ZERO-CENSUS with the sharp instrument: landing
rows must be off-32-grid in x AND z (rng%200 both axes, P(false neg) <0.1% per
landing) — 0 of 6,184 st4 rows off-grid, y mod 32 == 0 all; W2 frame hunt 0;
use-site law stays static-cited S19 T3 with zero runtime witnesses. (5) t266
feed: the only st4 mid-turn moves in the corpus are INSIDE the softlock window
(turn frozen at 1255 while tail movement ran; repeating identical triples) —
new bug-class tell turn-frozen-but-tail-running. Row STAYS OPEN (strict-close):
remaining runtime residues all need sub-ring instrumentation or a
player-driven magnetron use; no documented-default in the rewrite changes on
this evidence. | open | STATUS t273 (2026-11-02): magnetron USE-frame harvest re-run over the full corpus (r273_harvest leg C, r265 W2 signature verbatim): ZERO candidates (st5 control-class 160,747 rows, other 0). Honest negative; row STAYS OPEN. STATUS t275 (2026-11-02, ENGAGEMENT RESOLVER VERBATIM — docs/re/combat.md S2k, listing work/t275_resolver.txt, capstone 5.0.7): 0x42c60..0x42e6e read instruction-by-instruction for the first time (t179 P3 was a summary). CONFIRMS first-eligible selection both legs (no strength/value ranking anywhere). NEW LEGS: (1) caller-side ship array (0x41260 loop 0x41318) is OWNER-RACE FILTERED ([ship+0x54]>>16 == engagement race) + POWER>0 + kind!=1 — the resolver NEVER sees the defender's ships, so return fire is a separate resolution pass (t85g discrete-step observation corroborated); (2) leg-selection GATE 0x39a00 objective planet with ACTIVE item 23 Ship / 26 Orbital Shield / 27 Orbital Mega Shield SKIPS the invasion-carrier leg straight to firepower; (3) 0x4a55c inside leg B WRITES the shooter's stance/target (+0x62/67/68) — the resolver commits the firing order. HONEST NEGATIVES: region never reads +0x59 (queue-row citation misdirected — threat byte is t201/buildPhase); every selection input is per-ship/per-planet state the rewrite's fleet_ vector cannot represent -> aggregate-mappable content of the four t89 sub-laws is COMPLETE; first-eligible wiring stays inside THIS row (OQ-019 boundary, row 16/17 accepted t256c). No rewrite default changes on this evidence; row STAYS OPEN.

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
docs/re/; code sites cited or marked analysis-only). Entries prefixed "- >"
so ledger tooling (which keys on ^OQ-) does not misparse this index:
- > OQ-001 .cob offsets -> formats/cob.h reader (format block cites this ledger + FINDINGS P1a)
- > OQ-002 FLIC codec -> formats/flic.h (cites docs/re/flc.md)
- > OQ-007 CP437 -> decode sites game/species.cpp, game/research.cpp, game/starstat.cpp, game/economy.cpp, game/diplomacy.cpp
- > OQ-008 loader control-flow model -> ANALYSIS-ONLY (rewrite is fresh-start-only; no loader in rewrite; spec docs/re/loader.md)
- > OQ-009 AI data side -> ANALYSIS-ONLY input to the W-B-gated diplomacy/AI build (docs/re/ai-data.md; nothing shipped reads it yet)
- > OQ-011 POINTER LAW (scripts/r1_pointer_law.py 12/12 slots, gate 3q) -> measurement instrument only, cited by capture scripts + campaign.cpp:593
- > OQ-017 .fnt codec + UI wiring -> formats/fnt.h (cites docs/re/fnt.md) + ui/ui.cpp wiring
