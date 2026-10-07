# research tree — `restree.txt` measurement
Source: `extracted/ascend00/restree.txt`, 4766 bytes, CP437, CRLF, 0x1A EOF (terminates the last row mid-line). Produced by `scripts/restree_probe.py`. All facts below are [verified] by this probe unless marked otherwise.

## 1. Grammar [verified]
```
row := NAME field0 cost prereq* 255      (whitespace-separated; '^' joins words in the display name)
file := count-line row+
```
- count line = `66`; data rows = **106** = **66** main-tree rows (Mixed-case names) + **40** variant rows (ALL-CAPS names). The count line counts the main tree only.
- every row's last integer is the terminator 255; self-prerequisites: 0; duplicate prereqs within a row: 0
- **field0**: == 0 on all 66 main rows; on variant rows takes values [0, 1, 2, 3, 4]. File-level semantics remain unknown, but the field is DEAD DATA at runtime — see §6c: the exe never loads rows past the count line. (OQ-013 CLOSED 2026-10-06r.)
- **cost = field1**.
- **prereqs = fields[2:-1]** as 0-based indices into the whole row list (effectively the main tree; see below).

## 2. Why field1 is cost and fields[2:-1] are indices (controls)
- reading fields[2:-1] as indices: in-range True, acyclic True, roots 7/106, depth-spread up to 17. A real prerequisite graph.
- CONTROL — reading fields[1:-1] as indices (cost folded in): acyclic **False**, in-range False. Fails; this is what crashed the first probe (RecursionError). The 10-multiple cost column read as indices creates cycles -> the reading is refuted.
- file order is NOT a topological order: 3 prereq references point forward (e.g. row 5 Environmental^Encapsulation lists 6:Xenobiology). Loaders must resolve by index, not by sequence.

## 3. Main tree (66 techs) [verified]
- roots: 3: Orbital^Structures, Tonklin^Diary, Xenobiology
- costs: 19 distinct, 50..400; histogram {50: 4, 70: 2, 75: 3, 80: 1, 90: 7, 100: 8, 110: 12, 120: 9, 130: 1, 140: 6, 150: 2, 160: 2, 170: 2, 180: 1, 200: 1, 230: 1, 240: 2, 300: 1, 400: 1}
- depth: max 17, mean 7.88; prereq-count histogram {0: 3, 1: 35, 2: 28}
- forward references exist (see section 2), so index != position-in-progress.

## 4. Variant block (40 ALL-CAPS rows) [verified facts, role inferred]
- cost is **uniformly 20** on all 40 variant rows (main tree: 50..300).
- field0 in 0..4 with histogram {0: 8, 1: 11, 2: 7, 3: 6, 4: 8}.
- all variant prereqs point into the main tree: True (none point at other variant rows) -> variants are leaves that extend the tree.
- variant names are unique file-wide (duplicates: 0); 4/40 variant names match a main-tree name in spaced form, and 4/66 main-tree names have a caps variant.
- [inferred] This matches a per-configurable-substitution table: 40 cheap (cost 20) techs gated by a small category index. Which game concept field0 selects (species? difficulty? expansion content?) is **OQ-013** — the file alone cannot say; 21 species vs field0 range 0..4 makes 'species index' doubtful.

