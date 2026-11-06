# OPEN QUESTIONS — live closeout ledger (v2, strict-close)

Statuses: open | CLOSED. Nothing else. A question closes ONLY with cited
evidence (Ghidra address / extracted-file offset / pointer-law guest-phys
measurement from a named capture) + the rewrite site upgraded + docs/re/
updated + a gate or test pin. FINAL-DEFAULT is not closing (docs/GOAL.txt).
v1 full evidence text for every row: archive/ralph-v1/OPEN-QUESTIONS.md.
v2 FULL LEDGER (every CLOSED row's complete evidence text, archived
2026-11-03 when this file was slimmed to open rows + pointers):
archive/state-v2-full/2026-11-03/OPEN-QUESTIONS.md (md5 e897be73e0fd4b06cb51aa0881c0ff5d).
Full per-iteration working notes for ALL of v2: archive/state-v2-full/2026-11-03/wip/.
Do-not-retry prohibitions: docs/REFUTED-ROUTES.md.

Format: ID | area | question | status | what closes it (in-hand route)

OQ-005 | shp | .shp shape-library codec: in-record DIMS location for the
80-record residual class (container CLOSED 208/208; grammar CLOSED t61-t69)
| open | CLOSED PORTION (full evidence: archive 2026-11-03 + shp.md):
control-byte grammar verbatim FUN_0005caac 0x5cca3..0x5ce77 (shp.md S9); blit
5-arg law + stream=PAY+(tsz|u64dir[k-1])+0x18 (S12/S14); runtime table uniform
delta{sel0:8,k>=1:24} 4 libs x 43 selectors live-RAM (S17 r1_shp_ramtable.py);
corpus MEASURED 208 libs/1557 recs/1484 decode-pass; dims-gate + span-bound
validator artifacts corrected t182/t197 (shp.md S18/S21 — do NOT re-litigate
those 31 records, they decode); cos_star selector law t200 (SEL=4*[star+0]+
cls ladder; k40..k51 addressable-empty, k52..k54 unreachable); pop-slot library
= 17np.shp (t254). CODE SITE: rewrite/src/formats/shp.{h,cpp} ShapeLibrary
(container laws, blit-faithful clamp, 4096 dims cap) + tests/test_shp.cpp.
RESIDUE (80 records/31 files, decomposed t278 shp.md S24.2): 25 zero-byte
ladder slots + 12 cos_star k40..k51 + 4 invalid-dims (mouse k6/k7, 1starmap k1,
sg50expl k9) + 2 t197 demotions (mouse k5, sg64expl k0) + 3cfgnew k12 (vendor
EOF truncation). W3 route EXECUTED NEGATIVE (all 75 decoder sites read dims
from record header only; docs/REFUTED-ROUTES). Closure class = human-verifiable
drawn frame (R13 blocks self-grading) OR user ruling on the shipped decision
sheet work/r1/shp_png/decision-sheet.md (88 rows, docs/DECISIONS.md D1) OR a
vendor draw-capture session. Blind sweeps FORBIDDEN (R2). Default in force:
decode per S16 V/A law, residual skip-and-warn in tooling only (rewrite renders
its own vector art; codec = validation asset). | open

OQ-016 | loop | campaign per-turn constants: income formula, pop growth
curve/cap, starting items, build order, expansion cadence, home placement
| open | CLOSED SUB-LAWS (full evidence + retraction history: archive
2026-11-03 + docs/re/income-law.md): income channel law 138/139 battery (pin
campaign_channel_law_oq016); POP GROWTH pop==+0x42 UPOP dots, counter-50,
colonise :=2 (verified chase capture r1deep-20261007-224831); BUILD QUEUE + AI
SELECTOR LAW (queue 1/planet, acc+=stored IND 0x39005, complete acc>=COST
0x390a3, selector queue-empty-only caller 0x3ead6, COST/IND>=70 abort; rewrite
buildPhase pendingItem/buildAcc + pin campaign_build_queue_law_oq016); POP-CAP
recalc +0x4a = clamp(0..100, +0x55 + MPOP sum ALL active slots) 72066/72066
(income-law T33 — t31/t32 '+2 residual' was the missing +0x88 harness artefact,
RETRACTED); +0x55 seed law nb//3+5 @0x37f84..0x37f9e + pin
campaign_pop_cap_seed_law_oq016; TERRAIN GENERATION LAW end-to-end (rng%5 size,
rng%11 row, draw chain @0x37eb7..0x37ee0, T36); terrain-mutation via item-36 +
world-gen |8 rock only (t29b 40k-sample census); HOME JOIN MEASURED t270
(DWORD[0x12e1d+race*0x1ee] == star base NAME-0x1C; trust turn>=1 only, turn-0 =
template residue) + home placement RUN-LOCAL (11 distinct sets/11 lineages;
rewrite pickHomeStars was a documented MISMATCH (deterministic max-min BFS) —
SUPERSEDED t295 by the cited HOME-STAR DRAW LAW, see S-T295 below);
pending-build reserves its
slot (t271: byte1:=item id, word2 bit0 CLEAR — pending IS ring-observable).
ATTRIBUTION FIXES t273 (binding for all future mining): owner INDEX byte +0x56
(NOT handle u16+0x54); stale-echo pairs mint phantom deltas; the t251 mine is
VOID on both bugs; damage-vs-non-at-war-owner STILL ZERO corpus-wide.
RESIDUE (each with a route): (1) Phase Bomb nuke law — capture-gated, BLOCKED
section + one-run recipe; (2) setup-time home DRAW law — CLOSED MEASURED
2026-11-04 t295: uniform rejection draw per race in race order, k=draw%T,
store row_r+0xd @0x22edd, claim gate 0x22ee0 (FUN_00022ce4 0x22eb4..0x22f55
full disasm + census scripts/r295_home_draw.py: equal-marker 30/30 turn<=2,
distinct 36/36, index chi2=31.0 df=49 crit 74.92); docs/re/income-law.md
S-T295 + docs/re/_wip_t295.md; rewrite pickHomeStars upgraded, stream
interleave vs world-gen stays UNMEASURED (isolated homeLcg_, distribution
law); (3) word[+0x16] template source — CLOSED MEASURED 2026-11-04 t294:
FILE TABLE, planitem.txt ASCII block after '#' (scalar->DS:0x66e4 @0x3802c,
11x4 weights->0x744f4 row-major @0x3801e..0x38067, grid B->0x7445c, grid C
->0x744a8); EXE-constant hypothesis dead two ways (0x744f4 past the
initialised data segment; image-wide SIB-aware store census = ONE writer,
the loader @0x3805f); file == banked runtime == live RAM 58/59/60.sav; the
INDEX itself stays the rng%11 draw @0x23a97; rewrite upgraded
(TerrainTables+loadTerrainTables economy.{h,cpp}, cfg.terrain consumed
campaign.cpp, main.cpp injects; pins tests/test_terrain_t294.cpp x5,
mutation-verified; income-law.md t294 block); (4) per-slot shield-byte
consumer (OQ-019 family); (5) human build-order minutiae 0.4% samples;
item-35/35 completion branches = MEASURED zero-witness + AI-unreachable
(REFUTED t271, re-open conditions there). t299 debugger leg witness ran
(2026-11-04): zero fires; t301 re-attributed as ARMING-FAILURE not a bypass
law (see OQ-019 note + ships.md S28); no OQ-016
constant moved, row stays open.

