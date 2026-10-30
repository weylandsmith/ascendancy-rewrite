# ai-dossier.md — consolidated stock-AI behaviour dossier (t179)

Synthesis of the t90..t105 static decodes into an answer to the player's open
question: **does the original AI defend systems and choose offensive thrusts,
or is it haphazard?** Every claim cites a docs/re section or an image address
verified there (plus three t179 probes, marked as such, run against
`work/ascend_restored.bin` — the base-0 OQ-011 pointer-law image; nothing here
was run against a device). Addresses are image offsets. `PLAIN` section at the
bottom is the player-facing restatement, no jargon.

## 0. ANSWER (one paragraph, then the evidence)

The AI is **policy-driven, not plan-driven** — a middle answer that the
evidence actually supports rather than a hedge. It runs a fixed per-turn
decision chain (diplomacy → build → expansion/research target → ability
maintenance → per-ship orders, aicode.md §1/§2) whose every stage has a cited
deterministic or stochastic law, and several of those stages are genuinely
strategic in the narrow sense: it buys defences when a threat counter rises, it
masses its fleet toward its nearest friendly ship, it fields its strongest
ships first, and it invades with a designated module-carrying ship. What it
demonstrably does NOT do is choose *where* to strike by evaluating the enemy:
the target slot that steers the whole race (DAT_00076492) holds a **research
row index, not a star** (§3b), the only "threat" quantity found anywhere is a
per-**planet** byte that gates shield purchases (§9), and the engagement code
picks who-fires by stored order state + slot availability in **list order**
(t179 P3), not by threat or value ranking. So: system-level defence is reactive
and local; offensive direction is essentially an accident of research order and
congregation, not a chosen thrust.

## 1. Turn frame — where the AI sits in the day

MASTER `FUN_00024f24` (aicode.md §1), single caller 0x55f06 in the END-TURN
dispatcher. Phase order verbatim from call sites: random-event window → income
0x2501c → order sweep 0x25023 → research 0x2502f → growth 0x2503c → pop-cap
0x25056 → **per-race AI loop 0x25062..0x25088** (skips the player row,
`DAT_0007458e`) → score/ownership 0x250aa → command exec 0x2542d..0x2546f with
the AI executor `FUN_00041260` at 0x2554f (§1 P8). Decisive structural fact:
**the AI acts through the same command primitives as the player** (build cmd
0x38818, gun dispatcher 0x49f28, ability 0x39c10 — callee set of 0x41260, §1
P8, verified). It has no privileged channel and no separate strategy module.

Per-race chain `FUN_0003e6e0` → decision block `FUN_0003ea54` (§2), in order:
(1) diplomacy update, (2) BUILD loop over the planet pool calling the selector
0x3f130 only where the build queue is empty (caller-side confirmation of the
t28 law), (3) EXPANSION/RESEARCH target pick if none, (4) `0x43b50(row,0)`
ability engine, (5) FLEET ORDERS: ship list then per-ship `0x40178`.
Elimination is a side effect of this function, not a strategy: no ships and no
colonies → row+3 := 0xffffffff (§2).

## 2. Diplomacy machine

Attitude is a stored per-pair word (relations base + `0x1b2`) with a stored
relation-STATE byte ladder (`+0x1c0`: 0/1/2/3 = none/contact/…/AT WAR/ally —
diplomacy.md §10–§12, t85b/t85c transitions), driven by per-race thresholds
from `raceNN.dip` DIPVALUES (ai-data.md §2, 21 races × 15 keys: DECLARE_WAR
130..450, ACCEPT_PEACE 200..530, PROPOSE_ALLIANCE 680..900 …) plus a BIO mood
sine (BIO_SIN_X / TWICE_X / HALF_X, period BIO_PERIOD 180..800 days — §2 keys).
Emitters: `0x3ecb8` attitude scorer → `0x3ef2c` state propagation →
`0x44690` proposal emitter (proposal builders 0x44fc0/0x454a4, relation-state
ladder tests 0x4492c..0x44a0e, adjacency 0x44634, escalation 0x44a44) →
`0x3eb88` ally-bitmask rebuild via 0x439f4 (§2 step 1, call order verified).

