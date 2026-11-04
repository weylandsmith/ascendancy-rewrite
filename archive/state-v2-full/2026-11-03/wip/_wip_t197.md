# _wip_t197 — SHP span-bound correction: validator X-class + rewrite decode()

## Trigger triage
- work/r1/playcap/live-timeline.jsonl: size 5,721,578,066 == frozen BASE_SIZE,
  mtime 1793294532 (+ .100000000 ns per t194 re-freeze). NO new sitting ->
  assigned task t197 stands.
- Tree at session start: `?? tools/shp_partialdump` ONLY — the t196 C++
  renderer binary (build artifact of tools/shp_partialdump.cpp, which IS
  committed). Adopt = gitignore it (parity with tools/shp_pngdump, already
  ignored) so the tree is clean; no uncommitted source was orphaned.

## Task (docs/STATE.md:256-298)
1. scripts/r1_shp_unifiedlaw.py: add tag X = canonical stream slot + canonical
   dims + EXACT-H row walk with NO [rec,nxt) bound; keep V/A/B + FAIL
   otherwise; paint-profile note per X record. Re-run corpus -> V/A/X/FAIL.
2. rewrite/src/formats/shp.cpp decode(): drop the directory-span walk bound
   (cache is a verbatim whole-library copy; blit FUN_0005caac has no length
   arg and no overrun error -1@0x5cb2b dims / -2@0x5cb36 empty clip /
   -3@0x5cea5 outside only). KEEP the 4096 W/H sanity clamp. Contract comment:
   rows past the span are real resident stream bytes; destination semantics
   unchanged. Pin test.
3. Regenerate work/r1/shp_png via scripts/r1_t182_pngdump.py + ids.tsv X-tags;
   update numbers cited in OPEN-QUESTIONS OQ-005 and shp.md S18/S20.

## Expected numbers (from t196, to be re-measured not assumed)
X-class 29 = planind k0..k12 (13) + 3cfgnew k0..k11 (12) + 14intel k8 (1) +
1starmap k3/k4/k6 (3). Still-rejected 42: cos_star k40..k51 (12, dims word 0),
26 zero-stream EMPTY slots, mouse k6/k7 (dims 0), 1starmap k1 (dims
0x7FFFFFFB-class), sg50expl k9, 3cfgnew k12 (EOF-truncated 55/79 rows).

## Log
- (appending as probes land)

## S1. Validator X-class [verified, scripts/r1_shp_unifiedlaw.py rerun]
rec_state gained tag X (+XS for swapped-only; ZERO XS in corpus): canonical
stream slot (rec+8 k0 / rec+0x18 k>=1) + canonical dims (rec / rec+0x10),
both sanity-clamped 0<v<=4096, EXACT-H row walk, NO [rec,nxt) bound, file EOF
the only hard bound. V/A/B evaluated first with the bound -> X only promotes
former FAILs, demotes nothing.
CORPUS MEASURED (2026-10-29, this session): 208 libs; V 197 + A 1289 +
X 29 + FAIL 42 = 1557 records; libraries passing EVERY record 188/208 (was
186; the two newly-clean libs are exactly planind (13 FAIL->13 X) and 14intel
(1 FAIL->X)). FAIL 42 by file: cos_star 12, mouse 2, and 28 singles —
1starmap k1, 3cfgnew k12, sg50expl k9 + the zero-stream EMPTY class (destroy
k14, expl00 k9, expl01 k8/9, expl03 k0/9, expl04 k0/9, expl05 k9, expl07 k0,
expl08 k0/9, orbex00 k8/9, sg37/45/47/49expl k0+k9, sg66expl k0/k9, sg70expl
k9). X set is EXACTLY the
t196 EXACT-H set: planind k0..k12, 3cfgnew k0..k11, 14intel k8, 1starmap
k3/k4/k6 -> 29. 3cfgnew k12 fails the UNBOUNDED walk too (EOF truncation,
55/79 rows) — honest remainder confirmed, not a bound artifact.
Paint profiles (--profiles flag, per X record): 1starmap tails 1-5 rows /
<=11 B past span; planind tails 4-22 rows / 114-2032 B; 3cfgnew tails 24-25
rows / ~0.9-1.5 kB.

## S2. WHAT past-span rows actually paint [verified, scripts/r1_t197_pastrows{,2}.py]
Decoding the 29 X records unbounded into the W x H plane:
  - past-span rows WRITE pixels: planind k0 past-22-rows = 40 distinct
    palette indices, index-0 fraction 0.014 (top values 20 c5 c6 01 42 = the
    factory art's own soil/metal ramp). 3cfgnew tails 21-92 distinct indices.
  - They are NOT the next record's leading rows: row-sim(past -> rec k+1
    row0) 0.21-0.98 (median ~0.5) with the control sim(past -> own row0) at
    the SAME level — no reproduction of the successor frame.
  - 14intel/1starmap tails are near-blank (frac0 0.96-1.00): transparent-ish.
  => CORRECTION to t196 S20.2 phrasing: "past-span rows are transparent
  garbage / planind rows 96-98 all-zero" came from the PARTIAL DUMPER
  (tools/shp_partialdump stops at span exhaustion and never paints past rows)
  — the vendor-law walk PAINTS the planind/3cfgnew bottom bands by desyncing
  into the next record's bytes. Whether the game's screen ever SHOWS those
  bands (blit clipping, or the widget only using 84-row frames) is a
  paint-routine question that stays with the queue item PER-PLANET ECONOMY
  FIELDS + GAUGE LIBRARY LAW. Decoding faithfully (what the blit computes from
  resident bytes) does not depend on it.
  TOOL PITFALL [verified]: r1_t197_pastrows2.py first run printed nothing —
  `[r for (st,r) in enumerate(rows)]` silently unpacked (idx, st) as (st, r);
  enumerate unpack MUST be (idx, value). Cross-check any list-comp filter with
  a second loop form before trusting a null result.

## S3. Dims-gate unification + parity numbers [verified BOTH SIDES]
The V/A trials in rec_state skipped a garbage dims COMPONENT with `continue`
and walked the other orientation anyway; the rewrite decode() requires BOTH
pair components in (0,4096] (models blit -1/-2 error branches). Two records
diverged corpus-wide: mouse k5 (W=0,H=46 — t196 already flagged its stream as
real but dims broken) and sg64expl k0 (W=18,H=0xfffffffb). Python demoted
both to FAIL; Python validator now == C++ decode EXACTLY.
FINAL NUMBERS [measured, this session]: V 196 + A 1288 + X 29 + FAIL 44 =
1557; libs clean 187/208; rewrite corpus test prints 208/1557/1513-pass/187 —
112 tests 0 failed (test_shp.cpp floors RAISED to 1513/187).
Pre-t197 for the record: Python 1486 pass/186 clean, C++ 1484/185.
Net motion: +27 pass (X29 minus 2 dims demotions), +1 clean lib (planind;
14intel already clean? no — planind+14intel became clean from FAIL, while
sg64expl left the clean set; net +1). TEST shp_span_free_t197 pins both
sides: planind k0 full 99-row decode, deterministic, tail band written,
canonical orientation; 3cfgnew k0..k11 decode / k12 rejected (EOF);
1starmap k1 + mouse k6/k7 rejected (garbage dims); 14intel k8 + 1starmap
k3/k4/k6 decode.
NOTE (clean-lib arithmetic, checked): 186 pre -> planind clean (13 FAIL->X),
14intel clean (1 FAIL->X), sg64expl NOT clean (k0 dims demotion) = 187.
