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
  who-researched-what lives elsewhere: MAPPED 2026-11-07 t326 (income-law.md
  S-T326) — per-race owned-mask byte at ds:0x7478e + 0x4b*i, bit (1<<race),
  count word ds:0x74744 (law from cheat body 0x47828 verbatim; census
  scripts/r326_precensus.py; semantics corroborated via prereq-closure, not
  proven — 10 deep-tree edges violate strict-AND, see S-T326.2).
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


## 7. tRS-B1 SET-PROJECT HANDLER LAW (2026-11-24, D26 "I can't set any projects")

The research-window UI function spans payload 0x41e34..0x47eb0 (single
function per work/functions_full.tsv; disassembly window
work/tRS_reswin_fn.asm). The set-project path is TWO-STAGE:

(a) SELECT (sub 0x47478, entry via the msg-arm call at 0x47da5 guarded by
    dword[win+0x35]!=0): scans the projected node table (100 slots stride
    0xc at win+0x143, zero-init loop 0x470c1..0x470ed, count checked
    against WORD[0x74744] at 0x4715d) from the LAST row downward; per node
    k: legality call 0x46d3c FIRST (0x474e8), then the bounds legs
    0x474fb..0x4752d — x word [winptr+0x5f1+2k] and y word [+0x6b9+2k],
    each sar 16, reject `jle` at centre-25 and `jge` at centre+25 on BOTH
    axes => accept iff |dx|<=24 AND |dy|<=24: an INCLUSIVE +-24 SQUARE,
    fixed size, NOT scaled with any radius. First hit wins (0x4752f->0x47533);
    store word [win+0x9db]=row ONLY if different (0x4753a), and a change
    clears dwords 0x764bc/0x764c0 to 0xffffffff (0x4754f/0x47555).
(b) COMMIT (0x47d99..0x47e43, msg arm dx>3): word [win+0x9db]==0xffff ->
    no-op; then OWNED gate (row+0x47 owned-mask dword >>24, race bit
    [0x7458e]) -> reject 0x47718; then LEGALITY call 0x46d3c (ebx=0xffff
    terminator) -> reject; then `mov word [specnum*2+0x76492],ax` (0x47e34,
    the t91 human-picker writer) + call 0x4fb30 with eax=0x78638 (side
    effect UNRECOVERED — named seam TRSB1-B) + the two scratch clears again.

FUN_00046d3c VERBATIM (0x46d3c..0x46dde): already-owned -> FALSE; else the
<=5 prereq bytes row+0x40 (0xFF terminator) must EVERY one have the race bit
set in [prereq+0x47]>>24 -> legality = ALL-prereqs-owned AND not-owned.
The port's setStudy() conjunction (researchview.cpp) matches gate-for-gate;
the queue field is DAT_00076492 == the SAME table as the AI picker target
(aicode.md S3b, t91 field identity 0x74744+0x1d4e).

PORT DELTA shipped tRS-B1: the hit box. The pre-tRS-B1 port hit-tested a
DISC of the ring radius (r30 scaled by perspective) — WRONG in both
directions vs (a): missed the square corners, accepted axis points 25..29.
researchview.cpp researchHit() now uses kResHitHalf=24 (inclusive square on
the PROJECTED centre). Pin test_researchhit_trsb1.cpp (mutation M-R1 half
25 CAUGHT, M-R2 disc CAUGHT; suite 515->516/0). Live witness
scripts/tRSB1_witness.sh VERDICT PASS (log "ui research study
Superconductivity"; right-panel green text px 0->854 — the t268 blank-at-
rest panel is the feedback canvas; gold Study rim 0->320 near the click).