Combat writes diplomacy back: `0x43a4c`, the DIPLOMACY-ON-ATTACK handler
(identity corrected t87 — combat.md S2f-b; it is NOT star defense), firing at a
non-at-war power
subtracts `10*(word[0x13bc4]+1)` from their attitude toward you, DOUBLED if the
relation state was 3, clamps under `word[obj+0x1cf]-10`, and sets a permanent
bit in the global "attacked" bitmap `[..+0x48304] |= 1<<race`. That is the
closest thing in the engine to a reputation system, and it is a *consequence*
of shooting, never an input to the decision to shoot.

Ability tie-in: `SA_ForcePeace` (profile 6, body 0x43bf0) pushes every other
race's attitude-toward-self up to `ACCEPT_PEACE_threshold + 20` (§6.3),
`SA_Hatred` (17, 0x440b5) pushes third parties' attitude toward an enemy DOWN
to that enemy's DECLARE_WAR threshold. Both are attitude arithmetic, not
military action.

## 3. Build / research / expansion: one target slot, two pickers

### 3a. Build selector `FUN_0003f130` (income-law.md §9) [verified]
Runs per owned planet only when the queue is empty and stored IND > 0.
Order of business, cited: over-population emergency → demolish the highest-MPOP
cell (Colony Base exempt); Transport-Tubes priority when researched; min-REQUIRES
demolish sweep (research-gated items go first); random-legal-cell fallback;
then the evaluator `FUN_0003fc4c` (forced-emergency items — **this is where the
AI's defensive buying lives**, see below) and the need-class scorer
`FUN_0003fec4` returning class 0..3 (pop-crunch / prosperity / industry /
research-vs-industry slot comparison), jump table image 0x3f120 mapping class →
score column (IND/RES/PROS/MPOP).
PICK LAW: candidates = surface rows 0..21 (Colony Base skipped), and the
**first candidate not already built wins immediately** — scores are not
compared for absent items — unless `COST/IND >= 70` which ABORTS the whole
scan; among already-built candidates a d66 roll (`rng>0x41`) chooses full-sum
(65%) vs stub-primary (35%), ties to the earlier row.

**Threat input, the one and only measured**: `FUN_0003fc4c` forces item 18
Surface Shield when `IND>=4 && PROS>0 && free cells>=3 && threat byte+0x59 < 6`,
and item 19 Surface Mega Shield when `(DAT_00012e10 - [+0x67]) / period > threat`
with period {200,225,300,400} selected by **threat class 0/1/>=4** out of the
0x45beb stride table (income-law.md §9, evaluator block). So the AI does buy
planetary defences in response to a threat measure — at the granularity of one
planet, on a day-count heuristic, with no notion of who is coming or how many.

### 3b. Research picker = expansion picker = `FUN_00040018` (aicode.md §3b/§3c/§3d)
[verified] One table `DAT_00076492[race]` is both "research target" and what t90
first read as "expansion target" — the field-identity key was 0x74744+0x1d4e ==
0x76492 (§3b). Candidate build = restree runtime rows in ROW ORDER, skip rows
the race owns, legality = prereq chain `FUN_00046d3c`, cap 0x20. Tiers, final
t93-corrected precedence: **sentinel** (race flagged in `DAT_00074902`;
live-measured 0x0f = every AI in the shipped 4-race scenario; `rng%100 < 45`
→ chosen := -2 which only SKIPS the preferred-bias scan), then
**first preferred member** (static list at 0x67be; on a 66-row table only values
1 and 47 can ever match), then **uniform `rng % count`** (0x4013f). In the
shipped scenario the bias tier is effectively dead: AI research content is
uniform-random over legal rows (§3d).
Consequence for the player question: the single value that steers the race is a
**research row index chosen by (mostly) uniform random over legal techs**, not a
geographic objective. The ship-order path reads it as a boolean "race has an
objective" (§2f, gate row+0x19b), so it modulates congregation, not direction.

### 3c. Research completion `FUN_00046aec` (§3) [verified]
Progress = Σ over owned planets of (planet RES word + 1-per-planet gated), ×1.2,
accumulated and compared against the row's runtime cost; completion sets two
owned-mask dwords. Also relevant: build completion can **grant a free tech**
(`FUN_00046e84`, sole caller 0x39173 in the item-completion branch) — it picks
uniformly among legal rows and marks them OWNED directly, never touching the
target slot.

## 4. Special-ability cadence engine `FUN_00043b50` (aicode.md §6) [verified]
16 case bodies, dispatch key = the race's special-ability number
(`row+0x19d`, from the `.dip` loader), cadence table image 0x6780 (zero stores
image-wide → static), counter `row+0x19e` +1/turn (AI-enable scenario bit
gated), fires when counter == cad exactly then resets. Charged set
{5..14,16,17,19,20} == the rewrite's 14 (species.cpp:30).
Military content is real but blunt and *area-of-effect, self-centric*:
`SA_HealShips` 0x43baf (own fleet integrity→max), `SA_DoublePower` 0x43c3f
(own ship +0x88 POWER <<= 1), `SA_RepelAlienShips` 0x43c79 (replaces alien
ships that are in-system, order-kind 4, back at their star), `SA_SapAlienPower`
0x43d33 (zeroes POWER of alien ships in systems you own),
`SA_BlockStarLanes` 0x4405f (sets the block bit on lanes from your stars),
`SA_KnowStarLanes`/`SA_FastLaneTravel` passive. Per §6.4 NOTE + t101
adjudication: **the 16 bodies touch POWER only — no ability targets MOVES**,
so no ability can stall an enemy fleet's travel. Effects are synchronous only:
event 24 is a UI signal with no effect arm (§7 SPLIT LAW, t102).

## 5. Ship orders: kinds, stickiness, congregation

Field map (§2f, §2g-correction-2): `+0x58` ORDER KIND, `+0x59` ORDER TARGET
ptr, `+0x5d` ACT enum, `+0x5e` ACT TARGET OBJECT. Kind values {0..5}
end-to-end verified (t94 + t107 corrections): stores imm0 0x24a00 (command
clear, also WORD +0x56 := 0xffff), imm1 0x3fb3e, imm2 0x3ca60 (second move
issuer), imm3 0x39859 / 0x49cd6, imm4 0x2202f / 0x22127 / 0x49db9, imm5
0x22243 / 0x2228f; travel issuer 0x220a8 with consumer 0x21f58 (kind 5 →
jittered placement → kind 4 on arrival); `0x220f2` downgrades kinds {3,1,2} to
kind 4 at the owning star when the target stops being targetable (`FUN_00039894`)
— the "retreat to system" law. Functional names from the SO_ block are NOT tied
to numbers (A5 residual — the block's 10 entries ≠ 6 kinds, §2h), so this
dossier uses functional descriptions, not SO_ labels.

Decider `FUN_00040178(race row, ship)` (§2f) [verified]:
- kind ∈ {1,2,5} → RETURN immediately: **orders are sticky**, the AI does not
  re-think a ship that already has a move/colonize/hold order.
- kind 3 → `0x39894` targetability gate → ability/gun chain handles it.
- no target and `FUN_0004105c(race, ship)` == 0 → ACT := 2 with the returned
  payload (act-legality decider; store is at caller 0x40224, t96 correction).
- **CONGREGATION LAW** (the AI's one fleet-level behaviour): if the race has a
  target (row+0x19b != 0) and the ship is capacity-idle, scan the race's ships
  for the MINIMUM path cost over the starlane distance table 0x45beb
  (`FUN_0004aa10`, formula ((idx*4-idx)<<3)*4) and set ACT := 1 toward that
  nearest friendly ship. Ships mass; they do not disperse to hold ground.

Ship list is sorted **descending design power** before the order loop
(`FUN_00040ec0` + comparator 0x40eb4, §2b) — strongest ships get first call on
orders and are the ones that move.

t179 P1 (new, verified this session, objdump `0x41960..0x41a60`): the command
executor holds two further callers of the decider (0x41991, 0x41a45 — aicode
§2f-supplement lists them as plain reg-reads of fn 2010; they are `call 0x40178`
sites). The surrounding law: ships with `+0x5d == 0` get re-decided (0x41970
`cmp BYTE [eax+0x5d],0`, owner-vs-`ds:0x7458e` and AI-control
`ds:0x10ba4 == -1` gates at 0x41976..0x41987), and the loop tracks the
candidate with MAX `[+0x88]` POWER among ships whose act is set (0x4199f
`cmp eax,[edx+0x88]` / 0x419af `mov cx,[edx+0x88]`) — **the powered ship is the
one whose act is processed**. After movement, kind must be 3 or 4 or the engine
asserts (`0x419cf` `cmp BYTE [esi+0x58],3` → `0x39894`; `0x419e3` `je` else
assert id 0x93e at 0x2a428). If a ship's act target `[+0x5e]` no longer equals
the current object, the act is cleared (`0x41a30` `mov BYTE [esi+0x5d],0`) and
the decider runs again (0x41a45). Reading: order maintenance is
target-validity-driven, per ship, with power as the tie-breaker for whose act
gets attention — still no cross-ship plan.

t179 P2 (new): rel32 caller census over obj0 (tool: inline struct scan, same
method as scripts/r1_t90_callgraph.py) — `FUN_00041260` (the AI command
executor) has exactly TWO callers: 0x16eb0 and 0x2554f, i.e. the AI's whole
military action passes through one executor invoked from the turn frame.
`FUN_00039894` (targetability gate) has 8 callers — 0x22109, 0x3d8d5, 0x401de,
0x419da, 0x41d0a, 0x42cb5, 0x434bb, 0x49df2: the decider, the executor, the
engagement resolver, and the ability path. A gate this widely reused is the
engine's only shared "may I shoot this" test.

## 6. Engagement: who fires, and how much

Firing-order law `0x4a55c` (combat.md S2g) [verified]: refuses if POWER == 0;
sets stance map arg→`+0x67` (0→2, 1→1, 2→0) and `[+0x68] := target`; volley
loop 0x4a5c1..0x4a5fc walks the ship's gizmo slots **in stored order, stride 7**,
fires EVERY cat-0 weapon. Callers of 0x4a55c: 0x41b4e, 0x421d0, 0x42351,
0x42e24, 0x43153, 0x43301 — all inside the AI-attack module region
0x41260..0x439c9 (combat.md S2g, S2i).

Damage (S2g/S2h) [verified]: same-system gate `ship+0x58==4 && target+0x58==4 &&
ship+0x59==target+0x59` (combat is strictly per-system-object), range gate on
`design[+0x3a]<<5`, damage = `design[+0x52]` (the file Level column; gizmo 0x2f
overrides to design[+0x4a]), two-layer absorb MIN(damage, shield +0x90) with
spill to hull +0x8c, death at hull < 1 → 0x49d2c. **Hit probability does not
exist** — measured negative (no rng anywhere in the gun/hit path; the only rng
in the region is target-position jitter `rng%1000-500`, clamp 250.0f).
Commit law (t88a, OPEN-QUESTIONS OQ-010 row): of the 13 callers of the
dispatcher 0x49f28 exactly TWO pass mode 1 (the resource-consuming commit,
0x25560/0x25570 inside player-command-exec 0x2547c) — every AI volley path is
a mode-0 dry run.

t179 P3 (new, verified this session, objdump `0x42c60..0x42e6e`): the
engagement resolver's **who-fires selection is first-eligible in list order**,
twice over. Leg A (invasion): after the `0x39894` gate at 0x42cb5 (assert
msg 0x84d44 requires a resolved target, 0x42cc1), a loop 0x42d09..0x42d5b walks
the ship pointer array `[esp+0x380]` (count `[esp+0x354]`), accepting a ship iff
`BYTE [+0x58]==4` (in-system) AND one of its stride-7 gizmo slots equals **0x49**
— `Invasion Module` (gizmos.txt row 73 of 76: Cat 5, Power 10, Range 0, Level 0,
NumUses 0, ResReq 0; parsed this session with the loader's column order from
scripts/r1_t87_gizmo_table.py) — and stops at the FIRST match (0x42d54 stores
it and jumps out). The result descriptor gets byte `3` + ship ptr (0x42da3/0x42da6),
the target's engagement flags are written (`+0x62:=0`, `+0x63:=0`, `+0x67:=1`,
`+0x68:=esi`). Leg B (firepower): loop 0x42de0..0x42e34 walks the same array
for the first ship with kind 4 where `0x4a604` (companion slot scan: first cat-0
slot with power/uses, S2g) returns nonzero **and** `0x4a55c(ship, 1, target)`
returns nonzero — first match wins, descriptor byte 3 (0x42e48). No strength
comparison, no value ranking, no retreat test anywhere in the region: eligibility
is order-state + equipment.

## 7. VERDICT: what doctrine existed vs what demonstrably did not

DOCTRINE THAT EXISTED (each item cited above):
1. Economic triage with real priorities: over-pop demolish, tubes priority,
   research-prereq-first demolish, 70-cost abort, need-class scoring (§3a).
2. Threat-responsive planetary defence buying (threat byte +0x59 + day-count
   period tiers → Surface Shield / Mega Shield) (§3a).
3. Personality from data: 21 races × 15 DIPVALUES thresholds + BIO mood sine
   produce per-race aggression timelines (ai-data.md §2, diplomacy.md §8) —
   race04 ("HANSHAKS" dip header: DECLARE_WAR 150, ACCEPT_PEACE 200) really
   does behave differently from race09 (DECLARE_WAR 450, ACCEPT_PEACE 530),
   deterministically for a given attitude path. (The Minions are specnum/race00
   — SuperMarines, DECLARE_WAR 290 — NOT the 150 row.)
4. Fleet massing (congregation to nearest friendly ship, §2f) and
   strongest-first ship handling (§2b, t179 P1).
5. Order persistence with validity-driven repair, plus an explicit retreat-to-
   system downgrade (0x220f2) — so ships that lose their target go home rather
   than dying in the lane.
6. Role-specialised combat: invasion requires the Invasion Module gizmo and the
   carrier must be in-system (t179 P3A); guns require same-system and POWER > 0
   (S2g); abilities are self-centric AoE (§4).
7. One-shot escalation bookkeeping: attacking a neutral costs attitude and
   leaves a permanent attacked-bit (§2 last para).

WHAT DEMONSTRABLY DID NOT EXIST — stated as SCOPE OF SEARCH, not as universal
fact. Searched: full obj0 rel32 call graph (scripts/r1_t90_callgraph.py, RC=0);
exhaustive u16/u32 disp32 writer censuses for the target slot, cadence table,
relation-state cells and order-kind byte (aicode §2f-supplement, §3b, §6.4;
census-audit.md t107–t109 full-op re-audit with boundary-checked verifier);
whole-body disassembly of the per-race decision block, both executors
(0x41260 region, 0x3f130 selector, 0x40178 decider, 0x4b8e4/0x4b740 combat,
0x42c60..0x42e6e engagement resolver, all 16 ability bodies); live-save
censuses over 2810 records / 32 slots (OPEN-QUESTIONS evidence). Within that
coverage:
- **No system-level threat plan.** The only quantities that behave like a threat
  measure are (a) the per-PLANET byte +0x59 feeding shield purchases (§3a),
  (b) the "enemy strength + 20" attitude floor inside the SA_ForcePeace body
  (§4), (c) the design-power sort (§2b). None of them is consumed to choose a
  target star, an axis of advance, or a defended frontier.
- **No target selection by enemy value.** Attack paths take their target from
  the ship's stored `+0x59` (set by the decider/act path) or from the
  first-eligible scan (t179 P3). No site scores candidate enemies.
- **No geographic objective at all in the target slot**: DAT_00076492 is a
  research row index (§3b), and ship-order code uses it as a boolean flag.
- **No reinforcement/triage behaviour** (no "shorten the line", no concentration
  against an incursion beyond the SA_ AoE abilities).
- Honest residuals that bound the negative: order-kind → SO_ name tie is
  UNCLOSED (A5), so a UI-facing order label we could not bind is conceivable;
  the P0 random-event window (0x24f32..0x24ffc) is unmapped; relation-state 3's
  writer is unclosed (OQ-023, t180 queued). None of these has any evidence of
  being a planning module — they are bookkeeping — but strict-close keeps them
  named rather than assumed away.

NET: a stock-AI player who "defends systems" is watching emergent behaviour —
shield items bought per-planet by a day-count heuristic, ships retreating to
their own star when their target dies, and AoE abilities firing on a fixed
cadence. A stock-AI player who appears to "choose a thrust" is watching a
uniform-random research order plus congregation. Neither is doctrine; the
engine never evaluates the enemy's order of battle.

## 8. Gap map — dossier fact vs rewrite (rewrite/src/game/campaign.cpp)

| # | Original law (cited) | Rewrite state | Site |
|---|---|---|---|
| 1 | Build queue 1/planet, selector on empty queue only, IND>0 (income-law §9) | MODELLED | buildPhase :726 |
| 2 | First-absent-item wins; 70-cost ABORT; d66 65/35 score roll; need classes 0..3 (§3a) | MODELLED | buildPhase :726 (kBuildOrder policy for the player is a documented default) |
| 3 | Threat byte +0x59 / Surface-Shield + Mega-Shield emergency chain, period tiers 200/225/300/400 (§3a) | MODELLED t201 (S10: threat law 2900/2900 + 2880/2900 corpus-verified; chain verbatim + pin campaign_emergency_chain_law_t201; residues: chain-C row-operand identity, +0x67 stamp site) | buildPhase emergency block + emergencyChainPick |
| 4 | Over-pop emergency demolish; min-REQUIRES demolish; tubes priority (§3a) | **GAP** — rewrite has no demolish channel | buildPhase :726 |
| 5 | Research PICK = FUN_00040018 tier chain, 66-main-row law (§3b/§3d, OQ-013) | MODELLED (t93, pin test campaign_research_picker_law_oq016) | researchPhase :885 |
| 6 | Research PROGRESS = Σ(RES+1-gated) ×1.2 vs runtime cost (§3) | MODELLED (income channel law, OQ-016 closed sub-law) | researchPhase :885 / incomeAndGrow :655 |
| 7 | Free-tech grant on build completion (0x46e84) | **GAP** | buildPhase completion path :757 |
| 8 | Single per-race target slot, research-row semantics, no geographic BFS (§3b) | **DIVERGENT BY DESIGN** — rewrite expansionPhase colonises via nearest-first BFS within drive range | expansionPhase :948 |
| 9 | Colonised star := pop 2 + Colony Base grant (t41, measured) | MODELLED | seedColonyBaseColony :395 |
| 10 | Ability cadence = cad[ability] days from image 0x6780, fire-on-exact-equality, reset (§6.4) | MODELLED (t100 kCad + abilityPhase) | abilityPhase :1077, species.cpp:30 |
| 11 | 16 SA_ bodies incl. Repel/Sap/Block-lanes/Force-Peace/Hatred attitude arithmetic (§6.3) | PARTIAL — Sap/Heal/DoubleHull/SuperMarines wired; Repel, BlockStarLanes, ForcePeace, Hatred are FILED NO-OPs (no lane-block/attitude-cell model) | abilities.md §2, abilityPhase :1077 |
| 12 | Diplomacy: attitude word + relation-STATE ladder 0..3 + proposal emitter + attacked-bitmap (§2) | PARTIAL — two-party war/peace/alliance from DIPVALUES thresholds (decideDipAction); no inter-race state ladder, no attacked marks | diplomacyPhase :1046, diplomacy.h:67 |
| 13 | Diplomacy-on-attack attitude cost (0x43a4c) | **GAP** — attacking never changes rewrite relations | combatPhase :1325 |
| 14 | Combat: deterministic damage, ordered cat-0 volley, shield-then-hull two-layer absorb, death at <1 (S2g/S2h, OQ-010 CLOSED t89) | MODELLED at empire-aggregate level (volley = Σ researched weapon Levels; shield absorb as clamped split) | attackScore :1249, defenseScore :1282, shieldChargesFor :1295 |
| 15 | Same-system gate (order kind 4 + identical system object) | NOT REPRESENTABLE — rewrite has no ship positions or system objects | combatPhase :1325 |
| 16 | Per-ship order kinds {0..5}, stickiness, congregation, retreat-downgrade, invasion-module carrier (§5, t179 P1/P3) | **GAP (largest)** — rewrite has no per-ship model whatsoever; A5 name tie still open | none |
| 17 | AI acts through the player's own command primitives (§1 P8) | DIVERGENT — rewrite phases are direct state mutation | campaign.cpp advance() |

Priority read for whoever picks up code work: #16 dwarfs everything (it is the
"does the sim have ships" question, not an AI question), then #3+#4 (a threat
input and a demolish channel would make the AI's economic behaviour visibly
match stock), then #13 (attitude cost of attacking — one call site, and it is
the only thing that makes AI-AI relations reactive to what they see).

