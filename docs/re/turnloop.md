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

Rewrite implements (campaign.cpp):
- `Control`  — player owns > 1/2 of all stars (end-ctrl; the "> half" IS the
  vendor comment, the per-star unit of "galaxy" is [inferred]).
- `Extinct`  — player owns 0 planets after turn 1 (end-xtnc).
- `LastAlive`— all AI owners eliminated (end-dest; "captured all home
  worlds" end-capt and alliance end-unit need combat/alliance accept
  mechanics that are R1-blocked, so they are NOT evaluated — recorded, not
  silently faked).

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
- Population per planet: logistic growth pop += g*(pop*(cap-pop))/cap^2 *4,
  g=1 base, cap = 100 (UPOP=1 column present on every built item — units
  undocumented, economy.md §1). Growth shape echoes the vendor '50' grid
  documented as pop growth (economy.md) but the exact curve is OQ-016.

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
  applied to expansion until OQ-010/OQ-016 resolve). Ships never attack —
  combat arithmetic is not implemented (OQ-010), stated loudly in code.

## 5. War + capture [weights/levels verified; resolution inferred]

Diplomacy (docs/re/diplomacy.md, weights [verified] from raceNN.dip) sets a
symmetric war table; `START_ATTITUDE` initialises each AI-vs-player relation
[verified field] - starting at zero would put every race under its own
DECLARE_WAR threshold on turn 1, which the data clearly does not intend. The
campaign default `freeForAll=true` starts everyone at war (arcade setting;
diplomacy-triggered declares also fire). Capture resolution [INFERRED -
original combat arithmetic is OQ-010 and is NOT claimed]:

- attack(empire) = total owned pop/10 + max owned weapon-gizmo `level`
  (levels 1..13, gating via `ResReq` -> owned techs [verified gizmos.md])
  + uniform noise 0..10.
- defend(star) = local pop/10 + max owned shield `level` (1..5 [verified])
  + terrain 2 + noise 0..5.
- Star-id-ordered sequential pass over borders; a capture fortifies the star
  for 2 turns. Captured pop resets to the settlement seed.

Extermination: an owner with 0 stars AND 0 ships in transit is eliminated
(`LastAlive` end-dest condition; the `Extinct` end-xtnc check likewise waits
for the player's last colony-ship to arrive).

## 6. Determinism

mt19937 seeded from --seed; same seed + turn count => byte-identical stdout
(asserted in tests). PLAYTHROUGH.md is generated from a real run.