D26 ATTRIBUTION [inferred, not a closure]: the click->queue loop is alive
in the port since t408; what the vendor communicates and the port did not
is WHICH disks are clickable ("empty disks represent technologies you CAN
CHOOSE TO STUDY" — help reswin ln1668-1690: clickability is the disk's
CONTENT, and the vendor's node art comes from restree.shp pictures). The
tree DRAW (tRS-V1) carries that half: layout generator FUN_0004709c
(work/tNGS_gen1/2.asm) + the projected table + per-node art.

SEAMS: TRSB1-A scan order first-hit(high->low, legality-gated) vs port
nearest-among-hits — equivalent while pitch 78/96 keeps the +-24 boxes
disjoint (pinned premise in the test); TRSB1-B call 0x4fb30(0x78638)
unrecovered; TRSB1-C the vendor SELECT-vs-COMMIT split means an illegal
click never even sets the selection word (the port collapses both into
setStudy — same observable outcome, no separate dossier state).

## 8. tRS-V1 TREE-GEOMETRY LAW (2026-11-24, D26 "the tree not being drawn
correctly"). FULL WORKING RECORD docs/re/_wip_tRSV1.md (P1-P9); this is the
distilled law. Generator = FUN_0004709c reswin init (asm work/tNGS_gen1/2.asm
+ fresh capstone windows work/tRSV1_proj0.asm, work/tRSV1_proj.asm of the
same function 0x4709c..0x48f80).

(a) FILE BRANCH DEAD: init opens 'reswin.txt' (ds:0x24b0 pool VERIFIED);
    absent in the shipped tree => generator branch 0x471f9 is the vendor law.
(b) DEPTH LAW = iterative relaxation over the <=5 prereq bytes (record
    stride 0x4b at census 0x74784): A[row] = max(A[p]+1) once every prereq
    has a final value; rows retry across passes until no pass marks an
    unmarked prereq. Converges to the LONGEST-CHAIN depth == the port's
    researchDepth (MEASURED replay: 66/66 rows, esi = maxdepth+1 = 18
    columns, max 17 — agrees §3).
(c) PLACEMENT LAW = A CHAIN OF CIRCLES, one per depth column k in [0,esi):
    C[k] = rows at depth k (measured [3,4,3,5,6,5,3,4,2,4,4,4,4,4,5,3,2,1]).
    Column angle acc = 240 + 30*k DEGREES. Per node i in column (file order):
    Y = 30*k + 15*(i&1); radius = R0(k) for i==0 else 23, where R0(k)=23 iff
    (k even AND C[k]>1) OR (k odd AND C[k]==2), else 4; X=0, Z=radius;
    node angle = acc + i*(360/d) accumulated by REPEATED FLOAT ADDS after
    each write (d = C[k], except odd k with C[k]>2 -> C[k]-1: the vendor
    quirk that such columns do not close the circle). Rotation primitive
    0x5324c VERBATIM (degrees, pi/180 ds:0x88b88): (X,Z) -> (X sin+Z cos,
    Z sin - X cos); with X=0 at call time: X = R sin(t), Z = R cos(t).
    KEY CORRECTION (self-caught, _wip P1c): the operand at 0x47367 is
    byte[esp+k] == C[k] (the count array zeroed at esp+0), NOT A[k] — the
    C-reading is the only one under which the divisor is never 0.
(d) CAMERA LAW (0x470ef call 0x203b8, args VERIFIED): fov 30, near 1, far
    1e5, half-width 320 => focal = 320/tan(15deg) = 1194.19 px (0x203e4:
    320/tan(fov*pi/180 * 0.5), fptan 0x77562, pi/180 pool 0x884b0, 0.5 pool
    0x833a4); position (0,0,-150) (0xc3160000). World = (X, Y, Z) via the
    row-major affine 0x53324 (VERIFIED); perspective 0x53374 (the tNGS-S5
    primitive) writes the u16 screen words at win+0x5f3+2k / win+0x6bb+2k ==
    the HIGH HALVES of the u32s the hit law reads at +0x5f1/+0x6b9 (lea pair
    0x47fe3/0x47fe9) + centres 240/235 + pan word [win+0xd3].
    CONSEQUENCE (arithmetic of the cited law): scale 1194.19/(Z+150) in
    [7.0,9.2] => the 18-column tree spans FAR beyond the 470x426 window —
    THE VENDOR SCREEN IS A PANNED WINDOW onto the tree (t252 capture
    corroborates: 3 disks + lines running off-frame). OPEN LEG (named,
    uncited): 0x53374's arg roles (which push is the focal factor) — diff
    vs cosmos call site 0x285bb (tNGS cycle-1 pinned) FIRST.
(e) DRAW-SCOPE LAW (0x48566): ONLY rows passing FUN_00046d3c (the frontier:
    all-prereqs-owned AND not-owned) are drawn; ancestors exist in the table
    for the prereq LINES only. Line = projected endpoints each shifted
    +27 px Y (0x48334/0x48353 `0x1b`), palette 0x6b - clamp(round(0.25*
    (win+0xe7 + depth word [win+0x783+4k])), -3, +3) (z-shaded).
(f) ART LAW: node ring = 'data\resring.shp' (pool 0x850bc VERIFIED, sole
    refs 0x48476/0x487b6), 4 records = frames 0..3 by the state law
    0x483fa..0x48470: 1 default; 0 iff row==studied AND not owned; 3 iff
    owned; 2 (SELECTED, gold path 0x5caac) iff row==word[win+0x9db].
    S8.2 DIMS CORRECTION (tPR-U, 2026-11-24): the earlier "4 records 29x29"
    was a header-pair reading, NOT the bbox. MEASURED directory (unified
    shp law; record starts 56/1200/2363/3532): bbox quads k1..k3 =
    (-30,-30,29,29) => dims 60x60 by the bbox-diff law, and the port's
    1:1-rendered rings measure 60 px on screen — MATCHING the vendor's
    measured 60 px rings (t252 vs tRSB1 shots, tPR-U P2/P3). Blit stays
    1:1 unscaled (0x5caac row-RLE) — the law is unchanged; only the
    quoted dims number is. The "gold path" label on 0x5caac is an
    INFERRED name, never pixel-witnessed (tPR-U: the selected/studied
    disk renders blue in our capture; ring-colour MEANING is now an
    open human-grading question, PR-checklist item 6).
    'data\restree.shp' = 66 records 24x24 = ONE PICTURE PER LIVE ROW, but
    NO code immediate references its name (the only 'restree' string is
    restree.txt for the text loader 0x468d3) — the picture consumer is
    UNRECOVERED (seam TRSV1-C; the t252 picture-in-disk is real, its
    painter is not yet found).
(g) HIT LAW survives: tRS-B1's +-24 square consumes the SAME projected
    words — unchanged by any layout swap.
(h) BLITTER ANCHOR LAW (tRS-V1d, seam TRSV1c-E CLOSED) [MEASURED, raw asm
    + decompile work/combat_decomp/5caac.c:58-64]: the research draw passes
    the projected word VERBATIM (0x4849f/0x484a5 word[win+0x5f1]/[+0x6b9]
    sar 16, NO centring arithmetic; frame esi==2 -> FUN_0005caac at
    0x484c4, else FUN_0005cf96 at 0x48501), and the blitter composes the
    destination from the record's SIGNED BBOX:
      dest = (bboxL + passed_x, bboxT + passed_y) .. (bboxR + passed_x,
      bboxB + passed_y)   (0x5caac 0x5cd0e..; 0x5cf96 twin 0x5d04b/0x5d057;
      dims/anchor getters FUN_00061058/FUN_0006108c, shp.md S27 law).
    The passed point is an ANCHOR, not a top-left. resring bbox
    (-30,-30,29,29) centres the 60x60 content on the anchor BY CONSTRUCTION
    => vendor drawn-centre == hit-centre. Port fix VERBATIM: blit at
    (x + record().left, y + record().top) (ui.cpp NODES block; the old
    (x-14) was the dead 29x29 dims reading). WITNESS scripts/tRSV1d_witness.sh
    + tRSV1d_ringcentre_census.py seed 5: content bbox (0,0,59,59) about the
    logged centre (397,240), offset (-0.5,-0.5), control +30/+30 crop
    non-full; MUTANT (-15,-15) CAUGHT (bbox (15,15,59,59), +7,+7), restored
    md5 089d35bf2644513f90aae1f62132027a. PINS test_researchanchor_tRSV1d.cpp
    x3 (record centring, source wiring, hit-at-drawn-centre); census v1
    lesson banked: a BRIGHTNESS threshold measures the bright-rim subset
    (art-biased -1.5 px artifact) — measure the CONTENT bbox vs the flat
    field bg instead.

## S8-CORRECTION (tRS-V1b, 2026-11-24) — supersedes S8d/S8e lines it contradicts
Full working record docs/re/_wip_tRSV1.md P6/P10/P11 (raw x87 hand-decode;
capstone in ~/tools/revenv; linear dumps desync on this image).
1. S8d "pan word [win+0xd3]" REFUTED: win+0xd3 == cam+0x28 == the FOCAL
   (320/tan 15deg = 1194.19, 0x203b8/0x203e4) — pointer identity. Projection
   law (both legs perspective-divided, chop-rounding 0x76e08 = RC-forced
   trunc of v+0.5f):
     screenX = chop(1194.19f*vX/Z + 0.5f) + 235   (word win+0x5f3+2k)
     screenY = chop(1194.19f*vY/Z + 0.5f) + 240   (word win+0x6bb+2k)
   0x53374 arg roles CLOSED by callee trace + cosmos diff (0x285bb same
   shape). No pan term exists in the projection.
2. S8e edge law CORRECTED: the prereq line runs (this.x, this.y-27) ->
   (prereq.x, prereq.y+27) (raw bytes 0x48343 `sub eax,0x1b` on the CURRENT
   node at 0x48353's counterpart; the "+27 both endpoints" reading was wrong).
   Colour index = 0x6b - clamp(chop(0.25f*(0.5f*(z_this+z_prereq) + posz)),
   -3,+3), posz = win+0xe7 = camera pos.z = -150; prereq == selected word ->
   index 0xf3 (0x48321).
3. 0x46d3c TRUE-FORM: returns TRUE for OWNED rows WITHOUT the prereq loop
   (0x46d88) — draw scope AND hit scope = OWNED + FRONTIER; Blocked rows are
   drawn by NOBODY and hittable by NOBODY. (tRS-B1's "legality" note was
   imprecise; the not-owned gate lives only in the commit chain 0x47d99.)
4. SCROLL LAW (supersedes the t419 screen-pan reuse): msg 50/51 = camera
   basis yaw +3/-3 deg per pump tick via the dat_764c4 bit-pair latch
   (0x47b44..0x47c42 verbatim, incl the DEAD (0,1) state); msg 52/53 =
   camera posZ += -1/+1 x runtime f32[0x9f108] (value NOT in the restored
   image — seam TRSV1b-A, port default 1.0). DOLLY, not screen translate.
5. Rotation 0x5324c raw VERBATIM: X' = X*cos + Z*sin, Z' = Z*cos - X*sin
   (0x7754a = fcos, 0x77556 = fsin, fprem reduce 0x7751e); angle step is
   INTEGER 360/d THEN repeated f32 adds (0x4743d).

S8.1 FOCAL VALUE CORRECTION (tRS-V1c, 2026-11-24). The "1194.19" cited in
   S8(d)/S8-CORRECTION is a transcription slip, NOT a law constant. The
   cited law is 320/tan(15deg): f64 = 1194.2562584; the vendor's f32 chain
   (fptan 0x77562 then fdiv, both single-precision) yields
   1194.2562255859375 (measured with struct round-trip this iteration). The
   port pins resFocal() = 320.0/std::tan(15.0*pi/180) in double and the
   mutation focal->tan(17.5deg) is CAUGHT by tests/test_researchgeom_trsvc.
   cpp. Scale consequences in S8 are unchanged at the cited precision.

## 9. tRS-V2 DISK FILL LAW (2026-11-24, D27 user law: empty -> center
sliver on select -> widens with progress -> full on completion). Working
record docs/re/_wip_tRSV2.md P1-P7; derivation RAW-STEPPER cited (the
tRSV1b linear dump desyncs in this region).
  (a) THE PICTURE CONSUMER (seam TRSV1-C CLOSED at code level): inside the
      reswin per-row draw loop (FUN_00041e34), AFTER the prereq line loop
      and BEFORE the ring blit, 0x48383..0x483f7: per-row value q =
      [esp+0x120]; if q==0 SKIP (no picture); else Q = (int16)q << 16
      (shl edx,0x10 = shift 16), qdiv = Q / 20 (signed idiv ebx=0x14),
      shapeId = FUN_0001fc34(cache 0x9f10c, slot word [0x6fd82]), then
      FUN_0005d5a1(shapeIdPtr, p2=[esp+0x154], p3=[esp+0x144], x=projX
      sar16, y=projY sar16, 0x48c44, 0, scaleU=qdiv, scaleV=qdiv, flags=1).
      The library at slot word 0x6fd82 = the 66-record per-row picture
      library (file data\\restree.shp, extracted/ascend01/data/restree.shp;
      READ sites 0x476c6/0x483dd/0x4873b/0x48785, no direct static writer -
      bulk-registered by the shape loader).
  (b) Q LAW (0x481aa..0x48239 VERBATIM): row = [esp+0x128]; rec = row*0x4b
      (table base 0x74744 = the count u16, OQ-013); raceBit = [0x7458e].
        q = 0;                       ; unowned AND not-studied -> EMPTY
        if dword[rec+0x47]>>24 has raceBit:  q = 20;   ; OWNED -> FULL
        else if row == word[0x76492 + 2*race] (the STUDIED/selected word,
             set verbatim 0x48130..0x48141, the tRS-B1 specnum field):
             q = (word[0x764a0+2*row]*18) / word[rec+0x3e] + 2;
             clamp q to [-17, +17];
      word[rec+0x3e] = the RUNTIME cost (S6b law, base+62/0x3e) - the
      divisor is the SCALED cost, not the file cost. dword[rec+0x47] is the
      SAME owned-mask field the ring-frame law reads at 0x4841d (consistency
      check: owned rows get ring frame 3 AND fill 1.0). Negative clamp is
      dead for real inputs (progress u16 >= 0 => q >= 2); ported verbatim.
  (c) WIPE SHAPE (DERIVED, not guessed): FUN_0005d5a1's scaled branch
      scales the whole source record by scaleU/scaleV about the passed
      ANCHOR (the S8(h) blitter anchor law; dest = record signed-bbox +
      anchor), clipped to the node rect. Both axes receive the SAME q/20
      factor => a uniform CENTER-OUT RADIAL SCALE: at select (progress 0)
      q=2 -> 0.10 of the picture (the central sliver the user sees APPEAR
      ON SELECT); q grows 2 -> 17 as progress 0 -> cost (scale 0.10 ->
      0.85 — the clamp legs 0x48222/0x48234 fire AFTER `add eax,2`, so the
      studied branch NEVER reaches 20; tRS-V2p recheck 2026-11-24 corrects
      the earlier "grows to 1.00 as progress -> cost" phrasing); the last
      15% is the OWN-completion JUMP 17 -> 20 (0.85 -> 1.00) at
      0x481ce; owned -> 1.00 = FULL DISK.
      NOT an angular wedge: no angle term exists anywhere in the cited
      chain. 16.16 pins (recomputed tRS-V2p against the cited truncating
      idiv q<<16/20: the earlier 0x19a9/0x6988/0xd9f9 were transcription
      slips — 0x19a9=0.1002, 0x6988=0.4123, 0xd9f9=0.8516 match no q):
      q=2 -> 0x1999; q=11 -> 0x8CCC; q=17 -> 0xd999; q=20 -> 0x10000.
  (d) UNRECOVERED LEGS (named, not stubbed): ~~the writer of word[0x764a0+
      2*row] (the per-turn research progress accumulator)~~ CLOSED tRS-V2w
      (see (e): FUN_00046aec, field identity 0x74744+0x1d5c==0x764a0 per
      t91); the exact
      arg roles of 0x5d5a1 p2/p3 (decompiler regparm mapping suspect; the
      0x48c44 immediate sits in the code region). Endpoints (a)+(b) close
      the user-law behavior regardless; port spec docs/re/_wip_tRSV2.md P7.
  (e) PROGRESS-ACCUMULATOR WRITER LAW CLOSED tRS-V2w (raw-stepper
      work/tRSV2w_46aec.asm = FUN_00046aec verbatim; turn call site
      0x25028 mov eax,0x74744 / 0x2502f call — t91's site):
      (1) per-turn RES bucket[race] rebuilds from zero: + word[planet+0x46]
          per owned planet (0x46b80/0x46b84), plus +1 per planet NOT owned
          by the current-turn player iff byte[0x13bc4]==2 AND that planet's
          RES word < 15 (0x46b5b..0x46b77; live gov == 1 in 20/20 saves =>
          DEAD in the shipped scenario).
      (2) APPLY 0x46bcd..0x46c1b: bucket==0 -> je 0x46c02 adds NOTHING;
          else progress word[0x764a0+2*row] += TRUNC((bucket+1)^0.85)
          (0x3feb3333:0x33333333 == double 0.85; pow 0x78a90, chop 0x76e08,
          fistp 0x46bfe). Completion cmp progress >= word[rec+0x3e] ->
          owned mask +0x4a/+0x4b |= 1<<race, target 0x76492[r] := 0xffff,
          progress := 0, event 0x55a60 iff human (0x46c7e).
      (3) target==0xffff -> progress := 0 EVERY turn (0x46b90).
      CONSEQUENCES: the S9 q law's input is a COMPRESSED accrual — the
      player's first ~117 turns on headless seed 5 run bucket 0 (home RES
      channel 0 by income-law T34; measured --dbg-res), so q=2 for many
      turns is FAITHFUL, and the port's old RAW add over-accrued for every
      bucket >= 2. Ported campaign.cpp researchPhase + incomeAndGrow; pins
      tests/test_resapply_trsv2w.cpp x4 (mutation-verified M1 pow->raw,
      M2 round, M3 strict-<, M4 zero-gate); instrument --dbg-res. Witness
      scripts/tRSV2w_witness.sh VERDICT PASS (grown fill q 2->3, seed 5,
      --autoplay). SEAM TRSV2w-A: the port KEEPS progress across a
      re-queue where the vendor zeroes it (0x46b90 leg unmodelled).


## 10. tPF-7 CONTROL LAW — HOLD-WITHOUT-LATCH + PUMP 0x3a AT ~29/s (2026-11-26)
D28 items 16/17/18 ("rotation too slow / buttons latch / scroll does
nothing"). Full working log docs/re/_wip_tPF7.md P1-P7; headline laws:
- PRESS TABLE (0x47b44..0x47c42, masks 0xf7/0xfb/0xfd/0xfe) was already
  ported faithfully — the complaint was NEVER the press table.
- RELEASE LEG (the missing half): framework msg 0x38/0x39 -> handler
  0x47d3b `latch &= ~mask` clears the released control's bit pair; press
  tail 0x47c48 (kind ebp==4) SCHEDULES that release via 0x5669c. Vendor
  help resmove states the resulting feel verbatim: "Use the right mouse
  button if you want to move or rotate continuously." Port: SDL_BUTTON_UP
  -> ResCam::releaseRot/releaseMove (resHold tracker, ui.cpp).
- PUMP = msg 0x3a (NOT cosmos's 0x3b), self-scheduled at reswin init
  (0x47713 -> 0x56374 with INTERVAL 0) and fired by the framework loop
  0x56608 (`cmp DAT_000a2044,[slot+0x12]`; repeat-add interval=0 => fires
  every pass). LOOP RATE derived from two cited measurements: live cosmos
  pump 58.5 deg/s (tNG-S S30-X5) / 2 deg cosmos delta (t416 F2) = 29.25
  passes/s => kPumpMs=34. The old kSpinTickMs=1000 rested on a t302 MISREAD
  ("within ~1 s" first-fire latency, flagged 'NOT yet a law') -> research
  controls ran 29x slow (same family as the tNG-R S28 30x cosmos defect).
- FLOAT[0x9f108] (pump magnitude multiplier) MEASURED = 1.0 EXACTLY in
  4233/4233 banked saves (scripts/tPF7_zoomscale_census.py); the earlier
  "~0 denormal" note (_wip_tNGS S12) was an offset misread.
- SHIPPED + PINS: test_rescontrols_tpf7 x4, suite 572->576/0/0; MUTATION
  5/5 CAUGHT (M1 cadence 1000: 4 fails; M2 release no-op: 11; M3 pair-bleed:
  3; M4 wiring removed: 2; M5 press polarity: 22; M5 first draft anchored
  the .h but pressPair lives in researchview.cpp — anchor the DEFINITION).
- WITNESS scripts/tPF7_witness.sh VERDICT PASS (seed 5): hold 4.75 s = 58
  centre re-logs (~12/s logged-change floor, cadence leg), freeze after
  clickup <= 1, no sticky latch after a plain click, latch 0 0 logged.
  Four existing research witnesses migrated to xsend clickdn/clickup +
  POLLLED hold (the sleep-6 idiom assumed the sticky 1 s latch).
- SEAMS: TPF7-A per-msg release mask split (0x38 vs 0x39; ship-safe =
  releasing control clears its own pair); TPF7-D direct fire-loop period
  measurement (expected 34.2 +-0.6 ms); tPF-7b cosmos/systemCam pumps still
  on kSpinTickMs=1000 (29x slow by this derivation — next research-screen
  adjacent task); user item 16 "feel" ruling may still land via a grade
  page (TPF7-C).

## 11. tPF-8 OPENING-RESEARCH + REST-VISIBILITY LAW (2026-11-26, D28 item 21)

THE LAW (three legs, all cited):
  (a) START MASK: the vendor begins with ZERO known techs for every race.
      MEASURED [verified]: mask byte ds:0x7478e + 0x4b*i (the field the
      legality predicate 0x46d3c reads via dword[rec+0x47]>>24, tPF-8 raw
      disasm work/tPF8_legal.asm: owned-bit short-circuit 0x46d88; else
      all-prereqs-owned loop 0x46d91..0x46dd3, 0xFF-terminated = vacuously
      legal for roots) is 0x00 for all 66 rows x 8 races in 72/72 boot
      captures; progress words ds:0x764a0 all 0; studied words ds:0x76492
      = 0xffff (scripts/tPF8_startmask_census.py). The production-ring
      matrix saves show 0x0f on the roots LATER (races own them via play).
  (b) DRAW/EDGE GATE [verified, raw work/tPF8_gate.asm + tPF8_edge.asm]:
      loop head 0x48524 reads row word[win+0x913+2k]; 0x48566 calls
      0x46d3c(THIS row); je 0x48504 skips the ENTIRE body (shape word q,
      prereq-edge loop 0x48275..0x48383, study chip, node blit). An
      illegal row paints NOTHING. Edge(row->p) additionally requires
      0x4829f legality(p). => edge exists iff BOTH endpoints legal.
  (c) REST-CAMERA FRAME [inferred from cited constants; witnessed]: roots
      are column k=0 (Y=30k+15*(i&1) in {0,15}); y = chop(1194.256*Y/Z+0.5)
      +240 over Z_cam in [127,173] gives 240..381 — INSIDE the RESWIN clip
      (7,46)-(476,472). Witness centres (63,239)/(406,239)/(234,343).

CONSEQUENCES: at game start the screen is EXACTLY three root disks (rows
0 Orbital Structures, 2 Tonklin Diary, 6 Xenobiology), zero lines, zero
other circles — the direct theorem of (a)+(b), i.e. D28 item 21 verbatim.
The frontier is clickable WITHOUT dollying (seam TRSV1c-D CLOSED: the
off-frame-at-rest frontier was the port's wrong owned set, not the camera).

PORT DEFECT FIXED: campaign.cpp constructor granted ownedTech rows 0/1/2
to every owner — an uncited pre-t45 default ("banked open"). Now deleted;
pins test_starttech_tpf8 x5 (zero mask, frontier=={0,2,6}, zero edges +
anti-vacuity, roots on-frame, retired-name + both-edge-gate wiring).
Mutation 4/4 caught (scripts/tPF8_mutate.sh). Witness
scripts/tPF8_witness.sh + tPF8_rest_census.py VERDICT PASS (seed 5: first
available centre row 0 at (64,240), no dolly; exactly 3 ring comps n=828,
0 strays). tRSB1 re-run PASS (study row 0, panel-green 0->754).
Census crop law: exclude y=46 (header line) and y>=456 (panel row) —
chrome the tree law does not constrain.
OPEN RESIDUE (named): early-AI lethality on smoke seeds (seed 42 Extinct
t10) — the zero-mask start changes early dynamics; finiteness holds on all
recorded runs (PLAYTHROUGH tPF-8 block), per-seed outcomes are not law.