## 9. PLAIN (player-facing restatement)

You asked whether the computer opponents defend their systems and pick attack
routes, or just muddle around. Answer: they have habits, not plans. They do
real, checkable things — they buy shields on a world when their "threat"
counter says the world is overdue for defence, they bunch their ships toward
whichever friendly ship is closest, they move their strongest ships first,
they pull a ship back into its own system when its target dies, and only a
ship carrying the Invasion Module can take a planet. But nowhere in the code
do they look at YOU and decide where to hit: the one "target" each AI race
tracks is a technology row it picked mostly at random, its threat measure is a
per-planet number used only for buying shields, and when a fight starts the
engine just lets the first eligible ship in list order shoot. So an AI empire
that seemed to be defending a frontier or pushing a corridor was an accident
of economics and tech order — a good opponent to play against, and the reason
our rewrite doesn't need to copy any "AI strategy" it can't already show you.

## S10 (t201) — THREAT-BYTE INPUT + EMERGENCY CHAIN CLOSED WITH MEASUREMENT

Raw listings: work/t201_fc4c.txt (FUN_0003fc4c 0x3fc4c..0x3fec3, fresh
capstone) + work/t201_recalc_scan.txt (FUN_00038ba4 esp-annotated).
Tools (RC=0 all): scripts/r201_threat_writers.py (obj0-wide disp32∈{58,59}
census; PITFALL: sequential capstone stops at the first data gap — the
resume-by-1-byte pass finds 325 sites vs 36 blind), r201_threat_census.py,
r201_threat_law_verify.py. Working notes docs/re/_wip_t201.md.

