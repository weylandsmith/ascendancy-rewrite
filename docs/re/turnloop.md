# turn loop — production, expansion, victory [part verified, part inferred]

Implementation: `rewrite/src/game/campaign.{h,cpp}`, exercised by
`--campaign N --seed S` in `rewrite/src/main.cpp` and by
`rewrite/tests/test_campaign.cpp`. Gate stage 3l. Everything NOT marked
[verified] is an OQ-016 documented default — the original per-turn arithmetic
is exe-side (R1-blocked, docs/BLOCKED.md); this file states exactly which
constants come from data and which are behavioural defaults.

## 1. Victory conditions [verified names; [inferred] thresholds]

The shipped `extracted/ascend00/end-*.txt` files each begin with a vendor
comment naming its condition, and carry `enddesc` text plus a `ranks` block
of exactly 10 rank names starting at lowest (asserted by gate 3l):

| file | vendor comment (verbatim first line) |
|---|---|
| end-capt.txt | "Player captured all home worlds." |
| end-ctrl.txt | "Player controls over half the galaxy." |
| end-dest.txt | "Player destroyed other races." |
| end-unit.txt | "Galaxy under one alliance, player alive." |
| end-xtnc.txt | "Player extinct." |

`static.txt` carries the score template "Your score is %d%%.\nThis gives you
the title of %s" — score is a percentage, consistent with a control-share
score. [verified both strings] Block grammar per file [verified]: vendor
comment, `enddesc`..`endtext`, `ranks` + EXACTLY 10 rank-name lines (walker
must stop at the next keyword — running past `congrat` miscounts 20),
`congrat`..`endtext`, `end`. Asserted by `scripts/endtext_probe.py` / gate 3l.

Rewrite implements (campaign.cpp — all five evaluated since 2026-10-04f):
- `Control`  — t291 UPGRADED to the CITED law: V >= floor(2T/3)+1 where V is
  the PRODUCED controlled-systems count (scoreStars_, DAT_482fb analog) and T
  is the total star count (DAT_16143) — strictly more than two-thirds, read
  verbatim from evaluator FUN_00024a34 file 0x24b9c..0x24bbe
  (docs/re/_wip_t290.md S1, distilled score.md S19). The vendor comment "over
  half" is decoration: enddesc/congrat prose ("over two-thirds", "more than
  two-thirds of the stars") matches the code (OQ-021's named dispute, ANSWERED
  t290; the pre-t291 `mine*2 > total` default was MEASURED-WRONG on both the
  operand and the threshold).
- `Captured` — player owns every AI's setup home star (end-capt). The home
  star is fixed at setup (`homeStar_`, the star pickHomeStars assigned each
  owner) [inferred unit: "home worlds" = those stars]. Evaluated BEFORE
  Control — taking all homes wins even at < half. Reachability by bot play
  is dynamics (test v1: skip-note if search seeds never take both homes),
  never a reason to fake a fixture.
- `Unification` — every live AI allied to the player, no player-AI war bit
  (end-unit). Player-relative ONLY: the diplomacy model has no AI-AI
  relations (abilities.md), so "galaxy under one alliance" can only mean the
  player's alliance web covers every survivor [documented reading]. Now
  reachable because diplomacyPhase ACTS on ProposePeace: an AI at war whose
  attitude recovers past its PROPOSE_PEACE threshold ends the war (2026-10-04f
  — before that, propose-peace was computed and dropped into the void).
- `Extinct`  — player owns 0 stars after turn 1, with a one-turn grace while
  a player colony ship is in transit (it can colonise next turn).
- `LastAlive`— player is the only owner with stars (end-dest).
Evaluation order (documented choice; vendor priority unknown — R1):
Extinct > LastAlive > Captured > Unification > Control.
Gate stage 3 pins enum->file mapping (test victory_condition_files_all_mapped).

## 2. Players [verified keys]

`windows.txt` (docs/re/ui.md §) carries NUMCONTROLS 7 and RACE1..RACE7CONTROL
with mask values 1,2,4,8,16,32,64 — the config UI supports up to 7 controlled
species [verified key/values]. The campaign therefore seeds 1 player + N AI,
N <= 6 default 6 (N default [inferred]).

## 3. Economy per turn [columns verified; application inferred]

