# ship devices (gizmos) — `gizmos.txt` measurement
Source: `extracted/ascend00/gizmos.txt` (7,263 B, CP437/CRLF, 0x1A EOF). The vendor documents this format himself above the `#` marker — that documentation is transcribed verbatim below and then re-measured. Produced by `scripts/gizmo_probe.py`; gate stage 3j.

## 1. Vendor grammar (transcribed) [verified against 76/76 records]
```
record := Name \n Cat Power Range Level NumUses Industry Special1 Special2 ResReq {flag_list} 255
```
- Cat: Weapon 0, Shield 1, Drive 2, Scanner 3, Generator 4, Special 5.
- Power: operating cost (generators: power SUPPLIED). Range: max range (weapons/scanners). Level: weapon damage / shield strength / scanner range-per-turn / drive max travel in sugar-cube units. NumUses: per turn, 0 = unlimited. Industry: cost added to the ship build. ResReq: research node index or 255.
- Flag bits (vendor table): TARGETSHIP 1, TARGETLANE 2, TARGETORBIT 4, TARGETSURFACE 8, TARGETOWNSHIPS 16, TOGGLEABLE 32, NOTARGET 64, PASSIVE 128. The flag_list lists BIT POSITIONS, not values, and ends with 255 (which doubles as the row terminator: rows with flags have one more field than rows without — never re-split on 255).

## 2. Measured shape [verified]
- **76 records**, names unique; category counts: {0: 10, 1: 6, 2: 5, 3: 6, 4: 5, 5: 44}
- weapon    n=10  power 0..6, range 25..100, level(damage/strength/scan-per-turn/drive-dist) 1..13, industry 15..100
- shield    n=6   power 0..4, range 0..0, level(damage/strength/scan-per-turn/drive-dist) 1..5, industry 10..200
- drive     n=5   power 1..5, range 0..0, level(damage/strength/scan-per-turn/drive-dist) 2..10, industry 10..80
- scanner   n=6   power 0..0, range 25..1000, level(damage/strength/scan-per-turn/drive-dist) 1..5, industry 20..200
- generator n=5   power 2..10, range 0..0, level(damage/strength/scan-per-turn/drive-dist) 1..5, industry 20..100
- special   n=44  power 0..30, range 0..120, level(damage/strength/scan-per-turn/drive-dist) 0..20, industry 10..150
- ResReq: 76/76 records gated by a research node; 53 distinct nodes; every index < 106 (restree row count) — **cross-validates the restree row numbering**: e.g. Fergnatz Lens -> 44 = `Fergnatz's^Last^Theorem`, Plasmatron -> 29 = `Plasmatics`, Ueberlaser -> 35 = `Coherent^Photonics`, Hypersphere Driver -> 48 = `Hypergeometry`. This is the second independent source pinning restree indices.
- flag-list histogram (top): [((7,), 23), ((0,), 18), ((6,), 13), ((0, 1, 2, 3), 6), ((5,), 6), ((0, 1, 2), 5), ((1,), 4), ((3,), 1)]

## 3. What this settles for combat (OQ-010 partial)
- weapon damage values ARE in data (level column, 1..13). Shield strength 1..5. What is NOT in data: the damage APPLICATION formula (hit probability, shields subtract vs absorb, overkill) — still needs R1 or battle.txt prose mining (docs/re/combat.md when written).