THREAT INPUT (gap row 3). +0x58/+0x59 are PURE DERIVED COUNTERS the planet
recalc FUN_00038ba4 zeroes and recomputes EVERY run (locals esp+0x24/esp+4
xored @0x38baf; stores @0x38ef7/0x38efe):
  +0x59 = #{ACTIVE slots (word[slot+2]&1) whose item file FLAGS (u16@+6,
          OQ-014 map) bit 8}  — bit8 items EXACTLY {18 Surface Shield,
          19 Surface Mega Shield, 26 Orbital Shield, 27 Orbital Mega
          Shield} (live table witness 60.sav).
  +0x58 = #{ACTIVE slots whose item FLAGS bit 4} — bit4 items EXACTLY
          {17 Tractor Beam, 28 Orbital Missile Base, 29 SR Orbital
          Whopper, 30 LR Orbital Whopper}.
VERIFIED 2900 corpus records / 20 saves: +0x59 EXACT 2900/2900; +0x58
2880/2900 (all 20 misses = one record, the evaluator self-init 0x3fb3e
signature). Census +0x58 {0:2400,1:240,2:260}, +0x59
{0:2120,1:320,2:300,3:120,4:20,5:20}; self-check IND/RES/PROS maxima ==
t198 (77/52/16). Static writers are ONLY recalc exits + evaluator
self-inits 0x3fa36/0x3fb3e + save round-trip FUN_0003a558 (callers
0x258dd/0x26044 snapshot deserialisers). SEMANTICS: threat is SELF-
ASSESSED defence infrastructure, not an enemy scan; enemy proximity
enters only via the chain-C hop tier.