## 5. Full table (global row id; f=field0, c=cost)
```
  0 f=0 c=50   Orbital^Structures           <- -  d=0
  1 f=0 c=50   Interplanetary^Exploration   <- 0:Orbital^Structures  d=1
  2 f=0 c=50   Tonklin^Diary                <- -  d=0
  3 f=0 c=90   Spacetime^Surfing            <- 1:Interplanetary^Exploration, 2:Tonklin^Diary  d=2
  4 f=0 c=100  Superconductivity            <- 2:Tonklin^Diary  d=1
  5 f=0 c=50   Environmental^Encapsulation  <- 6:Xenobiology  d=1
  6 f=0 c=90   Xenobiology                  <- -  d=0
  7 f=0 c=120  Spectral^Analysis            <- 2:Tonklin^Diary  d=1
  8 f=0 c=90   Advanced^Interferometry      <- 7:Spectral^Analysis  d=2
  9 f=0 c=100  Power^Conversion             <- 3:Spacetime^Surfing  d=3
 10 f=0 c=100  Advanced^Chemistry           <- 5:Environmental^Encapsulation  d=2
 11 f=0 c=140  Momentum^Deconservation      <- 3:Spacetime^Surfing  d=3
 12 f=0 c=140  Gravity^Control              <- 3:Spacetime^Surfing  d=3
 13 f=0 c=120  Molecular^Explosives         <- 7:Spectral^Analysis, 9:Power^Conversion  d=4
 14 f=0 c=140  Hyperlogic                   <- 6:Xenobiology, 8:Advanced^Interferometry  d=3
 15 f=0 c=180  Cloaking                     <- 8:Advanced^Interferometry  d=3
 16 f=0 c=110  Gravimetrics                 <- 12:Gravity^Control  d=4
 17 f=0 c=70   Strong^Force^Weakening       <- 9:Power^Conversion  d=4
 18 f=0 c=160  Light^Bending                <- 12:Gravity^Control  d=4
 19 f=0 c=230  Advanced^Exploration         <- 14:Hyperlogic, 21:Mass^Phasing  d=6
 20 f=0 c=100  Diplomatics                  <- 14:Hyperlogic  d=4
 21 f=0 c=100  Mass^Phasing                 <- 16:Gravimetrics  d=5
 22 f=0 c=100  Positron^Guidance            <- 13:Molecular^Explosives  d=5
 23 f=0 c=100  Gravimetric^Combustion       <- 16:Gravimetrics, 22:Positron^Guidance  d=6
 24 f=0 c=150  EM^Field^Coupling            <- 18:Light^Bending  d=5
 25 f=0 c=110  Subatomics                   <- 22:Positron^Guidance  d=6
 26 f=0 c=80   Planetary^Replenishment      <- 5:Environmental^Encapsulation, 23:Gravimetric^Combustion  d=7
 27 f=0 c=130  Momentum^Reflection          <- 11:Momentum^Deconservation, 25:Subatomics  d=7
 28 f=0 c=140  Hyperradiation               <- 24:EM^Field^Coupling, 27:Momentum^Reflection  d=8
 29 f=0 c=150  Plasmatics                   <- 25:Subatomics  d=7
 30 f=0 c=110  Energy^Redirection           <- 28:Hyperradiation  d=9
 31 f=0 c=100  Large^Scale^Construction     <- 19:Advanced^Exploration, 23:Gravimetric^Combustion  d=7
 32 f=0 c=75   Level^Logic                  <- 14:Hyperlogic  d=4
 33 f=0 c=75   Star^Lane^Anatomy            <- 29:Plasmatics, 30:Energy^Redirection  d=10
 34 f=0 c=75   Stasis^Field^Science         <- 28:Hyperradiation  d=9
 35 f=0 c=140  Coherent^Photonics           <- 30:Energy^Redirection  d=10
 36 f=0 c=70   Superstring^Compression      <- 29:Plasmatics  d=8
 37 f=0 c=110  Murgatroyd^Hypothesis        <- 32:Level^Logic, 36:Superstring^Compression  d=9
 38 f=0 c=90   Matter^Duplication           <- 27:Momentum^Reflection, 36:Superstring^Compression  d=9
 39 f=0 c=90   Energy^Focusing              <- 35:Coherent^Photonics, 37:Murgatroyd^Hypothesis  d=11
 40 f=0 c=90   Scientific^Sorcery           <- 37:Murgatroyd^Hypothesis  d=10
 41 f=0 c=90   Advanced^Fun^Techniques      <- 20:Diplomatics  d=5
 42 f=0 c=110  Repulsion^Beam^Tech          <- 39:Energy^Focusing  d=12
 43 f=0 c=110  Hyperwave^Technology         <- 28:Hyperradiation, 39:Energy^Focusing  d=12
 44 f=0 c=160  Fergnatz's^Last^Theorem      <- 40:Scientific^Sorcery  d=11
 45 f=0 c=110  Thought^Analysis             <- 32:Level^Logic  d=5
 46 f=0 c=140  Inertial^Control             <- 33:Star^Lane^Anatomy, 38:Matter^Duplication  d=11
 47 f=0 c=170  Nanoenergons                 <- 43:Hyperwave^Technology, 44:Fergnatz's^Last^Theorem  d=13
 48 f=0 c=170  Hypergeometry                <- 44:Fergnatz's^Last^Theorem  d=12
 49 f=0 c=110  Teleinfiltration             <- 43:Hyperwave^Technology, 45:Thought^Analysis  d=13
 50 f=0 c=110  Hyperdrive^Technology        <- 33:Star^Lane^Anatomy, 49:Teleinfiltration  d=14
 51 f=0 c=110  Microbotics                  <- 38:Matter^Duplication  d=10
 52 f=0 c=110  Ecosphere^Phase^Control      <- 26:Planetary^Replenishment, 48:Hypergeometry  d=13
 53 f=0 c=110  Hyperwave^Emission^Control   <- 43:Hyperwave^Technology  d=13
 54 f=0 c=200  Nanopropulsion               <- 47:Nanoenergons, 50:Hyperdrive^Technology  d=15
 55 f=0 c=240  Nanodeflection               <- 46:Inertial^Control, 56:Nanofocusing  d=15
 56 f=0 c=240  Nanofocusing                 <- 47:Nanoenergons  d=14
 57 f=0 c=400  Doom^Mechanization           <- 49:Teleinfiltration, 53:Hyperwave^Emission^Control  d=14
 58 f=0 c=120  Snooping                     <- 45:Thought^Analysis, 53:Hyperwave^Emission^Control  d=14
 59 f=0 c=120  Megagraph^Theory             <- 44:Fergnatz's^Last^Theorem  d=12
 60 f=0 c=120  Self^Modifying^Structures    <- 51:Microbotics, 56:Nanofocusing  d=15
 61 f=0 c=120  Advanced^Planetary^Armaments <- 31:Large^Scale^Construction, 35:Coherent^Photonics  d=11
 62 f=0 c=120  Accel^Energy^Replenishment   <- 54:Nanopropulsion, 59:Megagraph^Theory  d=16
 63 f=0 c=120  Gravity^Flow^Control         <- 54:Nanopropulsion  d=16
 64 f=0 c=120  Action^At^A^Distance         <- 49:Teleinfiltration, 59:Megagraph^Theory  d=14
 65 f=0 c=300  Illusory^Machinations        <- 56:Nanofocusing, 62:Accel^Energy^Replenishment  d=17
 66 f=2 c=20   INFORMATION^SYSTEMS          <- -
 67 f=4 c=20   BIO^RESEARCH                 <- -
 68 f=0 c=20   ION^POWER                    <- -
 69 f=1 c=20   ORBITAL^STRUCTURES           <- -
 70 f=4 c=20   XENOBIOLOGY                  <- 1:Interplanetary^Exploration
 71 f=0 c=20   ADVANCED^POWER^DISTRIBUTION  <- 2:Tonklin^Diary
 72 f=1 c=20   CELESTIAL^ARMS               <- 3:Spacetime^Surfing
 73 f=3 c=20   HIGH^EFFICIENCY^PRODUCTION   <- 0:Orbital^Structures, 5:Environmental^Encapsulation
 74 f=1 c=20   INTERPLANETARY^DRIVE         <- 2:Tonklin^Diary, 6:Xenobiology
 75 f=4 c=20   XENOARCHEOLOGY               <- 4:Superconductivity
 76 f=4 c=20   CROP^ENGINEERING             <- 1:Interplanetary^Exploration
 77 f=0 c=20   ADVANCED^POWER^GENERATION    <- 5:Environmental^Encapsulation, 8:Advanced^Interferometry
 78 f=1 c=20   STAR^DRIVE                   <- 8:Advanced^Interferometry
 79 f=1 c=20   SHIPS^OF^WAR                 <- 6:Xenobiology, 8:Advanced^Interferometry
 80 f=0 c=20   HYPERRADIATION               <- 11:Momentum^Deconservation
 81 f=3 c=20   MEGAPONICS                   <- 7:Spectral^Analysis, 10:Advanced^Chemistry
 82 f=3 c=20   ADVANCED^ROBOTICS            <- 7:Spectral^Analysis
 83 f=1 c=20   HYPERRADITION^DRIVE          <- 14:Hyperlogic
 84 f=1 c=20   ADVANCED^SPACE^STRUCTURES    <- 13:Molecular^Explosives, 17:Strong^Force^Weakening
 85 f=2 c=20   INTENSE^HYPERSCANNING        <- 14:Hyperlogic
 86 f=1 c=20   ADVANCED^SHIP^ARMAMENTS      <- 13:Molecular^Explosives
 87 f=4 c=20   HABITATRY                    <- 15:Cloaking, 16:Gravimetrics
 88 f=3 c=20   AUTOMATION                   <- 16:Gravimetrics
 89 f=0 c=20   HYPERRAD^POWER               <- 14:Hyperlogic
 90 f=4 c=20   HIGH^DENSITY^EXISTENCE       <- 22:Positron^Guidance
 91 f=4 c=20   XENOLOGY                     <- 4:Superconductivity
 92 f=2 c=20   ADVANCED^XENODIPLOMACY       <- 25:Subatomics
 93 f=3 c=20   TERRAFORMING                 <- 21:Mass^Phasing
 94 f=1 c=20   HIGH^EFFICIENCY^SHIP^DESIGN  <- 18:Light^Bending, 20:Diplomatics, 23:Gravimetric^Combustion, 24:EM^Field^Coupling
 95 f=2 c=20   ADVANCED^RESEARCH^TECHNIQUES <- 0:Orbital^Structures, 7:Spectral^Analysis
 96 f=4 c=20   CLONING                      <- 15:Cloaking, 23:Gravimetric^Combustion
 97 f=0 c=20   NANOATOMIC^PARTICLES         <- 23:Gravimetric^Combustion, 29:Plasmatics
 98 f=2 c=20   NANOATOMIC^COMMUNICATIONS    <- 28:Hyperradiation, 31:Large^Scale^Construction
 99 f=3 c=20   NANOATOMIC^ENGINEERING       <- 28:Hyperradiation, 31:Large^Scale^Construction
100 f=2 c=20   MEGASCANNING                 <- 32:Level^Logic
101 f=1 c=20   NANOATOMIC^ARMAMENTS         <- 33:Star^Lane^Anatomy
102 f=2 c=20   ADVANCED^ESPIONAGE           <- 26:Planetary^Replenishment, 32:Level^Logic
103 f=1 c=20   ADVANCED^INVISOLOGY          <- 32:Level^Logic, 33:Star^Lane^Anatomy
104 f=0 c=20   NANOENERGONS                 <- 33:Star^Lane^Anatomy
105 f=0 c=20   PLANETARY^CONVERSION         <- 27:Momentum^Reflection, 38:Matter^Duplication
```

