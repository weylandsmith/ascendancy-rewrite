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

1. Place N stars (default **75** = snapshot; configurable 30..200).
   Positions: uniform on a 1024x1024 logical map (snapshot coord bounds
   <=639x479, §3; we use a power-of-two grid and scale at render — choice,
   OQ-012), rejection-sampled to a minimum separation of 60 units so lane
   geometry stays readable (choice).
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

- UI map-size options (the original's new-game config strings are glyph
  data in `3cfgnew.tmp`, not text — no size knobs recoverable statically).
- Planets-per-star distribution shape beyond uniform.
- Whether star positions influenced type (hub-stars central?) — no
  position/type joint evidence in the snapshot strings.
- galactic.bin column semantics (OQ-004, runtime-dependent).