From `planitem.txt` raw rows (docs/re/economy.md; verbatim rows re-read
2026-10-04): Factory `1 0 0 0 1 30`, Laboratory `0 1 0 0 1 50`, Agriplot
`0 0 2 0 1 30`, Ship `0 0 0 0 1 20` — IND/RES/PROS/UPOP/cost columns.
[verified column values]

[INFERRED application, OQ-016]:
- Each owned planet produces base 1 IND + per-built-item IND (Factory +1).
  IND and RES ACCUMULATE as stockpiles (build queues need saving: Factory
  cost 30 vs income 2/turn early). An income-reassign model starved every
  economy at 2 IND — caught by the expansion test on first run (2026-10-04).
- RES income = built Laboratories (+1 each per Laboratory's RES column).
- PROS (prosperity) adds a one-time-ish growth nudge; modelled as +2 growth
  per Agriplot while pop < cap.
- Population per planet: [CLOSED t24 — the earlier logistic default was
  REPLACED by measured counter semantics] pop = word +0x42 (UPOP units);
  growth tick: gate pop<cap(+0x4a) else counter(+0x4e):=0; counter +=
  stored PROS(+0x48); +1 iff owner != turn-player AND stored PROS < 4;
  counter >= 50 -> pop += 1 (+1 if first active slot Cloning Plant),
  clamp to cap, counter := 0; colonization SETS pop := 2 verbatim.
  Evidence: income-law.md §6e (live + disasm, chase capture
  r1deep-20261007-224831 slots 45->46); rewrite growthPhase matches
  (campaign.cpp growthCounter law).

## 4. Production + expansion decisions [inferred policy, OQ-016]

- Build order per planet: Factory until 2, Laboratory until 1, then Agriplot.
  Costs are [verified] (30/50/30); the ORDER is policy.
- Research: accumulate RES; when the queued tech's restree `cost` (field1,
  [verified research.md §1]) is met it becomes owned. Player picks the
  cheapest available tech; AI picks a uniform-random available tech
  ([inferred] selection).
- Expansion: when a player has spare production, spend cost-20 Ship [verified
  cost] at an owned star; next turn it claims the nearest UNOWNED adjacent
  star (movement one lane per turn, [inferred]; drives/gizmo ranges not
  applied to expansion until OQ-016 resolve). Ships never attack — the
  rewrite models capture resolution as an empire-level aggregate law
  (t89, §5 below + combat.md S2i); per-ship combat is OQ-019 territory.

## 5. War + capture [t89-UPGRADED to cited laws — evidence docs/re/combat.md S2d..S2j]

Diplomacy (docs/re/diplomacy.md, weights [verified] from raceNN.dip) sets a
symmetric war table; `START_ATTITUDE` initialises each AI-vs-player relation
[verified field] - starting at zero would put every race under its own
DECLARE_WAR threshold on turn 1, which the data clearly does not intend. The
campaign default `freeForAll=true` starts everyone at war (arcade setting;
diplomacy-triggered declares also fire). Capture resolution (rewrite sites
campaign.cpp attackScore/defenseScore/combatPhase; original laws instruction-
verified t85g..t88a):

- volley(empire) = total owned pop/10 + SUM of researched weapon-gizmo
  `level`s with NumUses!=0 — the original volley loop 0x4a5c1 engages EVERY
  cat-0 weapon per engagement, damage per hit = Level (design[+0x52], map
  t87); v1's max-level reading is SUPERSEDED.
- shield absorb = MIN(volley, SUM researched shield `level`s) (charge law
  0x49f15 + hit-path clamp 0x4b7c4..0x4b7d1); hull = volley - absorb.
- defend(star) = local pop/10 + 2 (hull/reserves layer only — shields never
  join a defense total in the original).
- Capture iff hull > defend. NO NOISE: combat has no hit roll (measured-
  negative, combat.md S2g) — v1's uniform 0..10/0..5 draws were an uncited
  abstraction and are removed (t89); timelines regenerated accordingly.
- Star-id-ordered sequential pass over borders; a capture fortifies the star
  for 2 turns. Captured pop resets to the settlement seed.

Extermination: an owner with 0 stars AND 0 ships in transit is eliminated
(`LastAlive` end-dest condition; the `Extinct` end-xtnc check likewise waits
for the player's last colony-ship to arrive).

## 6. Determinism

mt19937 seeded from --seed; same seed + turn count => byte-identical stdout
(asserted in tests). PLAYTHROUGH.md is generated from a real run.
