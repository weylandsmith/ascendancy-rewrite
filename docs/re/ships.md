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

## 6. Gizmo loader + record law (OQ-019 t15, 2026-10-08) [verified static]
- gizmos.txt unique code referrer: pool imm 0x2538 @0x49081 inside
  FUN_00049074. POOL-BASE LAW TRIPLE-CONFIRMED: pool offset = image offset
  - 0x82bb0 (soundfx.txt 0x2a08->0x84bb8...; RACE%02d.DIP 0x21f0->0x84da0 ✓;
  gizmos.txt 0x2538->0x850e8 ✓ literal verified).
- Record: stride 0x6a, LOOP COUNT 76 (`CMP EBP,0x4c @0x490ed`), record base
  = PTR_DAT_0007650c table. Parse: '%s' (name, '^'->' ' substitution loop
  @0x4916x family) then EIGHT %d then a 255-terminated bit list:
  +0x32 cat (byte), +0x36/+0x3a/+0x3e/+0x42/+0x46/+0x4a/+0x4e/+0x35 = the
  eight fixed columns in file order, +0x33 u16 RESREQ BITMASK (bits set
  from the list until value 0xff — v1's "column 8 ResReq" is this list,
  refined: multi-node capable).
- Derived slots (init to 0 @0x4923a..0x49250, then category switch):
  cat 0 weapon -> +0x52 = Level[+0x3e]; cat 1 shield -> +0x56 = Level;
  cat 2 drive -> +0x5e = Level; cat 3 scanner -> +0x62 = Level;
  cat 4 generator -> +0x66 = POWER[+0x36] (matches vendor header "power
  supplied by the generator"); cat >4 -> vendor error 0x2a438 (EBX=0x190?
  msg pool 0x2567). Jump table RAW at 0x49060 (encoded disp 0x344b0 is the
  usual 143-class fiction; REAL table sits BEFORE the function entry,
  second instance of the t11 pattern — bank the pattern, stop re-scanning).
  Switch default falls through to next-record path @0x490e6 (INC/ADD/CMP).
- This switch is the DOCUMENTED per-category parameter interpretation, NOT
  the JJTTODO cost hack. Cost-hack hunt = writers of +0x46 (Industry,
  5th fixed col) OUTSIDE FUN_00049074, or build-cost sites reading +0x46.
- Design-screen assets/edges banked: name-table idx 61 `data\8shipdes.tmp`,
  74 `data\8shipdes.shp`, plus shipicon + 21 smshipNN + dkship shps;
  strings SHIPDESIGN@0x83a69 (refs 0x26fcb,0x31da4,0x52630),
  SHIPDESSCREEN@0x83aae (ref 0x27bba), shipdesx@0x83ac7 (ref 0x27c05),
  owner coswnd.cpp. ship.bin (386)/ship.tsv (393) in table.
## 7. NEXT residues (open, do not re-derive §6)
cost-hack location; per-ship inventory record (ship.bin table law?);
sugar-cube numeric scale (drive Level in hop math at move code);
Orbital Docks effect readers.

## 8. init_global_gizmos located — and it is NOT the cost hack (t15b)
- FUN_0004929c = sole caller of the loader; vendor owner string pool 0x2567
  `..\ship.cpp` (verified verbatim in banked RAM pool). One-time guard
  DAT_00076508. What it does: init ship-object template fields, copy 8
  species names into 0x14-stride slots via FUN_00021a20, CALL the gizmo
  loader, then compute a QUOTA-DISTRIBUTION bitmask over gizmo tables
  (research-bit masks DAT_0000685c/DAT_0000686c, 14 columns) writing bytes
  at &PTR_PTR_000764cc — the "available gizmos by level" spread using
  fVar3 = count/(levels-1) float rounding with epsilon pool 0x2573.
- ZERO writes to record+0x46 (Industry) here or in the loader. So the
  JJTTODO "hack in Ship::init_global_gizmos()" is EITHER (a) this quota
  spread changing *effective* acquisition cost semantics, or (b) removed by
  ship date while the comment stayed. [unverified] which. DECISIVE cheap
  probe queued NEXT: readers of +0x46 (build-cost sites) — if every reader
  uses +0x46 unmodified, the shipped engine charges file values and the
  rewrite ALREADY matches (file values unmodified, §2 v1 default stands,
  closure cites the reader census).
