# P4 spec — map generation (galaxy generator)

All evidence is from extracted files; offsets quoted as `file+decimal`.
No claim here needs the exe (docs/re/loader.md §4 makes exe data-lifting a
runtime-only operation; this system is derivable from data + snapshot).

## 1. Star types and lane rates [verified]

`extracted/ascend00/starstat.txt` (471 B, CP437, tab/space separated),
13 rows, grammar `TYPE_<n>\t<pct> Percent\t<lanes> Lanes`:

| type | percent | mean lanes |
|---|---|---|
| 0 | 12.57 | 2.62 |
| 1 | 3.14 | 2.59 |
| 2 | 5.55 | 2.57 |
| 3 | 5.55 | 2.60 |
| 4 | 10.35 | 2.20 |
| 5 | 12.38 | 2.10 |
| 6 | 13.31 | 2.18 |
| 7 | 8.50 | 2.15 |
| 8 | 4.07 | 2.05 |
| 9 | 5.73 | 2.16 |
| 10 | 1.48 | 1.62 |
| 11 | 9.06 | 2.04 |
| 12 | 8.32 | 2.04 |

Percent column sums to 100.01 (rounding at 2 dp) [verified]; mean of the
lanes column = 2.225; min 1.62 (isolated type 10), max 2.62 (hub type 0).
`lanes` is mean star-lane degree for that star type.

## 2. Star names [verified]

`extracted/ascend00/names.txt`, 100 single-line bases (Vega, Algol, ..., Bindacia; the file ends with two blank lines and a 0x1A EOF marker — a naive strip counts 101, the C-side C-isspace trim counts 100; unique, verified),
no numbering). The generator appends Roman numerals ONLY to planets:
every `"<Base> <roman>"` string found in the galaxy snapshot has its base
in names.txt (223/223 strings, 75/75 distinct bases) [verified 2026-10-04].

## 3. Galaxy shape, measured from the golden snapshot [verified for this save]

`extracted/ascend02/galactic.tsv` is the string pool of a saved/seeded
galaxy (116,022 B; also holds a u32 data area whose layout is OQ-004).
String evidence [verified]:

- 75 distinct star bases ("Parsimony", "Yorbins", ...); **223** planet strings
  (erratum 2026-10-04: an earlier revision of this file said 177, from a
  scan that is not reproducible; re-measured NUL-delimited: 223 total,
  histogram below sums to 223).
- Orbit numerals observed: I 75, II 58, III 46, IV 31, V 13; **never VI+**.
  Orbit I count == star count exactly (75) -> orbits are contiguous from I.
  75+58+46+31+13 = 223 = the planet-string count [verified].
- Planets-per-star histogram: {1:17, 2:12, 3:15, 4:18, 5:13} — consistent
  with a uniform 1..5 draw; no zero-planet star observed in this snapshot.
- `galactic.bin` (1028 records x 6 u32): cols 3/4 are bounded (0..639,
  0..479 — coordinate-shaped), col0 ranges 26..2065 with 836 distinct.
  Semantics remain OQ-004; NOT used by our generator, listed for context.

## 4. Generator model we implement [inferred decisions, cited]

Default campaign parameters below come from the snapshot (§3) and the
starstat table (§1). The connective ALGORITHM (edge selection) is NOT in
any extracted file — it is our documented choice, constrained to match the
measured degree statistics:

1. Place N stars (default **50** = fresh campaigns measured 5/5,
   docs/re/r1-savestate.md 2026-10-06p; configurable 30..100).
   Positions [MEASURED 2026-10-06p, supersedes the earlier uniform-box
   choice]: star at table slot k sits at radius SHELL[k] from the map centre
   in a uniformly random direction. SHELL = 440 (k 0..25), 365 (26..37),
   290 (38..43), 215 (44..46), 140 (47), 65 (48), 50 (49) — populations
   26/12/6/3/1/1/1, radius identity exact-float across 5 campaigns with 0
   inversions of 1225 pairs. NO minimum separation (closest observed pair
   24.4 < old 60 choice; rejection sampling removed). The original is 3D
   (sphere r=440 shells, uniform-on-sphere direction); the rewrite keeps its
   documented 2D model — the xy-projection of a uniform-on-sphere direction
   is uniform in angle, so one uniform angle reproduces the projected law.
   Scale note: default mapSize 1024 keeps radii at ORIGINAL values (centre
   512,512, outer shell 440 <= 512-60); maps smaller than 2*(440+pad)
   scale ALL shells uniformly by (mapSize/2 - pad)/440 so ordering and
   populations are preserved (choice; OQ-012(a) may pin other sizes).
2. Star type: weighted draw from the §1 percent column.
3. Planets per star: **uniform 1..5** (choice, uniform-vs-biased indistingui-
   shable from the §3 histogram at n=75; OQ-012). Orbit index = index+1,
   numeral I..V; home race's first colonisable choice is a diplomacy/P6
   concern, not generation.
4. Lanes: target = sum over stars of the type mean from §1. Build a nearest-
   neighbour spanning tree first (guarantees connectivity — the original
   cannot have shipped disconnected space or interstellar movement breaks,
   inferred), then add distance-ascending edges while sum(deg)+2 <= target
   AND deg(x)+1 <= mean(type(x)) for both endpoints (the per-endpoint cap is
   what keeps distance-greedy from inflating hubs; realised mean degree lands
   within +-0.35 of 2.225 over 40 seeds — pinned by unit test). No
   multi-edges; no self-loops.