## 6. LIVE TABLE LAW — CLOSED 2026-10-06r (OQ-013)

Three independent evidence lines below (6a code, 6b cost arithmetic, 6c census);
none is an inference from another.

### 6a. The loader: `FUN_00046870` (work/ascend_restored.bin, body 0x46870..0x46ae9)
Found by pointer law, not guessed: the payload holds exactly one
`restree.txt` string (payload file offset 0x85014, inside a cluster with
`..\research.cpp` at 0x85032..0x85052 — the research module's own string pool).
The only u32 in guest RAM pointing at it sits at guest-phys 0x205d23, and
0x205d23 - P0(0x1bf450) = 0x468d3, which is inside this function. Exactly two
callers (`get_xrefs_to` total 2): `FUN_00022ce4` (new-game init) and
`FUN_00046fa0` (serialize into .gam, reached from the save writer
`FUN_00025604` whose stride families 0x60/0x7b/0x1ee were tied to the live
record table on 2026-10-06). Load-once guard: global [0x00074740], tested at
0x468a5, set to -1 at 0x46ab9. Entry clears the 100-slot capacity (100*75 =
0x1d4c bytes) and sets each slot's byte 69 to 0xFF.

Record = **75 bytes (0x4b)**; table base = address of the count u16, name at
base+2. Field map from the DISASSEMBLY (the C pseudocode's `ushort*` arithmetic
is not trustworthy — its `+0x25`/`+0x45` are word-indexed):

| offset | width | field | instruction |
|---|---|---|---|
| base+0 | u16 | count, clamped `min(parsed,100)` | 0x4690b store; 0x46913 `CMP EAX,0x64`; 0x46918 cap |
| base+2 | 60 B | name, `^` -> 0x20 | 0x46a0a `CMP byte [EDX+0x2],0x5e` -> 0x46a10 `MOV ...,CL` (CL=0x20 from 0x46930); scan `i<0x3c` |
| base+62 | u16 | **runtime cost** (see 6b) | 0x469bc `MOV word [EDI+0x3e],AX` |
| base+64 | <=5 B | prereq row indices, 0xFF-terminated | 0x469dd `MOV byte [EBX+0x40],AL`; 0x469f2 `CMP EDX,0x5` |
| base+69..72 | 4 B | child list, second pass | 0x46a35 `CMP EBX,0xff` (free slot); 0x46a44 writes 0xFF to 69+k+1; 0x46a48 `MOV byte [EDX+0x45],AL` (AL = row index) |
| base+76 | u8 | file field0 | 0x4698f `MOV byte [EDI+0x4c],AL` (format 0x2476, first output) |

Second pass, verbatim from 0x46a21..0x46a48: for each row `j` in file order, for
each prereq `q` of `j`, write `j` into q's first slot k<4 whose byte 69+k still
reads 0xFF. Reproduced against live RAM: **66/66 rows exact, 0 mismatches**.

### 6b. MEASURED COST LAW — the runtime cost is NOT the file cost
The row loop (0x4691d..0x46a15) carries a running multiplier in EBP:
```
EBP = -0x14                       (0x4691d, = -20; before the loop)
if (row > 10) cost *= EBP         (0x46992 CMP 0xa; 0x46999 IMUL EAX,EBP)
if (cost > 65000) cost = 65000    (0x469a4 CMP 0xfde8; 0x469ae)
store cost at base+62             (0x469bc)
EBP += 2                          (0x4693b, loop tail, AFTER the store)
```
=> **runtime_cost(row) = file_cost for row <= 10, else file_cost * (2*row - 20),
clamped to 65000.** Re-executing that loop reproduces the captured RAM costs for
**66/66 rows with zero mismatches**. Multipliers are 2, 4, 6, 8 ... for rows 11,
12, 13, 14; no shipped row reaches the clamp (largest product: row 57,
400 * 94 = 37600). Worked examples from the captures: row 11 Momentum
Deconservation 140 -> 280; row 15 Cloaking 180 -> 1800; row 30 Energy
Redirection 110 -> 4400; row 65 Illusory Machinations 300 -> **33000**.

The file column survives nowhere else: the verbatim u16[66] cost sequence
appears nowhere in guest RAM and nowhere in the payload, so the scaled value at
base+62 is the only cost the game holds. Two consequences for a rewrite: charging
the file column makes late techs ~100x cheaper than the original, and
"cheapest available tech" is not the same choice on the two scales — selection
must compare runtime costs too.

### 6c. In play = the 66 main rows; the 40 variants are never loaded
The row loop is bounded by the count line (66, cap 100), so rows 66..105 — every
ALL-CAPS variant — are never parsed. Checked by census rather than by trusting
that reading:
- Tool `scripts/r1_restree_law.py` (added 2026-10-06r): anchors on row 0's name,
  walks stride 75, hard-codes no address, and exits 0 only if the 6b law
  cross-checks >=90% of the located rows.
- **27 slots x 13 banked captures** (`work/r1/r1deep-*`, `r1ad-*`, `r1sav-*`,
  turns 0..9): main rows present **66/66** in every slot; variant rows
  **0/40** — under both the `^` and space spellings, and multi-word substring
  probes (`ADVANCED PLANETARY`, `CROP ENGINEERING`, `TERRAFORMING`, ...) are
  also zero.
- RAM names are the **space-substituted** forms: `^` is a file-level display
  joiner replaced by 0x20 at load time, so a research name in RAM never contains
  `^` (0 hits across the loaded block).
- The vendor's mid-game save `game/resume.gam` carries the same stride-75 table
  (count u16 = 66 at file offset 180, scaled costs included) and its
  4950-byte research block is **byte-identical (0 diffs)** to a fresh-campaign
  RAM copy. So this table is static definition data, not research progress —
  who-researched-what lives elsewhere and is still unmapped.
- Weak corroboration only: no extracted table *names* a variant tech (40 spaced
  variant names searched in gizmos/static/cosmos/names/help -> 0 hits). This
  proves little — the 66 main-tree names score 0 in the same files, so the test
  cannot discriminate. What closes the question is the loader bound plus the RAM
  census. `planitem.txt`'s RESEARCH-REQ column is deliberately NOT cited:
  parsing that file's variable-width name column is OQ-014's open work and every
  quick parse attempted here misaligned it.

### 6d. Rewrite upgrade (2026-10-06r)
- `rewrite/src/game/research.h`: `Tech::runtimeCost()` implements 6b (file
  `cost` retained as the file column; the row index is captured at parse time
  because the multiplier keys on FILE row order, not on a filtered index).
  `available()`'s default flips `includeVariants` **true -> false** per 6c.
- `rewrite/src/game/campaign.cpp`: researchPhase queries main-tree-only
  (:265), the player's cheapest-tech comparison (:271-272) and the FreeResearch
  pick (:551, :554) compare `runtimeCost()`, and the completion charge test
  (:283) uses `runtimeCost()`.
- Pins: `research_runtime_cost_law_measured` (280/1800/4400/37600/33000, the
  clamp branch, and "55 of 66 rows scale") and `research_variants_are_not_in_play`
  (default `available()` yields no variant rows, and exactly the 3 main roots on
  an empty empire). 86 tests, 0 failed. Gate green. Seeded seed-2024 headless
  campaign still wins Control, turn 145 (was 148) — the research curve moved, as
  it should have.
- Residue, stated not papered over: the file-level meaning of variant field0
  (0..4) is still unknown, but it is dead data — rows past the count line never
  reach memory, so no runtime behaviour can depend on it.