## 4. Full table
```
Mass^Barrage^Gun             0 1 25 1 1 15 0 0 4 0 1 2 255
Fourier^Missiles             0 1 40 2 1 25 0 0 7 0 1 2 255
Quantum^Singularity^Launcher 0 2 25 4 1 40 0 0 12 0 1 2 255
Molecular^Disassociator      0 2 50 4 1 50 0 0 17 0 1 2 255
Electromagnetic^Pulser       0 1 50 1 5 60 0 0 24 0 1 2 255
Plasmatron                   0 2 100 4 1 70 0 0 29 0 1 2 3 255
Ueberlaser                   0 3 50 6 2 70 0 0 35 0 1 2 3 255
Fergnatz^Lens                0 0 35 4 2 70 0 0 44 0 1 2 3 255
Hypersphere^Driver           0 6 75 10 2 100 0 0 48 0 1 2 3 255
Nanomanipulator              0 6 50 13 3 100 0 0 56 0 1 2 3 255
Ion^Wrap                     1 1 0 1 0 10 0 0 5 5 255
Concussion^Shield            1 2 0 2 0 30 0 0 11 5 255
Wave^Scatterer               1 0 0 1 0 50 0 0 18 5 255
Deactotron                   1 2 0 3 0 60 0 0 30 5 255
Hyperwave^Nullifier          1 4 0 4 0 100 0 0 43 5 255
Nanoshell                    1 3 0 5 0 200 0 0 55 5 255
Tonklin^Motor                2 1 0 2 0 10 0 0 2 7 255
Ion^Banger                   2 1 0 4 0 30 0 0 10 7 255
Graviton^Projector           2 3 0 6 0 40 0 0 23 7 255
Inertia^Negator              2 1 0 6 0 20 0 0 46 7 255
Nanowave^Space^Bender        2 5 0 10 0 80 0 0 54 7 255
Tonklin^Frequency^Analyzer   3 0 25 1 0 20 0 0 2 7 255
Subspace^Phase^Array         3 0 50 1 0 40 0 0 8 7 255
Aural^Cloud^Constructor      3 0 75 2 0 60 0 0 24 7 255
Hyperwave^Tympanum           3 0 100 3 0 80 0 0 28 7 255
Murgatroyd's^Knower          3 0 200 4 0 100 0 0 37 7 255
Nanowave^Decoupling^Net      3 0 1000 5 0 200 0 0 47 7 255
Proton^Shaver                4 2 0 1 0 20 0 0 1 7 255
Subatomic^Scoop              4 4 0 2 0 35 0 0 9 7 255
Quark^Express                4 6 0 3 0 60 0 0 25 7 255
Van^Creeg^Hypersplicer       4 8 0 4 0 80 0 0 28 7 255
Nanotwirler                  4 10 0 5 0 100 0 0 47 7 255
Lane^Blocker                 5 3 40 0 1 30 0 0 33 1 255
Molecular^Tie^Down           5 7 50 0 1 20 0 0 16 0 255
Intellect^Scrambler          5 7 50 0 1 20 0 0 14 0 255
Brunswik^Dissipator          5 15 50 0 1 100 0 0 34 0 255
Recaller                     5 7 0 0 0 40 0 0 30 6 255
Disarmer                     5 5 60 0 1 30 0 0 38 0 255
Smart^Bomb                   5 7 0 7 0 30 15 0 40 6 255
Gravity^Distorter            5 4 0 0 1 20 65 0 27 6 255
Fleet^Disperser              5 5 120 0 1 30 45 0 42 0 255
X^Ray^Megaglasses            5 3 120 0 0 30 0 0 14 7 255
Cloaker                      5 3 0 0 0 30 0 0 15 7 255
Star^Lane^Drive              5 0 0 1 0 25 0 0 3 7 255
Star^Lane^Hyperdrive         5 0 0 2 0 50 0 0 19 7 255
Positron^Bouncer             5 2 60 0 1 10 100 0 22 0 255
Gravimetric^Catapult         5 3 0 0 1 15 0 0 21 6 255
Myrmidonic^Carbonizer        5 4 40 20 1 70 20 0 39 0 1 2 3 255
Containment^Device           5 5 50 0 1 50 0 0 40 0 255
Shield^Blaster               5 7 50 0 1 30 0 0 49 0 255
Backfirer                    5 10 50 0 1 60 0 0 53 0 255
Lane^Destabilizer            5 7 40 0 1 40 0 0 33 1 255
Tractor^Beam                 5 3 120 0 1 30 65 0 34 0 255
Cannibalizer                 5 0 0 0 1 20 5 20 35 6 255
Moving^Part^Exploiter        5 10 50 0 1 60 0 0 64 0 255
Hyperswapper                 5 3 120 0 1 20 0 0 48 0 255
Gravimetric^Condensor        5 5 0 0 1 30 65 10 63 6 255
Accutron                     5 7 0 0 1 60 0 0 39 6 255
Remote^Repair^Facility       5 30 0 0 0 70 5 0 60 6 255
Sacrificial^Orb              5 3 70 0 0 20 6 0 30 0 255
Lane^Magnetron               5 10 50 0 1 50 0 0 50 1 255
Disintegrator                5 25 25 0 1 150 0 0 57 0 255
Lane^Endoscope               5 10 50 0 0 20 0 0 58 1 255
Toroidal^Blaster             5 0 0 0 1 20 40 0 23 6 255
Gizmogrifier                 5 4 60 0 1 30 0 0 44 0 255
Replenisher                  5 8 0 0 1 60 0 0 18 6 255
Specialty^Blaster            5 5 60 0 1 30 0 0 49 0 255
Gyro-Inductor                5 0 0 0 1 20 10 0 37 7 255
Plasma^Coupler               5 4 70 0 1 20 0 0 29 0 255
Invulnerablizer              5 20 0 0 1 60 0 0 65 6 255
Phase^Bomb                   5 4 25 0 1 40 0 0 13 3 255
Colonizer                    5 5 0 0 0 35 0 0 5 7 255
Self^Destructotron           5 0 40 20 0 50 20 0 57 6 255
Invasion^Module              5 10 0 0 0 70 0 0 8 7 255
Mass^Condensor               5 8 120 0 1 50 50 5 13 0 255
Hyperfuel                    5 0 0 0 0 20 40 0 36 6 255
```