5. Naming: stars = shuffled names.txt bases (unique); planets =
   `"<star base> <roman>"` matching the §3 string shape exactly.
6. Everything seeded: std::mt19937 from a u64 campaign seed; same seed ->
   byte-identical galaxy (contract requirement).

Implementation: `rewrite/src/game/starstat.{h,cpp}`,
`rewrite/src/game/mapgen.{h,cpp}`; tests
`rewrite/tests/test_mapgen.cpp` (14/14 green via gate stage 4/5).
Deviation policy: unit tests pin §1 table load (13 rows, pct sum within
0.02 of 100), determinism, connectivity, orbit contiguity I..k, planets in
1..5, name uniqueness, lane simplicity, and realised mean degree within
+-0.35 of the table mean 2.225 over 40 seeded galaxies.
Erratum recorded here (was in earlier draft of this doc): names.txt has
**100** bases, not 101 — the 0x1A EOF marker is not whitespace to a C
isspace-trim, and the original Python count `strip()`ped it as a line.

## 5. Open [-> OPEN-QUESTIONS OQ-012]

- UI map-size options: CLOSED-BY-MEASUREMENT 2026-10-12 (t78, below) —
  GALAXY_MORE button cycles five densities with measured star totals.
- Planets-per-star distribution shape beyond uniform. (OQ-012(b) closed.)
- Whether star positions influenced type (hub-stars central?) — no
  position/type joint evidence in the snapshot strings.
- galactic.bin column semantics (OQ-004, runtime-dependent).

## OQ-012(a) CLOSED — density cycle measured live (t78, 2026-10-12)

The setup screen's GALAXY_MORE button (windows.txt NEWGAMEWND child, rect
7,381..122,472 -> click (64,426)) CYCLES five galaxy densities; total star
count DAT_00016143>>16 (pointer law, per-slot anchor vote >=5) per click
count N, fresh New Game each arm (harness scripts/r1_t78c_cycle.sh, reader
scripts/r1_t78_read.py; preview labels read off screenshot crops):

  N=0  "Average Star Cluster"         T=50   (r1size-033341, 040859)
  N=1  "Dense Star Cluster"           T=75   (r1size-041459; label 034418)
  N=2  "Very Dense Star Cluster"      T=100  (r1size-042719)
  N=3  "Vacuous Star Cluster"         T=15   (r1size-043229)
  N=4  "Sparse Star Cluster"          T=25   (r1size-044658)
  N=5  "Average Star Cluster" (wrap)  T=50   (r1size-045501)

Five-state cycle: Average -> Dense -> Very Dense -> Vacuous -> Sparse ->
Average. Order is the click-cycle order; N=3/N=4/N=5 prove the control
WRAPS (no ceiling monotonicity). Slot-value law note: in-campaign slots carry the
armed T while pre-entry/post-quit slots read 50 (default), so each arm's
in-game majority T is the measured value.

POSITION LAW AT NON-DEFAULT T does NOT extend the §4.1 exact shell-slot
schedule: over the T=100 chain (stride-96 records, idx==k verified 0..99,
names Zoroaster.. genuine) slot-vs-radius inversions are 3537/4950
(r1size-042719 slot 41; scripts/r1_t78_shell.py) vs 0/1225 at T=50.
Radii still respect the outer envelope (max <= 440.0). The rewrite's
cycled-kShellR extension for non-default starCount (mapgen.cpp:92 comment)
is therefore a DOCUMENTED DEFAULT, not a closed law — OQ-012(a) closes the
SIZE OPTIONS question; the non-default position sub-law stays banked here
as open sub-item (caveat) without holding the ledger.

Rewrite upgrade: --stars CLI knob (main.cpp Options) so campaign runs can
play all five measured densities; default remains 50 = "Average"
(measurement-consistent, mapgen.h:50 comment re-cited).

## OQ-012(a) static value-path probe — NULL (t56 cycle)

Full re-decompile of the galaxy-fill driver FUN_000238e8 confirms the ONLY
map-size-shaped quantity in it is per-star pps = rng%5+1 (banked OQ-012(b));
the loop terminates on `(*(int)(&DAT_00003333 + base*4) >> 16) <=
star_index` where base walks the scenario table (stride 0x1ee) — i.e. a
PER-SCENARIO star cap from a runtime-initialised table whose image bytes at
VA 0x3333 are mid-instruction noise (0x0a 02 aa d3, R7 pattern), NOT a
static constant. Total star count is therefore runtime/scenario-capped, and
the new-game SIZE OPTION's numeric effect is not reachable through any
static constant in the image. Closing route (one observation): default-size
new-game run (New Game click banked at (318,333), docs/re/refcap.md:21),
campaign-entry detection via the grid-hash law, then COUNT stars in fresh
campaign RAM — size->star-count data point; repeated per option only if the
first two differ.
STATIC LEADS ALSO NEGATIVE (t57 prep): message-id 501 appears as NO
CMP-immediate/PUSH-immediate anywhere in the image (dispatch not visible to
the generalized immediate sweep — do not re-sweep); option display names
(Tiny/Enormous/Star Density) absent from the image (glyph/shp-resident,
consistent with R13 no-screenshot law). Launch: scripts/r1_t57_density.sh,
click (65,427) = GALAXY_MORE center between New Game tour click and start
re-fire; measurement via banked star-table law on entry checkpoint.