OQ-019 | ships | per-ship design model (hull+gizmo inventory), sugar-cube->
hop scale, vendor cost hack, Orbital Docks effect
| open | CLOSED PORTION (full evidence: archive 2026-11-03 + docs/re/ships.md):
gizmo record law FUN_00049074 stride 0x6a x 76 == file census, RESREQ bitmask
+0x33, cat-switch copies Level->+0x52/56/5e/62, generator Power->+0x66 (§6);
cost hack CLOSED t16/§9 (sole gizmo-record write = loader parse 0x491b5; the
inherited +0x46-writers pointer is STALE — do NOT re-census); inventory law
CLOSED t46 (landed ship = active item-23 ring row, §10); Orbital Docks readers
§12-13 (upkeep/propulsion/range/step/fuel; executor has NO drive->distance
term); BUDGETS CITED t101: MOVES=[ship+0x94] refilled each resolver call to
drive stat SUM [ship+0x10] (FUN_0004a658, live 32/35), POWER=[ship+0x88];
SCALE MEASURED t183 (ships.md §17): FUN_00049f54 walks min(d/160, MOVES) sugar
units per resolver call, steps=max(1,round(walk)) capped by fuel; const pool
live 20/20 (1/160@0x25ff, 32.0, 5.0, grid quantizer DAT_000895dc=32);
round-robin = min-fuel one-ship-per-call inside turn loop FUN_00024f24
 (0x12e10 zero obj0 writers — no autonomous day-tick); LANE-STEP
