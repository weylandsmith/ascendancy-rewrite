# BLOCKED.md — v2 (decision history in archive/ralph-v1/BLOCKED.md)

## Standing decision (NOT re-openable)
Option C hybrid, B-priority, chosen by the user 2026-10-04: data-first work
plus R1 runtime capture via dosbox-x save states, no cadence limit (abolished
2026-10-05). Full rationale and the refuted A/B fork: archive/ralph-v1/BLOCKED.md.

## Current blocks
### OQ-021 — Control-victory threshold: >1/2 or >=2/3? (user decision; default in force: >1/2)
The vendor's own artifact contradicts itself: extracted end-ctrl.txt line 2
(header comment, the condition's own title) says "over half the galaxy",
while its enddesc/congrat prose says "spans over two-thirds" / "more than
two-thirds of the stars" (verified 2026-10-06g by direct read). The threshold
is code-side (numeric constant in the end-condition evaluator); the .txt has
no numeric grammar, filename refs exist only as runtime stack strings
(eventwnd.cpp region; static xref of the data string = 0 hits), and locating
the comparator statically needs obj1 call-edge recovery — long horizon, not
this loop. DEFAULT IN FORCE: rewrite keeps `mine * 2 > total`
(rewrite/src/game/campaign.cpp:738), citing the header-comment title over
display prose. UPDATE 2026-10-06s (pool-relative law, docs/re/datafiles.md):
all five end-*.txt literals have exactly one referrer each (0x2c04e/0x2c065/
0x2c07c/0x2c093/0x2c0aa), all inside the ending PRESENTER FUN_0002bfa8 (rank
= clamp(DAT_0004350c/10 - 1, 0, 9), switch on DAT_00043510 selects the file).
DAT_0004350c and DAT_00043510 have READERS ONLY — exhaustive writes search
(moffs + disp32 + SIB-base + fixup_sites.tsv + Ghidra xrefs over full code
range 0x200..0x82bb0) found ZERO writers, so the comparator is NOT in the
image: former option (b) "obj1 call-edge recovery" is REFUTED, not merely
long-horizon. CORRECTION 2026-10-11 (t73, docs/re/score.md): the 06s
conclusion overreached — Ghidra never analysed the dark zone 0x26b32..0x284bb
(0 functions in functions_full.tsv) where the score disproducer and the
end-*.txt presenter (eventwnd.cpp cluster 0x2c03a..0x2c0b6) both live; a
zero-Ghidra-xref result there is vacuous (R12-class). The evaluator still has
no located writer under 8 DIRECT-address encodings (score.md S4), but a base+
disp writer inside the dark zone remains fully open — route t73b = raw-objdump
function enumeration of 0x26b32..0x2c600 + threshold-idiom grep, then the
controlled-mutation capture (set player-owned systems to just over 1/2 in RAM
at the 0x3a095 owner table (stride 0x162, owner = +0x54 sar 16 per
FUN_00040ec0) before an end-turn, and observe whether end-ctrl fires; a
second run at 60% discriminates >1/2 from >=2/3). CORRECTION 2026-10-11 t74:
that recipe's SITE IS WRONG — the static 0x3a095 table stays all-0xFF (never
written) across every banked campaign slot; the LIVE owner state is a heap
copy (score.md S5 / STATE T74: candidate at corollary X=0x38ad8 in ck067, to
be pinned across two checkpoints). Static writer hunt is now CLOSED-EXHAUSTIVE
(all direct encodings + runtime-relocated full-RAM scans negative; f32 2/3
(absent image-wide); closing = the capture with the corrected live site.
T75 POST-MORTEM (2026-10-12, runs r1thr-001410/004333/010746/013404/015525/
023112, harnesses r1_t75_inject/run/read committed): the .gam-capture route is
MEASURED DEAD. Harness now WORKS (rev5 churn=1 proves campaign entry via
menu row (318,325); menu law pinned by two empirical anchors (318,293)=New
Game (r1ad corpus) and (318,372)=Load-Game (rev4 shot — five <EMPTY> slots:
.gam resume is NOT a save slot); end-turn (511,67) fires per t56 cadence).
But THREE escalating fabrications — (r5) owner byte .gam+0x33=0 on 29 chain
stars, (r6) + colonization marks +0x1e=02/+0x20/+0x24/+0x28, (r7) full
clone of the one real colony's 123B body (Verithil I) onto every chain star —
ALL count exactly 1/50 (owned DAT_482fb=1, selector 0x43510=0x00, every
post-end-turn slot). Load-side star bitmaps (star-record stride 96 RAM,
+0x14/+0x15) do NOT derive from the .gam planet chain's owner bytes; only
in-game colony state populates them. RECLASSIFIED: BLOCKED-USER-LEVEL, same
class as OQ-010/OQ-019 (needs an interactive original session where a
colony is really founded, or a scenario file from real play at >50% owned).
LAST SURVIVING STATIC LEAD (t75 raw objdump, work/ascend_restored.bin):
function @0x3ecb8 (Ghidra-blind zone) is an owned-star PREDICATE loop:
count u16 ds:0x13b98 (0x3ecc5, jle exit), iterate rec base 0x13bc5 stride
0x60 while edx < (ds:0x16143 sar 0x10) (0x3ecfd..0x3ed08 — same hi-word as
the score law); per rec test bitmap +0x14 bit (1<<[ebp]) AND bitmap +0x15
bit (1<<([esp+6] sar 0x10)) (0x3ed12..0x3ed30); survivors copy the 0x67aa
31-byte record and fall through to 0x1ee-stride planet rec 0x12e16+0x1ee*k
(0x3ed52) with two calls to 0x439f4. Third u32-site of 0x16143 = 0x44659
(also unexamined). NEXT t76 = one decompile batch {0x3ecb8 callers/callees,
0x44659 region}; if the comparator still isn't there, OQ-021 stands BLOCKED
with default >1/2 (campaign.cpp:738 unchanged).
Item STAYS OPEN per strict-close policy; other workstreams unaffected.

### OQ-020 — ability charge days (static route EXHAUSTED 2026-10-07; default in force: 30 turns)
Seven static probes, all negative: (1) `%d day`/`amass`/`SA_*` count ZERO in
the image and in ascend00 .cob/.bin tables — the help text reaches RAM as a
runtime-loaded string table (phys 0x252f50..; entry array at phys 0x252ba8,
u32-per-entry, ~0x330 entries), so no static string xref exists; (2) pointer
scan of the r1deep capture for u32 == phys of a `%d day` string hit only two
HEAP sites (0x252cc8/0x252d8c = the string table itself), no code/global
holder; (3) no 21-entry or 14-entry all-(0,200] static table in image data
except a triangular 1..10 ramp at 0x88f90 (economy-shaped, not charge);
(4) race .dip DIPVALUES carry no charge parameter (15 params verified,
diplomacy/bio only); (5) the stride-494 per-race table at DAT TB=0x12fb3 is
pointer/text data, NOT the dip param block; (6) the one dip-params copy found
(phys 0x255067, race00 6-u16 anchor 290,360,450,510,600,750 — byte-exact) is
a single unpaced heap buffer, race01 absent within +-64 KB, no stride law;
(7) the help blocks around all 14 `%d day` lines contain no other numeric
token (template + `pos 10 160` only). REMAINING ROUTES: obj1 call-edge
recovery of the help-formatter argument (same class as OQ-015/OQ-021) or a
controlled-mutation capture (activate an ability, read the countdown field
over end-turns). DEFAULT IN FORCE: 30 turns (abilities.md §Charge; no
rewrite upgrade). Item STAYS OPEN per strict-close policy.

### Nuke law (Phase Bomb gizmo 70) — capture-gated; default in force: NOT modelled (2026-10-09)
What is blocked: the exact per-structure destruction law of the Phase
Bomb (which slots it clears, in what order, whether orbital structures
and Colony Base are exempt, class/rock fallout on destroyed cells).
Why static died: special-device effects are DATA-DISPATCHED (no in-code
caller; same shape as the S10 event-24 dispatch at 0x4402a). Every
CMP-imm70 site in the restored binary resolves to ASCII parsing
(0x796ad/0x7a49a), the AI 70-turn reject (0x3f6eb), message-id
constants (0x3ddc0 region), or data (0x820xx) — income-law.md T39e.
Why no capture has it: 13 runs of scripted AI play never research/build
Phase Bomb; r1_destruction_census.py over the full corpus finds ZERO
device-destruction events (all structure losses are depopulation or
world-restart artifacts, T39c/d).
Best default proceeding under: Phase Bomb NOT modelled in rewrite
combat (rewrite combat is a documented abstraction, ships.md). No
silent stub: OQ-016 row names this sub-law open.
Closing route (one R1 run): scripted campaign forcing Phase Bomb —
research path per restree tree (its tech prereqs), build on any ship at
a Shipyard, launch at an owned planet with >=3 surface items; capture
slot states before/launch/after via the pointer law. Identify the
dispatch table entry by which code first writes FF into a mid-record
slot byte at launch time (whole-image watch not needed: 3-save diff +
static sweep of the launch handler reached through the gizmo-use UI).
## R1 runbook (mandatory safety invariants — a run without them is a bug, not research)
Route: scripts/r1_savestate.sh (+ r1_sav_scan.py per-run base; never hard-code
B). Deep capture: scripts/r1_deepcapture.sh. Invariants (enforced statically
by gate 3n):
- dosbox NEVER mounts pristine game/ — scratch copy under work/r1/ only
- headless-safe config: output=x11 under Xvfb for captures needing vblank
  autosave (host-clock autosave is checked at vblank — dummy video = no
  saves); nosound=true; stdin=/dev/null
- -time-limit always; all output bounded (head -c); DOSBOX RULE in STATE.md
- kill ONLY pkill -x dosbox-x
- CADENCE LAW (measured 2026-10-06m, 19 runs): host-clock autosave period is
  a CONSTANT 10 s (median gap 10 s in every run's save dir). Turn advance is
  NEVER automatic: 14 idle runs (zero landed clicks) hold turn constant for
  the whole run. Each NEXTTURN click that lands ON THE STRATEGIC MAP advances
  exactly +1 turn (r1ad-144225: 0->1->2; r1deep-230146: 8 scheduled clicks ->
  7 boundaries, the missing one landed while a modal screen was open — modal
  views SWALLOW clicks, see 06f/06j). Schedule by TIME and verify by TURN
  number in checkpoints, never by counting slots: at 10 s autosaves a turn
  may straddle 1-3 slot copies and slots rotate 41..60 cyclically.
- exit codes: 0 = base derived / upgrade formulas; 1 = normal negative,
  record ONE line in STATE.md, no in-turn retry; 2 = harness bug, fix it

## Closed-as-dead capture routes (do not resurrect; full trail in
## docs/REFUTED-ROUTES.md)
- external ptrace tracer: dosbox-x 2025.02.01 makes itself untraceable
  (ATTACH/SEIZE EPERM, maps EACCES by t+2 s) — dead on this box
- dosbox-x -break-start: superseded by save states AND carries the EOF-spam
  trap; do not pilot
- static absolute-base schemes: four refuted, fifth forbidden — the runtime
  pointer law (OQ-011 CLOSED) is the answer



## OQ-CARGO AI landing-site chooser (opened t44, BLOCKED-static route)
Chain CLOSED (income-law.md S13.5): cargo placement = EVENT 4 with
+0xae from EVENT 8's FUN_0003a880 coord->slot converter; legality re-gated
by FUN_0003830c (rule G). WHAT'S MISSING: who picks the AI's landing COORDS
before dispatching event 8 — the dispatch site of event types 8/4 in the AI
ship-control code is unidentified (31 +0xae xrefs are all handler/UI code;
player provenance is the mouse). Search for the event DISPATCH (calls into
FUN_0003aa0a or a dispatcher with (obj, 8|4, payload)) failed to bound the
space cheaply; a blind sweep is a retry spiral. BEST DEFAULT PROCEEDING
UNDER: rewrite places arrival CBs by the uniform non-rock picker draw
(consistent with the rule-G-exempt CB + 26% barren + ranks 4/40;
campaign.cpp seedColonyBaseColony). ONE-ROUTE CLOSING RECIPE (future):
find callers of FUN_0003aa0a via the event dispatcher table, read the AI
branch that builds the event payload for transports with cargo item 5; the
coordinate pick IS the law.

### t44 dispatch-route probe result (round 1-2, STOPPED per no-spiral rule)
get_xrefs_to(0x3aa0a) = 0 refs; byte-pattern '0a aa 03 00' = 0 hits;
operand scan '0x3aa0a' = 0 hits — the event handler is reached ONLY via a
data-resident handler table (no direct call/immediate anywhere in the
97,413-instruction listing). The closing route as written needs a whole-
image DATA scan for table-shaped dword runs then call-shape validation —
that exceeds the bounded recipe. Stays BLOCKED under the picker-draw
default (observation-consistent, unchanged).

## t48 drive-hop conversion route (BLOCKED-by-design, one-run closing route)
The executor family (FUN_0004b8e4 + walk snapshot +0x4b3xx, sweep-exhaustive
sites for +0x88/+0x90) contains NO term converting drive Level (or the +0x90
speed accumulator) into per-turn float displacement. The only observed
per-turn coordinate rewrites use gizmo STEP dword[row+0x1a]<<5. CLOSING
ROUTE (next session, ONE R1 run): capture consecutive saves (End-Turn x3,
deep-schedule law), identify ships in flight (state +0x58 == 4 with order
type 1), diff float coords [+0x9e/+0xa2/+0xa6] per turn, regress against
(sum drive Levels + design base [+0x10]) per ship; if the regression is
exact the sugar-cube scale := the float coefficient; if not, the per-turn
flight law lives in the animation/walk code and the campaign model uses
the queued-order TURN WORD +0xac only (delay law, S11) — in which case the
rewrite's immediate-arrival model is the CORRECT campaign-level reading
and OQ-019's scale sub-item closes as NOT-MODELLED-BY-DESIGN with this
census cited. Default under which we proceed meanwhile: [1,3] launch
adjacency (AI-layer fact, verified; execution layer has no hop term).

## t49 update to t48 trajectory route: corpus CANNOT support it (exit-1 branch taken)
Ran scripts/r1_trajectory_regression.py over all 484 saves: 452 consecutive pairs,
5 ship slots all owner 0xFFFF state 0 pos (0,0,0), ZERO state-4, ZERO movement
(harness fixed this turn: heap-span arr B+0x82bb0+0x3a095, count WORD B+0x82bb0+
0x43483; the image-span dword read 200 uniformly = wrong mapping). Independent
cross-check: orbit-ring census 484 saves, active ids {1 Agriplot, 5 Colony Base}
only, ZERO item-23 rows -> no ship has EVER LANDED in the corpus (§10 law: landed
ship = active item-23 ring entry). The 511:67 End-Turn deep schedule never issues
orders; interaction-state laws (flight, combat, abilities incl. OQ-020 charge,
partly OQ-021) are STRUCTURALLY uncapturable from existing saves.
BEST DEFAULT TO PROCEED UNDER (unchanged, explicitly NOT contradicted by any
measurement): ship adjacency [1,3] AI-preference launch + immediate arrival at
campaign level; sugar-cube scale remains OPEN. CLOSING ROUTE REQUIRES a new R1
capture that SCRIPTS A MOVE (click home-orbit ship, click destination star,
End-Turn x2, save ring each step) — capture-capability extension; first R1 run
budget for it starts when no cheaper ledger item remains (OQ-003 field semantics
is cheaper: same idle corpus suffices for record-map diffs).


## t51 — ONE consolidated R1 capture session closes three questions (scheduled route, NOT yet run)

Static code routes for the save-writer / OQ-003 field meanings are DEAD
(REFUTED-ROUTES R12: direct-reference scanning is provably blind in this
image — even CLOSED parsers show zero xrefs). Remaining closure needs ONE
scripted interactive session against a scratch copy (all t49 invariants:
scratch copy never mounts game/, headless xvfb, -time-limit, pkill -x
dosbox-x only, bounded output):

1. CONTROLLED MUTATION [DONE t53 — r1mut-20261011-092253, evidence
   r1-savestate.md t53 section]: load path PROVEN (verbatim 123-B blob copy,
   HERMESSEN needle at member 0x26edd7, sentinels landed, zero collateral);
   pointer fields preserved not rebuilt. REMAINING for OQ-003 = field
   MEANINGS, which mutation cannot supply — needs play-mutation variants
   (see step 2 session: mutate channel words +0x44..+0x4f before turns
   advance and watch production) OR is parked per strict-close.
2. MOVE SCRIPT (closes t49 sugar-cube scale residue): new game, build one
   scout-ish design if reachable, issue order to a lane neighbour, save
   every turn while in flight, run scripts/r1_trajectory_regression.py —
   nonzero (x,y,z) deltas vs lane distance = scale law; all-idle again =
   second independent null (then BLOCKED stands as permanent, rewrite
   immediate-arrival closes as correct-by-absence).
3. ABILITY CHARGE OBSERVATION (OQ-020 free ride): while scripted, buy/use
   one cell-special and record planet +0x54 + +0x66 across saves.
4. END-CTRL CORRELATION (OQ-021, added t52): reach/view the victory or score
   screen; correlate displayed % against owned-star share — over-half vs
   two-thirds discriminates in ONE observation (Extinct fires early on known
   seeds t557/t583; score block shared per static.txt template).

Best default proceeding under this block (already in rewrite): scale stays
[1,3] hops + immediate arrival (explicitly uncontradicted); OQ-003 unknown
fields stay unwired (never stubbed). Budget rule: one session, parse
offline; exit-1 nulls recorded once, not re-attempted.


## t52 — OQ-021 end-ctrl threshold static route exhausted (round 2 dead)
Leads tried: FUN_0002a428 (measured = 3-line error stub), R12 (string xrefs
blind), IMUL-100 arith scan (score% producer family only, banked ships.md
S15). Default >1/2 (vendor comment) stands, unwired difference unknown.
Closing route: t51 capture session STEP 4 — trigger/view victory+score screen
in the scripted run; correlate shown % with owned-star share (over-half vs
two-thirds discriminates in ONE observation once any end fires; seeds already
known to hit Extinct t557/t583 — Extinct screen path shares the score block
per static.txt template). Do NOT re-scan statics for this constant.


## t54 — scenario-table RAM join: naive chain scan TIMED OUT (harness, not negative)
Round-2 probe scanned 17 MB Memory byte-by-byte with per-position chain
extension (O(n^2) worst case) -> 300 s kill. RECIPE for the retry: anchor on
ONE known scenario type-name string (starstat/names pool), then verify
stride-0x1ee chain ONLY at anchor +-small window; bound total work with
mem.find loops (no nested extension per position). Budget: one retry inside
the t51 capture session (step 2), never as a standalone idle probe.


## t55 — synthetic End-Turn click flakiness blocks step-2 turn advance (driver ready)
CLOSED t56: recipe worked exactly as designed — (511,67) advanced on try 3
of 8 in run r1ad-20261011-110013 (2 inert tries first = flakiness, then 6
clean 1-turn advances). Treat End-Turn as WORKING-but-flaky: always verify
per click (turn counter), always allow >=3 tries at 25 s spacing.
(511,67) advanced turns in run 20261006-131350 (three clicks, turn 0->2)
but did nothing in 20261011-102543 (3 clicks, both frame candidates). Same
flakiness law as the 2026-10-05k title-click note; NOT a geometry refutation.
NEXT attempt recipe (one bounded run): adaptive phase, click (511,67) with
25 s spacing up to 8 tries, turn-counter verification per try; if still
dead, try key mode ('key Return') once before conceding the End-Turn route
to mouse-only flakiness. Idle-campaign value from today's run already
banked (income-law.md T55 RUN RESULTS: pop=2 + cap==seed+2 + one-CB 4/4 on
banked +0x88 law for a 5th campaign; acc0->stored(1,0,1) fresh-campaign
corroboration of the S6 recalc residual).


## t57 — OQ-012(a) density-control probe: AMBIGUOUS (count==50), closed to best-default

Run r1ad-20261011-122006: ONE click at (65,427) = GALAXY_MORE center
(windows.txt absolute-root coord law) landed during setup (dens.log
timestamps), campaign entered with fresh grid t=114, and the star-table
battery counts 50 stars at presetup, postclick2, AND fresh entry ck001.
Two readings survive and cannot be separated: (a) the click was inert
(synthetic-click flakiness law — End-Turn showed 2 inert tries before
working); (b) one cycle step happened to land back on STARS=50 (cosmos.txt
default). Discriminating needs a change-VERIFIED click loop with a visible
option readout — the only readout is glyph-rendered (R13), so no needle
exists. Not retried (exit-1 discipline; this probe budget was ONE click by
design).
BEST DEFAULT (proceeding, rewrite unchanged): star count = 50 = cosmos.txt
scenario default AND measured fresh-map count across every banked campaign
(5 campaigns + this run). New-game size options are scenario-layer values
not wired into any image constant (t56c static NULL); rewrite fixed-50
matches the only measured campaign behaviour.

## t68 — OQ-005 .shp dims-location residue (BLOCKED-USER-LEVEL)
State: control-byte grammar, blit 5-arg law, uniform runtime table
(sel0->rec0+8, k>=1->rec+0x18) all CLOSED with citations (shp.md
S9/S12/S14/S16/S17). Residual: 80/1557 records in 31 files whose
in-record dims-field location is unknown (classes: span-undersized
planind/3cfgnew, simple-format cos_star, stragglers), and .tmp/1starmap
cached heads are non-verbatim so file-space inference is unsound there.
[AMENDED t182: count corrected by measurement to 71 records/28 files —
10 k==0 records were validator off-by-8 false FAILs, see shp.md S18;
classes otherwise unchanged.]
Why blocked: closing needs a human-verifiable drawn frame (r1-savestate
capture exists, but R13 means we cannot confirm the panel drew; blind
sweeps are FORBIDDEN and the fixup-vary theory is measured dead).
Best default to proceed under: decode records per S16 V/A law, dims at
rec (k0) / rec+0x10 (k>=1); for the 80-record residual class, mark
skip-and-warn in tooling, never in game-visible paths (rewrite renders
its own vector art; the codec is a validation asset).

## t70 — OQ-010 combat application laws (capture class = OQ-019's)
State: device constants data-verified (gizmos damage 1..13, shields 1..5);
combat APPLICATION (hit prob, shield subtract-vs-absorb, overkill, firing
order) has NO known code site. Static route hits its banked HARD BOUNDARY
(r1-savestate.md 05k: absolute immediates unresolvable; inputs are runtime
pointers; "critical path not more static batches"). batmode-module join
under full analysis = 6 real functions (0x5b47c..0x5ba30), all small UI-ish;
E1 batch 1+3 REFUTED their candidates. Headless autoplay corpora contain
ZERO ships (T49 2,260 obs, T58 565 obs) so in-battle click-diff capture is
UNREACHABLE without manual gameplay reaching combat -> same
BLOCKED-USER-LEVEL class as OQ-019 scale. Best default to proceed under:
documented research-gated attack/defense scores (ships.md §4) stay;
rewrite combatPhase unchanged. Closing needs: user-run original game to
ONE fire event with autosave capture running (single battle = enough for
slot-diff of the two combatant records + damage application).

## t82 — the three user-level blocks collapse to ONE played session
(scripts/r1_playcap.sh, banked ready 2026-10-12)

OQ-021 (victory selector), OQ-023 (relation-state enum), OQ-010 (combat
application) all close from ONE real playthrough of the ORIGINAL game in
the scratch build with the autosave ring running. The script boots
work/r1/game/ascend.exe (scratch copy only, game/ never mounted), ring
autosave=10 41-60, -time-limit default 1500 s (TL= override), pkill -x
dosbox-x cleanup only, and prints an instant offline readout per slot
(T, owned records, scored-stars DAT_000482fb, selector DAT_00043510,
rank DAT_0004350c). Nothing is scripted — real play is the whole point.
Head-invocation note: the per-run headless invariant serves agent-
automated runs; a user-run session is interactive BY DESIGN (user's own
DISPLAY). What the user must do inside the game, minimum: colonize past
50% of stars (OQ-021), declare war once AND accept/join an alliance once,
end turn (OQ-023), and let two fleets exchange fire once, end turn
(OQ-010). Zero-slot edge measured pre-deploy: title-menu slots read T=0
with selector = uninitialized heap (e.g. 0xC500) — slot-adjudication
law for the analyzer: trust slots with T>0 only.
Status: READY, not yet run (agent does not play; needs the user).
t111 AMENDMENT: the script's DISPLAY default was :0, which does not exist
on this host (only socket X9 / Xvfb :9 + x11vnc localhost:5910) — a bare
invocation silently failed, the probable reason ten VNC connection bursts on
2026-10-27 produced no capture. Default is now autodetect (verified: a
TL=90 self-test on :9 captured 9 slots end-to-end; artifact renamed
work/r1/selftest-t111-playcap). Watch hygiene: idle boots still write slots
with in_game=true, T=50, score=0 — mtimes + score movement, not in_game,
prove a sitting.

## t89a — OQ-010 code-site upgrade: session budget interrupt (NOT a research block)

The t70 entry above is SUPERSEDED for the research leg: t85g..t88a closed
every named OQ-010 residual with cited static evidence (docs/re/combat.md
S2d-S2h). What remains is the contract's second leg — the rewrite
combatPhase code-site change + pin test — and that work was CUT OFF this
iteration by the run-time budget, not by a research or tool blocker.
Best default to proceed under: t89 runs next session exactly as scoped in
docs/re/combat.md S2i (site campaign.cpp:1247-1322; edit = SUM-of-researched-
weapon-Levels volley + explicit decision on the uncited noise draws; then
run_tests + scripts/record_playthrough.sh regeneration + gate). The
"rewrite has no combat phase" BLOCKED branch is MEASURED DEAD — the phase
exists. If t89's noise removal changes timeline outcomes, that is expected
regeneration (PLAYTHROUGH.md is generated output), not a regression; the
gate 3l budget (1200 turns) must still end VICTORY on seed 2024 or t89
reverts the (b) leg and keeps the draws with a documented-default note.
RESOLVED t89 (2026-10-26): executed as scoped. Noise removal stands (cited
determinism); seed 2024 resolves Control t777 FINITE inside the 1200 budget
(42 Extinct t581, 13 Extinct t503, 1/2 Control t842/t677), 109 tests 0 failed,
PLAYTHROUGH regenerated. OQ-010 CLOSED; this block is closed history.
