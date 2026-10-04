# Ships — hulls, Gizmo loadout, drive range, combat participation

Sources (all read-only): extracted/ascend00/planitem.txt (hull rows),
extracted/ascend00/gizmos.txt (component table; field semantics are the
VENDOR's own header comments, lines 19-49), extracted/ascend02/ship.bin +
ship.tsv (inventory stats in docs/re/tables.md §ship.bin), tutorial text in
ascend00 files (Shipyard definition), docs/re/economy.md (REQUIRES
semantics), docs/re/turnloop.md (where phases run).

## 1. Hull items [verified rows, planitem.txt]

| item       | IND RES PROS MPOP UPOP COST REQUIRES | meaning |
|---|---|---|
| Shipyard   | 1 0 0 0 1 240, REQUIRES 0        | orbital structure that enables building ships (vendor tutorial: "Shipyard, the orbital structure that makes building ships possible") |
| Ship       | 0 0 0 0 1 20,  REQUIRES 1        | the ship hull itself; industry cost 20 plus Gizmo Industry column |
| Orbital^Docks | 1 0 0 0 1 170, REQUIRES 16    | listed, not modelled (P-scope) |

REQUIRES indexes restree rows (economy.md §1). Shipyard req row 0 =
"Orbital Structures"; Ship req row 1 = "Interplanetary Exploration" (both
names verified verbatim in the restree string pool).

## 2. Gizmo loadout [verified table]

Ship-borne components are the Weapon(0)/Shield(1)/Drive(2)/Scanner(3)
categories plus Generator/Special. The Industry column is ADDED to the
Ship hull cost (vendor header, gizmos.txt lines 43-45: "The cost in
industry points added to the cost of building a ship" — note the vendor's
own TODO about a cost hack in Ship::init_global_gizmos(); the exe-side
hack is R1-blocked, so the rewrite uses the file values unmodified).
ResReq gates each device per restree row, exactly like planitem REQUIRES.

## 3. Drive range [verified semantics, inferred composition]

Vendor header (gizmos.txt lines 33-36): "For drives, the maximum distance
that can be travelled, in sugar cube units". ALL FIVE drive rows (Cat 2),
Level then ResReq (column 8, the same layout the gizmo loader uses),
verified: Tonklin Motor 2/2, Ion Banger 4/10, Graviton Projector 6/23,
Inertia Negator 6/46, Nanowave Space Bender 10/54.
(Note: "Hypersphere Driver" is Cat 0 — a weapon despite the name; verified
row `0 6 75 10 2 100 0 0`. A first draft of this section mis-read ResReq
from `r[-2]`, which is flag position 7, not the gate row.)
"Sugar cube" = one map-grid cell: [inferred] — the map coordinate system
is the 0..1023 grid of docs/re/mapgen.md; no extracted file defines the
sugar-cube scale numerically. The rewrite therefore treats drive Level as
LANE HOPS per turn [inferred default], one ship = best researched drive
per owner (no per-ship design UI exists statically; OQ-019).

## 4. Combat participation [inferred model delta on turnloop.md §5]

The static data names every input but never the arithmetic (OQ-010):
- attack of a ship = best researched Weapon Level (damage per vendor
  header line 29: "For weapons, damage"),
- defence of a target = best researched Shield Level (header: "For
  shields, strength") + garrison term,
- NumUses (uses per turn, 0 = unlimited) limits how many attack actions a
  fleet performs per turn per owner.
The shipped capture model (turnloop.md §5) is: attack = owned-pop/10
reserve + highest RESEARCHED weapon Level, defence = garrison + highest
RESEARCHED shield Level, small seeded noise. The gizmo levels are the
data-cited inputs [verified distinct Level values]: weapons {1,2,4,6,10,13}
(verified rows; note "Hypersphere Driver" is a weapon), shields
{1,2,3,4,5}. The linear composition (pop/10, additive) is the documented
default — the exe arithmetic stays OQ-010. No rebalance multiplier was
invented in this pass: when R1 lands, replace composition, not inputs.

## 5. Implementation mapping

- Campaign::buildPhase: a star builds Shipyard when REQUIRES row 0 is
  researched (one per star, existing quota behaviour); a Ship hull may
  then be LAUNCHED from that star — Shipyard is the launch precondition
  (tutorial text §1), hull industry cost 20 charged at launch as today.
- Launch distance: owner's best researched drive Level /2, clamped to
  [1, 3] lane hops (documented default for the sugar-cube scale; a unit
  test pins the five drive levels).
- Campaign::combatPhase: attackScore/defenseScore keep §4's research-gated
  gizmo levels (already shipped).
- Gate: campaign smoke still reaches VICTORY with the gates active;
  test_ships.cpp pins the Ship/Shipyard rows, all five drive rows, and the
  no-Shipyard = no-launch invariant.
NOT modelled (stated): ship design screen, per-ship inventories,
Orbital Docks effects, the vendor cost hack (R1), fleet stacking.