LAW two corpora zero violations (|dx| == step0 or step0/3, step0=u16[+0x8]+
u16[+0xc]; /3 lane-scoped) + TURN-ATOMICITY (same-turn st5 dx EXACTLY 0,
17,595 pairs — t187 '4.67=3 substeps' DEAD, 4.6667 is one step); st4 = DWELL
state, in-system march resolves inside one turn boundary, invisible at 10 s
ring cadence (t265, 21 runs d=0.00 — corpus mining class CLOSED t49/t58/t265,
scripted capture ONLY); MAGNETRON runtime witness ZERO x3 (t265 off-grid
instrument P(false neg)<0.1%, t273, t285) — use-site stays static-cited
(gizhelp.txt:1173-1181 verbatim; kind==5 handler 0x21f58).
RESIDUE: (1) sugar-cube per-turn clamp/arrival granularity — t293 SPENT the
3-launch scripted-capture budget, NEGATIVE (order never issued: orbital-grid
dot-clicks navigate, never select; full autopsy docs/re/_wip_t293.md +
ships.md t293 block; drive background=true, 420 s foreground cap kills a full
session). t296 CLOSED THE SELECTION SUB-PROBLEM STATICALLY (ships.md S24 +
_wip_t296 S1..S9, every block re-dumped verbatim): four cited gates — clip
exists iff [ship+0x58]==4 (builder 0x1d6bb), clip kind==2 (0x1b6fc/0x1b9f6),
owner [ship+0x54]>>16==ds:0x7458e (0x1b709/0x1ba16), MOVES [ship+0x88]>0
(0x1b716/0x1ba2c) -> [batwin+0xb7]:=2 (0x1b71f/0x1ba39); the dots are kind-3
PLANET clips so G2 always skipped, and in mode 2 a plain map click CLEARS
selection (0x1b114). REMAINING UNKNOWN = the destination-entry widget that
posts msg 0x50 (ds:0x43508 := [sel+0x42+ebx*4] @0x1b5dd/0x1b5e6 + command-ring
0x56ad4 code 0x11): no widget-side poster outside the batmode family in the
image-wide imm census; t297 re-read the msg-4 ROUTER 0x1b070..0x1b0d6
(verbatim, _wip_t297 S1/S2): a non-null [win+0xaf] routes EVERY click to the
batcon handler 0x1b91c(ecx=1) BEFORE the mode-2 deselect branch, and the
0x1ba8c leg publishes ds:0x43508 + ring code 0x11 directly at mode 0 — the
mouse route MAY reach publication with NO msg-0x50 widget. LIVE SESSION #1
t297 (work/r1/t297-order-20261104-152048, scripts/r297_order_session.py)
NEGATIVE: picker bug aimed it at an owner-1 ship (owner==0 filter missing —
fixed same-session), no kind-2 ever appeared. MEASURED corrections T297-A: ds
globals live at B+0x82bb0+X NOT B+X, and BOTH have non-order writers (0x43504
= 0x256825 non-null at idle t1086; 0x43508 churns without input) -> DELTA-only
witnesses. T297-B: batwin INSTANCE unpinned (u32 0x1aef8 zero refs in RAM;
0x1b91c only inside a verbatim payload-image copy at 0x22cac1/0x22eb3b).
GATING FACT: at t=1086 owner 0 has NO kind-4 ship (11 ships, kinds {3,5}) —
nothing is selectable; slot 8 becomes kind-4 MOVES=12 at t=1087 (the t293 5->4
lander) -> t298 MUST End-Turn ONCE before picking, target slot 8, and find the
sprite by COLOUR CLASS (ships.md S25). LIVE SESSION #2 t298
(work/r1/t298-order-20261104-174236, scripts/r298_order_session.py, 3
launches, mouse budget SPENT): End-Turn-once worked, full S1-S7 battery ran,
STILL no kind-2 — but the battery never saw the target (ships.md S26):
FLEET-LIST ORDER IS NOT ARRAY ORDER (measured rows Sparrowhawk/Erebor/
Erchamion/Ignatz = slots 18/7/16/22; sort law UNKNOWN) and unbounded colour
finders return SIDEBAR CHROME (client rect x 7..465 hard bound). New
measured law: RAM pointer VALUES are guest-PHYSICAL (target = member
value+0x88; t297-B zero-refs negative refuted — physical pattern of 0x1aef8
has 1 hit @0x247978); ds:0x43504 = current-system STAR record ptr ("Icarus"
read from it) = system-identity oracle; ship_array_law count 30 UNDERCOUNTS
(named owner-0 ships at 31/32/33; header "14 Ships" == 14 named records);
command ring churns from non-order input (delta-only, not an oracle).
NEXT WITNESS = DEBUGGER CLASS t299 (BPLM 0x1ba39/0x1ba5e/0x1baa7/0x1bad3/
0x1b114, r290 poke skeleton, dosbox-debugger.md) — no fourth mouse launch.
t299 RUN (2026-11-04, 6 debugger sessions work/r1/t299-leg-*): instrument
PROVEN (8 code BPs armed incl. handler 0x1aef8 + router 0x1b070, control
MEMDUMPBIN byte-exact) and NEGATIVE x3 with attribution: the same sessions'
FLEET/row/End-Turn clicks changed game state, yet ship/planet/empty clicks
in the Icarus system view fired ZERO legs. t301 RE-ATTRIBUTES the negative
(runs t299-leg-{213540,214042} + offline law, ships.md S28 + _wip_t301): the
TOGGRID control-click ZEROED but was INVALID (rect 557,403-587,433 pixel-black
in the Icarus view; windows.txt gives the SAME rect to TOGSHIPS/COSMOSWnd and
TOGGRID/BatModeWnd — sibling ambiguity), and the offline dispatch law shows
every msg goes `mov ecx,[win+0xa7]; call [ecx+4]` into the ACTIVE window's
class table (slot 1 = universal dispatcher file 0x30d08, verified in all
sampled tables). t299/t300 armed NEITHER slot-1 NOR the active class slots —
zero-fires = ATTRIBUTION FAILURE, not a bypass law; the WORKING FLEET/End-Turn
clicks executed type-0 class 0x247cb8 legs nobody armed. Window-record law
(magic 0x12345678, NAME@+0x20, table@+0xa7) + re-armed r299_leg_session.py
(router/cos_*/btn_* legs, stop dumps record NAME) are in hand; NEXT = one
debugger run, witness on the class the stops name (ships.md S28). t302 RAN IT
(run work/r1/t299-leg-20261105-004605 rc=0, ships.md S29 + _wip_t302): the
dispatch law is LIVE-CONFIRMED (cos_hdlr stop names COSMOSWnd, msg 0x3b
periodic; End-Turn fires btn_hdlr on NEXTTURN record with edx=0x7 ==
windows.txt SENDMESSAGE 7 VERBATIM = positive control; the turn-advancing
click fires COSMOS slot 3 edx=0x0). The t299-era zero-fires are fully
re-attributed: wrong legs + a fire-detector pattern that never matched this
build's DrawCode form. t303 RAN THE CENSUS (2 sessions
work/r1/t299-leg-20261105-{015611,020416} rc=1, _wip_t303 + REFUTED t303
amendment): whole-log pty census {cos_hdlr:15, all five call-[ecx+4] sites:0}
— the 0x3b pump reaches cos_hdlr WITHOUT slot 1, and t302's own log shows
btn_hdlr firing with router armed+silent, so the t301 "universal slot-1
router" law is REFUTED; a pixel-proven WORKING sprite click (modal "Ship
'Sparrowhawk'" dialog, vision-cited) fired NONE of cos_hdlr+5 sites. Map-click
entry is neither cos_hdlr nor slot-1 [verified negative]; the real dispatch
instruction is UNKNOWN. REMAINING RESIDUE: no per-ship selection WRITER
witnessed; t304 = [esp] caller-witness at any cos_hdlr stop (bank_stop
already patched: ret_stack.ret0/ret0_file_off) -> arm census at the named
caller; controls need close_eventwin between clicks + btn_hdlr armed. Row
stays open.
(2) per-ship build/redesign path =
BUILD DECISION not RE unknown (t256c census 62,762 rows, AI dossier row 16
GAP->BOUNDARY; docs/DECISIONS.md D3); (3) magnetron witnessed use (scriptable
via t289 drive class). | open
t304 note (run t299-leg-20261105-033648, ret_stack witnesses): the working sprite click DOES walk the class msg layer — btn_hdlr msg 0x1 NAME='Leave Orbit' via pump site file 0x56cda (ff 56 08 call [esi+8]); planet/empty clicks both hit the SAME 'Cancel' record msg 0x4 via 0x56c74 = modal residue, controls INVALID-AS-RUN (re-run with dialog-drain loop needed); NEXTTURN = btn_hdlr msg 0x8 NAME='PLSQUARE' direct E8 call site 0x3d38f. Selection WRITER still unnamed — row stays open (strict-close).
t305 note (run t299-leg-20261105-061825 rc=0, close_eventwin pre-arm + FIXED fire detector, docs/re/_wip_t305.md S4): per-target msg-ids MEASURED under normal core — baseline pump s2_56cda+cos_hdlr msg 0x3b COSMOSWnd (15/60 s); sprite(48,151) s2_56cda x2 msg 0x8 NAME='PLIND' + btn_hdlr x1; planet(439,331) s2_56cda msg 0x8 NAME='PLANETALLOC' (t304 'Cancel residue' SUPERSEDED for planet once drain applied); empty(236,200) fires ONLY site 0x56c74 (unbanked render, autosave-gap proven); NEXTTURN s2_56cda x2 msg 0x8 NAME='PLSQUARE' + btn_hdlr x1; 20 other slot-2 sites ZERO in every window. Selection WRITER still unnamed (msg 0x8 = repaint/dispatch at window records, not the selection store) — row stays open (strict-close).
t306 note (run t299-leg-20261105-101054 rc=0, batmode sites armed under corrected core + FirePat, docs/re/_wip_t306.md + ships.md S32): BATMODE STATIC-GATE ROUTE CLOSED AS A NEGATIVE — working sprite click (48,151, PLIND msg 0x8 btn_hdlr witnessed, control alive) fired ZERO at entry 0x1aef8, msg-4 router 0x1b070, and BOTH effect writers 0x1b71f/0x1ba39; selection oracle pairs moved nothing attributable (consistent with gating fact: t=1086 owner-0 has no kind-4 ship, but entry/router zeros are pre-gate). Writer hunt re-scoped to the non-batmode t296 store-census members: DAT_43508 {0x51a8e, 0x51fc2, 0x55bbd} + DAT_43504 {0x28ec2, 0x28ef6, 0x36b01, 0x52003, 0x55d35} (ships.md S24/S32). Selection WRITER still unnamed — row stays open (strict-close).
t307 note (run t299-leg-20261105-112859 rc=0, the eight non-batmode census
legs armed from the galaxy map + new --star-click battery, docs/re/_wip_t307.md
+ ships.md S33): FIRST LIVE FIRE AT A CENSUS MEMBER — w43504_28ec2 stopped
with EAX=0x256825 (Icarus star record) seconds after the (238,282) star click
that ENTERED the system (REQ-correlated pty render, follow-on bytes match
disasm 0x28ec7..0x28ed8 incl. ring post code 0x10). The writer is the COSMOS
FALLBACK star-select publisher (fn 0x28e70, caller 0x27332; gates: empty clip
list [win+0x582]==0, ds:0x7e582>>16==1), NOT the per-ship selection writer —
OQ-019 residue (per-ship select + destination widget) UNTOUCHED, row stays
open. Census instrument now LIVE-VALIDATED (it catches these writers), so the
seven remaining zeros are context statements. Binding instrument law from the
fire: data-segment immediates are REBASED +0x242000 in code RAM
(a3 04 55 28 00 @0x28ec2). NEXT: resolve the DAT-base question (true
DAT_43504 = B+OFF-0x88+X reads 0xff idle = SELECTED-NONE vs the t297-A
oracle address 0x28558c star ptr — ds:0x4358c zero disasm refs), then the
ring-consumer windows (0x55a60 family fires only on a turn advance).
t308 note (runs t299-leg-20261105-{140250,143815} both rc=0, docs/re/_wip_t308.md
+ ships.md S34): DAT-BASE QUESTION CLOSED — the oracle was NEVER off-target
(sav Memory member = linear+0x88; member B+SL.OFF+0x43504 IS linear 0x285504 =
the rebased store target; the t307 0xff datum read the member as if linear = a
different variable, REFUTED t308 amendment). DAT_43504 STAR-CASE WRITER FULLY
WITNESSED WITH A REAL DELTA: green-annulus pip law click (182,284) ENTERED
Vega; w43504_28ec2 stopped EAX=0x255BC5 (= star-record base k=0, name law
0x255be1-0x1c 'Vega'; screenshot vision 'Vega / White Dwarf'); oracle pair
0x256825 'Icarus' -> 0x255bc5 'Vega'; fire reproduced 3/3; DAT_43508 unchanged
(order-destination semantics consistent). STILL OPEN (strict-close): OQ-019
residue = per-SHIP selection writer (kind-2 clip; no kind-4 owner-0 ship at
t=1086) + the msg-0x50 destination widget (DAT_43508 legs zero x3 runs,
instrument live-validated); NEW SHARPENED HOLE: ring code 0x10 POSTED 3x but
the 0x55a60 consumer family never ran inside any armed window incl. a
NEXTTURN-msg window — consumer timing unresolved. NEXT: t309 ring-consumer
windows (arm the 0x55a60 family + advance the turn INSIDE the armed window).
t309 note (run t299-leg-20261105-161711 rc=0, consumer/post family legs armed
in every window incl. two HOT HOLDS, docs/re/_wip_t309.md + ships.md S35):
THE RING SELECTION CHANNEL IS DORMANT AT MAP IDLE — measured, not inferred:
leg ringB_post (RING-B POST FN ENTRY 0x55a60, gate-free prefix) fired ZERO
whole-log across baseline+star+hold+nextturn+hold, snapshots ringB_count=0/
widx=0 in EVERY window, consumer 0x55ae8 zero, and the star-click RING-A post
BODY never ran (its sole side effect inc [core+0x44ac] left idx 0 through
every snapshot; post-fn entry leg zero too). RING-B is structurally shut at
idle (pump gate [core+0x475a]==0 blocks unconditionally), so 'consumer timing'
was the wrong question — SELECTION IS RENDER-DIRECT (direct DAT stores). NEW
WRITER INVENTORY (whole-image a3+89/15 sweep): DAT_43504 has SIX writers (the
t296 census missed 0x51ac9 in fn 0x51b68, edx=0x13bc5+32*k star record addr);
DAT_43508 has SIX (missed 0x55bcc); fn 0x51b68 owns three of twelve. mode4226
IS A VIEW ID (map=1, system=0x10) — the consumer's mode==1 gate confines it to
the galaxy map. Star witness delta reproduced 4th time (Icarus->Vega). Turn
advance across NEXTTURN UNRESOLVED (1086->1086 but 10 s sav granularity,
t260 law — claim neither way). OQ-019 row STAYS OPEN (strict-close): per-ship
selection writer + msg-0x50 destination widget still unnamed; NEXT t310 = arm
fn 0x51b68 trio + ringA post entry/body legs {0x56ad4,0x56b4e} + snapshot
rd(0x7e5aa)/rd(0x7e89e), star-click + hold; EAX dump at 0x56ad4 settles the
core-base identity live.
t310 note (run t299-leg-20261105-173627 rc=0 attempt 2, order battery pre-turn
1086->1087 + sprite + planet + digit keys 1..9 + NEXTTURN, legs {w43508_51a8e,
w43508_51fc2, w51ac9 NEW, w43504_52003, s2_1616f NEW, btn_hdlr}, docs/re/
_wip_t310.md + ships.md S36): THE WRITER'S CLASS IS NAMED — fn 0x51834 is the
STATUSWND msg handler (RAM class-grid scan: fn entry+P0 exactly 1 hit RAM
0x248050; sole window-magic referrer of the instance class ptr 0x247FC0 named
'STATUSWND'; FILE-image scan 0 hits = relocation blindness CONFIRMED). The
msg-0x1c01 destination path (0x51A67: mouse-X gate -> DAT_43508=system ptr +
ring-A 0x11 / DAT_43504=star addr 0x13bc5+k*96 + ring-A 0x10) was NOT reached:
whole-log zeros on all five writer/relay legs with btn_hdlr x4 alive; digit
keys entered the dispatcher (ret0 0x56c77, ret1='1') but a 'Cancel' popup held
focus, not STATUSWND. ds:0x484ec MEASURED = last mouse X (0x30/0x1b7 after
x=48/x=439 clicks) — 'turn gate' reading REFUTED (REFUTED-ROUTES t310
amendment binding). Span fix: 0x51ac9 lives in fn 0x51834, NOT fn 0x51b68
(label builder). OQ-019 row STAYS OPEN (strict-close): destination-widget
fire still unwitnessed; per-ship select untouched. NEXT t311 = STATUSWND-
focused digit keys: close_eventwin to the bare map immediately before the key
window + ENTRY leg at fn 0x51834 0x51834 (dx=msg id, ret0=dispatch site) —
witnesses or refutes 0x1c01->STATUSWND in one run.
t311 note (run t299-leg-20261105-182822 rc=0 attempt 1, ENTRY leg
fn51834_entry FIRST (census MATCH=True 7/7) + {w43508_51a8e, w51ac9,
s2_1616f, btn_hdlr}, battery pre-turn 1086->1087 -> close_eventwin +
assert_on_map BARE MAP -> digit keys 1..9 one armed window (post-arm popup
reguard) -> sprite -> planet -> NEXTTURN -> hold, docs/re/_wip_t311.md +
ships.md S37): BRANCH (c) MEASURED — STATUSWND RECEIVES NO MSG TRAFFIC AT ALL
(entry leg gate-free, fires for any caller; whole-log fn51834_entry:0 with
btn_hdlr x4 alive). Focus defect FIXED: bare-map keys hit btn_hdlr window
'NEXTTURNCONT' (edx=0x3, ret0 file 0x3177d), NOT the 'Cancel' popup — the
key-focused window on the bare map is a button-family class, so the digit-key
sender's call [esi+8] structurally cannot reach fn 0x51834 from map focus.
0x1c01-into-STATUSWND REFUTED as a live trigger (REFUTED-ROUTES t311
amendment binding). OQ-019 row STAYS OPEN (strict-close, honest negative):
destination-widget fire still unwitnessed; per-ship select untouched. NEXT
t312 = ORDER-PLACEMENT choreography (t298-B: select ship mode 0->2 -> click
planet clip dl==3 @0x1bad3 relay 0x326 ecx=4) with the TWO NEVER-ARMED
destination writers armed — w43508_51fc2 + w43504_52003 (the fn 0x51b68 pair;
0x51ac9 belongs to fn 0x51834 per t310 span fix) — plus s2_356a5 (the digit
sender's own call site, closes the t311 sender question) + fn51834_entry
first; all four legs already exist in LEGS, no script delta. fn 0x51b68 is
table-member-called (t309), the run names its caller from ret_stack. Pre-turn
gate must yield a kind-4 owner-0 ship (t298 law) or the sprite select is a
no-op.
t312 note (run t299-leg-20261105-192246 rc=0 attempt 1, BREAK lottery won
first try, scripts/r312_relaunch.sh, zero script delta; legset fn51834_entry,
w43504_52003, w43508_51fc2, s2_356a5, btn_hdlr; battery = t298-B order shape
pre-turn 1086->1087 -> bare-map keys -> rowjump -> sprite 48x151 -> planet
439x331 -> NEXTTURN, docs/re/_wip_t312.md + ships.md S38): BRANCH (b)
MEASURED — SECOND HONEST NEGATIVE. Whole-log {fn51834_entry:0,
w43504_52003:0, w43508_51fc2:0, s2_356a5:0, btn_hdlr:4}, census MATCH=True
7/7. DECISIVE: sel43510=0 in EVERY oracle snapshot (sprite_before AND
sprite_after included) and mode4226 0x1->0x11 is the map->system VIEW id —
the sprite-pixel click NEVER selects, so the t298-B order never exists and
fn 0x51b68's writer pair stays structurally dark (REFUTED-ROUTES t312
amendment binding: sprite-pixel select DEAD; both msg-0x1c01 senders
s2_1616f+s2_356a5 measured dead — do not re-run any map/key battery shape
for this row). SENDER QUESTION CLOSED (negative): digit keys reach a window
(btn_hdlr 'NEXTTURNCONT') yet s2_356a5 zero => the taken keysym path is not
the 0x1c01 sender. OQ-019 row STAYS OPEN (strict-close): the two residues
(destination fire + per-ship select) are ONE hole. NEXT t313 = fn 0x51b68
CALLER hunt OFFLINE on this run's own save/ dir — class-grid RAM scan for
0x51b68+P0 (t310 route: grid slot index FIRST, then infer which table the
game consults; file scan is blind, RAM only), and inventory what dispatches
slot hits for that class; only if the caller names a FLEET-window path does
a new capture shape earn its keep.
t313 note (OFFLINE, zero capture; save dir of run t299-leg-20261105-192246;
scripts/r313_class_scan.py + r313_name_b.py + r313_fleetwnd_map.py +
r313_writer_callers.py + r313_handler_chain.py; docs/re/_wip_t313.md +
ships.md S39 + REFUTED-ROUTES t313 amendment): CALLER HUNT LANDED — THE
WRITERS ARE FLEETWND's. 0x51b68 is mid-body of fn 0x51b64 = FLEETWND class-
grid slot 3 (cp 0x247fa8, magic rec 0xfe7a90 'FLEETWND'); FLEETWND handler fn
0x51cc4 has its OWN msg-0x1c01 path (je 0x51f3b exact) -> confirm leg (ecx==5,
string 0x2b6b) or jne 0x52059 -> system-state table (file 0x3d100 unrelocated;
RAM instance 0x211188 {0x51fb5 x3, 0x51ff6, 0x52037} runtime-composed, whole-
RAM unique, identical 3/3 savs) -> state 1/2/3 writes DAT_43508+ring 0x11,
state 4 writes DAT_43504+ring 0x10. CLASS LAW FIXED (grid stride 6, cp =
base-0x88, dispatcher 0x30d37 call [cp+0xc]; t310's slot-4 was an 8-byte-
shifted read). t312 dark writers EXPLAINED: digit 0x1c01 hit 'NEXTTURNCONT'
focus, never FLEETWND. Row STAYS OPEN (strict-close — offline chain names the
mechanism but no live store witnessed). NEXT t314: ONE capture — legs
fn51cc4_entry (NEW, census leg[0]) + w43508_51fc2 + w43504_52003 + btn_hdlr
control; establish FLEET-window focus via open_fleet, then digit-key + a
map-click x>150 variant; oracle DAT_43504/43508 + sel43510 + mode4226.
t314 note (runs t299-leg-20261105-{210255,212402} both rc=0, docs/re/
_wip_t314.md S0-S7 + ships.md S40 + REFUTED-ROUTES t314 amendment): FLEETWND-
FOCUS TEST RUN VALID + NEGATIVE. Run 1 exposed a drive law (rowjump click
(200,93) CLOSES the FLEET window, rails 188->0) so its keys went to 'PLBUILD'
— invalid, not counted. Run 2 VERIFIED focus at arm (reguard logs rails=188,
popup-closed) then pressed 1..9: whole-log census {fn51cc4_entry:0,
w43508_51fc2:0, w43504_52003:0, btn_hdlr:4} — FLEETWND received NO msg of any
kind with its window open; the single fleet_keys stop was btn_hdlr win=
'STATSHIPLST' edx=0x3 ret0 file 0x32943 (inside STATSHIPLST's own slot-2 fn,
cp 0x247c70 read from RAM). GAP named: s2_356a5 was NOT armed run 2, so
"sender never fires under FLEET focus" stays t312-extrapolation. Offline this
session (objdump verbatim): sender branch 0x35675..0x356a5 fully decoded —
gated on [ebp+0xaf] (max digit 9, 10 if ==1), sends edx=0x1c01 ecx=0 via
call [esi+8] on ITS OWN window [ebp]; fn 0x32fa4 = 8-stride accessor
[[win]+0xc7+idx*8] (idx from msg arg, 0..0xff bound) — the writer-block state
byte [eax+0x58] reads a TABLE-SELECTED record (t313 "system-record" label
unproven); STATSHIPLST[+0x58]==0 in 40/40 saves across both runs (rec datum
only); payload store census for [r+0x58] = ZERO sites (computed offsets, file
blind). Row STAYS OPEN (strict-close — no live store witnessed). NEXT t315
(offline, zero capture): name the digit-handler window — find the fn containing
0x35696 (ret-bounded walk + E8 census), then RAM grid scan for fn+P0 (r313
route, NEW target so not spent) and magic-rec naming; that window is who the
digit key talks to, and its class decides whether FLEETWND can EVER receive
0x1c01 from keys.
t315 note (OFFLINE, zero capture; scripts/r315_handler_scan.py; docs/re/
_wip_t315.md S0-S6 + ships.md S41 + REFUTED-ROUTES t315 amendment): DIGIT-
HANDLER WINDOW NAMED — IT IS 'LOADSCREEN' (loadwin.cpp save/load screen). fn
0x35696 lives in fn 0x354f8 (unique prologue 56 57 55 81 ec 44 01; ZERO E8
callers); RAM hit exactly 1 @0x247db0, grid 0x247da8 slot 2, cp 0x247d20,
magic rec 0xfd705c NAME='LOADSCREEN' 3/3 saves both runs (controls 1-hit
exact, 5th reproduction). The digit->0x1c01 route is a MENU MECHANISM:
FLEETWND can NEVER receive 0x1c01 from keys (t314 zero explained, not just
measured). Whole-payload 0x1c01 census CLOSED at 5 sites (LOADSCREEN sender,
BatControlWnd receiver fn 0x16420 grid slot 3 cp 0x247850, relay 0x16169
t311-dead, msg-emit builder 0x33375 via fn 0x56ca4, E8-operand false
positive 0x1756b) — no in-game-window sender exists. GATE CHAIN MEASURED
EXACT: caller 0x51f3b eax=[rec+0xab] -> fn 0x32fa4 [win+0xc7+idx*8] ->
record; gate 0x52059 rec[+0x58] in 1..5; writer arms copy rec[+0x59..c] to
DAT_43508/43504. FLEETWND chain 0xfe7a90 -> inst 0xfe7ac0 -> slot0 rec
0x600000: GATE BYTE GUEST 0x600058 == 0, datum 0x600059..c == 0, 212/212
valid-chain saves (221 have [win+0xab]==0 -> accessor error path). Row
STAYS OPEN (strict-close — no live store witnessed; the gate byte was again
never evaluated live). NEXT t316 = the state-byte WATCHPOINT route on guest
0x600058 designed against the msg-emit path fn 0x56ca4 (NEW target), the
only route left that can witness a writer (key shapes are dead-by-mechanism
per t315 amendment; FLEET-rect interior click still untried as the intake
shape, t314 residue (a)).
CLOSED (slimmed 2026-11-03: full evidence text of every row below lives in
archive/state-v2-full/2026-11-03/OPEN-QUESTIONS.md and the cited law file.
DO NOT re-open, re-derive, or re-census any of these from a fresh session —
the law-file citation is the working handle; re-treading is iteration waste.
Format identical to open rows: ID | area | question | CLOSED date+task | evidence; code site.)
OQ-003 | gam | .gam packed-entropy residue | CLOSED 2026-10-13 t181 | measured three-class disclaim scripts/r1_t181_banddiff.py (band boot-vs-played 432/2048 vs header/S-table 87-100%); docs/re/savegame.md section t181; rewrite unchanged (fresh-start-only)
OQ-004 | tables | which tables load; .cob container grammar | CLOSED 2026-10-06 06s | u32 N + N x 50B names + N x u32 offsets, ascend00 54/54 md5; RAM name table 0x250c1c 3/3 captures; pool-relative immediate law 337 sites; docs/re/datafiles.md S3-S5 (gate 3i2 scripts/cob_probe.py); no rewrite delta (reads extracted dir directly)
OQ-006 | audio | headerless sample rate | CLOSED 2026-10-07 | DEVICE rate 22050 measured (open chain PUSH 0x5622 @0x4f690 -> setter 0x6e000 stores [obj+0x3c]; default 11025 always overwritten); docs/re/audio.md 3.1; pin audio_open_rate_measured_oq006; channels documented default mono (no vendor field)
OQ-010 | rules | combat damage application | CLOSED 2026-10-14 t89 | firing order 0x4a5c1, damage design[+0x52]/[+0x4a] no hit roll (measured-negative), shield-then-hull absorb, death 0x49d2c, commit mode==1 0x25560/0x25570; docs/re/combat.md S2d..S2j; rewrite campaign.cpp attackScore/defenseScore/combatPhase + pin campaign_combat_law_oq010
OQ-012 | mapgen | size options + pps + shell position | CLOSED (a 2026-10-12, b-d 06o/06p/06q/06k) | density cycle 50/75/100/15/25; pps U{1..5}; shell position law; docs/re/mapgen.md; rewrite --stars knob + upgraded shells (rewrite site mapgen.cpp)
OQ-013 | tables | restree semantics | CLOSED 2026-10-06 | live = 66 main rows; stride 75 record map; COST LAW runtime = file_cost x (row-20) clamp 65000 reproduced 66/66 (0x4691d..0x46a15); docs/re/research.md 6; rewrite Tech::runtimeCost + 2 pinned tests
OQ-014 | tables | planitem unknowns | CLOSED 2026-10-06 | loader FUN_00037fc0 + checker FUN_0003830c; stride 0x28 record map 39/39 byte-exact; REQUIRES law avail iff req==0xFF || (req<66 && owned) -> 254 DEAD; grid C row sums = size-class cells 2650/2650; docs/re/economy.md section 4; 3 pin tests (gate 3l Trucking grep); rewrite requiresAvailable
OQ-015 | dip | DA_ template order + %token | CLOSED 2026-10-08 t12-t14 | chooser FUN_00044a44 == ACTIONS pool idx; %token census 22/22 == {%m,%y,%s,%t}; pins dip_action_chooser_law_oq015_t12/d_t13/d_t14; rewrite unchanged (trade gates -> engine build, docs/PLAN.md A7)
OQ-018 | audio | soundfx.txt pairs + VOC + theme map | CLOSED 2026-10-07 | voiceBand law 327/328 spans == disk sizes; VOC u16@25==0x0911 15/15; race->theme REFUTED (DAT_00010ba0 sole writer 0x21309); docs/re/audio.md 2.1; rewrite/src/formats/voc.cpp pins + test_audio_voice_band_law_oq018
OQ-020 | abilities | charge days for 14 charged SA_ | CLOSED 2026-10-15 t100 | cadence word WORD[0x6780+2*ability] == FILE 0x89330 zero writers (5:60 6:100 7:62 8:77 9:90 10:150 11:70 12:63 13:66 14:72 16:92 17:100 19:89 20:68); wired kCad[21] in rewrite/src/game/species.cpp abilityChargeTurns + COUNT-UP law; verify scripts/r1_t100_cad_verify.py
OQ-021 | victory | end-ctrl threshold | CLOSED 2026-11-03 t292 | LIVE presenter witness: BPLM sentinel 0028A2FB mid-pass stop 0x24274, evaluator FUN_00024a34, sel 0->5 DAT_00043510 @0x24d9f + rank 42 DAT_0004350c @0x24dab, end-ctrl.txt verbatim on screen; comparator V >= floor(2T/3)+1 MEASURED; run work/r1/t290-poke-a40-20261103-165405; docs/re/score.md S18-S20; rewrite arm campaign.cpp:2157 upgraded t291 + pins test_control_t291.cpp
OQ-022 | audio | music span-vs-check contradiction | CLOSED 2026-10-07 t8 | guard @0x59984 precedes checked call; DS:0xa200c all-zeros 10/10 saves; engine INACTIVE in captured states; docs/re/audio.md 3.4; no rewrite dependency
OQ-023 | dip | relation-state enum semantics | CLOSED 2026-10-29 t189b | state-3 ALLIANCE event OBSERVED @t1335 (cell0i=celli0=3, att +10/+10, 68 rows, scripts/r1_t188_state3_arbiter.py RC=0); flip 631>570 = static law 0x4562f/0x45641; enum 2=WAR/1=PEACE/3=ALLIANCE; docs/re/diplomacy.md 13+16; rewrite unchanged diplomacy.cpp:227/:244; engine residual -> PLAN.md A7
OQ-024 | rules | planet GOVERNOR assignment | CLOSED 2026-10-09 t45 | @0x38df0 branch pinned verbatim (item 33 -> PROS+=IND>>2, 34 -> RES+=IND>>2); [0x743b9]>>0x18 == UPOP(35) 32/32 saves; activator @0x38b26 sole trigger 0/2810; rewrite PlanetState::governor + pin campaign_governor_law_t45; docs/re/economy.md
OQ-025 | mapgen | non-default-density position law | CLOSED 2026-10-15 t79 | shell radii fixed at every size, populations halving law (T//2+1 then halve), reproduces T=50 battery exactly; docs/re/mapgen.md; rewrite shellRadiiFor replaces i%50 wrap
OQ-026 | visibility | fogged lane/star gating | CLOSED 2026-10-29 t195 | implement+pin at the row's own bar: viewerMaskFor == FUN_00021a84 verbatim, filter == 0x2914e AND, shareLaneVision == FUN_00046354 shape; rewrite laneVis_/starLaneVis_/starSelVis_ (obj +0x16/+0x17 twins); pin campaign_visibility_law_oq026_t195; docs/re/ships.md S23 L10

- > OQ-001 .cob offsets -> formats/cob.h reader (format block cites this ledger + FINDINGS P1a)
- > OQ-002 FLIC codec -> formats/flic.h (cites docs/re/flc.md)
- > OQ-007 CP437 -> decode sites game/species.cpp, game/research.cpp, game/starstat.cpp, game/economy.cpp, game/diplomacy.cpp
- > OQ-008 loader control-flow model -> ANALYSIS-ONLY (rewrite is fresh-start-only; no loader in rewrite; spec docs/re/loader.md)
- > OQ-009 AI data side -> ANALYSIS-ONLY input to the W-B-gated diplomacy/AI build (docs/re/ai-data.md; nothing shipped reads it yet)
- > OQ-011 POINTER LAW (scripts/r1_pointer_law.py 12/12 slots, gate 3q) -> measurement instrument only, cited by capture scripts + campaign.cpp:593
- > OQ-017 .fnt codec + UI wiring -> formats/fnt.h (cites docs/re/fnt.md) + ui/ui.cpp wiring
