# items and planetary economy — `planitem.txt` measurement
Source: `extracted/ascend00/planitem.txt` (3,180 B, CP437/CRLF, 0x1A EOF). Vendor-documented above `#`; produced by `scripts/gizmo_probe.py`; gate stage 3j.

## 1. Item grammar [verified against 39/39 records]
```
NAME IND RES PROS MPOP UPOP COST REQUIRES {flags} 255
```
(vendor header line, verbatim: `NAME IND RES PROS MPOP UPOP COST   REQ      FLAG DELIMITER`). Field roles by that header: IND/RES/PROS = industry/research/prosperity contribution; MPOP/UPOP = pop maintenance/upkeep pop; COST = industry; REQUIRES = restree node or 255. Field counts vary 8/9/10 because the flag list, when present, shares the 255 terminator — same trap as gizmos.md §1.
- **39 items** after the count triple `39 22 9`. The `39` equals the record count (verified). `22` and `9` match no property we could test (sentinel REQUIRES: 6; gated: 33; rows with a flag list: 19; nonzero IND/RES/PROS/MPOP/UPOP: 5/6/4/35/39) — semantics unknown, OQ-014; recorded verbatim, never forced. Names unique.
- REQUIRES (field 7 of the row, v[6]): 33 rows carry real restree indices, 5 rows carry 255 (vendor: no research required), and exactly ONE row — Interstellar Trucking — carries **254**, a second sentinel the vendor comment does not define (OQ-014). Sampled gates are semantically coherent (Shipyard->Orbital Structures, Terraforming->Planetary Replenishment, Surface Shield->Superconductivity), which cross-validates the restree row numbering a third time.
- parse trap (caught by this probe mid-run): testing v[7] for tech-range passes VACUOUSLY because flag bit-positions 0..7 also fall in [0, 106). Always test the vendor-named field index, not a neighbour.
- CONTROL (disambiguates v[6] vs v[7] on the 19 longer rows): reading v[7] as REQUIRES gives semantically broken gates — Surface Shield -> Spacetime Surfing, Orbital Missile Base -> Tonklin Diary, Terraforming -> Orbital Structures. The v[6] reading gives Surface Shield -> Superconductivity, Orbital Missile Base -> Power Conversion, Terraforming -> Planetary Replenishment. Vendor header order + meaning both select v[6]; v[7..] are the flag bit-positions.

## 2. Planet-type order and grids [verified, semantics inferred]
- vendor lists the order: HUSK PRIMORDIAL CONGENIAL EDEN MINING MOFFET CHAPEL CATHEDRAL RICH TYCOON CORNUCOPIA (11 types).
- numeric blocks between `#` and the count triple, shapes [(1, 1), (11, 4), (5, 15), (5, 15)]:
  - `50` alone = "pop growth amount" (vendor sentence: *first, note we have pop growth amount number*).
  - 11x4 = per planet type: first column reads as a decline curve (100,50,20,0,...) and cols 2-4 as [?]. Semantics NOT documented -> OQ-014.
  - 5x15 and 5x15 = two more matrices (rows = 5 of something; cols = 15). Values 0..9, ridge-shaped. Semantics undocumented -> OQ-014.

## 3. Full item table
```
Factory                1 0 0 0 1 30 255 255
Agriplot               0 0 2 0 1 30 255 255
Laboratory             0 1 0 0 1 50 255 255
Habitat                0 0 2 3 1 160 26 255
Metroplex              1 1 1 2 1 200 31 255
Colony^Base            1 0 1 2 1 120 5 0 255
Industrial^Megafacility 3 0 0 0 1 110 22 255
Artificial^Hydroponifer 0 0 3 0 1 100 10 255
Research^Campus        0 3 0 0 1 160 14 255
Logic^Factory          0 1 1 0 1 80 41 255
Engineering^Retreat    1 1 0 0 1 80 45 255
Surface^Cloaker        0 0 0 0 1 40 15 255
Hyperpower^Plant       0 0 0 0 1 200 25 255
Fertilization^Plant    0 0 0 0 1 200 52 255
Internet               0 0 0 0 1 250 59 255
Cloning^Plant          0 0 0 0 1 250 38 255
Observation^Installation 0 0 0 0 1 40 20 255
Tractor^Beam           0 0 0 0 1 50 34 2 255
Surface^Shield         0 0 0 0 1 100 4 3 255
Surface^Mega^Shield    0 0 0 0 1 180 61 3 255
Outpost                0 0 0 1 1 120 255 6 255
Transport^Tubes        0 0 0 0 1 10 255 0 6 255
Shipyard               1 0 0 0 1 240 0 255
Ship                   0 0 0 0 1 20 1 255
Orbital^Docks          1 0 0 0 1 170 16 255
Orbital^Cloaker        0 0 0 0 1 40 15 255
Orbital^Shield         0 0 0 0 1 60 0 3 255
Orbital^Mega^Shield    0 0 0 0 1 120 43 3 255
Orbital^Missile^Base   0 0 0 0 1 60 9 2 255
Short^Range^Orbital^Whopper 0 0 0 0 1 90 37 2 255
Long^Range^Orbital^Whopper 0 0 0 0 1 180 61 2 255
Alien^Hospitality      0 0 0 0 0 1 20 1 5 255
Interstellar^Trucking  0 0 0 0 0 1 254 1 5 255
Endless^Party          0 0 0 0 0 1 41 1 5 255
Scientist^Takeover     0 0 0 0 0 1 32 1 5 255
Automation             0 0 0 0 1 1 51 0 255
Terraforming           0 0 0 0 1 50 26 0 255
Lush^Growth^Bomb       0 0 0 0 1 200 62 1 255
Xeno^Archeological^Dig 0 0 0 0 1 50 6 0 255
```