EMERGENCY CHAIN (FUN_0003fc4c, sole caller 0x3f4d5 inside FUN_0003f130 —
return -1 SKIPS need-class scoring @0x3f4ec). Order verbatim:
  A Xeno dig item 38 when byte+0x66 bit1 (arm site world-gen 0x37f7b —
    the ROCK branch; clear-on-success 0x3fc78). [t28's "item 22" was an
    immediate misread; 0x26=38]
  B Surface Shield 18: IND>=4 && PROS!=0 && item22 PRESENT (0x3fcb9) &&
    empty-nonrock-noclass0 (+0x1c - +0x20) >= 3 && +0x59 < 6 && legal
    && absent. IND/PROS/shipyard/freeCells failures EXIT the evaluator
    (0x3feb9 ret 0) — no D, no fallback for those planets.
  C Mega Shield 19, REACHED ONLY when 18 legal+PRESENT (0x3fd0e):
    period tiers MEASURED VERBATIM 0xc8/0xe1/0x12c/0x190 = 200/225/300/
    400 selected by hop byte DAT_00045beb[4*starIdx(+row)] : 0->200,
    1->225, <4->300, >=4->400 (0x3fd73..0x3fd92); FIRE iff UNSIGNED
    (DAT_00012e10 - dword+0x67)/period > +0x59 (DIV @0x3fda1). Stamp
    +0x67 writer on the buy path NOT found statically (census: only
    UI-side 0x3a4c9 pre-recalc + zero + save round-trip) — HONEST
    NEGATIVE; rewrite stamps on C-purchase [documented default]. Mega
    ILLEGAL + fire -> buys 18 AGAIN (shared block, no absence test).
  D Surface Cloaker 11: owner ODD && IND STRICTLY > 20 (cmp 0x14 jle
    @0x3fdfb — corrects t28's ">=20") && rng%100 < 4 && legal && ABSENT.
  E Fallback template MEASURED live at relocated 0x67b8 pool bytes =
    items {12 Hyperpower, 13 Fertilization, 14 Internet, 15 Cloning,
    37 Lush Growth Bomb}, first legal+absent. (The OTHER template, imm
    0x89360 inside FUN_0003f758 = obj1 data == pool 0x67b0 window, is
    {28,29,30,0,26} orbital-defence set — belongs to the shipyard tail,
    not this chain.)
OPEN residues (row keeps them): chain-C row operand [ctx+7]->[+2]>>16
identity UNVERIFIED (rewrite: lane-BFS distance to nearest enemy star,
documented default); +0x67 buy-path stamp write site; DAT hop-matrix
stride-100 (t190) vs chain-C index-stride tension.
REWRITE LANDED: Campaign::emergencyChainPick (pure, verbatim control
flow incl. the hard exits) + emergencyPeriodFor + shieldThreatFor/
orbitalThreatFor wired into buildPhase AI branch BEFORE scoring
(0x3f4d5 ordering); digQueuedOrDone armed by the rock event (same
original branch); pin TEST(campaign_emergency_chain_law_t201) — 115
tests 0 failed.
